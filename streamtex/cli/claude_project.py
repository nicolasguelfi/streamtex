"""Claude profiles in *project mode*: ``[claude]`` in stx.toml + ``stx claude sync`` (#71).

A project declares its Claude content::

    [claude]
    mode = "project"          # "project" | absent (= the classic install/update)
    profile = "presentation"
    include = []              # extra profiles merged in, e.g. ["library"]
    exclude = []              # groups left out, e.g. ["stx-ce", "stx-pe"]

``stx claude sync`` makes ``.claude/`` match the declaration and records
what it installed in ``.claude/stx.lock`` (profile, streamtex-claude revision,
sha256 of every file). The lock gives a 3-way comparison — local file /
source file / locked hash — so that an upstream change is applied while a
local edit is kept and reported (supersedes #5):

=================  ===================  ==========================
local vs locked     source vs local      action
=================  ===================  ==========================
equal               different            update (upstream changed)
different           different            keep, report (local edit)
—                   equal                nothing to do
absent              —                    install
=================  ===================  ==========================

Files no longer declared are removed only when unchanged since sync; a file
stx never installed is never touched; ``.claude/custom/`` is never touched.
"""

from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
import tomllib
from dataclasses import dataclass, field

import click

from ._claude_files import (
    PROFILE_CLAUDE_MD,
    SETTINGS_PATH,
    merge_settings,
    settings_cover,
    sha256_file,
    sha256_text,
    write_profile_claude_md,
)
from .console import get_console

LOCK_PATH = os.path.join(".claude", "stx.lock")
# Format of stx.lock. A lock without ``format`` (written by 0.7.35-0.7.40) is
# format 1. A higher number comes from a newer stx: refused, never rewritten.
LOCK_FORMAT = 1
_LOCK_GITIGNORE_LINE = "!.claude/stx.lock"


# ---------------------------------------------------------------------------
# Declaration
# ---------------------------------------------------------------------------

@dataclass
class ClaudeDecl:
    profile: str
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)


def read_declaration(project_dir: str) -> ClaudeDecl | None:
    """The ``[claude]`` project-mode declaration of *project_dir*, or None."""
    path = os.path.join(project_dir, "stx.toml")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None
    section = data.get("claude", {})
    if not isinstance(section, dict) or section.get("mode") != "project":
        return None
    profile = section.get("profile")
    if not isinstance(profile, str) or not profile:
        raise click.ClickException(
            f"{path}: [claude] mode = \"project\" needs a profile, e.g. profile = \"presentation\""
        )
    return ClaudeDecl(
        profile=profile,
        include=[str(x) for x in section.get("include", [])],
        exclude=[str(x) for x in section.get("exclude", [])],
    )


def is_project_mode(project_dir: str) -> bool:
    try:
        return read_declaration(project_dir) is not None
    except click.ClickException:
        return False


def _excluded(rel: str, exclude: list[str]) -> bool:
    if not exclude or not rel.startswith(".claude" + os.sep):
        return False
    parts = rel.split(os.sep)[1:]
    names = set(parts) | {p[:-3] for p in parts if p.endswith(".md")}
    return any(x in names for x in exclude)


def desired_files(claude_repo: str, decl: ClaudeDecl) -> dict[str, str]:
    """Target-relative path → source path, for the declared profile set."""
    from .claude_cmd import collect_source_files

    profiles_dir = os.path.join(claude_repo, "profiles")
    files: dict[str, str] = {}
    for name in [decl.profile, *decl.include]:
        if not os.path.isdir(os.path.join(profiles_dir, name)):
            raise click.ClickException(f"Profile '{name}' not found in {profiles_dir}")
        files.update(collect_source_files(claude_repo, name))
    return {rel: src for rel, src in files.items() if not _excluded(rel, decl.exclude)}


def validate_declaration(project_dir: str, claude_repo: str | None) -> list[str]:
    """Problems with the ``[claude]`` section (for ``stx validate``)."""
    try:
        decl = read_declaration(project_dir)
    except click.ClickException as e:
        return [e.message]
    if decl is None or claude_repo is None:
        return []
    problems = []
    profiles_dir = os.path.join(claude_repo, "profiles")
    for name in [decl.profile, *decl.include]:
        if not os.path.isdir(os.path.join(profiles_dir, name)):
            problems.append(f"[claude] profile '{name}' does not exist in {profiles_dir}")
    if not problems:
        from .claude_cmd import collect_source_files

        every = {}
        for name in [decl.profile, *decl.include]:
            every.update(collect_source_files(claude_repo, name))
        known = {p for rel in every for p in rel.split(os.sep)[1:]}
        known |= {p[:-3] for p in known if p.endswith(".md")}
        for x in decl.exclude:
            if x not in known:
                problems.append(f"[claude] exclude '{x}' matches nothing in the profile")
    return problems


# ---------------------------------------------------------------------------
# Lock file
# ---------------------------------------------------------------------------

@dataclass
class Lock:
    profile: str = ""
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    source: str = ""
    source_rev: str = ""
    claude_md: str = ""
    claude_md_sha: str = ""
    files: dict[str, str] = field(default_factory=dict)


def read_lock(target: str) -> Lock | None:
    path = os.path.join(target, LOCK_PATH)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None
    head = data.get("lock", {})
    fmt = head.get("format", 1)
    if not isinstance(fmt, int) or fmt > LOCK_FORMAT:
        raise click.ClickException(
            f"{LOCK_PATH} has format {fmt!r}, this stx reads format {LOCK_FORMAT} — "
            "upgrade streamtex before syncing")
    return Lock(
        profile=head.get("profile", ""),
        include=list(head.get("include", [])),
        exclude=list(head.get("exclude", [])),
        source=head.get("source", ""),
        source_rev=head.get("source_rev", ""),
        claude_md=head.get("claude_md", ""),
        claude_md_sha=head.get("claude_md_sha", ""),
        files=dict(data.get("files", {})),
    )


def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_lock(target: str, lock: Lock) -> None:
    lines = [
        "# .claude/stx.lock — written by `stx claude sync`; do not edit.",
        "# Versioned with the project: a clone + `stx claude sync` rebuilds the same .claude/.",
        "[lock]",
        f"format = {LOCK_FORMAT}",
        f"profile = {_q(lock.profile)}",
        f"include = [{', '.join(_q(x) for x in lock.include)}]",
        f"exclude = [{', '.join(_q(x) for x in lock.exclude)}]",
        f"source = {_q(lock.source)}",
        f"source_rev = {_q(lock.source_rev)}",
        f"claude_md = {_q(lock.claude_md)}",
        f"claude_md_sha = {_q(lock.claude_md_sha)}",
        "",
        "[files]",
    ]
    lines += [f"{_q(rel)} = {_q(sha)}" for rel, sha in sorted(lock.files.items())]
    path = os.path.join(target, LOCK_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _source_rev(claude_repo: str) -> str:
    try:
        r = subprocess.run(["git", "-C", claude_repo, "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

@dataclass
class SyncPlan:
    install: list[str] = field(default_factory=list)      # absent locally
    update: list[str] = field(default_factory=list)       # upstream changed, local untouched
    merge: list[str] = field(default_factory=list)        # settings.json
    keep_modified: list[str] = field(default_factory=list)  # local edit: kept (or forced)
    prune: list[str] = field(default_factory=list)        # no longer declared, unchanged
    keep_orphan: list[str] = field(default_factory=list)  # no longer declared, edited: kept
    unchanged: list[str] = field(default_factory=list)


def plan_sync(target: str, desired: dict[str, str], lock: Lock | None) -> SyncPlan:
    plan = SyncPlan()
    locked = lock.files if lock else {}
    for rel, src in sorted(desired.items()):
        if rel == "CLAUDE.md":
            continue  # handled with the template rule
        dst = os.path.join(target, rel)
        if not os.path.isfile(dst):
            plan.install.append(rel)
            continue
        if filecmp.cmp(src, dst, shallow=False):
            plan.unchanged.append(rel)
            continue
        if rel == SETTINGS_PATH:
            (plan.unchanged if settings_cover(dst, src) else plan.merge).append(rel)
            continue
        if rel in locked:
            stx_copy = sha256_file(dst) == locked[rel]
        else:
            # No lock entry (first sync over a classic install): a read-only
            # file is an stx copy (stx always set 0o444, a user edit needs
            # the file made writable first).
            stx_copy = (os.stat(dst).st_mode & 0o222) == 0
        (plan.update if stx_copy else plan.keep_modified).append(rel)
    for rel, sha in sorted(locked.items()):
        if rel in desired:
            continue
        dst = os.path.join(target, rel)
        if not os.path.isfile(dst):
            continue
        (plan.prune if sha256_file(dst) == sha else plan.keep_orphan).append(rel)
    return plan


def _ensure_gitignore(target: str, console) -> None:
    """Ignore the copies, keep custom/, .stx-profile and the lock (v1). Never commits."""
    from .claude_cmd import _CLAUDE_GITIGNORE_BLOCK

    if not os.path.isdir(os.path.join(target, ".git")):
        return
    path = os.path.join(target, ".gitignore")
    content = ""
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            content = f.read()
    add = ""
    if ".claude/*" not in content:
        add += _CLAUDE_GITIGNORE_BLOCK
    if _LOCK_GITIGNORE_LINE not in content + add:
        add += _LOCK_GITIGNORE_LINE + "\n"
    if add:
        if content and not content.endswith("\n"):
            add = "\n" + add
        with open(path, "a", encoding="utf-8") as f:
            f.write(add)
        console.print("  [green]✓[/green] .gitignore: .claude/ copies ignored, "
                      "custom/, .stx-profile and stx.lock kept")


def _protect_read_only(target: str, claude_repo: str) -> None:
    for kind in ("references", "commands"):
        if not os.path.isdir(os.path.join(claude_repo, "shared", kind)):
            continue
        for root, _dirs, files in os.walk(os.path.join(target, ".claude", kind)):
            for f in files:
                os.chmod(os.path.join(root, f), 0o444)


def _copy(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isfile(dst):
        os.chmod(dst, 0o644)
    shutil.copy2(src, dst)


def sync_project(
    target: str,
    claude_repo: str,
    decl: ClaudeDecl | None,
    *,
    dry_run: bool = False,
    force: bool = False,
    remove: bool = False,
    console=None,
) -> SyncPlan:
    """Make ``target/.claude`` match *decl* (or uninstall with *remove*)."""
    from .claude_cmd import (
        _CUSTOM_README,
        FileDiff,
        _backup_modified_files,
        _previous_profile_render,
        _remove_empty_dirs,
        _render_claude_md,
    )

    console = console or get_console()
    target = os.path.abspath(target)
    lock = read_lock(target)
    if remove:
        desired: dict[str, str] = {}
    else:
        if decl is None:
            raise click.ClickException(
                f"No [claude] mode = \"project\" declaration in {os.path.join(target, 'stx.toml')}"
            )
        desired = desired_files(claude_repo, decl)
    plan = plan_sync(target, desired, lock)
    to_write_modified = plan.keep_modified if force else []

    _print_plan(plan, target, force, dry_run, remove, console)
    if dry_run:
        return plan

    profile = decl.profile if decl else (lock.profile if lock else "")
    previous_render = _previous_profile_render(target, profile) if profile else None

    if to_write_modified:
        backup = _backup_modified_files(
            target, [FileDiff(p, "modified") for p in to_write_modified], desired)
        if backup:
            console.print(f"  [dim]Backup saved to {os.path.relpath(backup, target)}/[/dim]")

    new_files: dict[str, str] = {}
    for rel in plan.install + plan.update + to_write_modified:
        _copy(desired[rel], os.path.join(target, rel))
    for rel in plan.merge:
        merge_settings(desired[rel], os.path.join(target, rel))
    for rel in plan.prune:
        p = os.path.join(target, rel)
        os.chmod(p, 0o644)
        os.remove(p)
    if plan.prune:
        _remove_empty_dirs(target, plan.prune)

    for rel, src in desired.items():
        if rel == "CLAUDE.md":
            continue
        dst = os.path.join(target, rel)
        if rel in plan.keep_modified and not force:
            # keep the locked hash: the file is still the user's edit of it
            if lock and rel in lock.files:
                new_files[rel] = lock.files[rel]
            continue
        if os.path.isfile(dst):
            new_files[rel] = sha256_file(src)
    for rel in plan.keep_orphan:
        new_files[rel] = lock.files[rel] if lock else ""

    claude_dir = os.path.join(target, ".claude")
    if remove:
        for rel in (os.path.join(".claude", ".stx-profile"), LOCK_PATH):
            p = os.path.join(target, rel)
            if os.path.isfile(p):
                os.remove(p)
        if lock and lock.claude_md and lock.claude_md_sha:
            p = os.path.join(target, lock.claude_md)
            if os.path.isfile(p) and sha256_file(p) == lock.claude_md_sha:
                os.remove(p)
        console.print("[green]Claude profile removed[/green] (.claude/custom/ kept).")
        return plan

    _protect_read_only(target, claude_repo)

    custom_dir = os.path.join(claude_dir, "custom")
    if not os.path.isdir(custom_dir):
        os.makedirs(custom_dir, exist_ok=True)
        with open(os.path.join(custom_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(_CUSTOM_README)
    with open(os.path.join(claude_dir, ".stx-profile"), "w", encoding="utf-8") as f:
        f.write(decl.profile + "\n")

    # CLAUDE.md — the template rule (#67), with the lock as proof of ownership
    claude_md, claude_md_sha = "", ""
    j2 = os.path.join(claude_dir, "CLAUDE.md.j2")
    raw = desired.get("CLAUDE.md")
    content = None
    if os.path.isfile(j2):
        content = _render_claude_md(j2, os.path.basename(target), decl.profile)
    elif raw:
        with open(raw, encoding="utf-8") as f:
            content = f.read()
    if content is not None:
        locked_sha = lock.claude_md_sha if lock and lock.claude_md == "CLAUDE.md" else None
        claude_md, changed = write_profile_claude_md(
            target, content, candidates=(previous_render,), locked_sha=locked_sha)
        claude_md_sha = sha256_text(content)
        if changed:
            console.print(f"  [green]✓[/green] {claude_md} (profile text)")
            if claude_md == PROFILE_CLAUDE_MD:
                console.print("  [dim]Your root CLAUDE.md is your own: left untouched "
                              "(Claude Code reads both).[/dim]")

    write_lock(target, Lock(
        profile=decl.profile, include=decl.include, exclude=decl.exclude,
        source=claude_repo, source_rev=_source_rev(claude_repo),
        claude_md=claude_md, claude_md_sha=claude_md_sha, files=new_files,
    ))
    _ensure_gitignore(target, console)
    return plan


def _print_plan(plan: SyncPlan, target: str, force: bool, dry_run: bool, remove: bool, console) -> None:
    head = "Dry run — nothing written" if dry_run else ("Removing" if remove else "Syncing")
    console.print(f"[cyan]{head}[/cyan]: {target}/.claude")
    rows = [
        ("+", "install", plan.install, "green"),
        ("~", "update (upstream changed)", plan.update, "green"),
        ("≈", "merge", plan.merge, "green"),
        ("!", "overwrite local edit (backup)" if force else "keep local edit", plan.keep_modified, "yellow"),
        ("−", "remove (no longer declared)", plan.prune, "cyan"),
        ("!", "keep edited file no longer declared", plan.keep_orphan, "yellow"),
    ]
    for mark, label, items, color in rows:
        if not items:
            continue
        console.print(f"  [{color}]{mark}[/{color}] {len(items)} {label}")
        for rel in items[:20]:
            console.print(f"      {rel}")
        if len(items) > 20:
            console.print(f"      ... and {len(items) - 20} more")
    if not any(items for _m, _l, items, _c in rows):
        console.print(f"  [green]up to date[/green] ({len(plan.unchanged)} file(s))")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command("sync")
@click.argument("path", default=".")
@click.option("--dry-run", is_flag=True, help="Show what would change; write nothing.")
@click.option("--force", is_flag=True, help="Overwrite your local edits too (backup in .claude/.backup/).")
@click.option("--remove", is_flag=True, help="Uninstall: remove every file stx installed (custom/ kept).")
def sync_cmd(path: str, dry_run: bool, force: bool, remove: bool) -> None:
    """Make .claude/ match the [claude] declaration of stx.toml (project mode).

    \b
    [claude]
    mode = "project"
    profile = "presentation"
    exclude = ["stx-ce", "stx-pe"]

    Records what it installed in .claude/stx.lock. Your edits to installed
    files are kept (use --force to replace them); files you added are never
    touched; nothing is ever committed.
    """
    from .claude_cmd import find_claude_repo
    from .workspace_cmd import load_stx_toml

    target = os.path.abspath(path)
    decl = None if remove else read_declaration(target)
    if decl is None and not remove:
        raise click.ClickException(
            f"No project-mode declaration in {os.path.join(target, 'stx.toml')}.\n"
            "Add:\n  [claude]\n  mode = \"project\"\n  profile = \"project\"   # or presentation, …"
        )
    config = load_stx_toml(target) if os.path.isfile(os.path.join(target, "stx.toml")) else {}
    claude_repo = find_claude_repo(target, config)
    sync_project(target, claude_repo, decl, dry_run=dry_run, force=force, remove=remove)
