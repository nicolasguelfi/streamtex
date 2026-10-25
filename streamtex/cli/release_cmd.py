"""``stx release`` — publish the documents of a multi-document project (#136, #111).

See :mod:`streamtex.release`. ``stx deploy hetzner`` stays for one document per application.
"""

from __future__ import annotations

import subprocess

import click

from ..release import ReleaseError, build, coolify, ops
from ..release import passwords as pw
from ..release.config import load_config, run_checks
from ..release.state import STATE_FILE, import_prototype, load_state, save_state, sites_of
from ..release.target import target_of


def _ctx(target: str | None):
    cfg = load_config()
    state = load_state(cfg.root)
    return cfg, state, target_of(state, target)


def _passwords(cfg):
    return pw.load_file(cfg.root / pw.PASSWORDS_FILE)


_target = click.option("--target", "target", default=None, help="Target name in .stx-release.json "
                       "(default: its default_target).")


@click.group("release")
def release():
    """Publish the sites of a multi-document project: two long-lived applications, snapshots, rollback."""


def _html_env(items) -> dict[str, str]:
    env = {}
    for item in items:
        if "=" not in item:
            raise ReleaseError(f"--html-env {item!r}: expected KEY=VALUE")
        k, v = item.split("=", 1)
        env[k] = v
    return env


def _skew(cfg, t, allow_skew: bool) -> str:
    """Why the exporting streamtex is not the live image's, refused unless --allow-skew (rel version=a)."""
    skew = build.library_skew(cfg)
    running = ops.image_version(t)
    wanted = (cfg.lock_dir / "stx-version").read_text(encoding="utf-8").strip()
    if not skew and running and running != wanted:
        how = ("stx release rebuild" if "live" in coolify.repo_faces(t.cfg)
               else "stx release setup --show live, paste, redeploy")
        skew = (f"the live application runs streamtex {running}, {cfg.dir}/stx-version says {wanted} — "
                f"rebuild it ({how})")
    if skew and not allow_skew:
        raise ReleaseError(f"{skew} — publish with the image's streamtex, or pass --allow-skew for a trial")
    if skew:
        click.echo(f"  ⚠ {skew} (--allow-skew: the sites are marked in status)")
    return skew


@release.command("publish")
@click.argument("sites", nargs=-1)
@click.option("--group", "groups", multiple=True, help="Publish every site of this group (repeatable).")
@_target
@click.option("--allow-skew", is_flag=True,
              help="Publish although the exporting streamtex is not the live image's (marked in status).")
@click.option("--html-env", "html_env", multiple=True, metavar="KEY=VALUE",
              help="An environment variable for the HTML export only (e.g. a partial deck).")
def publish_cmd(sites, groups, target, allow_skew, html_env):
    """Publish SITES (default: every site not marked explicit): both faces together, all or nothing."""
    cfg, state, t = _ctx(target)
    chosen = cfg.select(sites, groups)
    env = _html_env(html_env)
    release_name = build.require_committed(cfg.root)
    build.require_lock(cfg)
    skew = _skew(cfg, t, allow_skew)
    run_checks(cfg, chosen)
    data = _passwords(cfg)
    faces = {s.site: pw.for_site(data, s) for s in chosen}     # every password checked before any copy
    for s in chosen:
        ops.publish_site(t, cfg, state, s, release_name, faces[s.site], click.echo, env, skew)


@release.command("status")
@_target
def status_cmd(target):
    """What each site SERVES (as a visitor), against what was published."""
    cfg, state, t = _ctx(target)
    try:
        data = _passwords(cfg)
    except ReleaseError:
        data = None
    head = build.git(cfg.root, "rev-parse", "--short=12", "HEAD")
    running = ops.image_version(t) or "?"
    wanted_path = cfg.lock_dir / "stx-version"
    wanted = wanted_path.read_text(encoding="utf-8").strip() if wanted_path.exists() else "?"
    gap = "" if running == wanted else "  ← GAP"
    click.echo(f"target {t.name} · HEAD {head} · live image streamtex {running} (stx-version {wanted}){gap}\n")
    rows = ops.status_rows(t, cfg, state, data)
    w = max([28] + [len(r[0]) + 2 for r in rows])
    click.echo(f"{'site':<{w}}{'published':<14}{'served (html)':<19}{'live':<8}{'html':<11}date")
    for name, rel, html, live, access, date, flag in rows:
        click.echo(f"{name:<{w}}{rel:<14}{html:<19}{live:<8}{access:<11}{date}{flag}")


@release.command("limit")
@click.argument("site")
@click.argument("slide")
@_target
@click.option("--allow-skew", is_flag=True,
              help="Export although the exporting streamtex is not the live image's.")
@click.option("--html-env", "html_env", multiple=True, metavar="KEY=VALUE",
              help="An environment variable for the HTML export.")
def limit_cmd(site, slide, target, allow_skew, html_env):
    """What participants see on SITE's HTML face: slides 1 to SLIDE, or `all`.

    \b
    The number is the slide counter's (n / N), as projected; the block that holds
    that slide is kept whole, and later blocks are not exported at all. Only the
    HTML face is exported again, from the release already published, and switched:
    no password is rewritten and the live face does not restart, so participants
    stay logged in. The limit is kept: every later `publish SITE` applies it, and
    `rollback SITE` undoes it alone.

    \b
    Examples:
        stx release limit gai4as-slides 120
        stx release limit gai4as-slides all
    """
    if slide == "all":
        up_to = None
    elif slide.isdigit() and int(slide) >= 1:
        up_to = int(slide)
    else:
        raise ReleaseError(f"{slide!r}: a slide number (1 or more) or `all`")
    cfg, state, t = _ctx(target)
    s = cfg.site(site)
    _skew(cfg, t, allow_skew)
    html_pw = "" if "html" not in s.faces else pw.first_password(pw.for_site(_passwords(cfg), s)["html"])
    ops.limit_site(t, cfg, state, s, up_to, html_pw, click.echo, _html_env(html_env))


@release.command("rollback")
@click.argument("site")
@_target
def rollback_cmd(site, target):
    """Undo SITE's last change: a limit (the HTML face alone), else a publication (both faces)."""
    cfg, state, t = _ctx(target)
    click.echo(f"{site}: {ops.rollback(t, cfg, state, cfg.site(site))}")


@release.command("passwd")
@click.argument("sites", nargs=-1)
@_target
def passwd_cmd(sites, target):
    """Write the password records of SITES (default: every published site) without publishing again.

    HTML face: effective at once; live face: the site's process restarts. Changing a record closes the
    open sessions of that face."""
    cfg, state, t = _ctx(target)
    data = _passwords(cfg)
    published = sites_of(state, t.name)
    names = sites or tuple(n for n in published if n in cfg.by_name)
    for name in names:
        if name not in published:
            raise ReleaseError(f"{name} is not published on {t.name}")
        site = cfg.site(name)
        ops.apply_passwords(t, cfg, state, site, pw.for_site(data, site))
    ops.write_maps(t, state)
    t.dexec("static", "nginx -s reload")
    t.dexec("live", "nginx -s reload")
    t.dexec("live", "supervisorctl reread")
    t.dexec("live", "supervisorctl update")
    for name in names:
        if "live" in cfg.site(name).faces:
            t.dexec("live", f"supervisorctl restart {name}", check=False)
    save_state(cfg.root, state)
    click.echo(f"passwords written for {len(names)} site(s)")


@release.command("auth-status")
@click.argument("sites", nargs=-1)
def auth_status_cmd(sites):
    """Labels and end dates of each site's passwords, from the local file — never a password."""
    cfg = load_config()
    data = _passwords(cfg)
    for site in (cfg.select(sites) if sites else cfg.sites):
        faces = pw.for_site(data, site)
        parts = []
        for face, entries in faces.items():
            if entries is None:
                parts.append(f"{face}: open")
            else:
                parts.append(f"{face}: " + ", ".join(e.label + (f" (until {e.valid_until})" if e.valid_until else "")
                                                     for e in entries))
        click.echo(f"{site.site:<28}" + " · ".join(parts))


@release.command("sleep")
@click.argument("site")
@_target
def sleep_cmd(site, target):
    """Stop SITE's Streamlit process (its HTML face stays served)."""
    cfg, state, t = _ctx(target)
    ops.sleep_wake(t, cfg, state, cfg.site(site), True)
    click.echo(f"{site}: live face asleep (the HTML face stays served)")


@release.command("wake")
@click.argument("site")
@_target
def wake_cmd(site, target):
    """Start SITE's Streamlit process again."""
    cfg, state, t = _ctx(target)
    ops.sleep_wake(t, cfg, state, cfg.site(site), False)
    click.echo(f"{site}: live face running again")


@release.command("lock")
def lock_cmd():
    """Write the live image's requirements.txt and stx-version from uv.lock (then rebuild the live app).

    For the faces a target builds from the repository (``repo``), also their Dockerfile.<face>."""
    cfg = load_config()
    n, ver = build.write_lock(cfg)
    click.echo(f"{cfg.dir}/requirements.txt ({n} packages) and {cfg.dir}/stx-version ({ver}) written")
    if (cfg.root / STATE_FILE).is_file():
        faces = sorted({f for tc in load_state(cfg.root).get("targets", {}).values() for f in coolify.repo_faces(tc)})
        for path in coolify.write_dockerfiles(cfg, faces):
            click.echo(f"{path.relative_to(cfg.root)} written — commit and push it, then `stx release rebuild`")


@release.command("rebuild")
@_target
@click.option("--face", type=click.Choice(["static", "live"]), default="live", show_default=True)
def rebuild_cmd(target, face):
    """Rebuild an application built from the repository (after lock, commit, push) and wait for it."""
    cfg, _state, t = _ctx(target)
    coolify.rebuild(cfg, t.cfg, face, click.echo)
    if face == "live":
        running = ops.image_version(t)
        wanted = (cfg.lock_dir / "stx-version").read_text(encoding="utf-8").strip()
        if running != wanted:
            raise ReleaseError(f"rebuilt, but the live application runs streamtex {running or '?'}, not {wanted}")
        click.echo(f"  live application on streamtex {running}")


@release.command("server-config")
@_target
def server_config_cmd(target):
    """Send both applications' nginx configuration and login service; nginx -t before any reload."""
    _cfg, _state, t = _ctx(target)
    ops.server_config(t, click.echo)


@release.command("prune")
@_target
def prune_cmd(target):
    """Keep only the current and the previous release of every site on the target."""
    cfg, state, t = _ctx(target)
    total = 0
    for name, v in sorted(sites_of(state, t.name).items()):
        if name not in cfg.by_name:
            continue
        removed = ops.prune(t, cfg.site(name), {v.get("release"), v.get("previous")} - {None})
        total += len(removed)
        if removed:
            click.echo(f"  {name}: {', '.join(removed)}")
    click.echo(f"{total} old release(s) removed")


@release.command("setup")
@_target
@click.option("--apply", "apply_", is_flag=True, help="Create what is missing (default: only show the plan).")
@click.option("--show", type=click.Choice(["static", "live"]), help="Print the composed Dockerfile and stop.")
@click.option("--domains", is_flag=True, help="Set both applications' domains from the site list.")
@click.option("--deploy", is_flag=True, help="With --domains: redeploy both applications.")
@click.option("--migrate", type=click.Choice(["static", "live"]),
              help="Move this face from its pasted Dockerfile to the repository (run it twice: see its output).")
def setup_cmd(target, apply_, show, domains, deploy, migrate):
    """The two Coolify applications of an ssh target, through the API; prints the manual steps."""
    cfg, state, t = _ctx(target)
    if show:
        click.echo(coolify.compose_dockerfile(cfg, show), nl=False)
        return
    if t.kind != "ssh":
        raise ReleaseError(f"target {t.name} is local — use `stx release local up`")
    if migrate:
        def mounted(uuid: str) -> bool:
            r = t.sh(f"docker inspect --format '{{{{range .Mounts}}}}{{{{.Destination}}}} {{{{end}}}}' "
                     f"$(docker ps -q --filter name={uuid} | head -1)", check=False)
            return f"/srv/{migrate}" in r.stdout.split()
        try:
            done = coolify.migrate(cfg, t.cfg, migrate, mounted, click.echo)
        finally:
            save_state(cfg.root, state)
        click.echo(f"{migrate}: built from the repository from now on — `stx release rebuild` after each lock"
                   if done else f"{STATE_FILE}: the new application recorded")
        return
    if domains:
        coolify.apply_domains(cfg, t.cfg, click.echo, deploy)
        return
    for line in coolify.plan(cfg, t.cfg):
        click.echo(line)
    if not apply_:
        click.echo("dry run: nothing created (--apply to create)")
        return
    t.cfg.update(coolify.setup(cfg, t.cfg, click.echo))
    save_state(cfg.root, state)
    click.echo(f"{STATE_FILE}: the uuids of both applications recorded")


@release.command("import")
@click.option("--from", "source", required=True, type=click.Path(exists=True, dir_okay=False),
              help="The prototype's state.json.")
@click.option("--force", is_flag=True, help="Replace an existing .stx-release.json.")
def import_cmd(source, force):
    """Take over the prototype's state: nothing is sent to the server (then run `stx release status`)."""
    from pathlib import Path
    cfg = load_config()
    new = import_prototype(cfg.root, Path(source), set(cfg.by_name), force)
    n = sum(len(v) for v in new["sites"].values())
    click.echo(f"{STATE_FILE} written: {len(new['targets'])} target(s), {n} site entr(ies)")
    if new["_unknown"]:
        click.echo("  ⚠ not in the site list of stx.toml (kept, shown by status): " + ", ".join(new["_unknown"]))
    click.echo("next: `stx release status` compares with what each target serves")


@release.command("convert-passwords")
@click.option("--from", "source", required=True, type=click.Path(exists=True, dir_okay=False),
              help="The prototype's .stx-passwords.toml ([default] < [TRAINING] < [TRAINING.kind]).")
@click.option("--to", "dest", required=True, type=click.Path(dir_okay=False), help="The new file to write.")
def convert_passwords_cmd(source, dest):
    """Rewrite the prototype's password file in the library's grammar; not one password changes.

    Every site is checked: same passwords, labels and end dates before and after. Nothing is written
    when a check fails; the messages name sites, faces and labels, never a password."""
    from pathlib import Path
    cfg = load_config()
    report = pw.convert(cfg, Path(source), Path(dest))
    for line in report:
        click.echo(f"  {line}")
    click.echo(f"{dest} written ({len(report)} sites checked); the old file is untouched")


@release.group("local")
def local_group():
    """The two applications in Docker on this machine (a trial target)."""


def _local(target: str | None) -> tuple:
    cfg, state, t = _ctx(target)
    if t.kind != "local":
        raise ReleaseError(f"target {t.name} is not local")
    return cfg, state, t


@local_group.command("up")
@_target
def local_up(target):
    """Build both images from the templates and start them on the target's ports and folder."""
    from pathlib import Path
    from urllib.parse import urlparse
    cfg, _state, t = _local(target)
    for app in ("static", "live"):
        name, port = t.cfg[app], urlparse(t.cfg[f"{app}_url"]).port
        host_dir = Path(t.path(app))
        host_dir.mkdir(parents=True, exist_ok=True)
        image = f"stx-release-{cfg.project}-{app}:local"
        click.echo(f"building {image} …")
        r = subprocess.run(["docker", "build", "-t", image, "-"], input=coolify.compose_dockerfile(cfg, app),
                           text=True, capture_output=True)
        if r.returncode:
            raise ReleaseError(f"docker build {app}: {r.stderr[-1500:]}")
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
        r = subprocess.run(["docker", "run", "-d", "--name", name, "-p", f"127.0.0.1:{port}:80",
                            "-v", f"{host_dir}:/srv/{app}", image], text=True, capture_output=True)
        if r.returncode:
            raise ReleaseError(f"docker run {app}: {r.stderr[-800:]}")
        click.echo(f"{name} started on 127.0.0.1:{port} (volume {host_dir})")


@local_group.command("down")
@_target
def local_down(target):
    """Stop and remove both local containers (the folder stays)."""
    _cfg, _state, t = _local(target)
    for app in ("static", "live"):
        subprocess.run(["docker", "rm", "-f", t.cfg[app]], capture_output=True)
        click.echo(f"{t.cfg[app]} removed")

