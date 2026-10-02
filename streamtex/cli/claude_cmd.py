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
    target: str, profile: str, *, previous_render: str | None = None,
) -> str | None:
    """Render ``.claude/CLAUDE.md.j2`` (if present) where it belongs (#67).

    The root ``CLAUDE.md`` receives the render only when stx owns it (absent,
    or equal to *previous_render* / the new render); a user-authored root
    file is left untouched and the render goes to ``.claude/CLAUDE.md``.
    Returns the destination relative to *target*, or ``None`` without template.
    """
    from ._claude_files import write_profile_claude_md

    template_path = os.path.join(target, ".claude", "CLAUDE.md.j2")
    if not os.path.isfile(template_path):
        return None

    project_name = os.path.basename(os.path.abspath(target))
    rendered = _render_claude_md(template_path, project_name, profile)
    dest_rel, _changed = write_profile_claude_md(
        target, rendered, candidates=(previous_render,),
    )
    return dest_rel


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


def _previous_profile_render(target: str, profile: str) -> str | None:
    """Render of the template installed BEFORE an install/update (#67).

    A root CLAUDE.md equal to this render was produced by stx, so stx may
    replace it; any other content belongs to the user.
    """
    j2_path = os.path.join(target, ".claude", "CLAUDE.md.j2")
    if not os.path.isfile(j2_path):
        return None
    return _render_claude_md(j2_path, os.path.basename(os.path.abspath(target)), profile)


def install_profile(claude_repo: str, profile: str, target: str) -> list[str]:
    """Install a Claude profile into *target* project.

    The installed set is exactly :func:`collect_source_files` — the set that
    ``update``, ``diff`` and ``check`` compare against — so a child profile
    (``extends``) gets its parent then its ``overlay/`` (#65, #66).

    - Shared references and commands are read-only copies (``0o444``).
    - A user-authored root ``CLAUDE.md`` is never overwritten: the profile
      text then goes to ``.claude/CLAUDE.md`` (#67).
    - An existing ``.claude/settings.json`` is merged, never replaced (#68).

    Returns the list of installed file paths (relative to target).
    """
    from ._claude_files import SETTINGS_PATH, merge_settings, write_profile_claude_md

    profile_dir = os.path.join(claude_repo, "profiles", profile)
    if not os.path.isdir(profile_dir):
        raise click.ClickException(
            f"Profile '{profile}' not found in {os.path.join(claude_repo, 'profiles')}"
        )

    installed: list[str] = []
    target = os.path.abspath(target)
    claude_dir = os.path.join(target, ".claude")
    previous_render = _previous_profile_render(target, profile)
    os.makedirs(claude_dir, exist_ok=True)

    # Unlock any previously read-only files so they can be overwritten
    _make_writable(claude_dir)

    for rel, src in collect_source_files(claude_repo, profile).items():
        dst = os.path.join(target, rel)
        if rel == "CLAUDE.md":
            # A raw CLAUDE.md shipped by the profile: same ownership rule
            with open(src, encoding="utf-8") as f:
                dest_rel, _changed = write_profile_claude_md(
                    target, f.read(), candidates=(previous_render,),
                )
            installed.append(dest_rel)
            continue
        if rel == SETTINGS_PATH and os.path.isfile(dst):
            merge_settings(src, dst)
            installed.append(rel)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isfile(dst) and not os.access(dst, os.W_OK):
            os.chmod(dst, 0o644)
        shutil.copy2(src, dst)
        installed.append(rel)

    # Read-only protection, as in 0.7.34: every file under .claude/references
    # and .claude/commands (the shared copies land there, merged with the
    # profile's own commands).
    for kind in ("references", "commands"):
        if not os.path.isdir(os.path.join(claude_repo, "shared", kind)):
            continue
        for root, _dirs, files in os.walk(os.path.join(claude_dir, kind)):
            for f in files:
                os.chmod(os.path.join(root, f), 0o444)

    # Create .claude/custom/ directory with README if it doesn't exist
    custom_dir = os.path.join(claude_dir, "custom")
    if not os.path.isdir(custom_dir):
        os.makedirs(custom_dir, exist_ok=True)
        readme_path = os.path.join(custom_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(_CUSTOM_README)
        installed.append(os.path.relpath(readme_path, target))

    # Write .claude/.stx-profile marker
    marker_path = os.path.join(claude_dir, ".stx-profile")
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(profile + "\n")
    installed.append(os.path.relpath(marker_path, target))

    # Render CLAUDE.md from .claude/CLAUDE.md.j2 (if present), where it belongs
    rendered = _render_claude_md_for_target(target, profile, previous_render=previous_render)
    if rendered and rendered not in installed:
        installed.append(rendered)

    return sorted(installed)


# Files stx writes itself (never part of a profile source, never pruned).
_GENERATED_PATHS = frozenset({
    os.path.join(".claude", ".stx-profile"),
    os.path.join(".claude", "CLAUDE.md"),   # profile text when the root CLAUDE.md is the user's
    os.path.join(".claude", "stx.lock"),    # project mode lock file
})


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

    from ._claude_files import SETTINGS_PATH, settings_cover

    for rel_path, src_path in sorted(source_files.items()):
        dst_path = os.path.join(target, rel_path)
        if not os.path.isfile(dst_path):
            diffs.append(FileDiff(path=rel_path, status="missing"))
        elif filecmp.cmp(src_path, dst_path, shallow=False):
            diffs.append(FileDiff(path=rel_path, status="identical"))
        elif rel_path == SETTINGS_PATH and settings_cover(dst_path, src_path):
            # Merged settings (#68): the local file contains everything the
            # profile sets, plus the user's own entries.
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
                if rel not in source_files and rel not in _GENERATED_PATHS:
                    diffs.append(FileDiff(path=rel, status="extra"))

    return sorted(diffs, key=lambda d: d.path)


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------

def plan_install(claude_repo: str, profile: str, target: str) -> tuple[list[tuple[str, str]], list[str]]:
    """What :func:`install_profile` would do, without writing anything (#70).

    Returns ``(actions, conflicts)``: ``actions`` is a sorted list of
    ``(relative_path, action)`` with action in ``create`` / ``replace`` /
    ``keep`` / ``merge``; ``conflicts`` lists existing files that stx did not
    install (the target has no ``.claude/.stx-profile``) and that the install
    would replace.
    """
    from ._claude_files import SETTINGS_PATH, root_claude_md_is_owned

    target = os.path.abspath(target)
    previously_installed = read_installed_profile(target) is not None
    previous_render = _previous_profile_render(target, profile)
    actions: list[tuple[str, str]] = []
    conflicts: list[str] = []
    for rel, src in sorted(collect_source_files(claude_repo, profile).items()):
        dst = os.path.join(target, rel)
        if rel == "CLAUDE.md":
            with open(src, encoding="utf-8") as f:
                owned = root_claude_md_is_owned(target, candidates=(previous_render, f.read()))
            dest = rel if owned else os.path.join(".claude", "CLAUDE.md")
            exists = os.path.isfile(os.path.join(target, dest))
            actions.append((dest, "replace" if exists else "create"))
            continue
        if not os.path.isfile(dst):
            actions.append((rel, "create"))
        elif filecmp.cmp(src, dst, shallow=False):
            actions.append((rel, "keep"))
        elif rel == SETTINGS_PATH:
            actions.append((rel, "merge"))
        else:
            actions.append((rel, "replace"))
            if not previously_installed:
                conflicts.append(rel)
    j2 = [src for rel, src in collect_source_files(claude_repo, profile).items()
          if rel == os.path.join(".claude", "CLAUDE.md.j2")]
    if j2:
        rendered = _render_claude_md(j2[0], os.path.basename(target), profile)
        owned = root_claude_md_is_owned(target, candidates=(previous_render, rendered))
        dest = "CLAUDE.md" if owned else os.path.join(".claude", "CLAUDE.md")
        exists = os.path.isfile(os.path.join(target, dest))
        actions.append((dest, ("replace" if exists else "create") + " (rendered from CLAUDE.md.j2)"))
    return actions, conflicts


@click.command()
@click.argument("profile")
@click.argument("path", default=".")
@click.option("--dry-run", is_flag=True, help="Show every file the install would write; write nothing.")
@click.option("-y", "--yes", is_flag=True,
              help="Install even when existing files that stx did not install would be replaced.")
def install(profile, path, dry_run, yes):
    """Install a Claude AI profile into a project.

    A user-authored root CLAUDE.md is never overwritten: the profile text then
    goes to .claude/CLAUDE.md (Claude Code reads both). An existing
    .claude/settings.json is merged. Use --dry-run first in an existing
    repository.
    """
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )

    config = load_stx_toml(ws_root)
    claude_repo = find_claude_repo(ws_root, config)

    target = os.path.abspath(path)
    console = get_console()

    if not os.path.isdir(os.path.join(claude_repo, "profiles", profile)):
        raise click.ClickException(
            f"Profile '{profile}' not found in {os.path.join(claude_repo, 'profiles')}"
        )
    actions, conflicts = plan_install(claude_repo, profile, target)

    if dry_run:
        console.print(f"[cyan]Dry run[/cyan] — profile '{profile}' into {target} (nothing written)")
        if conflicts:
            console.print(f"\n[yellow]{len(conflicts)} existing file(s) not installed by stx "
                          "would be replaced:[/yellow]")
            for rel in conflicts:
                console.print(f"  [yellow]![/yellow] {rel}")
        counts: dict[str, int] = {}
        for _rel, action in actions:
            counts[action.split(" ")[0]] = counts.get(action.split(" ")[0], 0) + 1
        console.print("\n" + ", ".join(f"{n} {a}" for a, n in sorted(counts.items())))
        for rel, action in actions:
            if not action.startswith("keep"):
                console.print(f"  {action:<8} {rel}")
        return

    if conflicts and not yes:
        listing = "\n".join(f"  {rel}" for rel in conflicts[:20])
        more = f"\n  ... and {len(conflicts) - 20} more" if len(conflicts) > 20 else ""
        raise click.ClickException(
            f"{len(conflicts)} existing file(s) were not installed by stx and would be "
            f"replaced:\n{listing}{more}\n"
            "Review with --dry-run, then rerun with --yes to install anyway."
        )

    installed = install_profile(claude_repo, profile, target)

    console.print(f"[green]Profile '{profile}' installed into {target}[/green]")
    console.print(f"  {len(installed)} files copied")
    for f in installed:
        console.print(f"    {f}")
    if os.path.join(".claude", "CLAUDE.md") in installed:
        console.print(
            "  [dim]Your root CLAUDE.md was left untouched; the profile text is in "
            ".claude/CLAUDE.md (Claude Code reads both).[/dim]"
        )


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
    ``.claude/.stx-profile`` markers or a project-mode ``[claude]``
    declaration, plus the workspace root itself when it declares project mode.

    Returns a list of ``(target_path, profile_name)`` tuples.
    """
    from .claude_project import read_declaration

    results: list[tuple[str, str]] = []

    def _declared(dirpath: str) -> str | None:
        try:
            decl = read_declaration(dirpath)
        except click.ClickException:
            return None
        return decl.profile if decl else None

    def _check(dirpath: str) -> None:
        profile = read_installed_profile(dirpath) or _declared(dirpath)
        if profile is not None:
            results.append((dirpath, profile))

    # The workspace root itself, only when it declares project mode (#71):
    # a root with a classic profile keeps 0.7.34 behaviour (not scanned).
    root_profile = _declared(ws_root)
    if root_profile is not None:
        results.append((ws_root, root_profile))

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


def _ensure_claude_gitignore(target: str, console, *, commit: bool = False) -> None:
    """Ensure .claude/ is in .gitignore; untrack it from git only on request (#69).

    The ``.gitignore`` block is always added when missing. Removing tracked
    ``.claude/`` files from the index and committing happen only when
    *commit* is True (``stx claude update --commit``); otherwise the git
    commands are printed for the user to run. stx never commits on its own.
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

    if not commit:
        console.print(
            f"  [yellow]Note:[/yellow] {len(tracked)} .claude/ file(s) are still tracked by git. "
            "To stop tracking them (local copies kept), run:\n"
            "    git rm -r --cached .claude/ && git add .claude/custom/ .claude/.stx-profile"
            + (" .gitignore" if gitignore_changed else "")
            + "\n    git commit -m \"chore: stop tracking .claude/ managed files\"\n"
            "  or rerun with [bold]--commit[/bold]."
        )
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

    # 5. Commit (explicitly requested) if no pre-existing staged changes
    if has_staged:
        console.print(
            "  [green]\u2713[/green] .claude/ untracked from git "
            "(run [bold]git commit[/bold] to finalize — "
            "not committed because you have other staged changes)"
        )
    else:
        result = _git(
            "commit", "-m",
            "chore: stop tracking .claude/ managed files\n\n"
            "Files in .claude/ (except custom/ and .stx-profile) are now\n"
            "managed by `stx claude install/update`, not git.\n"
            "Local copies are preserved. Requested with `stx claude update --commit`.",
        )
        if result.returncode == 0:
            console.print(
                "  [green]\u2713[/green] .claude/ untracked from git [dim](committed)[/dim]"
            )
        else:
            console.print(
                "  [green]\u2713[/green] .claude/ untracked from git "
                "(run [bold]git commit[/bold] to finalize)"
            )


def _is_managed_clone(target: str) -> bool:
    """True when *target* is a repo declared in the enclosing workspace's ``[repos]``.

    Those clones (streamtex-docs, …) are created and pulled by ``stx update``;
    they are not user projects.
    """
    parent = os.path.dirname(os.path.abspath(target))
    ws_root = find_workspace_root(parent)
    if ws_root is None:
        return False
    try:
        config = load_stx_toml(ws_root)
    except Exception:  # noqa: BLE001 — unreadable config: treat as a user project
        return False
    for name, conf in config.get("repos", {}).items():
        if not isinstance(conf, dict):
            continue
        path = os.path.abspath(os.path.join(ws_root, conf.get("path", name)))
        if path == os.path.abspath(target):
            return True
    return False


_BACKUP_PREFIX = os.path.join(".claude", ".backup")
_STX_PROFILE_PATH = os.path.join(".claude", ".stx-profile")
_RECAP_TRUNCATE_AT = 20  # show at most this many paths per category


def _is_protected_path(rel_path: str) -> bool:
    """Return True if rel_path must NEVER be removed, even under prune."""
    if rel_path == _BACKUP_PREFIX or rel_path.startswith(_BACKUP_PREFIX + os.sep):
        return True
    if rel_path == _STX_PROFILE_PATH or rel_path in _GENERATED_PATHS:
        return True
    # .claude/custom/ is already filtered by compare_profile(); this is
    # defence in depth in case the filter ever regresses.
    custom_prefix = os.path.join(".claude", "custom")
    return rel_path == custom_prefix or rel_path.startswith(custom_prefix + os.sep)


def _print_recap(
    to_install: list,
    to_overwrite: list,
    to_preserve: list,
    to_prune: list,
    target: str,
    console,
) -> None:
    """Print a human-readable summary of pending changes before confirmation."""
    console.print(f"\nThe following changes will be applied to [cyan]{target}/.claude/[/cyan]:")
    console.print()
    if to_install:
        console.print(f"  [green]+[/green]  {len(to_install)} file(s) to install (missing in target)")
    if to_overwrite:
        console.print(
            f"  [yellow]~[/yellow]  {len(to_overwrite)} file(s) to overwrite "
            "(locally modified — backup saved)"
        )
    if to_preserve:
        console.print(
            f"  [yellow]○[/yellow]  {len(to_preserve)} file(s) locally modified — will be "
            "[bold]PRESERVED[/bold] (run with --force to overwrite)"
        )
    if to_prune:
        console.print(
            f"  [cyan]−[/cyan]  {len(to_prune)} file(s) to remove (orphans — no longer "
            "declared by streamtex-claude)"
        )

    def _list_paths(label: str, items: list, marker: str, color: str) -> None:
        if not items:
            return
        console.print(f"\n[bold]{label}:[/bold]")
        for d in items[:_RECAP_TRUNCATE_AT]:
            console.print(f"  [{color}]{marker}[/{color}] {d.path}")
        if len(items) > _RECAP_TRUNCATE_AT:
            console.print(f"  [dim]... and {len(items) - _RECAP_TRUNCATE_AT} more[/dim]")

    _list_paths("Files to be removed", to_prune, "−", "cyan")
    _list_paths("Files to be overwritten", to_overwrite, "~", "yellow")
    console.print()


def _remove_empty_dirs(target: str, paths_removed: list[str]) -> None:
    """Walk up from each removed file path; rmdir any now-empty parents.

    Stops at .claude/ (never removes it) and never touches protected
    paths (custom/, .backup/).
    """
    claude_root = os.path.join(target, ".claude")
    seen: set[str] = set()
    for rel_path in paths_removed:
        # Start from the parent of the deleted file
        abs_dir = os.path.dirname(os.path.join(target, rel_path))
        while abs_dir and abs_dir not in seen:
            seen.add(abs_dir)
            # Stop at .claude/ itself (never remove it)
            if os.path.normpath(abs_dir) == os.path.normpath(claude_root):
                break
            # Stop if we've climbed above .claude/
            try:
                rel = os.path.relpath(abs_dir, target)
            except ValueError:
                break
            if not rel.startswith(".claude"):
                break
            # Never touch protected paths even when they look empty
            if _is_protected_path(rel):
                break
            if not os.path.isdir(abs_dir):
                break
            try:
                # rmdir succeeds only if the directory is empty
                os.rmdir(abs_dir)
            except OSError:
                # Not empty or permission issue — stop climbing this branch
                break
            abs_dir = os.path.dirname(abs_dir)


def _update_single_target(
    claude_repo: str,
    profile: str,
    target: str,
    force: bool,
    console,
    yes: bool = False,
    commit: bool | None = None,
) -> int:
    """Update a single target from its profile source.

    Behaviour:
    - Files missing in target           → installed
    - Files locally modified            → preserved (or overwritten if force=True,
                                          always with a backup to .claude/.backup/)
    - Files extra in target (orphans)   → removed (always — this is the only way
                                          to keep target aligned with the source
                                          of truth). Protected paths
                                          (.claude/custom/, .claude/.backup/,
                                          .claude/.stx-profile) are never touched.

    Before any destructive operation (overwrite or removal), a recap is shown
    and an interactive confirmation prompt is required, unless yes=True.

    Returns the number of files updated (installs + overwrites + prunes).

    A target in project mode (``[claude] mode = "project"``) is synced from
    its declaration instead (#71).
    """
    from .claude_project import is_project_mode, read_declaration, sync_project

    if is_project_mode(target):
        plan = sync_project(target, claude_repo, read_declaration(target), force=force, console=console)
        return len(plan.install) + len(plan.update) + len(plan.merge) + len(plan.prune) + (
            len(plan.keep_modified) if force else 0)

    diffs = compare_profile(claude_repo, profile, target)
    source_files = collect_source_files(claude_repo, profile)
    # Render of the template as installed BEFORE this update (#67)
    previous_render = _previous_profile_render(target, profile)

    # Ensure .claude/custom/ exists (for projects created before this feature)
    custom_dir = os.path.join(target, ".claude", "custom")
    if not os.path.isdir(custom_dir):
        os.makedirs(custom_dir, exist_ok=True)
        readme_path = os.path.join(custom_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(_CUSTOM_README)

    # Migrate: ensure .claude/ is gitignored (untracked only with --commit, #69).
    # Clones of official repos that stx itself manages and pulls keep the
    # 0.7.34 migration commit, so that their tree stays clean for `git pull`.
    if commit is None:
        commit = _is_managed_clone(target)
    _ensure_claude_gitignore(target, console, commit=commit)

    # Categorise diffs before showing the recap.
    to_install = [d for d in diffs if d.status == "missing"]
    modified = [d for d in diffs if d.status == "modified"]
    to_overwrite = modified if force else []
    to_preserve = [] if force else modified
    to_prune = [d for d in diffs if d.status == "extra" and not _is_protected_path(d.path)]

    # Confirmation prompt — only if there is something destructive to do.
    destructive = bool(to_overwrite) or bool(to_prune)
    if destructive and not yes:
        _print_recap(to_install, to_overwrite, to_preserve, to_prune, target, console)
        if not click.confirm("Proceed?", default=False):
            console.print("[yellow]Aborted. No changes applied.[/yellow]")
            return 0

    # Back up modified files before overwriting
    backup_dir = _backup_modified_files(target, diffs, source_files)
    if backup_dir:
        rel_backup = os.path.relpath(backup_dir, target)
        console.print(f"  [dim]Backup saved to {rel_backup}/[/dim]")

    updated: list[str] = []
    skipped: list[str] = []
    pruned: list[str] = []

    for d in diffs:
        if d.status == "identical":
            continue
        if d.status == "extra":
            if _is_protected_path(d.path):
                continue
            abs_path = os.path.join(target, d.path)
            try:
                # Make writable in case it was set 0o444 by a prior install
                if os.path.isfile(abs_path):
                    os.chmod(abs_path, 0o644)
                os.remove(abs_path)
                pruned.append(d.path)
            except OSError as exc:
                console.print(
                    f"  [yellow]⚠[/yellow] Could not remove {d.path}: {exc}"
                )
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

    # Clean up parent directories left empty by the prune step.
    if pruned:
        _remove_empty_dirs(target, pruned)

    # Re-render CLAUDE.md from .j2 template after any file update, where it
    # belongs (#67): the root file only when stx owns it, otherwise
    # .claude/CLAUDE.md — a user-authored root CLAUDE.md is never rewritten.
    j2_path = os.path.join(target, ".claude", "CLAUDE.md.j2")
    if os.path.isfile(j2_path):
        from ._claude_files import write_profile_claude_md

        project_name = os.path.basename(os.path.abspath(target))
        rendered = _render_claude_md(j2_path, project_name, profile)
        root_md = os.path.join(target, "CLAUDE.md")
        if force and os.path.isfile(root_md):
            # --force: take the root file back explicitly, with a backup
            # when it was the user's
            from ._claude_files import root_claude_md_is_owned

            with open(root_md, encoding="utf-8") as f:
                current = f.read()
            if not root_claude_md_is_owned(target, candidates=(previous_render, rendered)):
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                bdir = os.path.join(target, ".claude", ".backup", stamp)
                os.makedirs(bdir, exist_ok=True)
                shutil.copy2(root_md, os.path.join(bdir, "CLAUDE.md"))
                console.print(f"  [dim]Backup of your CLAUDE.md saved to "
                              f"{os.path.relpath(bdir, target)}/CLAUDE.md[/dim]")
            previous_render = current
            generated = os.path.join(target, ".claude", "CLAUDE.md")
            if os.path.isfile(generated):
                os.remove(generated)
        dest_rel, changed = write_profile_claude_md(
            target, rendered, candidates=(previous_render,),
        )
        if changed:
            updated.append(dest_rel)
            console.print(
                f"  [green]\u2713[/green] {dest_rel} [dim](rendered from .claude/CLAUDE.md.j2)[/dim]"
            )
            if dest_rel != "CLAUDE.md":
                console.print(
                    "  [dim]Your root CLAUDE.md is your own: it was left untouched; "
                    "Claude Code reads both files.[/dim]"
                )

    if updated:
        console.print(f"\n[green]Updated {len(updated)} file(s).[/green]")
        for f in updated:
            if f not in ("CLAUDE.md", os.path.join(".claude", "CLAUDE.md")):  # printed above
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

    if pruned:
        console.print(
            f"\n[cyan]Pruned {len(pruned)} orphan file(s).[/cyan]\n"
            "  These files were installed by a prior profile version but are "
            "no longer declared in any manifest."
        )
        for f in pruned:
            console.print(f"  [cyan]\u2212[/cyan] {f}")

    return len(updated) + len(pruned)


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
    help="Overwrite locally-modified files (with auto-backup to .claude/.backup/).",
)
@click.option(
    "--all", "update_all", is_flag=True,
    help="Update all projects in the workspace.",
)
@click.option(
    "-y", "--yes", is_flag=True,
    help="Skip the confirmation prompt before applying destructive changes.",
)
@click.option(
    "--commit", is_flag=True,
    help="Untrack managed .claude/ files from git and commit that change "
         "(by default stx prints the git commands and never commits).",
)
def update_cmd(path: str, force: bool, update_all: bool, yes: bool, commit: bool) -> None:
    """Update an installed Claude profile from the source repo.

    Aligns the installed .claude/ tree with the current streamtex-claude
    source: missing files are installed, orphans (no longer declared by
    any manifest) are removed, and locally-modified files are preserved
    unless --force is passed (which overwrites them with an auto-backup).

    Before any destructive operation (overwrite or removal), a recap is
    shown and confirmation is required, unless --yes is passed.

    Protected paths (NEVER touched): .claude/custom/, .claude/.backup/,
    .claude/.stx-profile.
    """
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
                claude_repo, profile, target_path, force, console, yes=yes,
                commit=True if commit else None,
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
    _update_single_target(claude_repo, profile, target, force, console, yes=yes,
                          commit=True if commit else None)


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

    from .claude_project import desired_files, is_project_mode, plan_sync, read_declaration, read_lock

    has_problems = False
    for target_path, profile in targets:
        rel = os.path.relpath(target_path, ws_root)
        if is_project_mode(target_path):
            plan = plan_sync(target_path, desired_files(claude_repo, read_declaration(target_path)),
                             read_lock(target_path))
            diffs = [FileDiff(p, "missing") for p in plan.install] + [
                FileDiff(p, "modified") for p in plan.update + plan.merge + plan.keep_modified]
        else:
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

    from .claude_global import print_commands_report

    print_commands_report(ws_root, targets, claude_repo, console)

    if has_problems:
        console.print(
            "\n[yellow]Run 'stx claude update --all' to synchronize "
            "(project mode: 'stx claude sync').[/yellow]"
        )
        raise SystemExit(1)
    else:
        console.print(
            f"\n[bold green]All {len(targets)} project(s) are up to date.[/bold green]"
        )
