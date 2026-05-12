"""Validate pattern files against the A2 spec.

Implements the PV001-PV020 family of rules (frontmatter completeness,
required sections, code skeleton parsing, optional cross-references).
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from .manifest import (
    ManifestError,
    parse_frontmatter,
    split_frontmatter,
)

logger = logging.getLogger(__name__)

REQUIRED_SECTIONS_DEFAULT: tuple[str, ...] = (
    "Visual",
    "Structure",
    "Styling rules",
    "Code skeleton",
    "When to use",
    "When NOT to use",
)

EXTRAPOLATION_SUBSECTIONS: tuple[str, ...] = ("INVARIANTS", "PARAMS", "INTERDITS")

_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_FENCED_PY_RE = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)
_BACKTICK_REF_RE = re.compile(r"`([a-z][a-z0-9_]+)`")


@dataclass(frozen=True)
class ValidationReport:
    """Outcome of validating a single pattern file."""

    name: str
    file: Path
    issues: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_sections(body: str) -> dict[str, str]:
    """Return a mapping ``{section_title: section_body_text}``."""
    matches = list(_SECTION_RE.finditer(body))
    sections: dict[str, str] = {}
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[title] = body[start:end]
    return sections


def _extract_python_blocks(text: str) -> list[str]:
    return [m.group(1) for m in _FENCED_PY_RE.finditer(text)]


def _check_python_skeleton(code: str) -> str | None:
    """Return None if *code* parses, else a short error message."""
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return f"line {exc.lineno}: {exc.msg}"
    return None


def _detect_pattern_refs(body: str) -> set[str]:
    """Heuristically detect snake_case references in backticks."""
    out: set[str] = set()
    for m in _BACKTICK_REF_RE.finditer(body):
        token = m.group(1)
        # Filter common Python builtins / function-call hints.
        if "_" in token and not token.endswith("_"):
            out.add(token)
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_file(
    path: Path,
    *,
    required_sections: tuple[str, ...] = REQUIRED_SECTIONS_DEFAULT,
    catalog: set[str] | None = None,
) -> ValidationReport:
    """Validate a single pattern file against the A2 contract."""
    issues: list[str] = []
    warnings: list[str] = []
    name = path.stem

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return ValidationReport(
            name=name, file=path, issues=(f"cannot read file: {exc}",), warnings=()
        )

    fm = None
    body = ""
    try:
        yaml, body = split_frontmatter(text)
        fm = parse_frontmatter(yaml)
        if fm.name != name:
            issues.append(
                f"frontmatter name {fm.name!r} != filename {name!r}"
            )
    except ManifestError as exc:
        issues.append(str(exc))

    sections = _extract_sections(body) if body else {}
    for required in required_sections:
        if required not in sections:
            issues.append(f"missing required section: {required}")

    if fm and fm.extrapolable:
        section = sections.get("Extrapolation rules", "")
        for sub in EXTRAPOLATION_SUBSECTIONS:
            if not re.search(rf"^###\s+{re.escape(sub)}\b", section, re.MULTILINE):
                issues.append(f"missing extrapolation subsection: {sub}")

    code_section = sections.get("Code skeleton", "")
    if code_section:
        blocks = _extract_python_blocks(code_section)
        if not blocks:
            issues.append("Code skeleton has no python fenced block")
        for code in blocks:
            err = _check_python_skeleton(code)
            if err:
                issues.append(f"code skeleton parse error: {err}")

    if fm and len(fm.description) > 100:
        warnings.append(
            f"description length {len(fm.description)} > 100"
        )

    if catalog and body:
        refs = _detect_pattern_refs(body)
        for ref in sorted(refs - catalog):
            warnings.append(f"reference to unknown pattern: {ref}")

    return ValidationReport(
        name=name,
        file=path,
        issues=tuple(issues),
        warnings=tuple(warnings),
    )


def validate_all(target: Path, **kwargs) -> list[ValidationReport]:
    """Validate every ``*.md`` pattern under *target* (non-recursive)."""
    reports: list[ValidationReport] = []
    target = Path(target)
    if not target.is_dir():
        return reports
    for path in sorted(target.iterdir()):
        if not path.is_file() or path.suffix != ".md":
            continue
        if path.name.startswith("_"):
            continue
        reports.append(validate_file(path, **kwargs))
    return reports
