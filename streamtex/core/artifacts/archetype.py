"""Archetype artifact — markdown with YAML frontmatter.

A scene archetype is a reusable visual composition pattern: "bridge",
"horizon", "balance", etc. Each archetype is a markdown file with a YAML
frontmatter that exposes its metadata machine-readably, while the body of
the file documents the composition for human/agent consumption.

Filesystem convention: ``<pack>/archetypes/<name>.md``

Frontmatter schema (all but `palette_refs` required):

    ---
    name: bridge
    description: Transition / 30-year horizon
    orientation: landscape | portrait | square | any
    status: validated | draft
    tags: [transition, narrative]
    extrapolable: true
    since: 2026-05-05
    palette_refs: [primary, accent, highlight]
    ---

Validation codes: ARV001-ARV010 (archetype validation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from streamtex.core.artifacts._frontmatter import split_frontmatter
from streamtex.core.validation import ValidationIssue

_REQUIRED_FIELDS = ("name", "description", "orientation", "status", "since")
_VALID_ORIENTATIONS = {"landscape", "portrait", "square", "any"}
_VALID_STATUSES = {"validated", "draft"}


@dataclass(frozen=True)
class Archetype:
    """Typed view of an archetype artifact."""

    name: str
    pack: str
    description: str
    orientation: str
    status: str
    since: str
    tags: list[str] = field(default_factory=list)
    extrapolable: bool = True
    palette_refs: list[str] = field(default_factory=list)
    body: str = ""


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_archetype(path: Path) -> list[ValidationIssue]:
    """Run validation checks on a single archetype markdown file.

    ARV001 — file readable
    ARV002 — has YAML frontmatter (opens with ---)
    ARV003 — required fields present
    ARV004 — `orientation` in {landscape, portrait, square, any}
    ARV005 — `status` in {validated, draft}
    ARV006 — `since` looks like ISO date YYYY-MM-DD
    ARV007 — body is non-trivial (≥ 200 characters)
    """
    issues: list[ValidationIssue] = []
    if not path.exists() or not path.is_file():
        return [_issue("ARV001", "error", path, "archetype file not found")]
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [_issue("ARV001", "error", path, f"unreadable: {exc}")]

    if not text.startswith("---"):
        issues.append(_issue("ARV002", "error", path, "missing YAML frontmatter (file must open with `---`)"))
        return issues

    fm, body = split_frontmatter(text)
    if not fm:
        issues.append(_issue("ARV002", "error", path, "frontmatter is empty or malformed"))
        return issues

    for key in _REQUIRED_FIELDS:
        if key not in fm or fm[key] in (None, ""):
            issues.append(_issue("ARV003", "error", path, f"missing required field '{key}'"))

    orient = fm.get("orientation")
    if isinstance(orient, str) and orient not in _VALID_ORIENTATIONS:
        issues.append(
            _issue(
                "ARV004",
                "error",
                path,
                f"orientation {orient!r} not in {{{', '.join(sorted(_VALID_ORIENTATIONS))}}}",
            )
        )

    status = fm.get("status")
    if isinstance(status, str) and status not in _VALID_STATUSES:
        issues.append(
            _issue(
                "ARV005",
                "error",
                path,
                f"status {status!r} not in {{{', '.join(sorted(_VALID_STATUSES))}}}",
            )
        )

    since = fm.get("since")
    if isinstance(since, str):
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", since):
            issues.append(_issue("ARV006", "warning", path, f"since {since!r} not in YYYY-MM-DD format"))

    if len(body.strip()) < 200:
        issues.append(_issue("ARV007", "warning", path, "archetype body is suspiciously short (< 200 chars)"))

    return issues


def load_archetype_from_path(path: Path, *, pack: str = "") -> Archetype:
    """Parse an archetype markdown file into a typed `Archetype` dataclass."""
    issues = validate_archetype(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid archetype at {path}:\n{joined}")

    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    palette_refs = fm.get("palette_refs") or []
    if isinstance(palette_refs, str):
        palette_refs = [palette_refs]
    return Archetype(
        name=str(fm.get("name") or path.stem),
        pack=pack,
        description=str(fm.get("description") or ""),
        orientation=str(fm.get("orientation") or "any"),
        status=str(fm.get("status") or "draft"),
        since=str(fm.get("since") or ""),
        tags=[str(t) for t in tags],
        extrapolable=bool(fm.get("extrapolable", True)),
        palette_refs=[str(r) for r in palette_refs],
        body=body,
    )


def load_archetype(name: str, *, pack: str | None = None) -> Archetype:
    """Convenience: resolve + load an archetype by name."""
    from streamtex.core.artifacts.loaders import load_artifact
    from streamtex.core.artifacts.spec import ArtifactKind

    return load_artifact(name, ArtifactKind.ARCHETYPE, pack=pack)
