"""Where to publish: a ``local`` folder and two Docker containers (a trial), or a server over ``ssh``.

The same gestures on both; on ``ssh`` they are prefixed by ssh. Paths are those of the target machine;
``/srv/static`` and ``/srv/live`` are the volume as the containers see it.
"""

from __future__ import annotations

import functools
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import ReleaseError


def _user_agent() -> str:
    """Sent with every visitor check: a CDN in front of the sites (Cloudflare) answers 403 to Python's
    default ``Python-urllib`` agent, which a check would then read as a failed publication."""
    try:
        from importlib.metadata import version
        return f"stx-release/{version('streamtex')} (+https://streamtex.org)"
    except Exception:  # noqa: BLE001
        return "stx-release (+https://streamtex.org)"


LIVE_ROOT = "/srv/live"
STATIC_ROOT = "/srv/static"


#: The shared SSH connection's socket (%C: a hash of host, port and user — short enough for the socket
#: path limit).
CONTROL_PATH = "~/.ssh/stx-cm-%C"

#: A connection cut while it opens, before any command ran (#152): measured on 2026-10-29, a network device
#: between the machine and the server cuts the 20th connection opened within a few seconds, and every next
#: one for about a minute (once 50 s were not enough). Such a failure is retried after these waits (seconds).
RETRY_WAITS = (5, 15, 30, 60)
_CUT_AT_OPEN = re.compile(r"kex_exchange_identification|Connection (?:reset|closed) by \S+ port \d+")


def _run(argv: list[str], input: str | None = None) -> subprocess.CompletedProcess:
    """Run an ssh (or rsync over ssh) command; retry it when the connection was cut while opening."""
    for wait in (*RETRY_WAITS, None):
        r = subprocess.run(argv, input=input, text=True, capture_output=True)
        if not r.returncode or wait is None or not _CUT_AT_OPEN.search(r.stderr or ""):
            return r
        print(f"  the SSH connection was cut while opening; new try in {wait} s", file=sys.stderr, flush=True)
        time.sleep(wait)
    return r


@functools.cache
def _openrsync() -> bool:
    """Whether the local ``rsync`` is openrsync (macOS's own since Sequoia)."""
    try:
        r = subprocess.run(["rsync", "--version"], text=True, capture_output=True)
    except OSError:
        return False
    return "openrsync" in (r.stdout + r.stderr)


class Target:
    def __init__(self, name: str, cfg: dict):
        self.name, self.cfg = name, cfg
        self.kind = cfg.get("type")
        if self.kind not in ("local", "ssh"):
            raise ReleaseError(f"target '{name}': type must be 'local' or 'ssh'")
        if "root" not in cfg:
            raise ReleaseError(f"target '{name}': 'root' is required (the folder that holds static/ and live/)")
        self.root = cfg["root"]
        self.domain = cfg.get("domain", "streamtex.org")
        #: a provisional suffix of every address (``-next``: docs-advanced-next.example.org), to try a
        #: new installation next to the one in service; removed at the switch
        self.suffix = cfg.get("site_suffix", "")

    # -- commands -----------------------------------------------------------------------
    def ssh_argv(self) -> list[str]:
        """One shared connection for every command and copy (ControlMaster): new connections beyond about
        18 in a burst are cut (seen by all-trainings, 2026-10-26; by a network device on the way, #152)."""
        key = os.path.expanduser(self.cfg.get("ssh_key", ""))
        return ["ssh", *(["-i", key] if key else []), "-o", "BatchMode=yes",
                "-o", "ControlMaster=auto", "-o", f"ControlPath={CONTROL_PATH}", "-o", "ControlPersist=120",
                self.cfg["host"]]

    def sh(self, cmd: str, check: bool = True, input: str | None = None) -> subprocess.CompletedProcess:
        if self.kind == "local":
            r = subprocess.run(["sh", "-c", cmd], input=input, text=True, capture_output=True)
        else:
            r = _run([*self.ssh_argv(), cmd], input=input)
        if check and r.returncode:
            raise ReleaseError(f"{self.name}: `{cmd[:120]}` failed: {(r.stderr or r.stdout)[-600:]}")
        return r

    def path(self, *parts: str) -> str:
        base = os.path.expanduser(self.root) if self.kind == "local" else self.root
        return os.path.join(base, *parts)

    def rsync(self, src: str, dest: str, *opts: str) -> None:
        if self.kind == "local":
            if _openrsync() and "--link-dest" in opts:
                # macOS's own rsync stops on an assertion (io.c:900) with -H and --link-dest together when
                # the source holds hard links (all-trainings, 2026-10-26): keep --link-dest, the space
                # saving, and drop -H, which only matters for hard links inside one export
                opts = tuple(o for o in opts if o != "-H")
            argv = ["rsync", "-a", *opts, src, dest]
        else:
            ssh = " ".join(shlex.quote(x) for x in self.ssh_argv()[:-1])
            argv = ["rsync", "-a", "-e", ssh, *opts, src, f"{self.cfg['host']}:{dest}"]
        r = subprocess.run(argv, text=True, capture_output=True) if self.kind == "local" else _run(argv)
        if r.returncode:
            raise ReleaseError(f"{self.name}: rsync to {dest} failed: {r.stderr[-600:]}")

    def dexec(self, app: str, cmd: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run *cmd* in the container of *app* (``static`` or ``live``). Under Coolify the container's name
        changes on every deployment: it is found from the application's uuid (its name starts with it)."""
        uuid = self.cfg.get(f"{app}_uuid")
        name = f"$(docker ps -q --filter name={uuid} | head -1)" if uuid else shlex.quote(self.cfg[app])
        return self.sh(f"docker exec {name} {cmd}", check=check)

    def running(self, app: str) -> bool:
        """Whether the container of *app* (``static`` or ``live``) runs."""
        uuid = self.cfg.get(f"{app}_uuid")
        flt = f"name={uuid}" if uuid else f"name=^{self.cfg.get(app, app)}$"
        return bool(self.sh(f"docker ps -q --filter {shlex.quote(flt)} | head -1", check=False).stdout.strip())

    def write(self, dest: str, content: str, mode: int | None = None) -> None:
        if self.kind == "local":
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(dest).write_text(content, encoding="utf-8")
            if mode is not None:
                os.chmod(dest, mode)
            return
        cmd = f"mkdir -p {shlex.quote(os.path.dirname(dest))} && cat > {shlex.quote(dest)}"
        if mode is not None:
            cmd += f" && chmod {mode:o} {shlex.quote(dest)}"
        r = _run([*self.ssh_argv(), cmd], input=content)
        if r.returncode:
            raise ReleaseError(f"{self.name}: writing {dest} failed: {r.stderr[-400:]}")

    def switch_cmd(self, base: str, release: str, link: str = "current") -> str:
        """Point *link* (``current``, or ``limited``: #147) at ``releases/<release>`` atomically (rename
        over the old link)."""
        mv = "mv -fh" if self.kind == "local" and sys.platform == "darwin" else "mv -fT"
        return f"cd {shlex.quote(base)} && ln -sfn releases/{release} {link}.new && {mv} {link}.new {link}"

    # -- HTTP, as a visitor -----------------------------------------------------------------
    def url_of(self, base_key: str, site: str, path: str) -> tuple[str, str | None]:
        if self.kind == "local":
            return self.cfg[base_key] + path, f"{site}{self.suffix}.{self.domain}"
        sub = self.cfg.get(f"{base_key}_suffix", "")
        return f"https://{site}{self.suffix}{sub}.{self.domain}{path}", None

    def get(self, base_key: str, site: str, path: str, cookie: str = "") -> tuple[int, str]:
        url, host = self.url_of(base_key, site, path)
        req = urllib.request.Request(url, headers={"User-Agent": _user_agent()})
        if host:
            req.add_header("Host", host)
        if cookie:
            req.add_header("Cookie", cookie)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, ""
        except OSError as e:
            return 0, str(e)

    def login(self, site: str, password: str) -> str:
        """Log in to the HTML face as a visitor: the session cookie, or ``""``."""
        url, host = self.url_of("static_url", site, "/html/_login")
        data = urllib.parse.urlencode({"password": password, "next": "/html/"}).encode()
        req = urllib.request.Request(url, data=data, method="POST", headers={"User-Agent": _user_agent()})
        if host:
            req.add_header("Host", host)

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None

        try:
            headers = urllib.request.build_opener(NoRedirect).open(req, timeout=20).headers
        except urllib.error.HTTPError as e:
            headers = e.headers
        except OSError:
            return ""
        raw = headers.get("Set-Cookie", "") if headers else ""
        # stx_session=…, or stx_session_<key tag>=… for a session shared by the sites (#147)
        return raw.split(";", 1)[0] if re.match(r"stx_session(_[0-9a-f]{8})?=", raw) else ""


def target_of(state: dict, name: str | None) -> Target:
    name = name or state.get("default_target")
    if not name or name not in state.get("targets", {}):
        known = ", ".join(state.get("targets", {})) or "none"
        raise ReleaseError(f"unknown target '{name}' — targets in .stx-release.json: {known}")
    return Target(name, state["targets"][name])
