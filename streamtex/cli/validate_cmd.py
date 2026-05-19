"""stx validate — aggregate validation across all reuse-architecture artifacts.

Exit codes (PLAN §7.5):
* 0 — no issues
* 1 — warnings only (becomes 2 with --strict)
* 2 — errors found
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import click

from .console import get_console


def _find_project_dir() -> Path:
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    raise click.ClickException("No pyproject.toml in current directory.")


def _print_issues(console, label: str, issues) -> tuple[int, int]:
    """Print issues grouped by severity; return (error_count, warning_count)."""
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    if errors:
        console.print(f"  [red]{label}: FAIL[/red]")
        for issue in errors:
            console.print(f"    [red][{issue.code}][/red] {issue.message}")
    elif warnings:
        console.print(f"  [yellow]{label}: WARN[/yellow]")
    else:
        console.print(f"  [green]{label}: OK[/green]")
    for issue in warnings:
        console.print(f"    [yellow][{issue.code}][/yellow] {issue.message}")
    return len(errors), len(warnings)


@click.command("validate")
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Promote warnings to errors (exit 2 instead of 1 when only warnings).",
)
def validate(strict: bool) -> None:
    """Run pack + component + design system + kit validation on the current project."""
    from streamtex.core import discovery, validation

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)

    total_errors = 0
    total_warnings = 0

    # 1) Packs
    console.print("[bold]Packs[/bold]")
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            console.print(f"  [yellow]{pack_obj.name}: not installed[/yellow]")
            continue
        mod = importlib.import_module(pack_obj.entry_point_module)
        pack_root = Path(mod.__file__).resolve().parent  # type: ignore[arg-type]
        issues = validation.validate_pack(pack_root)
        e, w = _print_issues(console, pack_obj.name, issues)
        total_errors += e
        total_warnings += w

    # 2) Components
    console.print("[bold]Components[/bold]")
    artifacts = discovery.discover_components(packs)
    for art in artifacts:
        if art.module is None:
            continue
        issues = validation.validate_component(art.module)
        e, w = _print_issues(console, f"{art.pack_name}:{art.name}", issues)
        total_errors += e
        total_warnings += w

    # 3) Design systems
    console.print("[bold]Design systems[/bold]")
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            continue
        try:
            mod = importlib.import_module(pack_obj.entry_point_module)
        except Exception:  # noqa: BLE001
            continue
        ds_dir = Path(mod.__file__).resolve().parent / "design_systems"  # type: ignore[arg-type]
        if not ds_dir.is_dir():
            continue
        for sub in sorted(ds_dir.iterdir()):
            if not (sub.is_dir() and (sub / "__init__.py").is_file()):
                continue
            ds_mod_name = f"{pack_obj.entry_point_module}.design_systems.{sub.name}"
            try:
                ds_mod = importlib.import_module(ds_mod_name)
            except Exception as exc:  # noqa: BLE001
                total_errors += 1
                console.print(f"  [red]{pack_obj.name}:{sub.name}: import error: {exc}[/red]")
                continue
            issues = validation.validate_design_system(ds_mod)
            e, w = _print_issues(console, f"{pack_obj.name}:{sub.name}", issues)
            total_errors += e
            total_warnings += w

    # 4) Kits
    console.print("[bold]Kits[/bold]")
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            continue
        try:
            mod = importlib.import_module(pack_obj.entry_point_module)
        except Exception:  # noqa: BLE001
            continue
        kits_dir = Path(mod.__file__).resolve().parent / "kits"  # type: ignore[arg-type]
        if not kits_dir.is_dir():
            continue
        for kit_path in sorted(kits_dir.glob("*.toml")):
            issues = validation.validate_kit(kit_path)
            e, w = _print_issues(console, f"{pack_obj.name}:{kit_path.stem}", issues)
            total_errors += e
            total_warnings += w

    # Summary + exit code (PLAN §7.5: 0 = OK, 1 = warnings, 2 = errors)
    if total_errors:
        console.print(
            f"[red]`stx validate` found {total_errors} error(s) "
            f"and {total_warnings} warning(s).[/red]"
        )
        sys.exit(2)
    if total_warnings:
        if strict:
            console.print(
                f"[red]`stx validate --strict` failed: "
                f"{total_warnings} warning(s) promoted to errors.[/red]"
            )
            sys.exit(2)
        console.print(
            f"[yellow]`stx validate` completed with {total_warnings} warning(s).[/yellow]"
        )
        sys.exit(1)
    console.print("[green]All artifacts validate cleanly.[/green]")
