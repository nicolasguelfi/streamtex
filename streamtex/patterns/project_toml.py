"""Read/write the project's pattern selection from its TOML config.

The user's *intent* (which patterns to install) lives in the project's
``stx.toml`` (or ``pyproject.toml`` under ``[tool.patterns]``) so it is
versioned and re-applies on a fresh clone. ``.patterns-meta.json`` is the
execution cache; the TOML is the source of truth.

Canonical form::

    [patterns]
    source = "../../streamtex-patterns"

    [patterns.selection]
    mode = "individual"          # "preset" | "individual" | "all"
    items = ["ptn_callout", "ptn_stat_hero"]

Accepted shortcuts on read (more natural to write by hand)::

    [patterns]
    preset = "slides"            # → mode="preset", items=("slides",)
    selected = ["ptn_callout"]   # → mode="individual"
    all = true                   # → mode="all"

On write, the canonical sub-table form is always produced.
"""

from __future__ import annotations

import logging
from pathlib import Path

import tomlkit
from tomlkit import TOMLDocument

from .manifest import PatternSelection

logger = logging.getLogger(__name__)


def _config_files(project_dir: Path) -> tuple[Path, Path]:
    """Return ``(stx.toml, pyproject.toml)`` paths in *project_dir*."""
    project_dir = Path(project_dir)
    return project_dir / "stx.toml", project_dir / "pyproject.toml"


def _parse_patterns_section(section: dict) -> PatternSelection | None:
    """Build a :class:`PatternSelection` from a parsed ``[patterns]`` mapping.

    Accepts:
      * v3 canonical: ``[patterns.selection]`` with presets/individuals/excludes/all,
      * v2 legacy: ``[patterns.selection]`` with ``mode`` and ``items``,
      * three shortcuts (``preset``, ``selected``, ``all``) for hand-edited files.

    Returns ``None`` when no selection info is present (a section may exist
    for ``source`` alone).
    """
    sel = section.get("selection")
    if isinstance(sel, dict):
        try:
            return PatternSelection.from_dict(dict(sel))
        except Exception as exc:  # MetaError or coercion failure
            logger.warning("ignoring [patterns.selection]: %s", exc)
            return None

    if "preset" in section:
        return PatternSelection.from_legacy(
            mode="preset", items=(str(section["preset"]),),
        )
    if section.get("all") is True:
        return PatternSelection.from_legacy(mode="all", items=())
    if "selected" in section:
        raw = section["selected"]
        if isinstance(raw, list):
            return PatternSelection.from_legacy(
                mode="individual",
                items=tuple(str(x) for x in raw),
            )
        logger.warning("ignoring [patterns].selected: must be a list")
    return None


def read_project_selection(project_dir: Path) -> PatternSelection | None:
    """Return the user-declared selection from project config, or None.

    Lookup order: ``stx.toml [patterns]`` then ``pyproject.toml [tool.patterns]``.
    """
    stx_toml, pyproject = _config_files(project_dir)

    for path, key_path in (
        (stx_toml, ("patterns",)),
        (pyproject, ("tool", "patterns")),
    ):
        if not path.is_file():
            continue
        try:
            doc = tomlkit.parse(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("ignoring malformed %s: %s", path, exc)
            continue
        section: object = doc
        for key in key_path:
            if not isinstance(section, dict) or key not in section:
                section = None
                break
            section = section[key]
        if isinstance(section, dict):
            selection = _parse_patterns_section(section)
            if selection is not None:
                return selection
    return None


def write_project_selection(
    project_dir: Path,
    selection: PatternSelection,
    *,
    source: str | None = None,
) -> Path:
    """Persist *selection* into the project's TOML config (idempotent).

    Strategy:
        1. If ``stx.toml`` exists → write under ``[patterns]``.
        2. Else if ``pyproject.toml`` exists → write under ``[tool.patterns]``.
        3. Else → create ``stx.toml`` with ``[patterns]`` only.

    Comments and ordering of unrelated keys are preserved via ``tomlkit``.
    Any of the three legacy shortcuts (``preset``/``selected``/``all``)
    found in the section is removed so the canonical form is the only
    source of truth after write.
    """
    project_dir = Path(project_dir)
    stx_toml, pyproject = _config_files(project_dir)

    if stx_toml.is_file():
        target_path, key_path = stx_toml, ("patterns",)
    elif pyproject.is_file():
        target_path, key_path = pyproject, ("tool", "patterns")
    else:
        target_path, key_path = stx_toml, ("patterns",)

    if target_path.is_file():
        doc = tomlkit.parse(target_path.read_text(encoding="utf-8"))
    else:
        doc = tomlkit.document()

    section = _ensure_table(doc, key_path)

    if source is not None and "source" not in section:
        section["source"] = source

    # Drop legacy shortcuts so the file has one canonical representation.
    for legacy_key in ("preset", "selected", "all"):
        if legacy_key in section:
            del section[legacy_key]

    sel_table = tomlkit.table()

    def _array_of(values: tuple[str, ...]):
        a = tomlkit.array()
        for v in values:
            a.append(v)
        return a

    sel_table["presets"] = _array_of(selection.presets)
    sel_table["individuals"] = _array_of(selection.individuals)
    sel_table["excludes"] = _array_of(selection.excludes)
    sel_table["all"] = selection.all_flag
    section["selection"] = sel_table

    target_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
    return target_path


def write_project_source(project_dir: Path, source: str) -> Path:
    """Record ``[patterns].source = <source>`` in the project's TOML.

    Same target-file precedence as :func:`write_project_selection`. Preserves
    comments, ordering, and any existing ``selection`` sub-table.
    """
    project_dir = Path(project_dir)
    stx_toml, pyproject = _config_files(project_dir)

    if stx_toml.is_file():
        target_path, key_path = stx_toml, ("patterns",)
    elif pyproject.is_file():
        target_path, key_path = pyproject, ("tool", "patterns")
    else:
        target_path, key_path = stx_toml, ("patterns",)

    if target_path.is_file():
        doc = tomlkit.parse(target_path.read_text(encoding="utf-8"))
    else:
        doc = tomlkit.document()

    section = _ensure_table(doc, key_path)
    section["source"] = source
    target_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
    return target_path


def _ensure_table(doc: TOMLDocument, key_path: tuple[str, ...]):
    """Walk *doc* creating tables for missing keys; return the final table."""
    current = doc
    for key in key_path:
        if key not in current:
            current[key] = tomlkit.table()
        current = current[key]
    return current
