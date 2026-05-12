"""Preset loader: parse ``presets/*.toml`` and resolve ``extends`` chains."""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path

from . import PresetError
from .manifest import load_repo_manifest

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Preset:
    """A single preset definition (raw, before extends resolution)."""

    name: str
    description: str
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    extends: str
    file: Path


@dataclass(frozen=True)
class ResolvedPreset:
    """A preset flattened after extends resolution."""

    name: str
    description: str
    pattern_files: tuple[Path, ...]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _preset_path(source_dir: Path, name: str) -> Path:
    """Return the canonical preset file path for *name*."""
    return source_dir / "presets" / f"{name}.toml"


def load_preset(source_dir: Path, preset_name: str) -> Preset:
    """Load a single preset by name.

    Raises:
        PresetError: if the preset does not exist or is malformed.
    """
    path = _preset_path(source_dir, preset_name)
    if not path.is_file():
        raise PresetError(f"unknown preset: {preset_name!r} (looked at {path})")

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise PresetError(f"{path}: malformed TOML: {exc}") from exc

    preset = data.get("preset", {})
    patterns = data.get("patterns", {})
    depends_on = data.get("depends_on", {})

    name = str(preset.get("name", preset_name))
    if name != preset_name:
        # tolerate but warn
        logger.warning(
            "preset name mismatch: file=%s declares name=%r", path, name
        )
    description = str(preset.get("description", ""))

    include_raw = patterns.get("include", []) or []
    exclude_raw = patterns.get("exclude", []) or []
    extends = str(depends_on.get("extends", ""))

    return Preset(
        name=preset_name,
        description=description,
        include=tuple(str(x) for x in include_raw),
        exclude=tuple(str(x) for x in exclude_raw),
        extends=extends,
        file=path,
    )


def list_presets(source_dir: Path) -> list[Preset]:
    """Return all presets declared in ``manifest.toml``, sorted by name."""
    manifest = load_repo_manifest(source_dir)
    out: list[Preset] = []
    for name in sorted(manifest.presets.keys()):
        try:
            out.append(load_preset(source_dir, name))
        except PresetError as exc:
            logger.warning("skipping preset %s: %s", name, exc)
    return out


# ---------------------------------------------------------------------------
# Glob expansion + extends resolution
# ---------------------------------------------------------------------------

def _expand_entry(source_dir: Path, entry: str) -> list[Path]:
    """Expand a single ``include``/``exclude`` entry into existing pattern files.

    Filters out files prefixed with ``_`` and entries pointing outside scopes.
    """
    if "*" in entry:
        # Limit globs to single-level wildcards (no `**` in phase 1).
        out = []
        for p in sorted((source_dir).glob(entry)):
            if not p.is_file() or p.suffix != ".md":
                continue
            if p.name.startswith("_"):
                continue
            out.append(p.resolve())
        return out

    p = (source_dir / entry).resolve()
    if not p.is_file():
        raise PresetError(f"include path does not exist: {entry!r} ({p})")
    if p.suffix != ".md":
        raise PresetError(f"include must be a .md file: {entry!r}")
    return [p]


def resolve_preset(source_dir: Path, preset_name: str) -> ResolvedPreset:
    """Recursively resolve a preset, applying ``extends`` chains.

    Raises:
        PresetError: on cycles, unknown presets, or empty results.
    """
    visited: list[str] = []

    def _walk(name: str) -> tuple[list[Path], str]:
        if name in visited:
            chain = " -> ".join([*visited, name])
            raise PresetError(f"cyclic preset extends: {chain}")
        visited.append(name)
        preset = load_preset(source_dir, name)

        # Start with parent's pattern_files
        if preset.extends:
            parent_files, _ = _walk(preset.extends)
        else:
            parent_files = []

        # Add own includes
        own: list[Path] = []
        for entry in preset.include:
            own.extend(_expand_entry(source_dir, entry))

        # Subtract excludes
        for entry in preset.exclude:
            try:
                excl = _expand_entry(source_dir, entry)
            except PresetError:
                continue
            excl_set = {p for p in excl}
            own = [p for p in own if p not in excl_set]
            parent_files = [p for p in parent_files if p not in excl_set]

        merged = parent_files + own
        # dedup preserving order
        seen: set[Path] = set()
        deduped: list[Path] = []
        for p in merged:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        visited.pop()
        return deduped, preset.description

    files, description = _walk(preset_name)
    if not files:
        raise PresetError(
            f"preset {preset_name!r} resolves to an empty file list"
        )
    files.sort()
    return ResolvedPreset(
        name=preset_name,
        description=description,
        pattern_files=tuple(files),
    )
