"""Helpers to read/write a project's stx.toml.

stx.toml schema is documented in PLAN.md §6.1. This module provides
non-destructive read/update primitives used by `stx pack` / `stx component`
/ `stx ds` / `stx kit` / `stx project new`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tomlkit


def _ensure(project_dir: Path) -> Path:
    p = project_dir / "stx.toml"
    if not p.is_file():
        # create skeleton
        skeleton = tomlkit.document()
        skeleton["project"] = tomlkit.table()
        skeleton["project"]["name"] = project_dir.name
        skeleton["project"]["version"] = "0.1.0"
        p.write_text(tomlkit.dumps(skeleton), encoding="utf-8")
    return p


def load(project_dir: Path) -> tomlkit.TOMLDocument:
    p = _ensure(project_dir)
    return tomlkit.parse(p.read_text(encoding="utf-8"))


def save(project_dir: Path, doc: tomlkit.TOMLDocument) -> None:
    (project_dir / "stx.toml").write_text(tomlkit.dumps(doc), encoding="utf-8")


def list_packs(project_dir: Path) -> list[dict[str, Any]]:
    doc = load(project_dir)
    raw = doc.get("packs") or []
    return [dict(entry) for entry in raw if isinstance(entry, dict)]


def add_pack(project_dir: Path, entry: dict[str, Any]) -> None:
    """Append a new `[[packs]]` entry. Refuses duplicates by `name`."""
    doc = load(project_dir)
    arr = doc.get("packs")
    if arr is None:
        arr = tomlkit.aot()
        doc["packs"] = arr
    name = entry.get("name") or entry.get("ref") or entry.get("constraint") or ""
    for existing in arr:
        existing_name = existing.get("name") or existing.get("ref") or ""
        if existing_name == name and name:
            raise ValueError(f"pack '{name}' already declared in stx.toml")
    table = tomlkit.table()
    for k, v in entry.items():
        if v is not None:
            table[k] = v
    arr.append(table)
    save(project_dir, doc)


def remove_pack(project_dir: Path, name: str) -> bool:
    doc = load(project_dir)
    arr = doc.get("packs") or []
    new_arr = tomlkit.aot()
    removed = False
    for existing in arr:
        existing_name = existing.get("name") or existing.get("ref") or ""
        if existing_name == name:
            removed = True
            continue
        new_arr.append(existing)
    if removed:
        if len(new_arr) > 0:
            doc["packs"] = new_arr
        else:
            del doc["packs"]
        save(project_dir, doc)
    return removed


def set_design_system(project_dir: Path, ref: str) -> None:
    doc = load(project_dir)
    if "design_system" not in doc:
        doc["design_system"] = tomlkit.table()
    doc["design_system"]["use"] = ref
    save(project_dir, doc)


def set_resolution_prefer(project_dir: Path, prefer: list[str]) -> None:
    doc = load(project_dir)
    if "resolution" not in doc:
        doc["resolution"] = tomlkit.table()
    doc["resolution"]["prefer"] = prefer
    save(project_dir, doc)


__all__ = [
    "load",
    "save",
    "list_packs",
    "add_pack",
    "remove_pack",
    "set_design_system",
    "set_resolution_prefer",
]
