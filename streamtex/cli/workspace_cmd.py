"""Workspace commands: init and status."""

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import click

from .console import get_console

# ---------------------------------------------------------------------------
# TOML helpers
# ---------------------------------------------------------------------------

def generate_stx_toml(name: str, created: str) -> str:
    """Generate the content of a stx.toml file."""
    return f"""\
[workspace]
name = "{name}"
created = "{created}"

[repos]
# library = {{ path = "streamtex", url = "https://github.com/nicolasguelfi/streamtex" }}
# docs = {{ path = "streamtex-docs", url = "https://github.com/nicolasguelfi/streamtex-docs" }}

[deploy]
# provider = "render"

[claude]
# profiles_repo = "streamtex-claude"
"""


def load_stx_toml(workspace_path: str) -> dict:
    """Load and parse a stx.toml file.

    Raises:
        click.ClickException: if the file does not exist or is invalid.
    """
    toml_path = os.path.join(workspace_path, "stx.toml")
    if not os.path.isfile(toml_path):
        raise click.ClickException(f"stx.toml not found in {workspace_path}")

    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(toml_path, "rb") as f:
        return tomllib.load(f)


def find_workspace_root(start_path: str | None = None) -> str | None:
    """Walk up from *start_path* looking for a directory containing stx.toml."""
    current = Path(start_path) if start_path else Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "stx.toml").is_file():
            return str(parent)
    return None


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def get_repo_status(repo_path: str) -> dict:
    """Return a dict with branch, clean, ahead, behind for a git repo."""
    result = {"path": repo_path, "branch": "?", "clean": True, "ahead": 0, "behind": 0}

    if not os.path.isdir(os.path.join(repo_path, ".git")):
        result["branch"] = "(not a git repo)"
        return result

    try:
        branch = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        result["branch"] = branch.stdout.strip() or "?"

        status = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
        result["clean"] = len(status.stdout.strip()) == 0

        ahead_behind = subprocess.run(
            ["git", "-C", repo_path, "rev-list", "--left-right", "--count", "HEAD...@{u}"],
            capture_output=True, text=True, timeout=5,
        )
        if ahead_behind.returncode == 0:
            parts = ahead_behind.stdout.strip().split()
            if len(parts) == 2:
                result["ahead"] = int(parts[0])
                result["behind"] = int(parts[1])
    except (subprocess.TimeoutExpired, OSError):
        pass

    return result


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------

@click.command()
@click.argument("path", default=".")
@click.option("--name", default=None, help="Workspace name (defaults to directory name).")
def init(path, name):
    """Initialize a StreamTeX workspace with stx.toml."""
    target = os.path.abspath(path)
    toml_path = os.path.join(target, "stx.toml")

    if os.path.isfile(toml_path):
        raise click.ClickException(f"stx.toml already exists in {target}")

    os.makedirs(target, exist_ok=True)

    ws_name = name or os.path.basename(target)
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    content = generate_stx_toml(ws_name, created)
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Create projects/ subdirectory
    projects_dir = os.path.join(target, "projects")
    os.makedirs(projects_dir, exist_ok=True)

    console = get_console()
    console.print(f"[green]Workspace initialized:[/green] {target}")
    console.print(f"  stx.toml created (name={ws_name!r})")
    console.print("  projects/ directory created")


@click.command()
def status():
    """Show git status of all repos in the workspace."""
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )

    config = load_stx_toml(ws_root)
    repos = config.get("repos", {})

    if not repos:
        console = get_console()
        console.print("[yellow]No repos configured in stx.toml[/yellow]")
        return

    from rich.table import Table

    table = Table(title=f"Workspace: {config.get('workspace', {}).get('name', '?')}")
    table.add_column("Repo", style="cyan")
    table.add_column("Branch", style="green")
    table.add_column("Status")
    table.add_column("Ahead/Behind")

    for repo_name, repo_conf in repos.items():
        repo_path = os.path.join(ws_root, repo_conf.get("path", repo_name))
        if not os.path.isdir(repo_path):
            table.add_row(repo_name, "-", "[red]not cloned[/red]", "-")
            continue
        info = get_repo_status(repo_path)
        status_text = "[green]clean[/green]" if info["clean"] else "[red]dirty[/red]"
        ab = f"+{info['ahead']}/-{info['behind']}" if info["ahead"] or info["behind"] else "-"
        table.add_row(repo_name, info["branch"], status_text, ab)

    console = get_console()
    console.print(table)
