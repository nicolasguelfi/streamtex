"""Migration registry and version detection."""

import os
import re

from .base import Migration

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_MIGRATIONS: list[Migration] = []


def register(cls: type[Migration]) -> type[Migration]:
    """Class decorator that registers a migration instance."""
    ALL_MIGRATIONS.append(cls())
    ALL_MIGRATIONS.sort(key=lambda m: _version_tuple(m.version))
    return cls


def _version_tuple(v: str) -> tuple[int, ...]:
    """Convert '0.4.0' to (0, 4, 0) for sorting."""
    return tuple(int(x) for x in v.split("."))


def get_pending_migrations(
    current_version: str, target_version: str,
) -> list[Migration]:
    """Return migrations between *current_version* (exclusive) and *target_version* (inclusive)."""
    cur = _version_tuple(current_version)
    tgt = _version_tuple(target_version)
    return [m for m in ALL_MIGRATIONS if cur < _version_tuple(m.version) <= tgt]


# ---------------------------------------------------------------------------
# Version detection
# ---------------------------------------------------------------------------

def detect_project_version(project_path: str) -> str:
    """Detect the streamtex version a project was created/upgraded for.

    Strategy:
    1. Read ``.stx-version`` marker file (written by ``stx project upgrade``)
    2. Parse the ``streamtex>=X.Y.Z`` specifier from ``pyproject.toml``
    3. Fall back to ``"0.0.0"`` (treat as never upgraded)
    """
    # 1. .stx-version marker
    marker = os.path.join(project_path, ".stx-version")
    if os.path.isfile(marker):
        with open(marker, encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            return text

    # 2. pyproject.toml
    pyproject = os.path.join(project_path, "pyproject.toml")
    if os.path.isfile(pyproject):
        with open(pyproject, encoding="utf-8") as f:
            content = f.read()
        # Match: "streamtex>=0.3.0" or "streamtex[pdf,ai]>=0.4.0"
        m = re.search(r'"streamtex(?:\[[^\]]*\])?>=([^"]+)"', content)
        if m:
            return m.group(1)

    return "0.0.0"


def write_version_marker(project_path: str, version: str) -> None:
    """Write the ``.stx-version`` marker after a successful upgrade."""
    marker = os.path.join(project_path, ".stx-version")
    with open(marker, "w", encoding="utf-8") as f:
        f.write(version + "\n")
