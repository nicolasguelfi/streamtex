"""Dev-link configuration — read/write global and project dev settings."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Official repos that can be linked
REPOS = ("streamtex", "streamtex-claude", "streamtex-docs")

# Validation markers per repo (file/dir that MUST exist)
_REPO_MARKERS: dict[str, tuple[str, str]] = {
    "streamtex": ("pyproject.toml", 'name = "streamtex"'),
    "streamtex-claude": ("install.py", ""),
    "streamtex-docs": ("manuals", ""),
}

# ---------------------------------------------------------------------------
# Global config  (~/.config/streamtex/dev.json)
# ---------------------------------------------------------------------------

_GLOBAL_DIR = Path.home() / ".config" / "streamtex"
_GLOBAL_FILE = _GLOBAL_DIR / "dev.json"


@dataclass
class GlobalDevConfig:
    repos: dict[str, str] = field(default_factory=dict)

    def save(self) -> None:
        _GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
        _GLOBAL_FILE.write_text(
            json.dumps({"repos": self.repos}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls) -> GlobalDevConfig:
        if not _GLOBAL_FILE.is_file():
            return cls()
        try:
            data = json.loads(_GLOBAL_FILE.read_text(encoding="utf-8"))
            return cls(repos=data.get("repos", {}))
        except (json.JSONDecodeError, KeyError):
            return cls()


# ---------------------------------------------------------------------------
# Project config  (.stx-dev.json in project root)
# ---------------------------------------------------------------------------

_PROJECT_FILE = ".stx-dev.json"


@dataclass
class ProjectDevConfig:
    linked: dict[str, str] = field(default_factory=dict)

    def save(self, project_dir: str | Path) -> None:
        p = Path(project_dir) / _PROJECT_FILE
        p.write_text(
            json.dumps({"linked": self.linked}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, project_dir: str | Path) -> ProjectDevConfig:
        p = Path(project_dir) / _PROJECT_FILE
        if not p.is_file():
            return cls()
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return cls(linked=data.get("linked", {}))
        except (json.JSONDecodeError, KeyError):
            return cls()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_repo_name(name: str) -> str:
    """Raise ValueError if *name* is not a known repo."""
    if name not in REPOS:
        raise ValueError(
            f"Unknown repo {name!r}. Must be one of: {', '.join(REPOS)}"
        )
    return name


def validate_repo_path(name: str, path: str | Path) -> Path:
    """Validate that *path* looks like the expected repo.

    Returns the resolved absolute path.
    Raises ValueError with a clear message on failure.
    """
    p = Path(path).resolve()
    if not p.is_dir():
        raise ValueError(f"Path does not exist: {p}")

    # Refuse .venv paths
    for part in p.parts:
        if part == ".venv":
            raise ValueError(
                f"Path is inside a .venv — link to the source repo, not an installed copy: {p}"
            )

    marker_file, marker_content = _REPO_MARKERS[name]
    target = p / marker_file
    if not target.exists():
        raise ValueError(
            f"Path does not look like a {name} repo "
            f"(missing {marker_file}): {p}"
        )
    if marker_content:
        try:
            text = target.read_text(encoding="utf-8")
            if marker_content not in text:
                raise ValueError(
                    f"Path does not look like a {name} repo "
                    f"({marker_file} does not contain {marker_content!r}): {p}"
                )
        except OSError:
            pass

    return p


def is_editable_install(project_dir: str | Path) -> Optional[str]:
    """Return the editable source path if streamtex is installed as editable,
    or None if it is a regular PyPI install."""
    try:
        import subprocess
        result = subprocess.run(
            ["uv", "pip", "show", "streamtex"],
            capture_output=True, text=True, cwd=str(project_dir),
            timeout=10,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Editable project location:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None
