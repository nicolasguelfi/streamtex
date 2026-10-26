"""The gestures of ``stx release``, on a target — the prototype's ``publish.py``, its server layout kept.

On the target (``<root>`` of the target, ``/srv/<face>`` in the containers)::

    static/sites/<site>/releases/<release>/   the HTML export of a release
    static/sites/<site>/current -> releases/<release>          all the content
    static/sites/<site>/releases/<release>-s<n>/               a cut: slides 1 to n (#146, #148)
    static/sites/<site>/levels                what each session sees, read by the login service (#148)
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

Each session has its level on the HTML face (#148, :mod:`.levels`): all the slides, slides 1 to N (a
cut of the release, exported once, hard-linked), "not open yet", or a schedule. The levels come from
``.stx-passwords.toml``; ``up_to_slide`` (``limit SITE N``) is the level of the labels without their
own. ``limit`` changes the levels alone, from the release already published: the live face, its program
and the passwords stay as they are, so the participants' sessions stay open; ``rollback`` after a limit
undoes the levels alone.
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
from . import levels as lv
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
    """The whole HTML release of a site (its sessions' levels are cuts of it, #148)."""
    return v.get("release")


def switch(t: Target, site: Site, release: str, faces: list[str] | None = None) -> None:
    """Each face's ``current`` link on *release*."""
    for face in faces or _faces_dirs(site):
        t.sh(t.switch_cmd(t.path(face, "sites", site.site), release))


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
                    pool: pw.RecordPool | None = None) -> None:
    """The record files of the site's faces; a changed password closes the open sessions of its label
    only."""
    v = sites_of(state, t.name)[site.site]
    pool = pool or pw.RecordPool()
    if "html" in site.faces:
        v["html_open"] = faces["html"] is None
        t.write(t.path("static", "sites", site.site, "pass"), pool.text(faces["html"]), mode=0o600)
    if "live" in site.faces:
        t.write(t.path("live", "sites", site.site, "pass"), pool.text(faces["live"]), mode=0o600)
        t.write(t.path("live", "conf", "programs", f"{site.site}.conf"), program_conf(cfg, site, v["port"]))


def served(t: Target, site: Site, v: dict, html_password: str) -> tuple[str, str]:
    """(what the HTML face serves to this password: its release, ``closed`` or the HTTP code; the live
    face's health) — as a visitor."""
    html = "-"
    if "html" in site.faces:
        cookie = "" if v.get("html_open") else t.login(site.site, html_password)
        code, body = t.get("static_url", site.site, "/html/version.txt", cookie=cookie)
        if code == 200 and "stx-closed" in body:
            html = lv.CLOSED
        else:
            html = body.splitlines()[0] if code == 200 and body else f"HTTP {code}"
    live = "-"
    if "live" in site.faces:
        live = "asleep" if v.get("asleep") else \
            ("ok" if t.get("live_url", site.site, "/_stcore/health")[0] == 200 else "down")
    return html, live


def check_levels(t: Target, site: Site, v: dict, entries: list | None, levels: dict, release: str,
                 names: dict[int, str]) -> list[str]:
    """What each level in force serves, logged in as one session of that level; [] when all is right."""
    if "html" not in site.faces:
        return []
    default = v.get("up_to_slide")
    words = {e.label: e.password for e in entries or []}
    if not levels:                          # no levels file: everyone sees `current`
        levels = {"open": "all"} if v.get("html_open") else {e.label: "all" for e in (entries or [])[:1]}
    expected = {lv.CLOSED: lv.CLOSED, lv.CURRENT: release, **{f"releases/{n}": n for n in names.values()}}
    seen_folders: dict[str, str] = {}
    for label, level in sorted(levels.items()):
        where = lv.folder(lv.now_of(level, default), names)
        if where in seen_folders or (label not in words and not v.get("html_open")):
            continue
        seen_folders[where] = label
    problems = []
    for where, label in seen_folders.items():
        got, _ = served(t, site, v, words.get(label, ""))
        if got != expected[where]:
            problems.append(f"{label} sees {got}, not {expected[where]}")
    return problems


def wait_live(t: Target, site: Site, seconds: int = 90) -> bool:
    for _ in range(max(1, seconds // 3)):
        if t.get("live_url", site.site, "/_stcore/health")[0] == 200:
            return True
        time.sleep(3)
    return False


def prune(t: Target, site: Site, keep: set[str], keep_html: set[str] | None = None) -> list[str]:
    """Keep only the releases *keep* of a site, and *keep_html* on its HTML face (its cuts too)
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


def _html_keep(v: dict) -> set[str]:
    """The HTML releases to keep: the whole ones and the cuts of the current and previous levels."""
    keep = {v.get("release"), v.get("previous")}
    for key in ("cuts", "cuts_previous"):
        keep |= set((v.get(key) or {}).values())
    return keep - {None}


def ensure_cuts(t: Target, cfg: ReleaseConfig, site: Site, release: str, need: set[int], known: dict,
                echo: Echo, html_env: dict[str, str] | None = None, code: Path | None = None) -> dict[int, str]:
    """The export of each slide number in *need*, from *release* (its code: its numbering); one already on
    the target is not made again. Returns {N: release folder name}."""
    base = t.path("static", "sites", site.site, "releases")
    present = set(t.sh(f"ls -1 {shlex.quote(base)} 2>/dev/null", check=False).stdout.split())
    names = {int(n): name for n, name in (known or {}).items() if int(n) in need and name in present}
    missing = sorted(need - set(names))
    if not missing:
        return names
    with tempfile.TemporaryDirectory(prefix="stx-levels-") as w:
        if code is None:
            code = build.snapshot(cfg, site, Path(w), rev=release)
        made: dict[str, int] = {}
        for n in missing:
            out = Path(w) / f"cut-{n}"
            out.mkdir()
            html, name = build.export(cfg, site, code, out, release, html_env, n)
            names[n] = name
            if name in present or name in made:
                echo(f"  level up to slide {n}: {name} (already there)")
                continue
            made[name] = n
            echo(f"  level up to slide {n}: slides 1 to {name.rsplit('-s', 1)[1]} → {name}")
            t.rsync(str(html) + "/", f"{base}/{name}/", "--delete", "-H", "-c", "--link-dest", f"{base}/{release}")
            t.sh(f"chmod -R a+rX {shlex.quote(base + '/' + name)}")
    return names


def write_levels(t: Target, site: Site, text: str) -> None:
    """The levels file the login service reads; the one in service is kept as ``levels.previous``."""
    base = t.path("static", "sites", site.site)
    t.sh(f"cd {shlex.quote(base)} && if [ -f levels ]; then cp -p levels levels.previous; "
         f"else rm -f levels.previous; fi")
    if text:
        t.write(f"{base}/levels", text, mode=0o600)
    else:                                   # no level known: everyone sees `current`, never all closed
        t.sh(f"rm -f {shlex.quote(base + '/levels')}")


def restore_levels(t: Target, site: Site) -> None:
    """Swap ``levels`` and ``levels.previous`` (a rollback); no previous file: no levels at all."""
    base = shlex.quote(t.path("static", "sites", site.site))
    t.sh(f"cd {base} && if [ -f levels.previous ]; then mv levels levels.tmp 2>/dev/null; "
         f"mv levels.previous levels; [ -f levels.tmp ] && mv levels.tmp levels.previous; true; "
         f"else rm -f levels; fi")


def apply_levels(t: Target, cfg: ReleaseConfig, state: dict, site: Site, release: str, entries: list | None,
                 levels: dict, echo: Echo, html_env: dict[str, str] | None = None,
                 code: Path | None = None) -> dict[int, str]:
    """Each session's level on the HTML face: the exports it needs, then the levels file (#148)."""
    v = sites_of(state, t.name)[site.site]
    default = v.get("up_to_slide")
    known = v.get("cuts") if v.get("release") == release else {}
    names = ensure_cuts(t, cfg, site, release, lv.cuts(levels, default), known, echo, html_env, code)
    write_levels(t, site, lv.text(levels, default, names))
    return names


def _levels_line(levels: dict, default: int | None) -> str:
    return "; ".join(f"{label} {lv.describe(level, default)}" for label, level in sorted(levels.items()))


def publish_site(t: Target, cfg: ReleaseConfig, state: dict, site: Site, release: str, faces: dict,
                 echo: Echo, html_env: dict[str, str] | None = None, skew: str = "",
                 levels: dict | None = None, pool: pw.RecordPool | None = None) -> None:
    echo(f"\n▶ {site.site} @ {release} ({t.name})")
    entries = sites_of(state, t.name)
    v = entries.setdefault(site.site, {})
    levels = levels if levels is not None else {}
    previous = v.get("release")
    check_dir = t.path(_faces_dirs(site)[0], "sites", site.site, "releases", previous) if previous else ""
    if previous and t.sh(f"test -d {shlex.quote(check_dir)}", check=False).returncode:
        previous = None          # the recorded release is not on this target: no hard link, no rollback to it
    static_rel = t.path("static", "sites", site.site, "releases")
    if "live" in site.faces and not v.get("port"):
        v["port"] = max([cfg.port_base - 1] + [s.get("port") or 0 for s in entries.values()]) + 1
    names: dict[int, str] = {}
    with tempfile.TemporaryDirectory(prefix="stx-release-") as w:
        work = Path(w)
        code = build.snapshot(cfg, site, work)
        html = None
        if "html" in site.faces:
            html, _ = build.export(cfg, site, code, work, release, html_env)
        if "live" in site.faces:
            dirs = [t.path("live", "sites", site.site, "releases")]
            if cfg.media:
                dirs.append(t.path("live", "media", cfg.project))
            t.sh("mkdir -p " + " ".join(shlex.quote(d) for d in dirs))
            if cfg.media and (cfg.root / cfg.media).is_dir():
                excl = [x for pat in cfg.media_exclude for x in ("--exclude", pat)]
                t.rsync(str(cfg.root / cfg.media) + "/", t.path("live", "media", cfg.project, cfg.media) + "/", *excl)
        if html is not None:
            t.sh("mkdir -p " + shlex.quote(static_rel))
            link = ["--link-dest", f"{static_rel}/{previous}"] if previous else []
            t.rsync(str(html) + "/", f"{static_rel}/{release}/", "--delete", "-H", "-c", *link)
            t.sh(f"chmod -R a+rX {shlex.quote(static_rel + '/' + release)}")
            names = ensure_cuts(t, cfg, site, release, lv.cuts(levels, v.get("up_to_slide")), {}, echo,
                                html_env, code)
        if "live" in site.faces:
            if cfg.media and (cfg.root / cfg.media).is_dir():
                media = code / cfg.media
                if media.is_symlink() or media.is_file():
                    media.unlink()
                elif media.is_dir():
                    import shutil
                    shutil.rmtree(media)
                media.parent.mkdir(parents=True, exist_ok=True)
                media.symlink_to(f"{LIVE_ROOT}/media/{cfg.project}/{cfg.media}")
            t.rsync(str(code) + "/", t.path("live", "sites", site.site, "releases", release) + "/", "--delete")
            t.sh(f"chmod -R a+rX {shlex.quote(t.path('live', 'sites', site.site, 'releases', release))}")
    if "live" in site.faces:
        t.sh(f"ln -sfn {LIVE_ROOT}/sites/{site.site}/current/{site.doc_dir}/static "
             f"{shlex.quote(t.path('live', 'sites', site.site, 'static'))}")
    apply_passwords(t, cfg, state, site, faces, pool)
    write_maps(t, state)
    if "html" in site.faces:
        write_levels(t, site, lv.text(levels, v.get("up_to_slide"), names))
    switch(t, site, release)        # both faces TOGETHER
    reload_all(t, site)
    ok_live = wait_live(t, site) if "live" in site.faces else True
    problems = check_levels(t, site, v, faces.get("html"), levels, release, names)
    if not ok_live or problems:
        echo(f"  ✗ check after the switch: html {'; '.join(problems) or 'ok'}, live {'ok' if ok_live else 'down'}")
        if previous:
            switch(t, site, previous)
            if "html" in site.faces:
                restore_levels(t, site)
            reload_all(t, site)
            echo(f"  ↩ both faces are back on {previous}")
        raise ReleaseError(f"{site.site}: what is served is not {release}")
    v.update(release=release, previous=previous, date=dt.datetime.now().isoformat(timespec="seconds"),
             asleep=False, last="publish", cuts_previous=v.get("cuts") if previous else None,
             cuts={str(n): name for n, name in names.items()}, up_to_slide_previous=v.get("up_to_slide"))
    for old in ("html_release", "html_previous"):
        v.pop(old, None)
    if skew:
        v["skew"] = skew
    else:
        v.pop("skew", None)
    save_state(cfg.root, state)
    echo(f"  ✓ {site.site}: html {release}, live {'ok' if 'live' in site.faces else '-'}"
         + (f" — port {v['port']}" if v.get("port") else "")
         + ("" if "html" not in site.faces else f", html {'open' if v.get('html_open') else 'protected'}"))
    if levels and "html" in site.faces:
        echo(f"  levels: {_levels_line(levels, v.get('up_to_slide'))}")
    if removed := prune(t, site, {release, previous} - {None}, _html_keep(v)):
        echo(f"  ⌫ {len(removed)} old release(s) removed: {', '.join(removed)}")


def _slides(v: dict) -> str:
    return "all slides" if v.get("up_to_slide") is None else f"slides 1 to {v['up_to_slide']}"


def limit_site(t: Target, cfg: ReleaseConfig, state: dict, site: Site, entries: list | None, levels: dict,
               echo: Echo, html_env: dict[str, str] | None = None, slide: int | None = None,
               default: bool = False) -> None:
    """Apply the sessions' levels (#148) — after ``.stx-passwords.toml`` changed, or with *default*, the
    site's level (*slide*, None = all) for the labels without their own (#146).

    Only the HTML face changes, from the release already published (its code, so its slide numbering is
    the one being projected): the live face, its program and the passwords stay as they are, so the
    participants' sessions stay open; a session's next page shows its new level.
    """
    if "html" not in site.faces:
        raise ReleaseError(f"{site.site} has no HTML face: a slide limit applies to the HTML face")
    v = sites_of(state, t.name).get(site.site)
    if not v or not v.get("release"):
        raise ReleaseError(f"{site.site} is not published on {t.name} — publish it first")
    release = v["release"]
    base = t.path("static", "sites", site.site, "releases")
    if t.sh(f"test -d {shlex.quote(base + '/' + release)}", check=False).returncode:
        raise ReleaseError(f"{site.site}: the whole HTML release {release} is not on {t.name} — publish the "
                           "site again first (stx release publish), then set the limit")
    echo(f"\n▶ {site.site}: levels of {release} ({t.name})")
    old_default, old_cuts = v.get("up_to_slide"), v.get("cuts")
    if default:
        v["up_to_slide"] = slide
    names = apply_levels(t, cfg, state, site, release, entries, levels, echo, html_env)
    problems = check_levels(t, site, v, entries, levels, release, names)
    if problems:
        restore_levels(t, site)
        v["up_to_slide"] = old_default
        echo("  ↩ the previous levels are back")
        raise ReleaseError(f"{site.site}: the HTML face is not right after the change: {'; '.join(problems)}")
    v.update(cuts={str(n): name for n, name in names.items()}, cuts_previous=old_cuts,
             up_to_slide_previous=old_default, last="limit",
             html_date=dt.datetime.now().isoformat(timespec="seconds"))
    save_state(cfg.root, state)
    echo(f"  ✓ {site.site}: {_levels_line(levels, v.get('up_to_slide'))} — live face and sessions unchanged")
    if removed := prune(t, site, {release, v.get("previous")} - {None}, _html_keep(v)):
        echo(f"  ⌫ {len(removed)} old release(s) removed: {', '.join(removed)}")


def _missing_on_target(t: Target, site: Site, release: str, cuts) -> list[str]:
    """The folders of *release* (each face, and its HTML cuts) that are not on the target."""
    wanted = [(face, release) for face in _faces_dirs(site)] + [("static", c) for c in cuts]
    return [f"{face}/{name}" for face, name in wanted
            if t.sh(f"test -d {shlex.quote(t.path(face, 'sites', site.site, 'releases', name))}",
                    check=False).returncode]


def rollback(t: Target, cfg: ReleaseConfig, state: dict, site: Site) -> str:
    """Undo the last change: the levels (the HTML face alone), else a publication (both faces)."""
    v = sites_of(state, t.name).get(site.site)
    if not v:
        raise ReleaseError(f"{site.site} is not published on {t.name}")
    if v.get("last") == "limit":
        restore_levels(t, site)
        v["cuts"], v["cuts_previous"] = v.get("cuts_previous"), v.get("cuts")
        v["up_to_slide"], v["up_to_slide_previous"] = v.get("up_to_slide_previous"), v.get("up_to_slide")
        save_state(cfg.root, state)
        return (f"the previous levels are back ({_slides(v)} by default); the live face is unchanged — "
                f"{pw.PASSWORDS_FILE} still holds the new levels: write the old ones back, or "
                f"`stx release passwd {site.site}` applies the file again")
    if not v.get("previous"):
        raise ReleaseError(f"{site.site}: no previous release")
    missing = _missing_on_target(t, site, v["previous"], (v.get("cuts_previous") or {}).values())
    if missing:
        raise ReleaseError(f"{site.site}: the previous release {v['previous']} is no longer on {t.name} "
                           f"({', '.join(missing)}) — nothing changed; publish the version you want instead")
    v["release"], v["previous"] = v["previous"], v["release"]
    v["cuts"], v["cuts_previous"] = v.get("cuts_previous"), v.get("cuts")
    v["up_to_slide"], v["up_to_slide_previous"] = v.get("up_to_slide_previous"), v.get("up_to_slide")
    switch(t, site, v["release"])
    if "html" in site.faces:
        restore_levels(t, site)
    reload_all(t, site)
    save_state(cfg.root, state)
    return f"both faces are back on {v['release']}, with their levels"


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
        entries, levels = None, {}
        if data is not None and "html" in site.faces:
            try:
                entries, levels = pw.for_site(data, site)["html"], pw.levels_for(data, site)
            except ReleaseError:
                entries = None
        names = {int(n): x for n, x in (v.get("cuts") or {}).items()}
        word = next((e.password for e in entries or []
                     if lv.now_of(levels.get(e.label), v.get("up_to_slide")) == "all"), None)
        html, live = served(t, site, v, word or pw.first_password(entries))
        if html == "HTTP 401" and entries is None and not v.get("html_open"):
            html, flag = "? (no password)", ""         # cannot read it: unknown, not a gap
        elif "html" not in site.faces:
            flag = ""
        elif entries is not None or v.get("html_open"):
            problems = check_levels(t, site, v, entries, levels, v.get("release"), names)
            flag = f"  ← GAP ({'; '.join(problems)})" if problems else ""
        else:
            flag = "" if html == v.get("release") else "  ← GAP"
        if v.get("skew"):
            flag += "  (skew)"
        if levels and "html" in site.faces and any(lvl != "all" for lvl in levels.values()):
            flag += f"  ({_levels_line(levels, v.get('up_to_slide'))})"
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
    files = {"stx-http.conf": http_conf(app, suffix),
             "stx_auth.py": (TEMPLATES / "static" / "stx_auth.py").read_text(encoding="utf-8"),
             "stx_auth_lib.py": _stx_auth_source()}
    if app == "static":                       # the "not open yet" page (#148)
        files["closed.html"] = (TEMPLATES / "static" / "closed.html").read_text(encoding="utf-8")
    return files


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
        extra = "".join(f"mv {root}/{n}.new {root}/{n} && " for n in server_files(app, t.suffix)
                        if n not in ("stx-http.conf", "stx_auth.py", "stx_auth_lib.py"))
        t.dexec(app, f"sh -c '{extra}mv {root}/stx_auth_lib.py.new {root}/stx_auth_lib.py && "
                     f"mv {root}/stx_auth.py.new {root}/stx_auth.py && rm -f {root}/stx-http.conf.new && "
                     f"nginx -s reload && {AUTH_RESTART[app]}'")
        if t.dexec(app, _WAIT_AUTH, check=False).returncode:
            raise ReleaseError(f"{app}: the login service does not answer after 10 s — see its logs")
        echo(f"{app}: configuration checked and reloaded without interruption; login service restarted")
