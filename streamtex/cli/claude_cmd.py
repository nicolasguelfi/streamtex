"""Claude AI profile commands: install and list."""

import os
import shutil

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
