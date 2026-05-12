"""Source resolver for ``stx patterns`` (R4 precedence, no env var).

Resolution order:
    1. CLI ``--source`` override.
    2. ``<project>/stx.toml`` then ``<project>/pyproject.toml`` ``[patterns].source``.
    3. ``<workspace>/stx.toml`` ``[patterns].source``.
    4. Auto-discover ``<workspace>/streamtex-patterns/``.
"""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from . import SourceNotFoundError

logger = logging.getLogger(__name__)


class SourceLevel(Enum):
    """Origin level of a resolved patterns source."""

    CLI_OVERRIDE = 1
    PROJECT_TOML = 2
    WORKSPACE_TOML = 3
    AUTO_SIBLING = 4


@dataclass(frozen=True)
class ResolvedSource:
    """A patterns source resolved to an absolute, valid directory."""

    path: Path
    level: SourceLevel
    raw_value: str | None
    declared_at: Path | None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_valid_source(path: Path) -> bool:
    """Return True if *path* looks like a patterns source repo."""
    return (path / "manifest.toml").is_file()


def _load_patterns_section(toml_path: Path) -> dict | None:
    """Return ``[patterns]`` section of *toml_path* or None if absent."""
    if not toml_path.is_file():
        return None
    try:
        with toml_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        logger.warning("ignoring malformed TOML at %s: %s", toml_path, exc)
        return None
    section = data.get("patterns")
    if not isinstance(section, dict):
        # Also try tool.patterns for pyproject.toml convention
        section = data.get("tool", {}).get("patterns")
    return section if isinstance(section, dict) else None


def _normalize(raw: str, base: Path) -> Path:
    """Normalize *raw* (relative or absolute) against *base*, expanding ``~``."""
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = base / p
    return p.resolve()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_source(
    project_dir: Path | str,
    *,
    cli_override: str | None = None,
    workspace_root: Path | str | None = None,
) -> ResolvedSource:
    """Resolve the patterns source according to R4.

    Args:
        project_dir: The project's root directory.
        cli_override: Value of ``--source`` flag.
        workspace_root: Workspace root, if known.

    Returns:
        A :class:`ResolvedSource` pointing to an existing patterns repo.

    Raises:
        SourceNotFoundError: when no level resolved successfully.
        NotImplementedError: for git+url sources (phase 1 limitation).
    """
    project_dir = Path(project_dir).resolve()
    workspace_root_p = Path(workspace_root).resolve() if workspace_root else None

    attempted: list[str] = []

    # Step 1: CLI override
    if cli_override:
        if cli_override.startswith("git+"):
            raise NotImplementedError(
                "remote git+ patterns sources are not supported yet "
                f"(got: {cli_override!r})"
            )
        path = _normalize(cli_override, Path.cwd())
        attempted.append(f"--source: {path}")
        if not path.is_dir():
            raise SourceNotFoundError(
                f"--source {cli_override!r}: directory not found ({path})"
            )
        if not _is_valid_source(path):
            raise SourceNotFoundError(
                f"--source {cli_override!r}: not a patterns source "
                f"(missing manifest.toml in {path})"
            )
        return ResolvedSource(
            path=path,
            level=SourceLevel.CLI_OVERRIDE,
            raw_value=cli_override,
            declared_at=None,
        )

    # Step 2: project-level TOML
    for fn in ("stx.toml", "pyproject.toml"):
        tp = project_dir / fn
        attempted.append(f"project {fn}")
        section = _load_patterns_section(tp)
        if section and "source" in section:
            raw = str(section["source"])
            path = _normalize(raw, tp.parent)
            if _is_valid_source(path):
                return ResolvedSource(
                    path=path,
                    level=SourceLevel.PROJECT_TOML,
                    raw_value=raw,
                    declared_at=tp,
                )
            raise SourceNotFoundError(
                f"{tp}: [patterns].source = {raw!r} → {path} "
                "is not a valid patterns repo (missing manifest.toml)"
            )

    # Step 3: workspace-level TOML
    if workspace_root_p:
        tp = workspace_root_p / "stx.toml"
        attempted.append(f"workspace stx.toml ({tp})")
        section = _load_patterns_section(tp)
        if section and "source" in section:
            raw = str(section["source"])
            path = _normalize(raw, tp.parent)
            if _is_valid_source(path):
                return ResolvedSource(
                    path=path,
                    level=SourceLevel.WORKSPACE_TOML,
                    raw_value=raw,
                    declared_at=tp,
                )
            raise SourceNotFoundError(
                f"{tp}: [patterns].source = {raw!r} → {path} "
                "is not a valid patterns repo (missing manifest.toml)"
            )

    # Step 4: autodiscover sibling
    if workspace_root_p:
        sibling = (workspace_root_p / "streamtex-patterns").resolve()
        attempted.append(f"sibling {sibling}")
        if _is_valid_source(sibling):
            return ResolvedSource(
                path=sibling,
                level=SourceLevel.AUTO_SIBLING,
                raw_value=None,
                declared_at=None,
            )

    raise SourceNotFoundError(
        "patterns: source not found. Tried:\n  - "
        + "\n  - ".join(attempted)
        + "\nUse --source PATH or declare [patterns].source in stx.toml."
    )
