"""stx sync — project-level deterministic dependency sync.

Wraps ``uv sync --locked`` for any directory containing a pyproject.toml.
Use this when you are not at a workspace root (where ``stx update`` is
the right command for the whole workspace), but inside a single project
— e.g. a pack subdirectory, a standalone document folder, or any
``pyproject.toml``-bearing dir outside the workspace orchestration.

Default uses ``--locked`` for idempotent, deterministic syncs. Pass
``--upgrade-deps`` to allow ``uv`` to refresh the lock from pyproject.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import click

from .console import get_console
from .workspace_cmd import _find_uv, _has_missing_local_sources, _restore_uv_lock_if_only_dirty


def _find_pyproject_dir(start: Path) -> Path | None:
    """Walk up from `start` until a directory containing pyproject.toml is found."""
    current = start.resolve()
    while True:
        if (current / "pyproject.toml").is_file():
            return current
        if current.parent == current:
            return None
        current = current.parent


@click.command("sync")
@click.option(
    "--upgrade-deps",
    is_flag=True,
    help="Allow uv to refresh uv.lock from pyproject.toml. Default is "
    "--locked (deterministic sync to the committed lock state).",
)
@click.argument("path", required=False, type=click.Path(exists=True, file_okay=False))
def sync(upgrade_deps: bool, path: str | None) -> None:
    """Sync the current project's venv from uv.lock (deterministic by default).

    With no arguments, syncs the project containing the current directory.
    Pass PATH to sync a specific project directory.
    """
    console = get_console()
    start = Path(path) if path else Path.cwd()
    project_dir = _find_pyproject_dir(start)
    if project_dir is None:
        raise click.ClickException(
            f"No pyproject.toml found in {start} or any parent directory."
        )

    uv = _find_uv()
    no_sources = _has_missing_local_sources(str(project_dir))

    cmd = [uv, "sync"]
    if no_sources:
        cmd.append("--no-sources")
        console.print(f"[cyan]{project_dir.name}[/cyan]: uv sync --no-sources (editable source not found) …")
    elif upgrade_deps:
        console.print(f"[cyan]{project_dir.name}[/cyan]: uv sync (upgrade-deps) …")
    else:
        cmd.append("--locked")
        console.print(f"[cyan]{project_dir.name}[/cyan]: uv sync --locked …")

    result = subprocess.run(
        cmd,
        cwd=str(project_dir),
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode == 0:
        console.print(f"[green]{project_dir.name}[/green]: ok")
        if no_sources:
            _restore_uv_lock_if_only_dirty(str(project_dir))
        return

    stderr_text = (result.stderr or "").strip()
    if "--locked" in cmd and ("lock" in stderr_text.lower() or "out of date" in stderr_text.lower()):
        console.print(f"[yellow]{project_dir.name}[/yellow]: lock out of date")
        console.print(
            "[dim]Run `stx sync --upgrade-deps` to refresh the lock from pyproject.toml, "
            "or fix the divergence manually.[/dim]"
        )
        if stderr_text:
            console.print(f"[dim]{stderr_text}[/dim]")
        raise click.ClickException("uv sync --locked failed")

    console.print(f"[red]{project_dir.name}[/red]: uv sync failed")
    if stderr_text:
        console.print(f"  {stderr_text}")
    raise click.ClickException("uv sync failed")
