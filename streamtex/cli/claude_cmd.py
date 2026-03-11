"""Claude AI profile commands: install, list, update, and diff."""

import filecmp
import os
import shutil
from dataclasses import dataclass

import click

from .console import get_console
from .workspace_cmd import find_workspace_root, load_stx_toml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_claude_repo(ws_root: str, config: dict) -> str:
    """Locate the streamtex-claude repo in the workspace.

    Raises:
        click.ClickException: if the repo cannot be found.
    """
    repos = config.get("repos", {})

    # 1. Check [claude].source
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
        "Run: stx install --preset user"
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

    # 3. Write .claude/.stx-profile marker
    marker_path = os.path.join(claude_dir, ".stx-profile")
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(profile + "\n")
    installed.append(os.path.relpath(marker_path, target))

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

    # Check for extra files in .claude/ not in source (excluding .stx-profile)
    claude_dir = os.path.join(target, ".claude")
    if os.path.isdir(claude_dir):
        for root, _dirs, filenames in os.walk(claude_dir):
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

    updated: list[str] = []
    skipped: list[str] = []

    for d in diffs:
        if d.status == "identical":
            continue
        if d.status == "extra":
            continue

        # Preserve CLAUDE.md unless --force
        if d.path == "CLAUDE.md" and d.status == "modified" and not force:
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
        # Re-protect shared references and commands
        if d.path.startswith(os.path.join(".claude", "references")) or \
           d.path.startswith(os.path.join(".claude", "commands")):
            os.chmod(dst_path, 0o444)
        updated.append(d.path)

    if updated:
        console.print(f"\n[green]Updated {len(updated)} file(s):[/green]")
        for f in updated:
            console.print(f"  [green]\u2713[/green] {f}")
    else:
        console.print("\n[bold green]Profile is already up to date.[/bold green]")

    if skipped:
        console.print(f"\n[yellow]Skipped {len(skipped)} file(s) (use --force to overwrite):[/yellow]")
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
