"""Shared helpers to mutate pyproject.toml's [tool.uv.sources] non-destructively.

The pre-existing regex-based logic in `dev_cmd._add_uv_source` rewrites the
whole section and assumes a single key. The new pack architecture supports
multiple editable packs side by side; this module replaces that approach
with a tomlkit-based round-trip that preserves comments and other keys.

See PLAN.md §29.4 step 0 and decision D17.
"""

from __future__ import annotations

from pathlib import Path

import tomlkit
from tomlkit import inline_table


def _load_pyproject(project_dir: Path) -> tomlkit.TOMLDocument:
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.is_file():
        raise FileNotFoundError(f"No pyproject.toml in {project_dir}")
    return tomlkit.parse(pyproject.read_text(encoding="utf-8"))


def _save_pyproject(project_dir: Path, doc: tomlkit.TOMLDocument) -> None:
    (project_dir / "pyproject.toml").write_text(tomlkit.dumps(doc), encoding="utf-8")


def _ensure_section(doc: tomlkit.TOMLDocument, path: tuple[str, ...]) -> tomlkit.items.Table:
    current: tomlkit.items.Table | tomlkit.TOMLDocument = doc
    for key in path:
        if key not in current:
            current[key] = tomlkit.table()
        current = current[key]  # type: ignore[assignment]
    return current  # type: ignore[return-value]


def set_uv_source(project_dir: Path, name: str, path: str, *, editable: bool = True) -> None:
    """Add or update a `[tool.uv.sources].<name>` entry without touching others.

    `editable=True` produces ``{ path = "<path>", editable = true }`` ; with
    ``editable=False`` only the path is set, which lets users pin a wheel-only
    dependency.
    """
    doc = _load_pyproject(project_dir)
    section = _ensure_section(doc, ("tool", "uv", "sources"))
    entry = inline_table()
    entry["path"] = path
    if editable:
        entry["editable"] = True
    section[name] = entry
    _save_pyproject(project_dir, doc)


def remove_uv_source(project_dir: Path, name: str) -> bool:
    """Remove `[tool.uv.sources].<name>`. Returns True if the entry existed.

    If the section becomes empty after removal, the section header is dropped
    too (parent [tool.uv] is preserved).
    """
    doc = _load_pyproject(project_dir)
    tool = doc.get("tool")
    if tool is None:
        return False
    uv = tool.get("uv")
    if uv is None:
        return False
    sources = uv.get("sources")
    if sources is None or name not in sources:
        return False
    del sources[name]
    if len(sources) == 0:
        del uv["sources"]
    _save_pyproject(project_dir, doc)
    return True


def get_uv_sources(project_dir: Path) -> dict[str, dict]:
    """Return the current `[tool.uv.sources]` as a plain dict (read-only view)."""
    try:
        doc = _load_pyproject(project_dir)
    except FileNotFoundError:
        return {}
    tool = doc.get("tool")
    if tool is None:
        return {}
    uv = tool.get("uv")
    if uv is None:
        return {}
    sources = uv.get("sources")
    if sources is None:
        return {}
    return {k: dict(v) for k, v in sources.items()}


__all__ = ["set_uv_source", "remove_uv_source", "get_uv_sources"]
