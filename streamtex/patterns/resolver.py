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


class TraceStatus(Enum):
    """Outcome of probing one level of the R4 chain."""

    SKIPPED = "skipped"            # level not applicable (no override, no toml)
    NOT_FOUND = "not_found"        # target path absent
    INVALID = "invalid"            # path exists but lacks manifest.toml
    MATCHED = "matched"            # first level to succeed
    UNREACHED = "unreached"        # an earlier level already matched


@dataclass(frozen=True)
class TraceEntry:
    """One step of the R4 resolution chain."""

    level: SourceLevel
    status: TraceStatus
    candidate: str | None
    """Stringified path or raw value probed at this level (None if skipped)."""
    detail: str | None
    """Reason for SKIPPED / INVALID, or origin path (e.g. which TOML)."""


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

def trace_source(
    project_dir: Path | str,
    *,
    cli_override: str | None = None,
    workspace_root: Path | str | None = None,
) -> tuple[list[TraceEntry], ResolvedSource | None]:
    """Probe each R4 level and return a structured trace + resolved source.

    Unlike :func:`resolve_source`, this never raises — it always returns a
    full trace, even when no level matches. The first MATCHED entry (if any)
    yields the second tuple element; subsequent levels are reported as
    UNREACHED (for readability of ``stx patterns source show``).

    Args:
        project_dir: The project's root directory.
        cli_override: Value of ``--source`` flag.
        workspace_root: Workspace root, if known.

    Returns:
        ``(entries, resolved_or_None)``.
    """
    project_dir = Path(project_dir).resolve()
    workspace_root_p = Path(workspace_root).resolve() if workspace_root else None

    entries: list[TraceEntry] = []
    resolved: ResolvedSource | None = None

    def _record(level: SourceLevel, status: TraceStatus,
                candidate: str | None, detail: str | None) -> None:
        if resolved is not None and status not in (TraceStatus.MATCHED,):
            status = TraceStatus.UNREACHED
        entries.append(TraceEntry(level, status, candidate, detail))

    # ---- Level 1: CLI override ------------------------------------------
    if cli_override is None:
        _record(SourceLevel.CLI_OVERRIDE, TraceStatus.SKIPPED, None,
                "no --source flag")
    elif cli_override.startswith("git+"):
        _record(SourceLevel.CLI_OVERRIDE, TraceStatus.INVALID,
                cli_override, "git+ remote sources are not supported yet")
    else:
        path = _normalize(cli_override, Path.cwd())
        if not path.is_dir():
            _record(SourceLevel.CLI_OVERRIDE, TraceStatus.NOT_FOUND,
                    str(path), f"--source {cli_override!r}: not a directory")
        elif not _is_valid_source(path):
            _record(SourceLevel.CLI_OVERRIDE, TraceStatus.INVALID,
                    str(path), "missing manifest.toml")
        else:
            resolved = ResolvedSource(
                path=path, level=SourceLevel.CLI_OVERRIDE,
                raw_value=cli_override, declared_at=None,
            )
            _record(SourceLevel.CLI_OVERRIDE, TraceStatus.MATCHED,
                    str(path), None)

    # ---- Level 2: project-level TOML ------------------------------------
    project_matched = False
    for fn in ("stx.toml", "pyproject.toml"):
        tp = project_dir / fn
        if not tp.is_file():
            continue
        section = _load_patterns_section(tp)
        if not section or "source" not in section:
            continue
        raw = str(section["source"])
        path = _normalize(raw, tp.parent)
        if resolved is not None:
            _record(SourceLevel.PROJECT_TOML, TraceStatus.UNREACHED,
                    raw, f"declared in {tp}")
        elif not _is_valid_source(path):
            _record(SourceLevel.PROJECT_TOML, TraceStatus.INVALID,
                    str(path), f"declared in {tp}; missing manifest.toml")
        else:
            resolved = ResolvedSource(
                path=path, level=SourceLevel.PROJECT_TOML,
                raw_value=raw, declared_at=tp,
            )
            _record(SourceLevel.PROJECT_TOML, TraceStatus.MATCHED,
                    str(path), f"declared in {tp}")
        project_matched = True
        break
    if not project_matched:
        _record(SourceLevel.PROJECT_TOML, TraceStatus.SKIPPED, None,
                "no [patterns].source in project stx.toml/pyproject.toml")

    # ---- Level 3: workspace-level TOML ----------------------------------
    if workspace_root_p:
        tp = workspace_root_p / "stx.toml"
        section = _load_patterns_section(tp) if tp.is_file() else None
        if section and "source" in section:
            raw = str(section["source"])
            path = _normalize(raw, tp.parent)
            if resolved is not None:
                _record(SourceLevel.WORKSPACE_TOML, TraceStatus.UNREACHED,
                        raw, f"declared in {tp}")
            elif not _is_valid_source(path):
                _record(SourceLevel.WORKSPACE_TOML, TraceStatus.INVALID,
                        str(path), f"declared in {tp}; missing manifest.toml")
            else:
                resolved = ResolvedSource(
                    path=path, level=SourceLevel.WORKSPACE_TOML,
                    raw_value=raw, declared_at=tp,
                )
                _record(SourceLevel.WORKSPACE_TOML, TraceStatus.MATCHED,
                        str(path), f"declared in {tp}")
        else:
            _record(SourceLevel.WORKSPACE_TOML, TraceStatus.SKIPPED, None,
                    "no [patterns].source in workspace stx.toml")
    else:
        _record(SourceLevel.WORKSPACE_TOML, TraceStatus.SKIPPED, None,
                "no workspace root provided")

    # ---- Level 4: autodiscover sibling ----------------------------------
    if workspace_root_p:
        sibling = (workspace_root_p / "streamtex-patterns").resolve()
        if resolved is not None:
            _record(SourceLevel.AUTO_SIBLING, TraceStatus.UNREACHED,
                    str(sibling), None)
        elif not sibling.is_dir():
            _record(SourceLevel.AUTO_SIBLING, TraceStatus.NOT_FOUND,
                    str(sibling), "no sibling clone of streamtex-patterns")
        elif not _is_valid_source(sibling):
            _record(SourceLevel.AUTO_SIBLING, TraceStatus.INVALID,
                    str(sibling), "directory present but lacks manifest.toml")
        else:
            resolved = ResolvedSource(
                path=sibling, level=SourceLevel.AUTO_SIBLING,
                raw_value=None, declared_at=None,
            )
            _record(SourceLevel.AUTO_SIBLING, TraceStatus.MATCHED,
                    str(sibling), None)
    else:
        _record(SourceLevel.AUTO_SIBLING, TraceStatus.SKIPPED, None,
                "no workspace root provided")

    return entries, resolved


_HINT_ON_FAILURE = (
    "Hint: run `stx patterns source clone` to fetch the official repo "
    "into this workspace, `stx patterns source link PATH` to point to an "
    "existing local clone, or `stx patterns source set PATH` to record a "
    "custom path in stx.toml. See `stx patterns source show` for what was "
    "probed."
)


def _format_trace_summary(entries: list[TraceEntry]) -> str:
    """One-line-per-level summary used in error messages."""
    lines: list[str] = []
    for e in entries:
        candidate = e.candidate or "(skipped)"
        suffix = f" — {e.detail}" if e.detail else ""
        lines.append(f"  - L{e.level.value} {e.status.value}: {candidate}{suffix}")
    return "\n".join(lines)


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
        SourceNotFoundError: when no level resolved successfully. The
            error message includes a per-level trace and a hint pointing
            to ``stx patterns source clone | link | set``.
    """
    entries, resolved = trace_source(
        project_dir,
        cli_override=cli_override,
        workspace_root=workspace_root,
    )
    if resolved is not None:
        return resolved
    raise SourceNotFoundError(
        "patterns: no usable source found.\n"
        + _format_trace_summary(entries)
        + "\n" + _HINT_ON_FAILURE
    )
