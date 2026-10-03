"""Facts read from a versioned source, with a staleness check (L23).

ai4se6d spent 24 commits in one day re-aligning counts, names and paths on a
new version of the method it teaches (GSE-One v0.85), with errors and
reverts on the way. Facts that come from an evolving source live in one
data file per source, which records the version they were read from::

    # facts/gse-one.toml
    [source]
    name = "GSE-One"
    version = "0.85.0"                   # the version these facts were read from
    current = "../gensem/VERSION"        # optional: where the CURRENT version is
                                         # (a text file, or a pyproject.toml)
    [facts]
    agents = 23
    commands = 41
    paths.registry = ".gse/registry"

In a block::

    from streamtex.facts import fact
    st_write(f"{fact('gse-one', 'agents')} specialised agents")

An unknown source or key raises (a fact never silently disappears from a
slide). ``stx validate`` warns when the current version of a source differs
from the one its facts were read from — the facts are then due for a re-check.
Files are re-read when they change.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FACTS_DIR = "facts"


def _project_root(start: str | None = None) -> Path:
    from .book import _find_upwards, _main_script_dir

    toml = _find_upwards(start or _main_script_dir(), "stx.toml")
    return Path(toml).parent if toml else Path(start or os.getcwd())


def _load(path: Path) -> dict:
    from .watch import load_toml

    return load_toml(path)


def facts_file(source: str, root: Path | None = None) -> Path:
    path = (root or _project_root()) / FACTS_DIR / f"{source}.toml"
    if not path.is_file():
        raise KeyError(f"no facts file for source {source!r}: {path}")
    return path


def fact(source: str, key: str, *, root: Path | None = None) -> Any:
    """The fact *key* (dotted for nested tables) of *source*."""
    data = _load(facts_file(source, root)).get("facts", {})
    node: Any = data
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"fact {key!r} not in facts/{source}.toml")
        node = node[part]
    return node


@dataclass
class StaleFacts:
    source: str
    recorded: str
    current: str
    count: int


def _current_version(spec: str, base: Path) -> str | None:
    path = (base / spec).resolve()
    if not path.is_file():
        return None
    if path.suffix == ".toml":
        try:
            with open(path, "rb") as f:
                return tomllib.load(f).get("project", {}).get("version")
        except (OSError, tomllib.TOMLDecodeError):
            return None
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return lines[0].strip() if lines else None


def _count(node: Any) -> int:
    return sum(_count(v) for v in node.values()) if isinstance(node, dict) else 1


def stale_facts(root: Path) -> list[StaleFacts]:
    """Sources whose current version differs from the one their facts were read from."""
    out: list[StaleFacts] = []
    folder = root / FACTS_DIR
    if not folder.is_dir():
        return out
    for path in sorted(folder.glob("*.toml")):
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError):
            continue
        src = data.get("source", {})
        recorded, spec = str(src.get("version", "")), src.get("current")
        if not spec or not recorded:
            continue
        current = _current_version(str(spec), path.parent)
        if current and current != recorded:
            out.append(StaleFacts(path.stem, recorded, current, _count(data.get("facts", {}))))
    return out
