"""Integration recipe artifact — helper code per third-party framework.

A pack may ship integration recipes for frameworks beyond streamtex itself
(e.g. ``figma``, ``midjourney``). The recipe lives at
``<pack>/integrations/<framework>/`` and is a free-form directory. The only
contract for v0.2 is:

* A ``README.md`` describing how to use the recipe.
* Any number of supporting files (Python helpers, config templates, …).

Validation codes: INV001-INV005 (integration validation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from streamtex.core.validation import ValidationIssue


@dataclass(frozen=True)
class Integration:
    """Typed view of an integration recipe."""

    name: str  # framework name (e.g. "streamtex", "figma")
    pack: str
    root: Path
    readme: str = ""
    files: list[str] = field(default_factory=list)


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_integration(path: Path) -> list[ValidationIssue]:
    """Validate an integration recipe directory.

    INV001 — directory exists
    INV002 — README.md present
    INV003 — README.md non-empty
    """
    issues: list[ValidationIssue] = []
    if not path.exists() or not path.is_dir():
        return [_issue("INV001", "error", path, "integration directory not found")]

    readme = path / "README.md"
    if not readme.exists():
        issues.append(_issue("INV002", "error", path, "README.md is required"))
    else:
        try:
            content = readme.read_text(encoding="utf-8").strip()
            if not content:
                issues.append(_issue("INV003", "warning", readme, "README.md is empty"))
        except Exception as exc:
            issues.append(_issue("INV003", "error", readme, f"unreadable: {exc}"))

    return issues


def load_integration_from_path(path: Path, *, pack: str = "") -> Integration:
    """Parse an integration directory into an Integration record."""
    issues = validate_integration(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid integration at {path}:\n{joined}")

    readme_path = path / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    files = [p.name for p in sorted(path.iterdir()) if p.is_file()]
    return Integration(name=path.name, pack=pack, root=path, readme=readme_text, files=files)
