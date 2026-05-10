"""Drift detection (Strategy U2) and update application for installed patterns."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from . import DriftError, PatternError
from .index import regenerate_index
from .manifest import load_meta, save_meta, sha256_file

logger = logging.getLogger(__name__)


class DriftStatus(Enum):
    """Possible drift states between local copy, meta record, and source."""

    CLEAN = "clean"
    UPSTREAM_AHEAD = "upstream_ahead"
    LOCAL_AHEAD = "local_ahead"
    DIVERGED = "diverged"
    ORPHAN_LOCAL = "orphan_local"
    UPSTREAM_GONE = "upstream_gone"


@dataclass(frozen=True)
class DriftReport:
    """Drift state for a single tracked pattern."""

    name: str
    status: DriftStatus
    local_sha: str | None
    installed_sha: str
    source_sha: str | None


def compute_drift(target: Path, source: Path) -> list[DriftReport]:
    """Compute drift reports for every pattern listed in target's meta."""
    target = Path(target)
    source = Path(source)
    meta = load_meta(target)
    out: list[DriftReport] = []
    for rec in meta.patterns:
        local_path = target / f"{rec.name}.md"
        source_path = source / rec.from_
        local_sha = sha256_file(local_path) if local_path.exists() else None
        source_sha = sha256_file(source_path) if source_path.exists() else None

        if local_sha is None:
            status = DriftStatus.ORPHAN_LOCAL
        elif source_sha is None:
            status = DriftStatus.UPSTREAM_GONE
        else:
            local_match = local_sha == rec.installed_sha
            source_match = source_sha == rec.installed_sha
            if local_match and source_match:
                status = DriftStatus.CLEAN
            elif local_match and not source_match:
                status = DriftStatus.UPSTREAM_AHEAD
            elif not local_match and source_match:
                status = DriftStatus.LOCAL_AHEAD
            else:
                status = DriftStatus.DIVERGED

        out.append(
            DriftReport(
                name=rec.name,
                status=status,
                local_sha=local_sha,
                installed_sha=rec.installed_sha,
                source_sha=source_sha,
            )
        )
    return out


def apply_update(
    target: Path,
    source: Path,
    *,
    force: bool = False,
    only: tuple[str, ...] = (),
    dry_run: bool = False,
) -> tuple[list[DriftReport], list[str]]:
    """Apply U2 update strategy to *target*.

    Returns ``(reports, applied_names)``.
    """
    target = Path(target)
    source = Path(source)
    reports = compute_drift(target, source)

    in_scope = lambda r: not only or r.name in only  # noqa: E731

    if not force:
        diverged = [
            r.name for r in reports
            if r.status == DriftStatus.DIVERGED and in_scope(r)
        ]
        if diverged:
            raise DriftError(
                ",".join(diverged),
                "diverged from source; use --force to overwrite local changes",
            )

    if dry_run:
        applied = [
            r.name for r in reports
            if in_scope(r)
            and r.status in (DriftStatus.UPSTREAM_AHEAD, DriftStatus.DIVERGED)
        ]
        return reports, applied

    meta = load_meta(target)
    applied: list[str] = []
    for r in reports:
        if not in_scope(r):
            continue
        if r.status in (DriftStatus.UPSTREAM_AHEAD, DriftStatus.DIVERGED):
            rec = next((x for x in meta.patterns if x.name == r.name), None)
            if rec is None:  # pragma: no cover - defensive
                continue
            src_path = source / rec.from_
            dst_path = target / f"{rec.name}.md"
            if not src_path.is_file():
                continue
            try:
                if dst_path.is_symlink() or dst_path.exists():
                    dst_path.unlink()
                dst_path.write_bytes(src_path.read_bytes())
            except OSError as exc:
                raise PatternError(
                    f"failed to update {rec.name}: {exc}"
                ) from exc
            new_sha = sha256_file(dst_path)
            rec.sha = new_sha
            rec.installed_sha = new_sha
            applied.append(rec.name)
        elif r.status == DriftStatus.ORPHAN_LOCAL:
            logger.warning(
                "%s tracked but missing locally; run 'sync' to reinstall",
                r.name,
            )
        elif r.status == DriftStatus.UPSTREAM_GONE:
            logger.warning(
                "%s removed upstream; consider 'stx patterns remove %s'",
                r.name, r.name,
            )

    if applied:
        meta.installed_at = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        save_meta(target, meta)
        try:
            regenerate_index(target)
        except Exception as exc:
            logger.warning("failed to regenerate index: %s", exc)

    return reports, applied
