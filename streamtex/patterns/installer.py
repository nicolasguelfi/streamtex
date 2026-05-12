"""Install / remove patterns into a project's target directory."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import DriftError, MetaError, PatternError
from .index import regenerate_index
from .manifest import (
    PatternRecord,
    PatternsMeta,
    load_meta,
    save_meta,
    sha256_file,
)
from .preset import resolve_preset

logger = logging.getLogger(__name__)

DEFAULT_TARGET_REL = ".claude/custom/streamtex-patterns"
_SCOPES = ("core", "slides", "docs")


# ---------------------------------------------------------------------------
# Plan + result dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InstallPlan:
    """Pre-computed install plan, ready to be applied."""

    target: Path
    source: Path
    preset_name: str | None
    selected_files: tuple[Path, ...]
    excluded: tuple[str, ...]
    mode: str
    overwrite_existing: bool
    is_initial: bool


@dataclass(frozen=True)
class InstallResult:
    """Outcome of :func:`execute_install`."""

    installed: tuple[str, ...]
    skipped: tuple[str, ...]
    overwritten: tuple[str, ...]
    target: Path
    meta_path: Path | None


# ---------------------------------------------------------------------------
# Source helpers
# ---------------------------------------------------------------------------

def _find_pattern_in_source(source: Path, name: str) -> Path:
    """Locate ``<name>.md`` across well-known scopes; raise on ambiguity/miss."""
    hits: list[Path] = []
    for scope in _SCOPES:
        candidate = source / scope / f"{name}.md"
        if candidate.is_file():
            hits.append(candidate.resolve())
    projects_dir = source / "projects"
    if projects_dir.is_dir():
        for proj in projects_dir.iterdir():
            if not proj.is_dir():
                continue
            candidate = proj / f"{name}.md"
            if candidate.is_file():
                hits.append(candidate.resolve())
    if not hits:
        raise PatternError(f"pattern {name!r} not found in source {source}")
    if len(hits) > 1:
        listing = ", ".join(str(p.relative_to(source)) for p in hits)
        raise PatternError(f"ambiguous pattern {name!r}: matches {listing}")
    return hits[0]


def _all_patterns(source: Path) -> list[Path]:
    """Return every ``.md`` pattern under known scopes (excluding leading ``_``)."""
    out: list[Path] = []
    for scope in _SCOPES:
        d = source / scope
        if d.is_dir():
            for f in sorted(d.glob("*.md")):
                if not f.name.startswith("_") and f.name != "README.md":
                    out.append(f.resolve())
    projects = source / "projects"
    if projects.is_dir():
        for proj in sorted(projects.iterdir()):
            if not proj.is_dir():
                continue
            for f in sorted(proj.glob("*.md")):
                if not f.name.startswith("_") and f.name != "README.md":
                    out.append(f.resolve())
    return out


def _resolve_source_commit(source: Path) -> str | None:
    """Return ``git rev-parse HEAD`` of *source*, or None if unavailable."""
    if not (source / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return None


def _relative_from_source(file_path: Path, source: Path) -> str:
    try:
        return str(file_path.resolve().relative_to(source.resolve()))
    except ValueError:
        # Fallback for unusual layouts
        return file_path.name


# ---------------------------------------------------------------------------
# Plan building
# ---------------------------------------------------------------------------

def build_install_plan(
    *,
    target: Path,
    source: Path,
    preset: str | None = None,
    individual_patterns: tuple[str, ...] = (),
    install_all: bool = False,
    exclude: tuple[str, ...] = (),
    mode: str = "copy",
    force: bool = False,
) -> InstallPlan:
    """Compute the list of files to install given the selectors.

    Exactly one of ``preset``, ``individual_patterns``, ``install_all`` must
    be truthy.
    """
    selectors = sum(
        bool(x) for x in (preset, individual_patterns, install_all)
    )
    if selectors == 0:
        raise PatternError(
            "install needs a selector: --preset, --pattern, or --all"
        )
    if selectors > 1:
        raise PatternError(
            "install selectors are mutually exclusive: "
            "use exactly one of --preset / --pattern / --all"
        )
    if mode not in ("copy", "symlink"):
        raise PatternError(f"unsupported mode: {mode!r}")

    source = Path(source).resolve()
    target = Path(target).resolve()

    if preset:
        resolved = resolve_preset(source, preset)
        files: list[Path] = list(resolved.pattern_files)
    elif individual_patterns:
        files = [_find_pattern_in_source(source, n) for n in individual_patterns]
    else:
        files = _all_patterns(source)

    excluded_names = {x for x in exclude}
    if excluded_names:
        files = [p for p in files if p.stem not in excluded_names]

    is_initial = not (target / ".patterns-meta.json").is_file()

    return InstallPlan(
        target=target,
        source=source,
        preset_name=preset,
        selected_files=tuple(files),
        excluded=tuple(exclude),
        mode=mode,
        overwrite_existing=force,
        is_initial=is_initial,
    )


# ---------------------------------------------------------------------------
# Plan execution
# ---------------------------------------------------------------------------

def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        dst.unlink()
    shutil.copy2(src, dst)
    try:
        os.chmod(dst, 0o644)
    except OSError:
        pass


def _symlink_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        dst.unlink()
    try:
        os.symlink(src.resolve(), dst)
    except OSError as exc:
        raise PatternError(
            f"symlink mode unsupported on this platform: {exc}"
        ) from exc


def execute_install(
    plan: InstallPlan,
    *,
    dry_run: bool = False,
    raw_source: str | None = None,
) -> InstallResult:
    """Apply *plan* to disk; returns an :class:`InstallResult`."""
    installed: list[str] = []
    skipped: list[str] = []
    overwritten: list[str] = []

    # Load existing meta if present
    existing_meta: PatternsMeta | None = None
    if not plan.is_initial:
        try:
            existing_meta = load_meta(plan.target)
        except MetaError:
            existing_meta = None
        else:
            if existing_meta.mode != plan.mode:
                raise PatternError(
                    f"in-place mode switch refused: existing meta is "
                    f"mode={existing_meta.mode!r}, requested {plan.mode!r}. "
                    "Remove .patterns-meta.json first or pass --force."
                )

    existing_records: dict[str, PatternRecord] = {
        r.name: r for r in (existing_meta.patterns if existing_meta else [])
    }

    # --- Pre-flight: detect drift transactionally -------------------------
    if not plan.overwrite_existing:
        for src in plan.selected_files:
            name = src.stem
            dst = plan.target / src.name
            if not dst.exists():
                continue
            try:
                installed_sha = sha256_file(dst)
            except OSError:
                continue
            rec = existing_records.get(name)
            if rec is None or installed_sha != rec.installed_sha:
                raise DriftError(
                    name,
                    "local copy differs from previously installed version; "
                    "use --force or `stx patterns promote " + name + "`",
                )

    # --- Apply ------------------------------------------------------------
    new_records: list[PatternRecord] = []
    for src in plan.selected_files:
        name = src.stem
        dst = plan.target / src.name
        existed = dst.exists()

        if dry_run:
            (overwritten if existed else installed).append(name)
            new_records.append(
                PatternRecord(
                    name=name,
                    from_=_relative_from_source(src, plan.source),
                    sha=sha256_file(src),
                    installed_sha=sha256_file(src),
                )
            )
            continue

        if plan.mode == "symlink":
            _symlink_file(src, dst)
        else:
            _copy_file(src, dst)

        sha = sha256_file(src)
        new_records.append(
            PatternRecord(
                name=name,
                from_=_relative_from_source(src, plan.source),
                sha=sha,
                installed_sha=sha,
            )
        )
        if existed:
            overwritten.append(name)
        else:
            installed.append(name)

    # Preserve previously installed records that we did not touch
    touched = {r.name for r in new_records}
    if existing_meta:
        for prev in existing_meta.patterns:
            if prev.name not in touched:
                new_records.append(prev)

    new_records.sort(key=lambda r: r.name)

    meta = PatternsMeta(
        schema_version=1,
        source=raw_source or str(plan.source),
        source_commit=_resolve_source_commit(plan.source),
        preset=plan.preset_name
        or (existing_meta.preset if existing_meta else None),
        mode=plan.mode,
        installed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        patterns=new_records,
    )

    meta_path: Path | None = None
    if not dry_run:
        plan.target.mkdir(parents=True, exist_ok=True)
        meta_path = save_meta(plan.target, meta)
        try:
            regenerate_index(plan.target)
        except Exception as exc:
            logger.warning("failed to regenerate index: %s", exc)

    return InstallResult(
        installed=tuple(installed),
        skipped=tuple(skipped),
        overwritten=tuple(overwritten),
        target=plan.target,
        meta_path=meta_path,
    )


def remove_pattern(target: Path, name: str, *, dry_run: bool = False) -> None:
    """Remove a single pattern from *target*."""
    target = Path(target)
    meta = load_meta(target)
    rec = next((r for r in meta.patterns if r.name == name), None)
    if rec is None:
        raise PatternError(f"pattern {name!r} not tracked in meta")

    file_path = target / f"{name}.md"
    if dry_run:
        return
    if file_path.is_symlink() or file_path.exists():
        file_path.unlink()
    meta.patterns = [r for r in meta.patterns if r.name != name]
    meta.installed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_meta(target, meta)
    try:
        regenerate_index(target)
    except Exception as exc:
        logger.warning("failed to regenerate index: %s", exc)
