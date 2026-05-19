"""stx ds — list / show / switch / new / validate design systems."""

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


def _resolve_local_pack_dir(project_dir: Path, pack_name: str | None) -> tuple[str, Path]:
    """Return (pack_name, filesystem_path) for a writable local pack.

    Refuses non-local packs (git remote / pypi) and packs not declared in stx.toml.
    Falls back to the primary local pack when ``pack_name`` is None.
    """
    from streamtex.core import discovery

    stx_toml = project_dir / "stx.toml"
    if pack_name is None:
        primary = discovery.get_primary_local_pack(stx_toml if stx_toml.is_file() else None)
        if primary is None:
            raise click.ClickException(
                "No primary local pack declared in stx.toml. "
                "Run `stx pack new <name>` then `stx pack set-primary <name>`."
            )
        target_name = primary["name"]
        target_path = Path(primary["path"])
    else:
        entries = _stx_toml.list_packs(project_dir)
        match = next((e for e in entries if e.get("name") == pack_name), None)
        if match is None:
            raise click.ClickException(
                f"Pack '{pack_name}' is not declared in stx.toml. "
                f"Run `stx pack new {pack_name}` or `stx pack add ...` first."
            )
        if match.get("type") != "local":
            raise click.ClickException(
                f"Pack '{pack_name}' is type='{match.get('type')}'; scaffolding only "
                "supported in local packs. Clone the remote pack locally first."
            )
        target_name = pack_name
        target_path = Path(match.get("path") or pack_name)
    if not target_path.is_absolute():
        target_path = (project_dir / target_path).resolve()
    return target_name, target_path


@click.group()
def ds():
    """Manage design systems available across installed packs."""


@ds.command("list")
def list_cmd() -> None:
    """List every design_systems/<name>/ across installed packs."""
    from streamtex.core import discovery

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    found_any = False
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            continue
        try:
            mod = importlib.import_module(pack_obj.entry_point_module)
        except Exception:
            continue
        ds_dir = Path(mod.__file__).resolve().parent / "design_systems"  # type: ignore[arg-type]
        if not ds_dir.is_dir():
            continue
        for sub in sorted(ds_dir.iterdir()):
            if sub.is_dir() and (sub / "__init__.py").is_file():
                found_any = True
                console.print(f"  • {pack_obj.name}:{sub.name}")
    if not found_any:
        console.print("No design systems found.")


@ds.command("show")
@click.argument("ref")
def show_cmd(ref: str) -> None:
    """Show a design system's metadata. REF = <pack>:<name>."""
    console = get_console()
    if ":" not in ref:
        raise click.ClickException("Use <pack>:<name> form, e.g. streamtex_design:default")
    pack_name, ds_name = ref.split(":", 1)

    from streamtex.core import discovery

    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    pack_obj = next((p for p in packs if p.name == pack_name), None)
    if pack_obj is None or pack_obj.entry_point_module is None:
        raise click.ClickException(f"Pack '{pack_name}' not installed.")
    mod_name = f"{pack_obj.entry_point_module}.design_systems.{ds_name}"
    try:
        mod = importlib.import_module(mod_name)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Cannot import {mod_name}: {exc}") from exc
    ds_class = getattr(mod, "DesignSystem", None)
    if ds_class is None:
        raise click.ClickException(f"{mod_name} does not export DesignSystem.")
    bundles = [a for a in dir(ds_class) if not a.startswith("_") and a != "name"]
    console.print(f"[bold]{ref}[/bold]")
    console.print(f"module:   {mod_name}")
    console.print(f"bundles:  {', '.join(sorted(bundles))}")


@ds.command("switch")
@click.argument("ref")
def switch_cmd(ref: str) -> None:
    """Switch the project's [design_system].use to REF."""
    console = get_console()
    project_dir = _find_project_dir()
    _stx_toml.set_design_system(project_dir, ref)
    console.print(f"[green]design_system.use = {ref}[/green]")


@ds.command("new")
@click.argument("name")
@click.option("--pack", "pack_name", default=None, help="Destination local pack (default: primary local).")
def new_cmd(name: str, pack_name: str | None) -> None:
    """Scaffold a new design system in the chosen (or primary local) pack."""
    console = get_console()
    project_dir = _find_project_dir()
    target_pack, target_path = _resolve_local_pack_dir(project_dir, pack_name)

    ds_root = target_path / "design_systems" / name
    if ds_root.exists():
        raise click.ClickException(f"{ds_root} already exists.")
    ds_root.mkdir(parents=True, exist_ok=False)

    init_file = ds_root / "__init__.py"
    init_file.write_text(_ds_skeleton(name), encoding="utf-8")
    console.print(f"[green]Design system scaffolded: {init_file}[/green]")
    console.print(
        f"Edit the bundles, then run `stx ds validate {target_pack}:{name}` to check Protocol conformance."
    )


def _ds_skeleton(name: str) -> str:
    return f'''"""{name} — design system (TODO short description).

Bundles exposed: TODO (e.g. colors, titles, callouts, body).
"""

from streamtex.styles import Style


class _Colors:
    primary = Style("color: #000000;", "primary")
    bg = Style("background-color: #ffffff;", "bg")
    text = Style("color: #000000;", "text")


class _Titles:
    section = Style("font-size: 28px; font-weight: 700;", "title_section")
    body = Style("font-size: 18px;", "title_body")


class _Body:
    paragraph = Style("font-size: 16px; line-height: 1.6;", "body_p")


class DesignSystem:
    """The {name} design system."""

    name = "{name}"
    colors = _Colors
    titles = _Titles
    body = _Body
'''


@ds.command("validate")
@click.argument("ref", required=False)
def validate_cmd(ref: str | None) -> None:
    """Validate one or every installed design system."""
    from streamtex.core import discovery, validation

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)

    refs: list[tuple[str, str]] = []
    if ref:
        if ":" not in ref:
            raise click.ClickException("Use <pack>:<name> form.")
        refs.append(tuple(ref.split(":", 1)))  # type: ignore[arg-type]
    else:
        for pack_obj in packs:
            if pack_obj.entry_point_module is None:
                continue
            mod = importlib.import_module(pack_obj.entry_point_module)
            ds_dir = Path(mod.__file__).resolve().parent / "design_systems"  # type: ignore[arg-type]
            if not ds_dir.is_dir():
                continue
            for sub in sorted(ds_dir.iterdir()):
                if sub.is_dir() and (sub / "__init__.py").is_file():
                    refs.append((pack_obj.name, sub.name))

    any_error = False
    for pack_name, ds_name in refs:
        pack_obj = next((p for p in packs if p.name == pack_name), None)
        if pack_obj is None or pack_obj.entry_point_module is None:
            continue
        mod_name = f"{pack_obj.entry_point_module}.design_systems.{ds_name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:  # noqa: BLE001
            any_error = True
            console.print(f"[red]{pack_name}:{ds_name} import error: {exc}[/red]")
            continue
        issues = validation.validate_design_system(mod)
        errors = [i for i in issues if i.is_error()]
        if errors:
            any_error = True
            console.print(f"[red]{pack_name}:{ds_name} FAIL[/red]")
            for issue in errors:
                console.print(f"  [{issue.code}] {issue.message}")
        else:
            console.print(f"[green]{pack_name}:{ds_name} OK[/green]")
    if any_error:
        raise click.ClickException("Some design systems failed validation.")
