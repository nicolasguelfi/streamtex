"""Shared CLI helpers used by several command modules.

Private module (underscore-prefixed) — not part of the public API.
Consumers: pack_cmd, component_cmd, ds_cmd, kit_cmd, dev_cmd, validate_cmd.

Function names keep their leading underscore so call sites in the
consumer modules can stay unchanged after the refactor.
"""

from pathlib import Path

import click


def _find_project_dir() -> Path:
    """Return the cwd if it contains pyproject.toml, else raise ClickException.

    Used by every `stx` subcommand that operates on a StreamTeX project
    (pack / component / ds / kit / dev / validate).
    """
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    raise click.ClickException(
        "No pyproject.toml in current directory. Run from a StreamTeX project root."
    )


def _resolve_local_pack_dir(
    project_dir: Path, pack_name: str | None
) -> tuple[str, Path]:
    """Return (pack_name, filesystem_path) for a writable local pack.

    Refuses non-local packs (git remote / pypi) and packs not declared in
    stx.toml. Falls back to the primary local pack when ``pack_name`` is None.
    """
    from streamtex.core import discovery

    from . import _stx_toml

    stx_toml = project_dir / "stx.toml"
    if pack_name is None:
        primary = discovery.get_primary_local_pack(
            stx_toml if stx_toml.is_file() else None
        )
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
