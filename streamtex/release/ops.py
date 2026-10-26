"""The gestures of ``stx release``, on a target — the prototype's ``publish.py``, its server layout kept.

On the target (``<root>`` of the target, ``/srv/<face>`` in the containers)::

    static/sites/<site>/releases/<release>/   the HTML export of a release
    static/sites/<site>/current -> releases/<release>          all the content
    static/sites/<site>/limited -> releases/<release>-s<n>     with a slide limit only (#146, #147)
    static/sites/<site>/pass                  the HTML face's password records (or "open")
    static/sites/<site>/full                  the labels that see all the content of a limited site
    live/sites/<site>/releases/<release>/     the code snapshot (its media folder a link to live/media)
    live/sites/<site>/current -> releases/<release>
    live/sites/<site>/pass                    the live face's records
    live/sites/<site>/static -> current/<doc>/static   the site's media, served by the router
    live/media/<project>/<media>/             the project's media, shared by every snapshot
    live/conf/programs/<site>.conf            the site's supervisord program
    live/conf/ports.map                       site → port, read by the router

Both faces switch together (all or nothing); a failed check after the switch puts both back on the
previous release. Two releases are kept per site: the current one and the previous one.

A slide limit (#146) is kept per site (``up_to_slide``): the HTML face then also holds
``<release>-s<last slide>`` (``html_release``, ``html_previous``), linked as ``limited``. The login
service opens it to every password not listed in ``full`` (#147); ``[admin]`` and the ``full`` labels
see ``current``, all the content. ``limit`` changes the limited release alone, from the release already
published: the live face, its program and the passwords stay as they are, so the participants' sessions
stay open; ``rollback`` after a limit undoes the limit alone.
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


def html_of(v: dict) -> str | None:
    """The release the participants see on the HTML face: the limited one (#146), else the site's."""
    return v.get("html_release") or v.get("release")


def switch(t: Target, site: Site, release: str, html_release: str | None = None,
           faces: list[str] | None = None) -> None:
    """Each face's ``current`` link on *release*; on the HTML face, ``limited`` on *html_release*."""
    faces = faces or _faces_dirs(site)
    for face in faces:
        t.sh(t.switch_cmd(t.path(face, "sites", site.site), release))
    if "static" in faces:
        switch_limited(t, site, release, html_release)


def switch_limited(t: Target, site: Site, release: str, html_release: str | None) -> None:
    """The HTML face's ``limited`` link on *html_release*; removed when the site has no limit."""
    base = t.path("static", "sites", site.site)
    if html_release and html_release != release:
        t.sh(t.switch_cmd(base, html_release, "limited"))
    else:
        t.sh(f"rm -f {shlex.quote(base + '/limited')}")


def server_records(t: Target) -> str:
    """Every record file already on the target, for :class:`passwords.RecordPool`."""
    files = " ".join(f"{shlex.quote(t.path(face, 'sites'))}/*/pass" for face in ("static", "live"))
    return t.sh(f"cat {files} 2>/dev/null", check=False).stdout or ""


def reload_all(t: Target, site: Site | None = None) -> None:
    t.dexec("static", "nginx -s reload")
    t.dexec("live", "nginx -s reload")
    t.dexec("live", "supervisorctl reread")
    t.dexec("live", "supervisorctl update")
    if site is not None and "live" in site.faces:
        t.dexec("live", f"supervisorctl restart {site.site}", check=False)


def apply_passwords(t: Target, cfg: ReleaseConfig, state: dict, site: Site, faces: dict,
                    full: frozenset[str] = frozenset(), pool: pw.RecordPool | None = None) -> None:
    """The record files of the site's faces, and the labels that see all the content; a changed
    password closes the open sessions of its label only."""
    v = sites_of(state, t.name)[site.site]
    pool = pool or pw.RecordPool()
    if "html" in site.faces:
        v["html_open"] = faces["html"] is None
        t.write(t.path("static", "sites", site.site, "pass"), pool.text(faces["html"]), mode=0o600)
        t.write(t.path("static", "sites", site.site, "full"), pw.full_text(faces["html"], full), mode=0o600)
    if "live" in site.faces:
        t.write(t.path("live", "sites", site.site, "pass"), pool.text(faces["live"]), mode=0o600)
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


def check_html(t: Target, site: Site, v: dict, entries: list | None, full: frozenset[str], release: str,
               html_release: str) -> list[str]:
    """What the HTML face serves to each view, as a visitor; the empty list when all is right."""
    if "html" not in site.faces:
        return []
    if v.get("html_open"):
        checks = [("everyone", "", html_release)]
    elif html_release == release:
        checks = [("everyone", pw.first_password(entries), release)]
    else:
        checks = [(view, word, want) for view, want in (("full", release), ("limited", html_release))
                  if (word := pw.view_password(entries, full, view)) is not None]
    problems = []
    for view, word, want in checks:
        seen, _ = served(t, site, v, word)
        if seen != want:
            problems.append(f"{view} sees {seen}, not {want}")
    return problems


def wait_live(t: Target, site: Site, seconds: int = 90) -> bool:
    for _ in range(max(1, seconds // 3)):
        if t.get("live_url", site.site, "/_stcore/health")[0] == 200:
            return True
        time.sleep(3)
    return False


def prune(t: Target, site: Site, keep: set[str], keep_html: set[str] | None = None) -> list[str]:
    """Keep only the releases *keep* of a site, and *keep_html* on its HTML face when it has its own
    (rsync --link-dest hard links make removal safe)."""
    removed: list[str] = []
    for face in _faces_dirs(site):
        base = t.path(face, "sites", site.site, "releases")
        kept = keep_html if face == "static" and keep_html is not None else keep
        for r in t.sh(f"ls -1 {shlex.quote(base)} 2>/dev/null", check=False).stdout.split():
            if r not in kept:
                t.sh(f"rm -rf {shlex.quote(base + '/' + r)}")
                removed.append(f"{face}/{r}")
    return removed


def publish_site(t: Target, cfg: ReleaseConfig, state: dict, site: Site, release: str, faces: dict,
                 echo: Echo, html_env: dict[str, str] | None = None, skew: str = "",
                 full: frozenset[str] = frozenset(), pool: pw.RecordPool | None = None) -> None:
    echo(f"\n▶ {site.site} @ {release} ({t.name})")
    entries = sites_of(state, t.name)
    v = entries.setdefault(site.site, {})
    previous = v.get("release")
    check_dir = t.path(_faces_dirs(site)[0], "sites", site.site, "releases", previous) if previous else ""
    if previous and t.sh(f"test -d {shlex.quote(check_dir)}", check=False).returncode:
        previous = None          # the recorded release is not on this target: no hard link, no rollback to it
    old_html = html_of(v) if previous else None
    static_rel = t.path("static", "sites", site.site, "releases")
    if old_html and "html" in site.faces and t.sh(
            f"test -d {shlex.quote(static_rel + '/' + old_html)}", check=False).returncode:
        old_html = None
    limit = v.get("up_to_slide")                  # kept: a publication does not open the whole document (#146)
    html_release = release
    if "live" in site.faces and not v.get("port"):
        v["port"] = max([cfg.port_base - 1] + [s.get("port") or 0 for s in entries.values()]) + 1
    with tempfile.TemporaryDirectory(prefix="stx-release-") as w:
        work = Path(w)
        code = build.snapshot(cfg, site, work)
        html = limited = None
        if "html" in site.faces:
            html, _ = build.export(cfg, site, code, work, release, html_env)
            if limit is not None:              # the participants' release beside the whole one (#147)
                (work / "limited").mkdir()
                limited, html_release = build.export(cfg, site, code, work / "limited", release, html_env, limit)
                echo(f"  slide limit kept: slides 1 to {html_release.rsplit('-s', 1)[1]} (asked: {limit})")
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
            t.sh("mkdir -p " + shlex.quote(static_rel))
            link = ["--link-dest", f"{static_rel}/{previous}"] if previous else []
            t.rsync(str(html) + "/", f"{static_rel}/{release}/", "--delete", "-H", "-c", *link)
        if limited is not None:
            t.rsync(str(limited) + "/", f"{static_rel}/{html_release}/", "--delete", "-H", "-c",
                    "--link-dest", f"{static_rel}/{release}")
        rel_dirs = " ".join(shlex.quote(t.path(f, "sites", site.site, "releases", release))
                            for f in _faces_dirs(site))
        if limited is not None:
            rel_dirs += " " + shlex.quote(f"{static_rel}/{html_release}")
        t.sh(f"chmod -R a+rX {rel_dirs}")
    if "live" in site.faces:
        t.sh(f"ln -sfn {LIVE_ROOT}/sites/{site.site}/current/{site.doc_dir}/static "
             f"{shlex.quote(t.path('live', 'sites', site.site, 'static'))}")
    apply_passwords(t, cfg, state, site, faces, full, pool)
    write_maps(t, state)
    switch(t, site, release, html_release)        # both faces TOGETHER
    reload_all(t, site)
    ok_live = wait_live(t, site) if "live" in site.faces else True
    problems = check_html(t, site, v, faces.get("html"), full, release, html_release)
    if not ok_live or problems:
        echo(f"  ✗ check after the switch: html {'; '.join(problems) or 'ok'}, live {'ok' if ok_live else 'down'}")
        if previous:
            switch(t, site, previous, old_html)
            reload_all(t, site)
            echo(f"  ↩ both faces are back on {previous}")
        raise ReleaseError(f"{site.site}: what is served is not {html_release}")
    html_seen = html_release
    v.update(release=release, previous=previous, date=dt.datetime.now().isoformat(timespec="seconds"),
             asleep=False, last="publish", up_to_slide_previous=limit)
    if "html" in site.faces:
        v.update(html_release=html_release, html_previous=old_html)
    if skew:
        v["skew"] = skew
    else:
        v.pop("skew", None)
    save_state(cfg.root, state)
    echo(f"  ✓ {site.site}: html {html_seen}, live {'ok' if 'live' in site.faces else '-'}"
         + (f" — port {v['port']}" if v.get("port") else "")
         + ("" if "html" not in site.faces else f", html {'open' if v.get('html_open') else 'protected'}"))
    if removed := prune(t, site, {release, previous} - {None},
                        {release, previous, html_release, old_html} - {None}):
        echo(f"  ⌫ {len(removed)} old release(s) removed: {', '.join(removed)}")


def _slides(v: dict) -> str:
    return "all slides" if v.get("up_to_slide") is None else \
        f"slides 1 to {html_of(v).rsplit('-s', 1)[1]}"


def limit_site(t: Target, cfg: ReleaseConfig, state: dict, site: Site, slide: int | None, entries: list | None,
               echo: Echo, html_env: dict[str, str] | None = None, full: frozenset[str] = frozenset()) -> None:
    """What the participants can see: slides 1 to *slide*, or all of them (``None``) — #146.

    Only the HTML face is exported again, from the release already published (its code, so its slide
    numbering is the one being projected), then it alone switches. The live face is not touched: no
    password is rewritten and no program restarts, so the participants' sessions stay open. The limit is
    kept for the site: every later publication applies it. The ``full`` labels keep seeing everything.
    """
    if "html" not in site.faces:
        raise ReleaseError(f"{site.site} has no HTML face: a slide limit applies to the HTML face")
    v = sites_of(state, t.name).get(site.site)
    if not v or not v.get("release"):
        raise ReleaseError(f"{site.site} is not published on {t.name} — publish it first")
    release, old_html, old_limit = v["release"], html_of(v), v.get("up_to_slide")
    echo(f"\n▶ {site.site}: HTML face of {release}, " + ("all slides" if slide is None else f"up to slide {slide}")
         + f" ({t.name})")
    base = t.path("static", "sites", site.site, "releases")
    if t.sh(f"test -d {shlex.quote(base + '/' + release)}", check=False).returncode:
        raise ReleaseError(f"{site.site}: the whole HTML release {release} is not on {t.name} — publish the "
                           "site again first (stx release publish), then set the limit")
    has_old = bool(old_html) and not t.sh(f"test -d {shlex.quote(base + '/' + old_html)}", check=False).returncode
    name = release
    if slide is not None:
        with tempfile.TemporaryDirectory(prefix="stx-limit-") as w:
            work = Path(w)
            code = build.snapshot(cfg, site, work, rev=release)
            html, name = build.export(cfg, site, code, work, release, html_env, slide)
            if name != old_html or not has_old:
                t.rsync(str(html) + "/", f"{base}/{name}/", "--delete", "-H", "-c", "--link-dest", f"{base}/{release}")
                t.sh(f"chmod -R a+rX {shlex.quote(base + '/' + name)}")
    if name == old_html and has_old:
        v["up_to_slide"] = slide
        save_state(cfg.root, state)
        echo(f"  ✓ {site.site}: nothing to change, the participants already see {name}")
        return
    switch_limited(t, site, release, name)
    t.dexec("static", "nginx -s reload")
    problems = check_html(t, site, v, entries, full, release, name)
    if problems:
        if has_old:
            switch_limited(t, site, release, old_html)
            t.dexec("static", "nginx -s reload")
            echo(f"  ↩ the participants see {old_html} again")
        raise ReleaseError(f"{site.site}: the HTML face is not right after the switch: {'; '.join(problems)}")
    html_seen = name
    v.update(html_release=name, html_previous=old_html if has_old else None, up_to_slide=slide,
             up_to_slide_previous=old_limit, last="limit",
             html_date=dt.datetime.now().isoformat(timespec="seconds"))
    save_state(cfg.root, state)
    echo(f"  ✓ {site.site}: html {html_seen} ({_slides(v)}) — live face and participants' sessions unchanged")
    if removed := prune(t, site, {release, v.get("previous")} - {None},
                        {release, v.get("previous"), name, v["html_previous"]} - {None}):
        echo(f"  ⌫ {len(removed)} old release(s) removed: {', '.join(removed)}")


def rollback(t: Target, cfg: ReleaseConfig, state: dict, site: Site) -> str:
    """Undo the last change: a limit (the HTML face alone), else a publication (both faces)."""
    v = sites_of(state, t.name).get(site.site)
    if not v:
        raise ReleaseError(f"{site.site} is not published on {t.name}")
    if v.get("last") == "limit":
        if not v.get("html_previous"):
            raise ReleaseError(f"{site.site}: no previous HTML release")
        v["html_release"], v["html_previous"] = v["html_previous"], v["html_release"]
        v["up_to_slide"], v["up_to_slide_previous"] = v.get("up_to_slide_previous"), v.get("up_to_slide")
        switch_limited(t, site, v["release"], v["html_release"])
        t.dexec("static", "nginx -s reload")
        save_state(cfg.root, state)
        return f"the participants see {v['html_release']} again ({_slides(v)}); the live face is unchanged"
    if not v.get("previous"):
        raise ReleaseError(f"{site.site}: no previous release")
    html_now = html_of(v)
    v["release"], v["previous"] = v["previous"], v["release"]
    if "html_release" in v:
        v["html_release"], v["html_previous"] = v.get("html_previous") or v["release"], html_now
        v["up_to_slide"], v["up_to_slide_previous"] = v.get("up_to_slide_previous"), v.get("up_to_slide")
    switch(t, site, v["release"], v.get("html_release"))
    reload_all(t, site)
    save_state(cfg.root, state)
    return f"both faces are back on {v['release']}" + \
        (f" (HTML {v['html_release']})" if v.get("html_release") not in (None, v["release"]) else "")


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


def image_version(t: Target) -> str:
    """The streamtex version the live application actually runs, or ``""`` when it cannot be read."""
    r = t.dexec("live", "/app/.venv/bin/python -c 'import streamtex; print(streamtex.__version__)'", check=False)
    return r.stdout.strip() if r.returncode == 0 else ""


def status_rows(t: Target, cfg: ReleaseConfig, state: dict, data: dict | None) -> list[tuple]:
    rows = []
    for name, v in sorted(sites_of(state, t.name).items()):
        site = cfg.by_name.get(name)
        if site is None:
            rows.append((name, v.get("release", "?"), "not in stx.toml", "", "", v.get("date", ""), "  ← UNKNOWN"))
            continue
        password, entries, full = "", None, frozenset()
        if data is not None and not v.get("html_open") and "html" in site.faces:
            try:
                entries, full = pw.for_site(data, site)["html"], pw.full_labels(data, site)
                limited = html_of(v) != v.get("release")
                password = (pw.view_password(entries, full, "limited") if limited else None) \
                    or pw.first_password(entries)
            except ReleaseError:
                password = ""
        html, live = served(t, site, v, password)
        if html == "HTTP 401" and not password and not v.get("html_open"):
            html, flag = "? (no password)", ""         # cannot read it: unknown, not a gap
        elif "html" not in site.faces:
            flag = ""
        elif entries is not None:
            problems = check_html(t, site, v, entries, full, v.get("release"), html_of(v))
            flag = f"  ← GAP ({'; '.join(problems)})" if problems else ""
        else:
            flag = "" if html == html_of(v) else "  ← GAP"
        if v.get("skew"):
            flag += "  (skew)"
        if v.get("up_to_slide") is not None and "html" in site.faces:
            flag += f"  ({_slides(v)})"
        access = "-" if "html" not in site.faces else ("open" if v.get("html_open") else "protected")
        rows.append((name, v.get("release", "?"), html, live, access, v.get("date", ""), flag))
    return rows


# -- the server configuration --------------------------------------------------------------

def _stx_auth_source() -> str:
    return Path(importlib.util.find_spec("streamtex.deploy.stx_auth").origin).read_text(encoding="utf-8")


_SITE_MAP = "    ~^(?<label>[a-z0-9-]+)\\.  $label;"


def http_conf(app: str, suffix: str = "") -> str:
    """The application's nginx configuration; with a provisional *suffix*, the site is the host's first
    label without it (docs-advanced-next.example.org → site docs-advanced)."""
    text = (TEMPLATES / app / "stx-http.conf").read_text(encoding="utf-8")
    if suffix:
        import re
        if not re.fullmatch(r"-[a-z0-9-]+", suffix):
            raise ReleaseError(f"site_suffix {suffix!r}: '-' then a-z, 0-9, '-' (e.g. '-next')")
        assert text.count(_SITE_MAP) == 1
        text = text.replace(_SITE_MAP, f"    ~^(?<label>[a-z0-9-]+?){re.escape(suffix)}\\.  $label;")
    return text


#: What server-config sends, per application: file name → content.
def server_files(app: str, suffix: str = "") -> dict[str, str]:
    return {"stx-http.conf": http_conf(app, suffix),
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
        for name, content in server_files(app, t.suffix).items():
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
