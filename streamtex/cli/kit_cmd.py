"""stx kit — list / show / install / new / validate kits."""

from __future__ import annotations

import importlib
from pathlib import Path

import click

from . import _stx_toml
from .console import get_console


def _find_project_dir() -> Path:
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    raise click.ClickException("No pyproject.toml in current directory.")


def _iter_kits() -> list[tuple[str, str, Path]]:
    """Return (pack_name, kit_name, kit_path) for every kit found."""
    from streamtex.core import discovery

    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    out: list[tuple[str, str, Path]] = []
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            continue
        try:
            mod = importlib.import_module(pack_obj.entry_point_module)
        except Exception:
            continue
        kits_dir = Path(mod.__file__).resolve().parent / "kits"  # type: ignore[arg-type]
        if not kits_dir.is_dir():
            continue
        for kit_file in sorted(kits_dir.glob("*.toml")):
            out.append((pack_obj.name, kit_file.stem, kit_file))
    return out


@click.group()
def kit():
    """Manage kits (a coherent bundle of DS + components + template)."""


@kit.command("list")
def list_cmd() -> None:
    """List every kit across installed packs."""
    console = get_console()
    kits = _iter_kits()
    if not kits:
        console.print("No kits found.")
        return
    for pack_name, kit_name, _ in kits:
        console.print(f"  • {pack_name}:{kit_name}")


@kit.command("show")
@click.argument("ref")
def show_cmd(ref: str) -> None:
    """Show a kit's manifest. REF = <pack>:<name>."""

    console = get_console()
    if ":" not in ref:
        raise click.ClickException("Use <pack>:<name> form.")
    pack_name, kit_name = ref.split(":", 1)
    for p, k, path in _iter_kits():
        if p == pack_name and k == kit_name:
            console.print(f"[bold]{ref}[/bold]  ({path})")
            console.print(path.read_text(encoding="utf-8"))
            return
    raise click.ClickException(f"Kit '{ref}' not found.")


@kit.command("validate")
@click.argument("ref", required=False)
def validate_cmd(ref: str | None) -> None:
    """Validate one or every kit TOML file."""
    from streamtex.core import validation

    console = get_console()
    kits = _iter_kits()
    if ref:
        if ":" not in ref:
            raise click.ClickException("Use <pack>:<name> form.")
        pack_name, kit_name = ref.split(":", 1)
        kits = [t for t in kits if t[0] == pack_name and t[1] == kit_name]
    any_error = False
    for pack_name, kit_name, path in kits:
        issues = validation.validate_kit(path)
        errors = [i for i in issues if i.is_error()]
        if errors:
            any_error = True
            console.print(f"[red]{pack_name}:{kit_name} FAIL[/red]")
            for issue in errors:
                console.print(f"  [{issue.code}] {issue.message}")
        else:
            console.print(f"[green]{pack_name}:{kit_name} OK[/green]")
    if any_error:
        raise click.ClickException("Some kits failed validation.")


@kit.command("install")
@click.argument("ref")
def install_cmd(ref: str) -> None:
    """Apply a kit to the current project: set design_system + record [kit].use."""
    console = get_console()
    project_dir = _find_project_dir()
    if ":" not in ref:
        raise click.ClickException("Use <pack>:<name> form.")
    pack_name, kit_name = ref.split(":", 1)

    matches = [t for t in _iter_kits() if t[0] == pack_name and t[1] == kit_name]
    if not matches:
        raise click.ClickException(f"Kit '{ref}' not found.")
    _pack, _kit, kit_path = matches[0]

    import tomllib
    with kit_path.open("rb") as fh:
        data = tomllib.load(fh)

    ds_ref = (data.get("design_system") or {}).get("ref")
    if ds_ref:
        # Prefix with pack if unqualified
        if ":" not in ds_ref:
            ds_ref = f"{pack_name}:{ds_ref}"
        _stx_toml.set_design_system(project_dir, ds_ref)

    doc = _stx_toml.load(project_dir)
    if "kit" not in doc:
        import tomlkit
        doc["kit"] = tomlkit.table()
    doc["kit"]["use"] = ref
    _stx_toml.save(project_dir, doc)

    console.print(f"[green]Kit '{ref}' installed (design_system: {ds_ref}).[/green]")
