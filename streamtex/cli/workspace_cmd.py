"""Workspace commands: init, clone, link, status, sync."""

import os
import shutil
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

[repos.streamtex]
url = "https://github.com/nicolasguelfi/streamtex.git"
path = "streamtex"
type = "library"

[repos.streamtex-docs]
url = "https://github.com/nicolasguelfi/streamtex-docs.git"
path = "streamtex-docs"
type = "docs"

[repos.streamtex-claude]
url = "https://github.com/nicolasguelfi/streamtex-claude.git"
path = "streamtex-claude"
type = "claude"

# [repos.stx-ai4se]
# url = "https://github.com/nicolasguelfi/stx-ai4se.git"
# path = "projects/stx-ai4se"
# type = "project"

[deploy]
# render_owner = "nicolasguelfi"
# render_region = "oregon"

[claude]
source = "streamtex-claude"
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


# ---------------------------------------------------------------------------
# Helpers for clone / link / sync
# ---------------------------------------------------------------------------

def _require_workspace() -> tuple[str, dict]:
    """Find workspace root and load config, or raise ClickException."""
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )
    config = load_stx_toml(ws_root)
    return ws_root, config


def _find_uv() -> str:
    """Locate the uv binary."""
    uv = shutil.which("uv")
    if uv is None:
        raise click.ClickException("uv not found in PATH. Install it: https://docs.astral.sh/uv/")
    return uv


def _run_uv_sync(
    repos: dict,
    ws_root: str,
    type_filter: set[str] | None = None,
) -> None:
    """Run ``uv sync`` in selected repos.

    Parameters
    ----------
    repos:
        The ``[repos]`` mapping from stx.toml.
    ws_root:
        Absolute path to the workspace root.
    type_filter:
        If provided, only sync repos whose *type* is in this set.
    """
    uv = _find_uv()
    console = get_console()
    synced = 0
    skipped = 0

    for repo_name, repo_conf in repos.items():
        repo_type = repo_conf.get("type", "")
        if type_filter and repo_type not in type_filter:
            skipped += 1
            continue

        repo_path = os.path.join(ws_root, repo_conf.get("path", repo_name))
        if not os.path.isdir(repo_path):
            console.print(f"  [yellow]{repo_name}[/yellow]: not cloned — skipped")
            skipped += 1
            continue

        # Only sync if there is a pyproject.toml
        if not os.path.isfile(os.path.join(repo_path, "pyproject.toml")):
            console.print(f"  [yellow]{repo_name}[/yellow]: no pyproject.toml — skipped")
            skipped += 1
            continue

        console.print(f"  [cyan]{repo_name}[/cyan]: running uv sync …")
        result = subprocess.run(
            [uv, "sync"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            console.print(f"  [green]{repo_name}[/green]: ok")
            synced += 1
        else:
            console.print(f"  [red]{repo_name}[/red]: failed")
            if result.stderr:
                console.print(f"    {result.stderr.strip()}")
            skipped += 1

    console.print(f"\n[bold]Done:[/bold] {synced} synced, {skipped} skipped")


# ---------------------------------------------------------------------------
# clone / link / sync commands
# ---------------------------------------------------------------------------

@click.command()
def clone():
    """Clone all repos declared in stx.toml."""
    ws_root, config = _require_workspace()
    repos = config.get("repos", {})

    if not repos:
        console = get_console()
        console.print("[yellow]No repos configured in stx.toml[/yellow]")
        return

    console = get_console()
    cloned = 0
    skipped = 0

    for repo_name, repo_conf in repos.items():
        url = repo_conf.get("url", "")
        rel_path = repo_conf.get("path", repo_name)
        target_path = os.path.join(ws_root, rel_path)

        if not url:
            console.print(f"  [yellow]{repo_name}[/yellow]: no url — skipped")
            skipped += 1
            continue

        if os.path.isdir(target_path):
            console.print(f"  [yellow]{repo_name}[/yellow]: already exists — skipped")
            skipped += 1
            continue

        # Ensure parent directory exists (e.g. projects/)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        console.print(f"  [cyan]{repo_name}[/cyan]: cloning {url} …")
        result = subprocess.run(
            ["git", "clone", url, target_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            console.print(f"  [green]{repo_name}[/green]: cloned")
            cloned += 1
        else:
            console.print(f"  [red]{repo_name}[/red]: clone failed")
            if result.stderr:
                console.print(f"    {result.stderr.strip()}")
            skipped += 1

    console.print(f"\n[bold]Done:[/bold] {cloned} cloned, {skipped} skipped")


@click.command()
def link():
    """Configure editable installs (uv sync in docs/project repos)."""
    ws_root, config = _require_workspace()
    repos = config.get("repos", {})

    console = get_console()
    console.print("[bold]Linking docs & project repos …[/bold]\n")
    _run_uv_sync(repos, ws_root, type_filter={"docs", "project"})


@click.command()
def sync():
    """Run uv sync in all workspace repos."""
    ws_root, config = _require_workspace()
    repos = config.get("repos", {})

    console = get_console()
    console.print("[bold]Syncing all repos …[/bold]\n")
    _run_uv_sync(repos, ws_root)
