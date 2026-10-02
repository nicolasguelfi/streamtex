"""Data files read at build time, kept live (L13, #53).

A block or a helper that reads a data file (tuning values, a schedule, a
list of slides…) with ``open()`` + ``functools.lru_cache`` keeps the first
content until the server restarts, and the page cache — whose key does not
know about the file — keeps serving the old TOC / markers even after a
restart. Use these instead::

    data = stx.load_json(HERE / "timers.json")     # re-read when the file changes
    cfg = stx.load_toml(HERE / "settings.toml")
    text = stx.load_text(HERE / "notes.md")
    stx.watch_file(HERE / "other.csv")             # read it yourself, but invalidate on change

Each call returns the cached value while the file's mtime and size are
unchanged, re-reads it otherwise, and registers the file: its mtime enters
the page-cache key (``book._compute_cache_hash``) and is checked again when a
persisted cache is loaded after a restart. Reloading the page is enough.
"""

from __future__ import annotations

import json
import os
import threading
import tomllib
from pathlib import Path
from typing import Any

_lock = threading.Lock()
_WATCHED: dict[str, None] = {}                      # insertion-ordered set of abs paths
_CACHE: dict[tuple[str, str], tuple[tuple[float, int], Any]] = {}


def _key(path: str | os.PathLike) -> str:
    return os.path.abspath(os.fspath(path))


def _stamp(path: str) -> tuple[float, int]:
    st = os.stat(path)
    return (st.st_mtime, st.st_size)


def watch_file(path: str | os.PathLike) -> str:
    """Register *path*: its changes invalidate the page cache. Returns the abs path."""
    p = _key(path)
    with _lock:
        _WATCHED[p] = None
    return p


def watched_files() -> list[str]:
    with _lock:
        return list(_WATCHED)


def watched_snapshot() -> dict[str, float]:
    """``{path: mtime}`` of every registered file (``-1`` when missing)."""
    out: dict[str, float] = {}
    for p in watched_files():
        try:
            out[p] = os.path.getmtime(p)
        except OSError:
            out[p] = -1.0
    return out


def snapshot_is_current(snapshot: dict[str, float] | None) -> bool:
    """True when every file of a stored snapshot still has its recorded mtime."""
    for p, mtime in (snapshot or {}).items():
        try:
            now = os.path.getmtime(p)
        except OSError:
            now = -1.0
        if now != mtime:
            return False
    return True


def _cached(kind: str, path: str | os.PathLike, read) -> Any:
    p = watch_file(path)
    stamp = _stamp(p)
    with _lock:
        hit = _CACHE.get((kind, p))
    if hit is not None and hit[0] == stamp:
        return hit[1]
    value = read(p)
    with _lock:
        _CACHE[(kind, p)] = (stamp, value)
    return value


def load_text(path: str | os.PathLike, encoding: str = "utf-8") -> str:
    """The file's text, re-read whenever it changes."""
    return _cached(f"text:{encoding}", path, lambda p: Path(p).read_text(encoding=encoding))


def load_json(path: str | os.PathLike) -> Any:
    """The parsed JSON file, re-read whenever it changes.

    The cached object is shared between calls: copy it before mutating it.
    """
    return _cached("json", path, lambda p: json.loads(Path(p).read_text(encoding="utf-8")))


def load_toml(path: str | os.PathLike) -> dict:
    """The parsed TOML file, re-read whenever it changes (shared object — copy to mutate)."""
    def _read(p: str) -> dict:
        with open(p, "rb") as f:
            return tomllib.load(f)
    return _cached("toml", path, _read)


def _reset_for_tests() -> None:
    with _lock:
        _WATCHED.clear()
        _CACHE.clear()
