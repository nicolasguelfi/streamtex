"""stx validate — aggregate validation across all reuse-architecture artifacts."""

from __future__ import annotations

import importlib
from pathlib import Path

import click

from .console import get_console


def _find_project_dir() -> Path:
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    raise click.ClickException("No pyproject.toml in current directory.")


@click.command("validate")
def validate() -> None:
    """Run pack + component + design system + kit validation on the current project."""
    from streamtex.core import discovery, validation

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)

    any_error = False

    # 1) Packs
    console.print("[bold]Packs[/bold]")
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            console.print(f"  [yellow]{pack_obj.name}: not installed[/yellow]")
            continue
        mod = importlib.import_module(pack_obj.entry_point_module)
        pack_root = Path(mod.__file__).resolve().parent  # type: ignore[arg-type]
        issues = validation.validate_pack(pack_root)
        errors = [i for i in issues if i.is_error()]
        if errors:
            any_error = True
            console.print(f"  [red]{pack_obj.name}: FAIL[/red]")
            for issue in errors:
                console.print(f"    [{issue.code}] {issue.message}")
        else:
            console.print(f"  [green]{pack_obj.name}: OK[/green]")

    # 2) Components
    console.print("[bold]Components[/bold]")
    artifacts = discovery.discover_components(packs)
    for art in artifacts:
        if art.module is None:
            continue
        issues = validation.validate_component(art.module)
        errors = [i for i in issues if i.is_error()]
        if errors:
            any_error = True
            console.print(f"  [red]{art.pack_name}:{art.name}: FAIL[/red]")
            for issue in errors:
                console.print(f"    [{issue.code}] {issue.message}")

    if any_error:
        raise click.ClickException("`stx validate` found issues.")
    console.print("[green]All artifacts validate cleanly.[/green]")
