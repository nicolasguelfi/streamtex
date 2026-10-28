"""``stx release`` — publish the documents of a multi-document project (#136, #111).

See :mod:`streamtex.release`. ``stx deploy hetzner`` stays for one document per application.
"""

from __future__ import annotations

import subprocess

import click

from ..release import ReleaseError, build, coolify, ops
from ..release import levels as lv
from ..release import passwords as pw
from ..release.config import load_config, run_checks
from ..release.state import STATE_FILE, import_prototype, load_state, save_state, sites_of
from ..release.target import target_of


def _ctx(target: str | None):
    cfg = load_config()
    state = load_state(cfg.root)
    return cfg, state, target_of(state, target)


def _passwords(cfg):
    return pw.load_file(pw.passwords_path(cfg.root))


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
@click.option("--all", "all_", is_flag=True, help="Publish every site not marked explicit.")
@_target
@click.option("--allow-skew", is_flag=True,
              help="Publish although the exporting streamtex is not the live image's (marked in status).")
@click.option("--html-env", "html_env", multiple=True, metavar="KEY=VALUE",
              help="An environment variable for the HTML export only (e.g. a partial deck).")
def publish_cmd(sites, groups, all_, target, allow_skew, html_env):
    """Publish SITES, the sites of --group, or --all (every site not marked explicit): both faces
    together, all or nothing."""
    if all_ and (sites or groups):
        raise ReleaseError("--all publishes every site: name no site and no group with it")
    if not (sites or groups or all_):
        # a forgotten argument would publish every site (#145, G10)
        raise ReleaseError("name the sites to publish, a --group, or --all for every site")
    cfg, state, t = _ctx(target)
    chosen = cfg.select(sites, groups)
    env = _html_env(html_env)
    release_name = build.require_committed(cfg.root)
    build.require_lock(cfg)
    skew = _skew(cfg, t, allow_skew)
    run_checks(cfg, chosen)
    data = _passwords(cfg)
    faces = {s.site: pw.for_site(data, s) for s in chosen}     # every password checked before any copy
    levels = {s.site: pw.levels_for(data, s) for s in chosen}
    pool = pw.RecordPool(ops.server_records(t))                # one record per password, on every site
    for s in chosen:
        ops.publish_site(t, cfg, state, s, release_name, faces[s.site], click.echo, env, skew,
                         levels[s.site], pool)


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
@click.option("--label", "labels", default=None, metavar="L[,L…]",
              help="The session(s) whose level changes: written on their line of .stx-passwords.toml.")
@_target
@click.option("--allow-skew", is_flag=True,
              help="Export although the exporting streamtex is not the live image's.")
@click.option("--html-env", "html_env", multiple=True, metavar="KEY=VALUE",
              help="An environment variable for the HTML export.")
def limit_cmd(site, slide, labels, target, allow_skew, html_env):
    """What participants see on SITE's HTML face: slides 1 to SLIDE, `all`, or `none`.

    \b
    With --label, the level of those sessions: `limite` is written on their line of
    .stx-passwords.toml (in the site's own section, nothing else changes; `none`
    removes it: "not open yet"), then applied. Without --label, the level of every
    label that has none of its own. The number is the slide counter's (n / N), as
    projected; the block that holds that slide is kept whole. Only the HTML face
    changes, from the release already published: no password is rewritten, the
    live face does not restart, participants stay logged in and see their new level
    on their next page. `rollback SITE` undoes it. [admin] always sees everything.

    \b
    Examples:
        stx release limit gai4as-slides 120 --label GAI4AS261027
        stx release limit gai4as-slides all --label GAI4AS261027,GAI4AS261103
        stx release limit gai4as-slides none --label GAI4AS261110
        stx release limit gai4as-slides 120          # the labels without their own level
    """
    if slide in ("all", "none"):
        value = None if slide == "none" else "all"
    elif slide.isdigit() and int(slide) >= 1:
        value = int(slide)
    else:
        raise ReleaseError(f"{slide!r}: a slide number (1 or more), `all` or `none`")
    cfg, state, t = _ctx(target)
    s = cfg.site(site)
    if "html" not in s.faces:
        raise ReleaseError(f"{s.site} has no HTML face: a slide limit applies to the HTML face")
    _skew(cfg, t, allow_skew)
    if labels:
        names = [x.strip() for x in labels.split(",") if x.strip()]
        path = pw.passwords_path(cfg.root)
        for line in pw.write_limit(path, s, names, value):
            click.echo(f"  {path.name}: {line}")
    elif value is None:
        raise ReleaseError("`none` closes sessions one by one: give them with --label")
    data = _passwords(cfg)
    entries, levels = pw.for_site(data, s)["html"], pw.levels_for(data, s)
    if labels:
        ops.limit_site(t, cfg, state, s, entries, levels, click.echo, _html_env(html_env))
    else:
        ops.limit_site(t, cfg, state, s, entries, levels, click.echo, _html_env(html_env),
                       slide=None if value == "all" else value, default=True)


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

    Effective at once on both faces, with each session's level as written in the file: the login service
    reads the records, so no site process restarts (a live participant stays connected). A changed
    password closes the open sessions of its label only; an unchanged one keeps its sessions.
    ``STX_PASSWORDS_FILE`` names another passwords file (a rehearsal with dummy passwords)."""
    cfg, state, t = _ctx(target)
    data = _passwords(cfg)
    published = sites_of(state, t.name)
    names = sites or tuple(n for n in published if n in cfg.by_name)
    for name in names:
        if name not in published:
            raise ReleaseError(f"{name} is not published on {t.name}")
    pool = pw.RecordPool(ops.server_records(t))
    for name in names:
        site = cfg.site(name)
        faces = pw.for_site(data, site)
        ops.apply_passwords(t, cfg, state, site, faces, pool)
        if "html" in site.faces:                  # the levels written in the file too (#148)
            ops.limit_site(t, cfg, state, site, faces["html"], pw.levels_for(data, site), click.echo)
    ops.write_maps(t, state)
    t.dexec("static", "nginx -s reload")
    t.dexec("live", "nginx -s reload")
    t.dexec("live", "supervisorctl reread")
    t.dexec("live", "supervisorctl update")       # restarts only a site whose program changed
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
        levels = pw.levels_for(data, site)
        parts = []
        for face, entries in faces.items():
            if entries is None:
                parts.append(f"{face}: open")
            else:
                parts.append(f"{face}: " + ", ".join(
                    e.label + (f" (until {e.valid_until})" if e.valid_until else "")
                    + (f" [{lv.describe(levels.get(e.label), None)}]" if face == "html" and levels.get(e.label)
                       not in (None, pw.DEFAULT) else " [not open yet]" if face == "html" and e.label in levels
                       and levels[e.label] is None else "") for e in entries))
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


@release.command("remove")
@click.argument("site")
@_target
@click.option("--yes", is_flag=True, help="Do not ask for confirmation.")
@click.option("--force", is_flag=True, help="Remove a site still declared in stx.toml.")
def remove_cmd(site, target, yes, force):
    """Take SITE off the server (#143): its program, its port, its folders, its state entry.

    Refused while SITE is still declared in stx.toml, unless --force. No other site is touched and the
    project's media stay. The domains are not changed here: `stx release setup --domains --dry-run`
    shows them, then `--domains --deploy` writes them (it redeploys both applications)."""
    cfg, state, t = _ctx(target)
    if site in cfg.by_name and not force:
        raise ReleaseError(f"{site} is still declared in stx.toml — remove it there first, or pass --force")
    plan = ops.remove_plan(t, state, site)
    if not plan:
        raise ReleaseError(f"{site}: nothing on {t.name}")
    click.echo(f"On {t.name}, this removes:")
    for line in plan:
        click.echo(f"  - {line}")
    if not yes and not click.confirm("Remove?", default=False):
        raise ReleaseError("nothing removed")
    ops.remove_site(t, cfg, state, site, click.echo)
    if site not in cfg.by_name:
        click.echo("Domains: `stx release setup --domains --dry-run` shows the one to drop; "
                   "`--domains --deploy` writes them (redeploys both applications, out of class).")


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
@click.option("--dry-run", "dry_run", is_flag=True,
              help="With --domains: show what each application would get against what it has; write nothing.")
@click.option("--migrate", type=click.Choice(["static", "live"]),
              help="Move this face from its pasted Dockerfile to the repository (run it twice: see its output).")
def setup_cmd(target, apply_, show, domains, deploy, dry_run, migrate):
    """The two Coolify applications of an ssh target, through the API; prints the manual steps."""
    if dry_run and not domains:
        raise ReleaseError("--dry-run goes with --domains (setup alone already only shows its plan)")
    if dry_run and deploy:
        raise ReleaseError("--dry-run writes nothing: it cannot --deploy")
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
        coolify.apply_domains(cfg, t.cfg, click.echo, deploy, dry_run)
        if dry_run:
            click.echo("dry run: nothing written (drop --dry-run to write the domains)")
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

