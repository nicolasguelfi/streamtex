"""Claude AI profile commands: install, list, update, and diff."""

import filecmp
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime

import click

from .console import get_console
from .workspace_cmd import find_workspace_root, load_stx_toml

logger = logging.getLogger(__name__)

_CUSTOM_README = """\
# .claude/custom/ — User Customizations

This directory is for **your** personalized extensions. Files here are:
- **Never overwritten** by `stx claude update`
- **Preserved** across preset upgrades (`stx install --preset`)
- **Loaded by Claude Code** as part of the `.claude/` context

## How to use

| What | Where | Example |
|------|-------|---------|
| Extra coding rules | `custom/references/` | `project_conventions.md` |
| Custom skills | `custom/skills/` | `my_domain_knowledge.md` |
| Custom templates | `custom/templates/` | `my_template.md` |

## Custom slash commands

Custom commands go directly in `.claude/commands/` (not in `custom/commands/`),
because Claude Code only scans `.claude/commands/` for slash commands.
Files you add there are safe — `stx claude update` only overwrites files
declared in the profile manifest.

## Official vs. custom files

- `.claude/references/`, `.claude/developer/`, `.claude/designer/` → **read-only** (managed by StreamTeX)
- `.claude/custom/` → **yours** (never touched by StreamTeX)
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _render_claude_md(template_path: str, project_name: str, profile: str) -> str:
    """Render a CLAUDE.md.j2 template into final CLAUDE.md content.

    Handles ``{{ project_name }}``, ``{{ profile }}``, and simple
    ``{% if profile == "..." %}...{% endif %}`` conditionals without
    requiring Jinja2.
    """
    import re

    with open(template_path, encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{ project_name }}", project_name)
    content = content.replace("{{ profile }}", profile)

    # Process {% if profile == "xxx" %}...{% endif %} blocks
    def _eval_conditional(match: re.Match) -> str:
        cond_profile = match.group(1)
        block = match.group(2)
        return block if cond_profile == profile else ""

    content = re.sub(
        r'\{%\s*if\s+profile\s*==\s*"(\w+)"\s*%\}(.*?)\{%\s*endif\s*%\}',
        _eval_conditional,
        content,
        flags=re.DOTALL,
    )

    # Clean up triple+ blank lines left by removed blocks
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content


def _render_claude_md_for_target(
    target: str, profile: str,
) -> str | None:
    """Render CLAUDE.md from .claude/CLAUDE.md.j2 if the template exists.

    Writes the rendered content to ``CLAUDE.md`` at the project root.
    Returns the rendered path, or ``None`` if no template was found.
    """
    template_path = os.path.join(target, ".claude", "CLAUDE.md.j2")
    if not os.path.isfile(template_path):
        return None

    project_name = os.path.basename(os.path.abspath(target))
    rendered = _render_claude_md(template_path, project_name, profile)

    dst = os.path.join(target, "CLAUDE.md")
    # Make writable if read-only
    if os.path.isfile(dst):
        st = os.stat(dst)
        if not st.st_mode & 0o200:
            os.chmod(dst, st.st_mode | 0o200)

    with open(dst, "w", encoding="utf-8") as f:
        f.write(rendered)

    return dst


def find_claude_repo(ws_root: str, config: dict) -> str:
    """Locate the streamtex-claude repo, checking dev links first.

    Lookup order:
    1. Dev link (project-level or global registration)
    2. Workspace clone (from stx.toml)

    Raises:
        click.ClickException: if the repo cannot be found.
    """
    # 0. Check dev links first
    try:
        from .dev_config import resolve_repo_path
        path, _is_dev = resolve_repo_path("streamtex-claude", ws_root, config)
        return path
    except FileNotFoundError:
        logger.debug("Failed to resolve dev-link for streamtex-claude repo", exc_info=True)

    # 1. Check [claude].source (legacy fallback)
    repos = config.get("repos", {})
    source = config.get("claude", {}).get("source")
    if source and source in repos:
        repo_path = os.path.join(ws_root, repos[source].get("path", source))
        if os.path.isdir(repo_path):
            return repo_path

    # 2. Fallback: find a repo of type "claude"
    for _name, repo_conf in repos.items():
        if repo_conf.get("type") == "claude":
            repo_path = os.path.join(ws_root, repo_conf.get("path", _name))
            if os.path.isdir(repo_path):
                return repo_path

    raise click.ClickException(
        "streamtex-claude repo not found in workspace.\n"
        "Run: stx dev register streamtex-claude /path/to/repo\n"
        "Or:  stx install --preset user"
    )


def list_profiles(claude_repo: str) -> list[dict]:
    """List available profiles from the streamtex-claude repo.

    Returns a list of dicts with keys: name, description, files.
    """
    profiles_dir = os.path.join(claude_repo, "profiles")
    if not os.path.isdir(profiles_dir):
        return []

    import tomllib

    profiles = []
    for entry in sorted(os.listdir(profiles_dir)):
        entry_path = os.path.join(profiles_dir, entry)
        if not os.path.isdir(entry_path):
            continue

        info: dict = {"name": entry, "description": "", "files": 0}

        # Read manifest.toml if present
        manifest_path = os.path.join(entry_path, "manifest.toml")
        if os.path.isfile(manifest_path):
            with open(manifest_path, "rb") as f:
                manifest = tomllib.load(f)
            info["description"] = manifest.get("profile", {}).get("description", "")

        # Count files recursively
        count = 0
        for _root, _dirs, files in os.walk(entry_path):
            count += len(files)
        info["files"] = count

        profiles.append(info)

    return profiles


def _make_writable(directory: str) -> None:
    """Make all files in *directory* writable (undo read-only protection)."""
    if not os.path.isdir(directory):
        return
    for root, _dirs, files in os.walk(directory):
        for f in files:
            fpath = os.path.join(root, f)
            st = os.stat(fpath)
            os.chmod(fpath, st.st_mode | 0o200)


def install_profile(claude_repo: str, profile: str, target: str) -> list[str]:
    """Install a Claude profile into *target* project.

    Returns the list of installed file paths (relative to target).
    """
    profile_dir = os.path.join(claude_repo, "profiles", profile)
    if not os.path.isdir(profile_dir):
        raise click.ClickException(
            f"Profile '{profile}' not found in {os.path.join(claude_repo, 'profiles')}"
        )

    installed: list[str] = []
    target = os.path.abspath(target)
    claude_dir = os.path.join(target, ".claude")
    os.makedirs(claude_dir, exist_ok=True)

    # Unlock any previously read-only files so copytree can overwrite them
    _make_writable(claude_dir)

    # 1. Copy profile contents into .claude/ (except CLAUDE.md and manifest.toml)
    for entry in os.listdir(profile_dir):
        if entry == "manifest.toml":
            continue
        src = os.path.join(profile_dir, entry)

        if entry == "CLAUDE.md":
            # CLAUDE.md goes to project root
            dst = os.path.join(target, "CLAUDE.md")
            shutil.copy2(src, dst)
            installed.append("CLAUDE.md")
            continue

        dst = os.path.join(claude_dir, entry)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            for root, _dirs, files in os.walk(dst):
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), target)
                    installed.append(rel)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            installed.append(os.path.relpath(dst, target))

    # 2. Copy shared/references/ and shared/commands/ (read-only copies)
    for shared_kind, dst_name in [("references", "references"), ("commands", "commands")]:
        shared_dir = os.path.join(claude_repo, "shared", shared_kind)
        if os.path.isdir(shared_dir):
            dst_dir = os.path.join(claude_dir, dst_name)
            shutil.copytree(shared_dir, dst_dir, dirs_exist_ok=True)
            for root, _dirs, files in os.walk(dst_dir):
                for f in files:
                    fpath = os.path.join(root, f)
                    os.chmod(fpath, 0o444)
                    rel = os.path.relpath(fpath, target)
                    if rel not in installed:
                        installed.append(rel)

    # 3. Create .claude/custom/ directory with README if it doesn't exist
    custom_dir = os.path.join(claude_dir, "custom")
    if not os.path.isdir(custom_dir):
        os.makedirs(custom_dir, exist_ok=True)
        readme_path = os.path.join(custom_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(_CUSTOM_README)
        installed.append(os.path.relpath(readme_path, target))

    # 4. Write .claude/.stx-profile marker
    marker_path = os.path.join(claude_dir, ".stx-profile")
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(profile + "\n")
    installed.append(os.path.relpath(marker_path, target))

    # 5. Render CLAUDE.md from .claude/CLAUDE.md.j2 template (if present)
    rendered = _render_claude_md_for_target(target, profile)
    if rendered:
        rel = os.path.relpath(rendered, target)
        if rel not in installed:
            installed.append(rel)

    return sorted(installed)


@dataclass
class FileDiff:
    """Comparison result for a single profile file."""

    path: str  # relative to target
    status: str  # "identical" | "modified" | "missing" | "extra"


def read_installed_profile(target: str) -> str | None:
    """Read the installed profile name from ``.claude/.stx-profile``.

    Returns ``None`` if no profile is installed.
    """
    marker = os.path.join(target, ".claude", ".stx-profile")
    if not os.path.isfile(marker):
        return None
    with open(marker, encoding="utf-8") as f:
        return f.read().strip() or None


def _read_profile_extends(profile_dir: str) -> str:
    """Read the ``extends`` field from a profile's manifest.toml."""
    manifest_path = os.path.join(profile_dir, "manifest.toml")
    if not os.path.isfile(manifest_path):
        return ""
    import tomllib
    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)
    return manifest.get("profile", {}).get("extends", "")


def _collect_dir_files(
    directory: str,
    base_dir: str,
    files: dict[str, str],
) -> None:
    """Walk *directory* and add entries to *files* using *base_dir* as root."""
    for entry in os.listdir(directory):
        if entry == "manifest.toml":
            continue
        src = os.path.join(directory, entry)

        if entry == "CLAUDE.md":
            files["CLAUDE.md"] = src
            continue

        if os.path.isdir(src):
            for root, _dirs, filenames in os.walk(src):
                for fname in filenames:
                    abs_src = os.path.join(root, fname)
                    rel = os.path.relpath(abs_src, base_dir)
                    files[os.path.join(".claude", rel)] = abs_src
        else:
            files[os.path.join(".claude", entry)] = src


def collect_source_files(claude_repo: str, profile: str) -> dict[str, str]:
    """Map relative target paths to absolute source paths for a profile.

    Replicates the path logic from :func:`install_profile`:
    - ``CLAUDE.md`` → project root
    - ``manifest.toml`` → skipped
    - everything else → ``.claude/``
    - ``shared/references/`` → ``.claude/references/``
    - ``shared/commands/`` → ``.claude/commands/``

    When a profile has ``extends``, the parent files are collected first
    (recursively), then the child's ``overlay/`` directory is applied on top.
    Shared references are collected by the root parent only.

    Returns a dict of ``{relative_target_path: absolute_source_path}``.
    """
    profile_dir = os.path.join(claude_repo, "profiles", profile)
    if not os.path.isdir(profile_dir):
        return {}

    parent = _read_profile_extends(profile_dir)

    if parent:
        # Start with parent files (includes shared/references)
        files = collect_source_files(claude_repo, parent)

        # Overlay child-specific files from overlay/ directory
        overlay_dir = os.path.join(profile_dir, "overlay")
        if os.path.isdir(overlay_dir):
            _collect_dir_files(overlay_dir, overlay_dir, files)

        return files

    # No extends — existing behaviour
    files: dict[str, str] = {}
    _collect_dir_files(profile_dir, profile_dir, files)

    # Shared references and commands
    for shared_kind in ("references", "commands"):
        shared_dir = os.path.join(claude_repo, "shared", shared_kind)
        if os.path.isdir(shared_dir):
            for root, _dirs, filenames in os.walk(shared_dir):
                for fname in filenames:
                    abs_src = os.path.join(root, fname)
                    rel = os.path.relpath(abs_src, shared_dir)
                    files[os.path.join(".claude", shared_kind, rel)] = abs_src

    return files


def compare_profile(
    claude_repo: str,
    profile: str,
    target: str,
) -> list[FileDiff]:
    """Compare installed profile files against the source repo.

    Returns a list of :class:`FileDiff` entries sorted by path.
    """
    source_files = collect_source_files(claude_repo, profile)
    target = os.path.abspath(target)
    diffs: list[FileDiff] = []

    for rel_path, src_path in sorted(source_files.items()):
        dst_path = os.path.join(target, rel_path)
        if not os.path.isfile(dst_path):
            diffs.append(FileDiff(path=rel_path, status="missing"))
        elif filecmp.cmp(src_path, dst_path, shallow=False):
            diffs.append(FileDiff(path=rel_path, status="identical"))
        else:
            diffs.append(FileDiff(path=rel_path, status="modified"))

    # Check for extra files in .claude/ not in source (excluding .stx-profile and custom/)
    claude_dir = os.path.join(target, ".claude")
    custom_prefix = os.path.join(".claude", "custom")
    if os.path.isdir(claude_dir):
        for root, _dirs, filenames in os.walk(claude_dir):
            rel_root = os.path.relpath(root, target)
            # Skip custom/ directory entirely — user-owned
            if rel_root == custom_prefix or rel_root.startswith(custom_prefix + os.sep):
                continue
            for fname in filenames:
                abs_path = os.path.join(root, fname)
                rel = os.path.relpath(abs_path, target)
                if rel not in source_files and fname != ".stx-profile":
                    diffs.append(FileDiff(path=rel, status="extra"))

    return sorted(diffs, key=lambda d: d.path)


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------

@click.command()
@click.argument("profile")
@click.argument("path", default=".")
def install(profile, path):
    """Install a Claude AI profile into a project."""
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )

    config = load_stx_toml(ws_root)
    claude_repo = find_claude_repo(ws_root, config)

    target = os.path.abspath(path)
    installed = install_profile(claude_repo, profile, target)

    console = get_console()
    console.print(f"[green]Profile '{profile}' installed into {target}[/green]")
    console.print(f"  {len(installed)} files copied")
    for f in installed:
        console.print(f"    {f}")


@click.command("list")
def list_cmd():
    """List available Claude AI profiles."""
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )

    config = load_stx_toml(ws_root)
    claude_repo = find_claude_repo(ws_root, config)
    profiles = list_profiles(claude_repo)

    if not profiles:
        console = get_console()
        console.print("[yellow]No profiles found.[/yellow]")
        return

    from rich.table import Table

    table = Table(title="Available Claude AI profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Files", justify="right")

    for p in profiles:
        table.add_row(p["name"], p["description"], str(p["files"]))

    console = get_console()
    console.print(table)


def _resolve_profile_context(
    path: str,
) -> tuple[str, str, str, str]:
    """Resolve workspace, claude repo, profile name, and target path.

    Returns ``(ws_root, claude_repo, profile, target)``.

    Raises:
        click.ClickException: if workspace or profile is not found.
    """
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )

    config = load_stx_toml(ws_root)
    claude_repo = find_claude_repo(ws_root, config)
    target = os.path.abspath(path)

    profile = read_installed_profile(target)
    if profile is None:
        raise click.ClickException(
            f"No Claude profile installed in {target}. "
            "Run 'stx claude install <profile> [path]' first."
        )

    return ws_root, claude_repo, profile, target


def _render_diff_table(
    diffs: list[FileDiff],
    *,
    title: str,
) -> None:
    """Display a Rich table of file diffs."""
    from rich.table import Table

    console = get_console()

    table = Table(title=title)
    table.add_column("File", style="cyan")
    table.add_column("Status")

    icons = {
        "identical": "[green]\u2713 Identical[/green]",
        "modified": "[yellow]\u25cb Modified[/yellow]",
        "missing": "[red]\u2717 Missing[/red]",
        "extra": "[dim]+ Extra[/dim]",
    }

    for d in diffs:
        table.add_row(d.path, icons.get(d.status, d.status))

    console.print(table)

    counts = {}
    for d in diffs:
        counts[d.status] = counts.get(d.status, 0) + 1

    parts = []
    if counts.get("identical"):
        parts.append(f"[green]{counts['identical']} identical[/green]")
    if counts.get("modified"):
        parts.append(f"[yellow]{counts['modified']} modified[/yellow]")
    if counts.get("missing"):
        parts.append(f"[red]{counts['missing']} missing[/red]")
    if counts.get("extra"):
        parts.append(f"[dim]{counts['extra']} extra[/dim]")
    console.print("  " + ", ".join(parts))


def find_profile_targets(ws_root: str) -> list[tuple[str, str]]:
    """Find all directories with an installed Claude profile.

    Scans first-level directories and ``projects/`` subdirectories for
    ``.claude/.stx-profile`` markers.

    Returns a list of ``(target_path, profile_name)`` tuples.
    """
    results: list[tuple[str, str]] = []

    def _check(dirpath: str) -> None:
        profile = read_installed_profile(dirpath)
        if profile is not None:
            results.append((dirpath, profile))

    for entry in sorted(os.listdir(ws_root)):
        entry_path = os.path.join(ws_root, entry)
        if os.path.isdir(entry_path) and not entry.startswith("."):
            _check(entry_path)

    projects_dir = os.path.join(ws_root, "projects")
    if os.path.isdir(projects_dir):
        for entry in sorted(os.listdir(projects_dir)):
            entry_path = os.path.join(projects_dir, entry)
            if os.path.isdir(entry_path) and not entry.startswith("."):
                _check(entry_path)

    return results


def _backup_modified_files(
    target: str,
    diffs: list,
    source_files: dict[str, str],
) -> str | None:
    """Back up locally modified files before overwriting.

    Creates a timestamped backup directory under ``.claude/.backup/``.
    Only backs up files that exist locally and differ from the source.

    Returns the backup directory path, or ``None`` if no files were backed up.
    """
    to_backup: list[str] = []
    for d in diffs:
        if d.status != "modified":
            continue
        dst_path = os.path.join(target, d.path)
        if not os.path.isfile(dst_path):
            continue
        src_path = source_files.get(d.path)
        if src_path and not filecmp.cmp(src_path, dst_path, shallow=False):
            to_backup.append(d.path)

    if not to_backup:
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = os.path.join(target, ".claude", ".backup", timestamp)
    os.makedirs(backup_dir, exist_ok=True)

    for rel_path in to_backup:
        src = os.path.join(target, rel_path)
        dst = os.path.join(backup_dir, rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        # Make readable even if source is read-only
        if os.path.isfile(src):
            shutil.copy2(src, dst)

    return backup_dir


_CLAUDE_GITIGNORE_BLOCK = """\

# Claude profile — managed by stx claude install/update, not git
.claude/*
!.claude/custom/
!.claude/.stx-profile
"""


def _ensure_claude_gitignore(target: str, console) -> None:
    """Ensure .claude/ is in .gitignore and untracked from git.

    This migrates existing repos where .claude/ was previously tracked.
    If the migration changes the git index and there are no pre-existing
    staged changes, the migration is auto-committed.  Otherwise the user
    is told to commit manually (to avoid mixing migration with unrelated
    staged work).
    """
    import subprocess

    git_dir = os.path.join(target, ".git")
    if not os.path.isdir(git_dir):
        return  # Not a git repo — nothing to do

    def _git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args],
            cwd=target,
            capture_output=True,
            text=True,
            timeout=30,
        )

    # 1. Ensure .gitignore has the .claude/ block
    gitignore_path = os.path.join(target, ".gitignore")
    gitignore_content = ""
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as f:
            gitignore_content = f.read()

    gitignore_changed = False
    if ".claude/*" not in gitignore_content:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write(_CLAUDE_GITIGNORE_BLOCK)
        gitignore_changed = True
        console.print("  [green]\u2713[/green] .gitignore: added .claude/ exclusion rules")

    # 2. Check if .claude/ files are tracked by git (excluding custom/ and .stx-profile)
    try:
        result = _git("ls-files", ".claude/")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return

    if result.returncode != 0 or not result.stdout.strip():
        return  # Nothing tracked

    tracked = [
        f for f in result.stdout.strip().splitlines()
        if not f.startswith(".claude/custom/") and f != ".claude/.stx-profile"
    ]

    if not tracked:
        return

    # 3. Check for pre-existing staged changes (to avoid mixing with migration)
    staged_before = _git("diff", "--cached", "--name-only")
    has_staged = bool(staged_before.stdout.strip())

    # 4. Untrack .claude/ files (keeps local copies, removes from git index)
    console.print(
        f"  [yellow]Migrating:[/yellow] removing {len(tracked)} "
        ".claude/ file(s) from git tracking (local copies preserved)"
    )
    _git("rm", "-r", "--cached", "--quiet", ".claude/")

    # Re-add the exceptions that should stay tracked
    for exception in [".claude/custom/", ".claude/.stx-profile"]:
        exc_path = os.path.join(target, exception)
        if os.path.exists(exc_path):
            _git("add", exception)

    # Stage .gitignore if we modified it
    if gitignore_changed:
        _git("add", ".gitignore")

    # 5. Auto-commit if no pre-existing staged changes
    if has_staged:
        console.print(
            "  [green]\u2713[/green] .claude/ untracked from git "
            "(run [bold]git commit[/bold] to finalize — "
            "skipped auto-commit because you have other staged changes)"
        )
    else:
        result = _git(
            "commit", "-m",
            "chore: stop tracking .claude/ managed files\n\n"
            "Files in .claude/ (except custom/ and .stx-profile) are now\n"
            "managed by `stx claude install/update`, not git.\n"
            "Local copies are preserved. This migration was performed\n"
            "automatically by `stx update`.",
        )
        if result.returncode == 0:
            console.print(
                "  [green]\u2713[/green] .claude/ untracked from git "
                "[dim](auto-committed)[/dim]"
            )
        else:
            console.print(
                "  [green]\u2713[/green] .claude/ untracked from git "
                "(run [bold]git commit[/bold] to finalize)"
            )


def _update_single_target(
    claude_repo: str,
    profile: str,
    target: str,
    force: bool,
    console,
) -> int:
    """Update a single target from its profile source.

    Returns the number of files updated.
    """
    diffs = compare_profile(claude_repo, profile, target)
    source_files = collect_source_files(claude_repo, profile)

    # Ensure .claude/custom/ exists (for projects created before this feature)
    custom_dir = os.path.join(target, ".claude", "custom")
    if not os.path.isdir(custom_dir):
        os.makedirs(custom_dir, exist_ok=True)
        readme_path = os.path.join(custom_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(_CUSTOM_README)

    # Migrate: ensure .claude/ is gitignored and untracked
    _ensure_claude_gitignore(target, console)

    # Back up modified files before overwriting
    backup_dir = _backup_modified_files(target, diffs, source_files)
    if backup_dir:
        rel_backup = os.path.relpath(backup_dir, target)
        console.print(f"  [dim]Backup saved to {rel_backup}/[/dim]")

    updated: list[str] = []
    skipped: list[str] = []

    for d in diffs:
        if d.status == "identical":
            continue
        if d.status == "extra":
            continue

        # Preserve locally modified files unless --force
        # (custom/ files never appear in source_files, so they are inherently safe)
        if d.status == "modified" and not force:
            skipped.append(d.path)
            continue

        src_path = source_files.get(d.path)
        if src_path is None:
            continue

        dst_path = os.path.join(target, d.path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        # Temporarily make writable if read-only
        if os.path.isfile(dst_path):
            os.chmod(dst_path, 0o644)
        shutil.copy2(src_path, dst_path)
        # Re-protect all .claude/ files (read-only copies of streamtex-claude sources)
        if d.path.startswith(".claude"):
            os.chmod(dst_path, 0o444)
        updated.append(d.path)

    # Re-render CLAUDE.md from .j2 template after any file update
    # (also renders if CLAUDE.md is missing or .j2 was updated)
    j2_path = os.path.join(target, ".claude", "CLAUDE.md.j2")
    claude_md_path = os.path.join(target, "CLAUDE.md")
    if os.path.isfile(j2_path):
        project_name = os.path.basename(os.path.abspath(target))
        rendered = _render_claude_md(j2_path, project_name, profile)
        needs_render = not os.path.isfile(claude_md_path)
        if not needs_render:
            with open(claude_md_path, encoding="utf-8") as f:
                needs_render = f.read() != rendered
        if needs_render:
            if os.path.isfile(claude_md_path):
                st = os.stat(claude_md_path)
                if not st.st_mode & 0o200:
                    os.chmod(claude_md_path, st.st_mode | 0o200)
            with open(claude_md_path, "w", encoding="utf-8") as f:
                f.write(rendered)
            updated.append("CLAUDE.md")
            console.print("  [green]\u2713[/green] CLAUDE.md [dim](rendered from .claude/CLAUDE.md.j2)[/dim]")

    if updated:
        console.print(f"\n[green]Updated {len(updated)} file(s).[/green]")
        for f in updated:
            if f != "CLAUDE.md":  # already printed above with render note
                console.print(f"  [green]\u2713[/green] {f}")
    else:
        console.print("\n[bold green]Profile is already up to date.[/bold green]")

    if skipped:
        console.print(
            f"\n[yellow]Skipped {len(skipped)} locally modified file(s).[/yellow]\n"
            "  These files differ from the source — local changes would be lost.\n"
            "  Use [bold]--force[/bold] to overwrite (a backup is saved to .claude/.backup/)."
        )
        for f in skipped:
            console.print(f"  [yellow]\u25cb[/yellow] {f}")

    return len(updated)


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------

@click.command("diff")
@click.argument("path", default=".")
def diff_cmd(path: str) -> None:
    """Compare installed Claude profile against the source repo."""
    _ws_root, claude_repo, profile, target = _resolve_profile_context(path)

    console = get_console()
    console.print(f"[cyan]Profile:[/cyan] {profile}")

    diffs = compare_profile(claude_repo, profile, target)

    if not diffs:
        console.print("[yellow]No profile files found to compare.[/yellow]")
        return

    _render_diff_table(diffs, title=f"Claude profile diff: {profile}")

    if all(d.status == "identical" for d in diffs):
        console.print("\n[bold green]Profile is up to date.[/bold green]")
    else:
        console.print(
            "\n[yellow]Profile has differences.[/yellow] "
            "Run 'stx claude update' to synchronize."
        )


@click.command("update")
@click.argument("path", default=".")
@click.option(
    "--force", is_flag=True,
    help="Overwrite all files including CLAUDE.md.",
)
@click.option(
    "--all", "update_all", is_flag=True,
    help="Update all projects in the workspace.",
)
def update_cmd(path: str, force: bool, update_all: bool) -> None:
    """Update an installed Claude profile from the source repo."""
    console = get_console()

    if update_all:
        ws_root = find_workspace_root()
        if ws_root is None:
            raise click.ClickException(
                "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
            )
        config = load_stx_toml(ws_root)
        claude_repo = find_claude_repo(ws_root, config)

        targets = find_profile_targets(ws_root)
        if not targets:
            console.print("[yellow]No projects with Claude profiles found.[/yellow]")
            return

        total_updated = 0
        for target_path, profile in targets:
            rel = os.path.relpath(target_path, ws_root)
            console.print(f"\n[bold cyan]\u2500\u2500 {rel} [/bold cyan]([cyan]{profile}[/cyan])")
            total_updated += _update_single_target(
                claude_repo, profile, target_path, force, console,
            )

        separator = "\u2500" * 40
        console.print(f"\n[bold]{separator}[/bold]")
        if total_updated:
            console.print(
                f"[green]Total: {total_updated} file(s) updated "
                f"across {len(targets)} project(s).[/green]"
            )
        else:
            console.print(
                f"[bold green]All {len(targets)} project(s) are up to date.[/bold green]"
            )
        return

    # Single target mode
    _ws_root, claude_repo, profile, target = _resolve_profile_context(path)
    console.print(f"[cyan]Profile:[/cyan] {profile}")
    _update_single_target(claude_repo, profile, target, force, console)


@click.command("check")
def check_cmd() -> None:
    """Check synchronization status of all Claude profiles in the workspace."""
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )

    config = load_stx_toml(ws_root)
    claude_repo = find_claude_repo(ws_root, config)
    console = get_console()

    targets = find_profile_targets(ws_root)
    if not targets:
        console.print("[yellow]No projects with Claude profiles found.[/yellow]")
        return

    has_problems = False
    for target_path, profile in targets:
        rel = os.path.relpath(target_path, ws_root)
        diffs = compare_profile(claude_repo, profile, target_path)

        problems = [d for d in diffs if d.status in ("modified", "missing")]
        if problems:
            has_problems = True
            console.print(
                f"[red]\u2717[/red] {rel} ({profile}) "
                f"\u2014 {len(problems)} file(s) out of sync"
            )
            for d in problems:
                if d.status == "missing":
                    icon = "[red]\u2717 Missing[/red]"
                else:
                    icon = "[yellow]\u25cb Modified[/yellow]"
                console.print(f"    {icon}: {d.path}")
        else:
            console.print(f"[green]\u2713[/green] {rel} ({profile}) \u2014 up to date")

    if has_problems:
        console.print(
            "\n[yellow]Run 'stx claude update --all' to synchronize.[/yellow]"
        )
        raise SystemExit(1)
    else:
        console.print(
            f"\n[bold green]All {len(targets)} project(s) are up to date.[/bold green]"
        )
