"""Workspace commands: init, clone, link, status, sync, upgrade."""

import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import click

from .console import get_console

# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------

PRESET_REPOS = {
    "basic": [],
    "user": ["claude"],
    "standard": ["docs", "claude"],
    "developer": ["library", "docs", "claude"],
}

PRESET_ORDER = ["basic", "user", "standard", "developer"]

ALL_REPOS = {
    "library": {
        "name": "streamtex",
        "url": "https://github.com/nicolasguelfi/streamtex.git",
        "path": "streamtex",
        "type": "library",
    },
    "docs": {
        "name": "streamtex-docs",
        "url": "https://github.com/nicolasguelfi/streamtex-docs.git",
        "path": "streamtex-docs",
        "type": "docs",
    },
    "claude": {
        "name": "streamtex-claude",
        "url": "https://github.com/nicolasguelfi/streamtex-claude.git",
        "path": "streamtex-claude",
        "type": "claude",
    },
}

# ---------------------------------------------------------------------------
# TOML helpers
# ---------------------------------------------------------------------------

def generate_stx_toml(name: str, created: str, preset: str = "standard") -> str:
    """Generate the content of a stx.toml file."""
    lines = [
        "[workspace]",
        f'name = "{name}"',
        f'created = "{created}"',
        f'preset = "{preset}"',
        "",
        "[repos]",
    ]

    for repo_key in PRESET_REPOS.get(preset, []):
        repo = ALL_REPOS[repo_key]
        lines.append("")
        lines.append(f"[repos.{repo['name']}]")
        lines.append(f'url = "{repo["url"]}"')
        lines.append(f'path = "{repo["path"]}"')
        lines.append(f'type = "{repo["type"]}"')

    lines.append("")
    lines.append("[deploy]")
    lines.append("# render_owner = \"nicolasguelfi\"")
    lines.append("# render_region = \"oregon\"")
    lines.append("")

    if "claude" in PRESET_REPOS.get(preset, []):
        lines.append("[claude]")
        lines.append('source = "streamtex-claude"')
    else:
        lines.append("[claude]")

    lines.append("")
    return "\n".join(lines)


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
@click.option(
    "--preset", default="standard",
    type=click.Choice(PRESET_ORDER),
    help="Installation preset (default: standard).",
)
def init(path, name, preset):
    """Initialize a StreamTeX workspace with stx.toml."""
    target = os.path.abspath(path)
    toml_path = os.path.join(target, "stx.toml")

    if os.path.isfile(toml_path):
        raise click.ClickException(f"stx.toml already exists in {target}")

    os.makedirs(target, exist_ok=True)

    ws_name = name or os.path.basename(target)
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    content = generate_stx_toml(ws_name, created, preset=preset)
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Create projects/ subdirectory
    projects_dir = os.path.join(target, "projects")
    os.makedirs(projects_dir, exist_ok=True)

    console = get_console()
    console.print(f"[green]Workspace initialized:[/green] {target}")
    console.print(f"  stx.toml created (name={ws_name!r}, preset={preset!r})")
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


def _has_missing_local_sources(repo_path: str) -> bool:
    """Return True if pyproject.toml has [tool.uv.sources] with local paths that don't exist."""
    pyproject = os.path.join(repo_path, "pyproject.toml")
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]
    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
    except (OSError, ValueError):
        return False
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    for _name, spec in sources.items():
        if isinstance(spec, dict) and "path" in spec:
            resolved = os.path.join(repo_path, spec["path"])
            if not os.path.exists(resolved):
                return True
    return False


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

        # If local editable sources are missing, fall back to PyPI
        cmd = [uv, "sync"]
        if _has_missing_local_sources(repo_path):
            cmd.append("--no-sources")
            console.print(f"  [cyan]{repo_name}[/cyan]: running uv sync --no-sources (editable source not found) …")
        else:
            console.print(f"  [cyan]{repo_name}[/cyan]: running uv sync …")
        result = subprocess.run(
            cmd,
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

    # --- Install shared commands globally (~/.claude/commands/) ---
    try:
        from .claude_cmd import find_claude_repo

        claude_repo = find_claude_repo(ws_root, config)
        shared_cmd_dir = os.path.join(claude_repo, "shared", "commands")
        if os.path.isdir(shared_cmd_dir):
            global_claude_cmd = os.path.join(Path.home(), ".claude", "commands")
            os.makedirs(global_claude_cmd, exist_ok=True)
            count = 0
            for fname in os.listdir(shared_cmd_dir):
                src = os.path.join(shared_cmd_dir, fname)
                if os.path.isfile(src):
                    dst = os.path.join(global_claude_cmd, fname)
                    # Remove read-only before overwrite
                    if os.path.exists(dst):
                        os.chmod(dst, 0o644)
                    shutil.copy2(src, dst)
                    os.chmod(dst, 0o444)
                    count += 1
            if count:
                console.print(
                    f"  [green]global[/green]: {count} shared command(s) → ~/.claude/commands/"
                )
    except click.ClickException:
        pass  # No claude repo configured/cloned yet — skip silently

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


# ---------------------------------------------------------------------------
# upgrade command
# ---------------------------------------------------------------------------

@click.command()
@click.argument("preset", type=click.Choice(PRESET_ORDER))
def upgrade(preset):
    """Upgrade workspace to a higher preset."""
    ws_root, config = _require_workspace()
    console = get_console()

    # Current preset — backwards compat: missing field → "developer"
    current = config.get("workspace", {}).get("preset", "developer")
    current_idx = PRESET_ORDER.index(current) if current in PRESET_ORDER else len(PRESET_ORDER) - 1
    new_idx = PRESET_ORDER.index(preset)

    if new_idx < current_idx:
        raise click.ClickException(
            f"Cannot downgrade from '{current}' to '{preset}'."
        )

    if new_idx == current_idx:
        console.print(f"[yellow]Already at preset '{current}'.[/yellow]")
        return

    # Repos to add
    current_repos = set(PRESET_REPOS.get(current, []))
    new_repos = set(PRESET_REPOS[preset])
    to_add = new_repos - current_repos

    # Rewrite stx.toml
    toml_path = os.path.join(ws_root, "stx.toml")
    with open(toml_path, encoding="utf-8") as f:
        text = f.read()

    # Update preset line
    if re.search(r'^preset\s*=', text, re.MULTILINE):
        text = re.sub(
            r'^(preset\s*=\s*).*$',
            f'preset = "{preset}"',
            text,
            flags=re.MULTILINE,
        )
    else:
        # Insert preset after created line in [workspace]
        text = re.sub(
            r'^(created\s*=\s*".+")$',
            f'\\1\npreset = "{preset}"',
            text,
            flags=re.MULTILINE,
        )

    # Add missing repo sections before [deploy]
    if to_add:
        new_sections = []
        for repo_key in PRESET_REPOS[preset]:
            if repo_key in to_add:
                repo = ALL_REPOS[repo_key]
                new_sections.append(f"\n[repos.{repo['name']}]")
                new_sections.append(f'url = "{repo["url"]}"')
                new_sections.append(f'path = "{repo["path"]}"')
                new_sections.append(f'type = "{repo["type"]}"')
        insert_block = "\n".join(new_sections) + "\n"
        text = text.replace("\n[deploy]", f"{insert_block}\n[deploy]")

    # Add claude.source if upgrading to a preset that includes claude
    if "claude" in to_add:
        if re.search(r'^\[claude\]\s*$', text, re.MULTILINE):
            text = re.sub(
                r'^\[claude\]\s*$',
                '[claude]\nsource = "streamtex-claude"',
                text,
                flags=re.MULTILINE,
            )

    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(text)

    console.print(f"[green]Upgraded from '{current}' to '{preset}'.[/green]")
    for repo_key in sorted(to_add):
        console.print(f"  + {ALL_REPOS[repo_key]['name']}")
    console.print("\nRun [bold]stx workspace clone[/bold] to clone the new repos.")


# ---------------------------------------------------------------------------
# hooks command
# ---------------------------------------------------------------------------

@click.command()
def hooks():
    """Install pre-commit hooks in all workspace repos and projects."""
    ws_root, config = _require_workspace()
    console = get_console()
    uv = _find_uv()

    console.print("[bold]Installing pre-commit hooks …[/bold]\n")

    installed = 0
    skipped = 0

    # Collect all directories to process: repos + projects/
    dirs_to_process: list[tuple[str, str]] = []

    # Repos from stx.toml (skip claude — not a Python project)
    for repo_name, repo_conf in config.get("repos", {}).items():
        repo_type = repo_conf.get("type", "")
        if repo_type == "claude":
            continue
        repo_path = os.path.join(ws_root, repo_conf.get("path", repo_name))
        dirs_to_process.append((repo_name, repo_path))

    # Projects in projects/ directory
    projects_dir = os.path.join(ws_root, "projects")
    if os.path.isdir(projects_dir):
        for entry in sorted(os.listdir(projects_dir)):
            proj_path = os.path.join(projects_dir, entry)
            if os.path.isdir(proj_path) and os.path.isfile(
                os.path.join(proj_path, "pyproject.toml")
            ):
                dirs_to_process.append((f"projects/{entry}", proj_path))

    for name, path in dirs_to_process:
        if not os.path.isdir(path):
            console.print(f"  [yellow]{name}[/yellow]: not found — skipped")
            skipped += 1
            continue

        if not os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
            console.print(f"  [yellow]{name}[/yellow]: no .pre-commit-config.yaml — skipped")
            skipped += 1
            continue

        result = subprocess.run(
            [uv, "run", "pre-commit", "install"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            console.print(f"  [green]{name}[/green]: ok")
            installed += 1
        else:
            console.print(f"  [red]{name}[/red]: failed")
            if result.stderr:
                console.print(f"    {result.stderr.strip()}")
            skipped += 1

    console.print(f"\n[bold]Done:[/bold] {installed} installed, {skipped} skipped")
