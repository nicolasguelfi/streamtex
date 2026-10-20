"""The gestures of ``stx release``, on a target — the prototype's ``publish.py``, its server layout kept.

On the target (``<root>`` of the target, ``/srv/<face>`` in the containers)::

    static/sites/<site>/releases/<release>/   the HTML export of a release
    static/sites/<site>/current -> releases/<release>
    static/sites/<site>/pass                  the HTML face's password records (or "open")
    live/sites/<site>/releases/<release>/     the code snapshot (its media folder a link to live/media)
    live/sites/<site>/current -> releases/<release>
    live/sites/<site>/pass                    the live face's records
    live/sites/<site>/static -> current/<doc>/static   the site's media, served by the router
    live/media/<project>/<media>/             the project's media, shared by every snapshot
    live/conf/programs/<site>.conf            the site's supervisord program
    live/conf/ports.map                       site → port, read by the router

Both faces switch together (all or nothing); a failed check after the switch puts both back on the
previous release. Two releases are kept per site: the current one and the previous one.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import shlex
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from . import ReleaseError, build
from . import passwords as pw
from .config import ReleaseConfig, Site
from .state import save_state, sites_of
from .target import LIVE_ROOT, Target

TEMPLATES = Path(__file__).parent / "templates"
Echo = Callable[[str], None]


def _faces_dirs(site: Site) -> list[str]:
    return [{"html": "static", "live": "live"}[f] for f in site.faces]


def program_conf(cfg: ReleaseConfig, site: Site, port: int) -> str:
    cur = f"{LIVE_ROOT}/sites/{site.site}/current"
    env = ['HOME="/tmp"']
    if cfg.pythonpath:
        env.insert(0, 'PYTHONPATH="' + ":".join(f"{cur}/{p}" for p in cfg.pythonpath) + '"')
    return (f"[program:{site.site}]\n"
            f"directory={cur}/{site.doc_dir}\n"
            f"command=/app/.venv/bin/streamlit run {Path(site.book).name} --server.port={port} "
            f"--server.address=127.0.0.1 --server.headless=true\n"
            f"environment={','.join(env)}\n"
            "autostart=true\nautorestart=true\nstartsecs=5\nstopasgroup=true\n"
            "stdout_logfile=/dev/stdout\nstdout_logfile_maxbytes=0\nredirect_stderr=true\n")


def write_maps(t: Target, state: dict) -> None:
    sites = sites_of(state, t.name)
    t.write(t.path("live", "conf", "ports.map"),
            "".join(f"{s} {v['port']};\n" for s, v in sorted(sites.items())
                    if v.get("port") and not v.get("asleep")))


def switch(t: Target, site: Site, release: str) -> None:
    for face in _faces_dirs(site):
        t.sh(t.switch_cmd(t.path(face, "sites", site.site), release))


def reload_all(t: Target, site: Site | None = None) -> None:
    t.dexec("static", "nginx -s reload")
    t.dexec("live", "nginx -s reload")
    t.dexec("live", "supervisorctl reread")
    t.dexec("live", "supervisorctl update")
    if site is not None and "live" in site.faces:
        t.dexec("live", f"supervisorctl restart {site.site}", check=False)


def apply_passwords(t: Target, cfg: ReleaseConfig, state: dict, site: Site, faces: dict) -> None:
    """The record files of the site's faces; changing them closes the open sessions of that face."""
    v = sites_of(state, t.name)[site.site]
    if "html" in site.faces:
        v["html_open"] = faces["html"] is None
        t.write(t.path("static", "sites", site.site, "pass"), pw.pass_text(faces["html"]), mode=0o600)
    if "live" in site.faces:
        t.write(t.path("live", "sites", site.site, "pass"), pw.pass_text(faces["live"]), mode=0o600)
        t.write(t.path("live", "conf", "programs", f"{site.site}.conf"), program_conf(cfg, site, v["port"]))


def served(t: Target, site: Site, v: dict, html_password: str) -> tuple[str, str]:
    """(what the HTML face serves: its release or HTTP code, the live face's health) — as a visitor."""
    html = "-"
    if "html" in site.faces:
        cookie = "" if v.get("html_open") else t.login(site.site, html_password)
        code, body = t.get("static_url", site.site, "/html/version.txt", cookie=cookie)
        html = body.splitlines()[0] if code == 200 and body else f"HTTP {code}"
    live = "-"
    if "live" in site.faces:
        live = "asleep" if v.get("asleep") else \
            ("ok" if t.get("live_url", site.site, "/_stcore/health")[0] == 200 else "down")
    return html, live


def wait_live(t: Target, site: Site, seconds: int = 90) -> bool:
    for _ in range(max(1, seconds // 3)):
        if t.get("live_url", site.site, "/_stcore/health")[0] == 200:
            return True
        time.sleep(3)
    return False


def prune(t: Target, site: Site, keep: set[str]) -> list[str]:
    """Keep only the releases *keep* of a site (rsync --link-dest hard links make removal safe)."""
    removed: list[str] = []
    for face in _faces_dirs(site):
        base = t.path(face, "sites", site.site, "releases")
        for r in t.sh(f"ls -1 {shlex.quote(base)} 2>/dev/null", check=False).stdout.split():
            if r not in keep:
                t.sh(f"rm -rf {shlex.quote(base + '/' + r)}")
                removed.append(f"{face}/{r}")
    return removed


def publish_site(t: Target, cfg: ReleaseConfig, state: dict, site: Site, release: str, faces: dict,
                 echo: Echo, html_env: dict[str, str] | None = None, skew: str = "") -> None:
    echo(f"\n▶ {site.site} @ {release} ({t.name})")
    entries = sites_of(state, t.name)
    v = entries.setdefault(site.site, {})
    previous = v.get("release")
    check_dir = t.path(_faces_dirs(site)[0], "sites", site.site, "releases", previous) if previous else ""
    if previous and t.sh(f"test -d {shlex.quote(check_dir)}", check=False).returncode:
        previous = None          # the recorded release is not on this target: no hard link, no rollback to it
    if "live" in site.faces and not v.get("port"):
        v["port"] = max([cfg.port_base - 1] + [s.get("port") or 0 for s in entries.values()]) + 1
    with tempfile.TemporaryDirectory(prefix="stx-release-") as w:
        work = Path(w)
        code = build.snapshot(cfg, site, work)
        html = build.export(cfg, site, code, work, release, html_env) if "html" in site.faces else None
        if "live" in site.faces:
            dirs = [t.path("live", "sites", site.site, "releases")]
            if cfg.media:
                dirs.append(t.path("live", "media", cfg.project))
            t.sh("mkdir -p " + " ".join(shlex.quote(d) for d in dirs))
            if cfg.media and (cfg.root / cfg.media).is_dir():
                excl = [x for pat in cfg.media_exclude for x in ("--exclude", pat)]
                t.rsync(str(cfg.root / cfg.media) + "/", t.path("live", "media", cfg.project, cfg.media) + "/", *excl)
                media = code / cfg.media
                if media.is_symlink() or media.is_file():
                    media.unlink()
                elif media.is_dir():
                    import shutil
                    shutil.rmtree(media)
                media.parent.mkdir(parents=True, exist_ok=True)
                media.symlink_to(f"{LIVE_ROOT}/media/{cfg.project}/{cfg.media}")
            t.rsync(str(code) + "/", t.path("live", "sites", site.site, "releases", release) + "/", "--delete")
        if html is not None:
            t.sh("mkdir -p " + shlex.quote(t.path("static", "sites", site.site, "releases")))
            link = (["--link-dest", t.path("static", "sites", site.site, "releases", previous)]
                    if previous and previous != release else [])
            t.rsync(str(html) + "/", t.path("static", "sites", site.site, "releases", release) + "/",
                    "--delete", "-H", "-c", *link)
        rel_dirs = " ".join(shlex.quote(t.path(f, "sites", site.site, "releases", release))
                            for f in _faces_dirs(site))
        t.sh(f"chmod -R a+rX {rel_dirs}")
    if "live" in site.faces:
        t.sh(f"ln -sfn {LIVE_ROOT}/sites/{site.site}/current/{site.doc_dir}/static "
             f"{shlex.quote(t.path('live', 'sites', site.site, 'static'))}")
    apply_passwords(t, cfg, state, site, faces)
    write_maps(t, state)
    switch(t, site, release)                      # both faces TOGETHER
    reload_all(t, site)
    ok_live = wait_live(t, site) if "live" in site.faces else True
    html_seen, _ = served(t, site, v, pw.first_password(faces.get("html")))
    if not ok_live or ("html" in site.faces and html_seen != release):
        echo(f"  ✗ check after the switch: html={html_seen} live={'ok' if ok_live else 'down'}")
        if previous:
            switch(t, site, previous)
            reload_all(t, site)
            echo(f"  ↩ both faces are back on {previous}")
        raise ReleaseError(f"{site.site}: what is served is not {release}")
    v.update(release=release, previous=previous, date=dt.datetime.now().isoformat(timespec="seconds"),
             asleep=False)
    if skew:
        v["skew"] = skew
    else:
        v.pop("skew", None)
    save_state(cfg.root, state)
    echo(f"  ✓ {site.site}: html {html_seen}, live {'ok' if 'live' in site.faces else '-'}"
         + (f" — port {v['port']}" if v.get("port") else "")
         + ("" if "html" not in site.faces else f", html {'open' if v.get('html_open') else 'protected'}"))
    if removed := prune(t, site, {release, previous} - {None}):
        echo(f"  ⌫ {len(removed)} old release(s) removed: {', '.join(removed)}")


def rollback(t: Target, cfg: ReleaseConfig, state: dict, site: Site) -> str:
    v = sites_of(state, t.name).get(site.site)
    if not v:
        raise ReleaseError(f"{site.site} is not published on {t.name}")
    if not v.get("previous"):
        raise ReleaseError(f"{site.site}: no previous release")
    v["release"], v["previous"] = v["previous"], v["release"]
    switch(t, site, v["release"])
    reload_all(t, site)
    save_state(cfg.root, state)
    return v["release"]


def sleep_wake(t: Target, cfg: ReleaseConfig, state: dict, site: Site, asleep: bool) -> None:
    if "live" not in site.faces:
        raise ReleaseError(f"{site.site} has no live face")
    v = sites_of(state, t.name).get(site.site)
    if not v:
        raise ReleaseError(f"{site.site} is not published on {t.name}")
    v["asleep"] = asleep
    write_maps(t, state)
    t.dexec("live", f"supervisorctl {'stop' if asleep else 'start'} {site.site}", check=False)
    t.dexec("live", "nginx -s reload")
    save_state(cfg.root, state)


def status_rows(t: Target, cfg: ReleaseConfig, state: dict, data: dict | None) -> list[tuple]:
    rows = []
    for name, v in sorted(sites_of(state, t.name).items()):
        site = cfg.by_name.get(name)
        if site is None:
            rows.append((name, v.get("release", "?"), "not in stx.toml", "", "", v.get("date", ""), "  ← UNKNOWN"))
            continue
        password = ""
        if data is not None and not v.get("html_open") and "html" in site.faces:
            try:
                password = pw.first_password(pw.for_site(data, site)["html"])
            except ReleaseError:
                password = ""
        html, live = served(t, site, v, password)
        if html == "HTTP 401" and not password and not v.get("html_open"):
            html, flag = "? (no password)", ""         # cannot read it: unknown, not a gap
        else:
            flag = "" if "html" not in site.faces or html == v.get("release") else "  ← GAP"
        if v.get("skew"):
            flag += "  (skew)"
        access = "-" if "html" not in site.faces else ("open" if v.get("html_open") else "protected")
        rows.append((name, v.get("release", "?"), html, live, access, v.get("date", ""), flag))
    return rows


# -- the server configuration --------------------------------------------------------------

def _stx_auth_source() -> str:
    return Path(importlib.util.find_spec("streamtex.deploy.stx_auth").origin).read_text(encoding="utf-8")


#: What server-config sends, per application: file name → content.
def server_files(app: str) -> dict[str, str]:
    return {"stx-http.conf": (TEMPLATES / app / "stx-http.conf").read_text(encoding="utf-8"),
            "stx_auth.py": (TEMPLATES / "static" / "stx_auth.py").read_text(encoding="utf-8"),
            "stx_auth_lib.py": _stx_auth_source()}


AUTH_RESTART = {"static": "pkill -f stx_auth.py", "live": "supervisorctl restart stx_auth"}
_WAIT_AUTH = ("python3 -c \"import socket, time\nfor _ in range(50):\n    try:\n"
              "        socket.create_connection(('127.0.0.1', 9100), 0.5).close(); break\n"
              "    except OSError:\n        time.sleep(0.2)\nelse:\n    raise SystemExit(1)\"")


def server_config(t: Target, echo: Echo) -> None:
    """Both applications' configuration on the server disk: nginx checks it BEFORE reloading (no
    interruption); a refused configuration is removed and the old one stays in service. The login
    service is restarted, and we wait until it answers."""
    for app in ("static", "live"):
        conf, root = t.path(app, "conf"), f"/srv/{app}/conf"
        for name, content in server_files(app).items():
            t.write(f"{conf}/{name}.new", content, mode=0o644)
        test = t.dexec(app, f"sh -c 'cp {root}/stx-http.conf /tmp/stx-http.conf.old 2>/dev/null; "
                            f"cp {root}/stx-http.conf.new {root}/stx-http.conf && nginx -t'", check=False)
        if test.returncode:
            t.dexec(app, f"sh -c 'cp /tmp/stx-http.conf.old {root}/stx-http.conf'", check=False)
            raise ReleaseError(f"{app}: nginx refuses the new configuration — the old one stays in service:\n"
                               f"{test.stderr[-800:]}")
        t.dexec(app, f"sh -c 'mv {root}/stx_auth_lib.py.new {root}/stx_auth_lib.py && "
                     f"mv {root}/stx_auth.py.new {root}/stx_auth.py && rm -f {root}/stx-http.conf.new && "
                     f"nginx -s reload && {AUTH_RESTART[app]}'")
        if t.dexec(app, _WAIT_AUTH, check=False).returncode:
            raise ReleaseError(f"{app}: the login service does not answer after 10 s — see its logs")
        echo(f"{app}: configuration checked and reloaded without interruption; login service restarted")
