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
        "streamtex-claude repo not found in workspace. Run 'stx workspace clone' first."
    )


def list_profiles(claude_repo: str) -> list[dict]:
    """List available profiles from the streamtex-claude repo.

    Returns a list of dicts with keys: name, description, files.
    """
    profiles_dir = os.path.join(claude_repo, "profiles")
    if not os.path.isdir(profiles_dir):
        return []

    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

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
            info["description"] = manifest.get("description", "")

        # Count files recursively
        count = 0
        for _root, _dirs, files in os.walk(entry_path):
            count += len(files)
        info["files"] = count

        profiles.append(info)

    return profiles


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

    # 2. Copy shared/references/ if it exists
    shared_refs = os.path.join(claude_repo, "shared", "references")
    if os.path.isdir(shared_refs):
        dst_refs = os.path.join(claude_dir, "references")
        shutil.copytree(shared_refs, dst_refs, dirs_exist_ok=True)
        for root, _dirs, files in os.walk(dst_refs):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), target)
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


def collect_source_files(claude_repo: str, profile: str) -> dict[str, str]:
    """Map relative target paths to absolute source paths for a profile.

    Replicates the path logic from :func:`install_profile`:
    - ``CLAUDE.md`` → project root
    - ``manifest.toml`` → skipped
    - everything else → ``.claude/``
    - ``shared/references/`` → ``.claude/references/``

    Returns a dict of ``{relative_target_path: absolute_source_path}``.
    """
    profile_dir = os.path.join(claude_repo, "profiles", profile)
    if not os.path.isdir(profile_dir):
        return {}

    files: dict[str, str] = {}

    for entry in os.listdir(profile_dir):
        if entry == "manifest.toml":
            continue
        src = os.path.join(profile_dir, entry)

        if entry == "CLAUDE.md":
            files["CLAUDE.md"] = src
            continue

        if os.path.isdir(src):
            for root, _dirs, filenames in os.walk(src):
                for fname in filenames:
                    abs_src = os.path.join(root, fname)
                    rel = os.path.relpath(abs_src, profile_dir)
                    files[os.path.join(".claude", rel)] = abs_src
        else:
            files[os.path.join(".claude", entry)] = src

    # Shared references
    shared_refs = os.path.join(claude_repo, "shared", "references")
    if os.path.isdir(shared_refs):
        for root, _dirs, filenames in os.walk(shared_refs):
            for fname in filenames:
                abs_src = os.path.join(root, fname)
                rel = os.path.relpath(abs_src, shared_refs)
                files[os.path.join(".claude", "references", rel)] = abs_src

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
def update_cmd(path: str, force: bool) -> None:
    """Update an installed Claude profile from the source repo."""
    _ws_root, claude_repo, profile, target = _resolve_profile_context(path)

    console = get_console()
    console.print(f"[cyan]Profile:[/cyan] {profile}")

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
        shutil.copy2(src_path, dst_path)
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
