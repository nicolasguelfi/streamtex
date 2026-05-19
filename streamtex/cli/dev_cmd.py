"""stx dev — manage development links to local source repos."""

from __future__ import annotations

import subprocess
from pathlib import Path

import click

from .console import get_console
from .dev_config import (
    REPOS,
    GlobalDevConfig,
    ProjectDevConfig,
    is_editable_install,
    validate_repo_name,
    validate_repo_path,
)


def _find_project_dir() -> Path:
    """Return the project directory (cwd must contain pyproject.toml)."""
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    raise click.ClickException(
        "No pyproject.toml in current directory. "
        "Run this command from a StreamTeX project root."
    )


def _ensure_gitignore(project_dir: Path) -> None:
    """Add .stx-dev.json to .gitignore if not already present."""
    gi = project_dir / ".gitignore"
    marker = ".stx-dev.json"
    if gi.is_file():
        text = gi.read_text(encoding="utf-8")
        if marker in text:
            return
        with open(gi, "a", encoding="utf-8") as f:
            if not text.endswith("\n"):
                f.write("\n")
            f.write(f"{marker}\n")
    else:
        gi.write_text(f"{marker}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# pyproject.toml manipulation (for streamtex editable install)
# ---------------------------------------------------------------------------

def _add_uv_source(project_dir: Path, path: str) -> None:
    """Add or update the `[tool.uv.sources].streamtex` editable entry.

    Delegates to the tomlkit-based helper (decision D17) so that other
    entries in `[tool.uv.sources]` (e.g. `mypack`, `streamtex-design`) and
    surrounding comments are preserved.
    """
    from ._toml_helpers import set_uv_source

    set_uv_source(project_dir, "streamtex", path, editable=True)


def _remove_uv_source(project_dir: Path) -> None:
    """Remove the `[tool.uv.sources].streamtex` entry only.

    Other entries in the section (e.g. local packs declared as editable
    sources) are preserved per decision D17.
    """
    from ._toml_helpers import remove_uv_source

    remove_uv_source(project_dir, "streamtex")


def _uv_sync(project_dir: Path, console) -> None:
    """Run uv sync --reinstall-package streamtex with friendly output."""
    # Check if already editable-installed at the right path
    existing = is_editable_install(project_dir)

    result = subprocess.run(
        ["uv", "sync", "--reinstall-package", "streamtex"],
        cwd=str(project_dir),
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        console.print("  [green]✓[/green] editable install updated")
    elif existing:
        # sync failed but editable link already exists — not a real problem
        console.print("  [green]✓[/green] editable install already active")
    else:
        # Real failure — show why
        stderr = result.stderr.strip().splitlines()
        reason = stderr[-1] if stderr else "unknown error"
        console.print(f"  [red]✗[/red] uv sync failed: {reason}")


# ═══════════════════════════════════════════════════════════════════════════
# CLI commands
# ═══════════════════════════════════════════════════════════════════════════


@click.command(name="register")
@click.argument("repo")
@click.argument("path")
def register_cmd(repo: str, path: str) -> None:
    """Register a local source repo path on this machine.

    REPO is one of: streamtex, streamtex-claude, streamtex-docs.
    PATH is the absolute path to the repo root.
    """
    console = get_console()
    try:
        validate_repo_name(repo)
        resolved = validate_repo_path(repo, path)
    except ValueError as e:
        raise click.ClickException(str(e))

    cfg = GlobalDevConfig.load()
    cfg.repos[repo] = str(resolved)
    cfg.save()
    console.print(f"[green]Registered[/green] {repo} → {resolved}")


@click.command(name="unregister")
@click.argument("repo")
def unregister_cmd(repo: str) -> None:
    """Remove a registered repo path.

    REPO is one of: streamtex, streamtex-claude, streamtex-docs.
    """
    console = get_console()
    try:
        validate_repo_name(repo)
    except ValueError as e:
        raise click.ClickException(str(e))

    cfg = GlobalDevConfig.load()
    if repo not in cfg.repos:
        raise click.ClickException(f"{repo} is not registered.")
    del cfg.repos[repo]
    cfg.save()
    console.print(f"[yellow]Unregistered[/yellow] {repo}")


@click.command(name="link")
@click.argument("repos", nargs=-1, required=True)
def link_cmd(repos: tuple[str, ...]) -> None:
    """Link the current project to registered dev repos.

    REPOS: one or more of streamtex, streamtex-claude, streamtex-docs, or 'all'.
    """
    console = get_console()
    project_dir = _find_project_dir()
    gcfg = GlobalDevConfig.load()
    pcfg = ProjectDevConfig.load(project_dir)

    targets = list(REPOS) if "all" in repos else list(repos)

    for repo in targets:
        try:
            validate_repo_name(repo)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            continue

        if repo not in gcfg.repos:
            console.print(
                f"[red]Error:[/red] {repo} is not registered. "
                f"Run: stx dev register {repo} /path/to/{repo}"
            )
            continue

        path = gcfg.repos[repo]
        try:
            validate_repo_path(repo, path)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            continue

        if repo == "streamtex":
            _add_uv_source(project_dir, path)
            console.print(f"[cyan]Linking[/cyan] {repo} → {path}")
            _uv_sync(project_dir, console)
        else:
            pcfg.linked[repo] = path
            console.print(f"[green]Linked[/green] {repo} → {path}")

    pcfg.save(project_dir)
    _ensure_gitignore(project_dir)


@click.command(name="unlink")
@click.argument("repos", nargs=-1, required=True)
def unlink_cmd(repos: tuple[str, ...]) -> None:
    """Unlink dev repos from the current project (revert to PyPI/standard).

    REPOS: one or more of streamtex, streamtex-claude, streamtex-docs, or 'all'.
    """
    console = get_console()
    project_dir = _find_project_dir()
    pcfg = ProjectDevConfig.load(project_dir)

    targets = list(REPOS) if "all" in repos else list(repos)

    for repo in targets:
        try:
            validate_repo_name(repo)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            continue

        if repo == "streamtex":
            _remove_uv_source(project_dir)
            console.print(f"[cyan]Unlinking[/cyan] {repo}")
            result = subprocess.run(
                ["uv", "sync", "--reinstall-package", "streamtex"],
                cwd=str(project_dir),
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                console.print("  [green]✓[/green] reverted to PyPI version")
            else:
                stderr = result.stderr.strip().splitlines()
                reason = stderr[-1] if stderr else "unknown error"
                console.print(f"  [red]✗[/red] uv sync failed: {reason}")
        else:
            if repo in pcfg.linked:
                del pcfg.linked[repo]
            console.print(f"[yellow]Unlinked[/yellow] {repo}")

    pcfg.save(project_dir)


@click.command(name="status")
def status_cmd() -> None:
    """Show dev link status for the current project and global registration."""
    console = get_console()
    gcfg = GlobalDevConfig.load()

    # --- Global registrations ---
    console.print("\n[bold]Global registrations[/bold]"
                  "  (~/.config/streamtex/dev.json)")
    if not gcfg.repos:
        console.print("  (none)")
    for repo in REPOS:
        path = gcfg.repos.get(repo)
        if path:
            exists = Path(path).is_dir()
            mark = "[green]✓[/green]" if exists else "[red]✗ missing[/red]"
            console.print(f"  {repo:20s} → {path}  {mark}")
        else:
            console.print(f"  {repo:20s}   (not registered)")

    # --- Project links ---
    try:
        project_dir = _find_project_dir()
    except click.ClickException:
        console.print("\n[dim]Not in a project directory.[/dim]")
        return

    console.print(f"\n[bold]Project links[/bold]  ({project_dir.name})")

    # streamtex — check editable install
    editable_path = is_editable_install(project_dir)
    if editable_path:
        console.print(
            f"  streamtex          → {editable_path}  "
            f"[green]✓ editable[/green]"
        )
    else:
        console.print("  streamtex            [dim](PyPI)[/dim]")

    # Other repos — check .stx-dev.json
    pcfg = ProjectDevConfig.load(project_dir)
    for repo in ("streamtex-claude", "streamtex-docs"):
        path = pcfg.linked.get(repo)
        if path:
            exists = Path(path).is_dir()
            mark = "[green]✓[/green]" if exists else "[red]✗ missing[/red]"
            console.print(f"  {repo:20s} → {path}  {mark}")
        else:
            console.print(f"  {repo:20s}   [dim](not linked)[/dim]")

    console.print()


def print_dev_status_section(project_dir: str | Path) -> None:
    """Print a compact dev-link section for inclusion in `stx status`.

    Called by status_cmd.py — does not print anything if no links are active.
    """
    console = get_console()
    project_dir = Path(project_dir)

    editable_path = is_editable_install(project_dir)
    pcfg = ProjectDevConfig.load(project_dir)
    has_links = editable_path or pcfg.linked

    if not has_links:
        return

    console.print("\n[bold cyan]Dev Links[/bold cyan]")
    if editable_path:
        console.print(f"  streamtex          → {editable_path}  [green](editable)[/green]")
    for repo in ("streamtex-claude", "streamtex-docs"):
        path = pcfg.linked.get(repo)
        if path:
            exists = Path(path).is_dir()
            mark = "[green]✓[/green]" if exists else "[red]✗[/red]"
            console.print(f"  {repo:20s} → {path}  {mark}")
