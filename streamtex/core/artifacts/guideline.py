"""Guideline artifact — markdown spec with R-numbered rules.

A guideline captures opinionated rules that apply to components, archetypes,
or projects (e.g. "R1 — one idea per slide", "R7 — center via parent block").
Distinct from a *project blueprint* (which is pure AI guidance for scaffolding):
a guideline is **opposable** — agents must respect it and humans cite it.

Filesystem convention: ``<pack>/guidelines/<name>.md``

Frontmatter schema:

    ---
    name: graphic-line
    description: GSE visual identity spec
    rules: [R1, R2, R7, R11, R12, R13]
    applies_to: [components, archetypes, projects]
    since: 2026-05-05
    ---

Validation codes: GLV001-GLV010 (guideline validation).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from streamtex.core.artifacts._frontmatter import split_frontmatter
from streamtex.core.validation import ValidationIssue

_REQUIRED_FIELDS = ("name", "description", "since")
_VALID_APPLIES_TO = {"components", "archetypes", "projects", "kits", "design_systems"}


@dataclass(frozen=True)
class Guideline:
    """Typed view of a guideline artifact."""

    name: str
    pack: str
    description: str
    since: str
    rules: list[str] = field(default_factory=list)
    applies_to: list[str] = field(default_factory=list)
    body: str = ""


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_guideline(path: Path) -> list[ValidationIssue]:
    """Run validation checks on a single guideline markdown file.

    GLV001 — file readable
    GLV002 — has YAML frontmatter (opens with ---)
    GLV003 — required fields present
    GLV004 — `applies_to` items in the supported set (warning if not)
    GLV005 — `rules` items are R-prefixed identifiers (warning if not)
    GLV006 — body is non-trivial (≥ 200 characters)
    """
    issues: list[ValidationIssue] = []
    if not path.exists() or not path.is_file():
        return [_issue("GLV001", "error", path, "guideline file not found")]
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [_issue("GLV001", "error", path, f"unreadable: {exc}")]

    if not text.startswith("---"):
        issues.append(_issue("GLV002", "error", path, "missing YAML frontmatter"))
        return issues

    fm, body = split_frontmatter(text)
    if not fm:
        issues.append(_issue("GLV002", "error", path, "frontmatter is empty or malformed"))
        return issues

    for key in _REQUIRED_FIELDS:
        if key not in fm or fm[key] in (None, ""):
            issues.append(_issue("GLV003", "error", path, f"missing required field '{key}'"))

    applies_to = fm.get("applies_to") or []
    if isinstance(applies_to, list):
        for item in applies_to:
            if isinstance(item, str) and item not in _VALID_APPLIES_TO:
                issues.append(
                    _issue(
                        "GLV004",
                        "warning",
                        path,
                        f"applies_to item {item!r} not in canonical set "
                        f"{{{', '.join(sorted(_VALID_APPLIES_TO))}}}",
                    )
                )

    rules = fm.get("rules") or []
    if isinstance(rules, list):
        for r in rules:
            if isinstance(r, str) and not re.match(r"^R\d+[a-z]?$", r):
                issues.append(
                    _issue(
                        "GLV005",
                        "warning",
                        path,
                        f"rule id {r!r} does not match expected pattern 'R<digits>[<letter>]'",
                    )
                )

    if len(body.strip()) < 200:
        issues.append(_issue("GLV006", "warning", path, "guideline body suspiciously short (< 200 chars)"))

    return issues


def load_guideline_from_path(path: Path, *, pack: str = "") -> Guideline:
    """Parse a guideline markdown file into a typed `Guideline` dataclass."""
    issues = validate_guideline(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid guideline at {path}:\n{joined}")

    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    rules = fm.get("rules") or []
    if isinstance(rules, str):
        rules = [rules]
    applies_to = fm.get("applies_to") or []
    if isinstance(applies_to, str):
        applies_to = [applies_to]
    return Guideline(
        name=str(fm.get("name") or path.stem),
        pack=pack,
        description=str(fm.get("description") or ""),
        since=str(fm.get("since") or ""),
        rules=[str(r) for r in rules],
        applies_to=[str(a) for a in applies_to],
        body=body,
    )


def load_guideline(name: str, *, pack: str | None = None) -> Guideline:
    """Convenience: resolve + load a guideline by name."""
    from streamtex.core.artifacts.loaders import load_artifact
    from streamtex.core.artifacts.spec import ArtifactKind

    return load_artifact(name, ArtifactKind.GUIDELINE, pack=pack)
