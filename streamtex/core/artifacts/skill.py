"""Skill artifact — Claude Code skill, pack-scoped.

A skill is a markdown file with Claude Code frontmatter (``name`` +
``description``) that ships inside a pack. At ``stx pack add <pack>``, the
skill is copied (with confirmation prompt) to the project's
``.claude/custom/skills/<pack>__<name>.md`` so the agent can discover it.

The namespace ``<pack>:<name>`` (or filename ``<pack>__<name>.md``) prevents
collisions across packs.

Filesystem convention: ``<pack>/skills/<name>.md``

Frontmatter schema:

    ---
    name: gse-author
    description: Skill helping authors write content in the GSE register
    ---

Validation codes: SKV001-SKV010 (skill validation).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from streamtex.core.artifacts._frontmatter import split_frontmatter
from streamtex.core.validation import ValidationIssue

_REQUIRED_FIELDS = ("name", "description")


@dataclass(frozen=True)
class Skill:
    """Typed view of a Claude Code skill artifact."""

    name: str
    pack: str
    description: str
    body: str

    @property
    def namespaced_name(self) -> str:
        """Globally unique slug used when installed into a project."""
        return f"{self.pack}:{self.name}"

    @property
    def install_filename(self) -> str:
        """Filename used when copied to ``.claude/custom/skills/``."""
        pack_slug = self.pack.replace("streamtex-pack-", "").replace("-", "_")
        return f"{pack_slug}__{self.name}.md"


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_skill(path: Path) -> list[ValidationIssue]:
    """Run validation checks on a single skill markdown file.

    SKV001 — file readable
    SKV002 — has YAML frontmatter
    SKV003 — required fields present
    SKV004 — body is non-trivial (≥ 100 chars)
    """
    issues: list[ValidationIssue] = []
    if not path.exists() or not path.is_file():
        return [_issue("SKV001", "error", path, "skill file not found")]
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [_issue("SKV001", "error", path, f"unreadable: {exc}")]

    if not text.startswith("---"):
        issues.append(_issue("SKV002", "error", path, "missing YAML frontmatter"))
        return issues

    fm, body = split_frontmatter(text)
    for key in _REQUIRED_FIELDS:
        if key not in fm or fm[key] in (None, ""):
            issues.append(_issue("SKV003", "error", path, f"missing required field '{key}'"))

    if len(body.strip()) < 100:
        issues.append(_issue("SKV004", "warning", path, "skill body suspiciously short (< 100 chars)"))

    return issues


def load_skill_from_path(path: Path, *, pack: str = "") -> Skill:
    """Parse a skill markdown file into a typed `Skill` dataclass."""
    issues = validate_skill(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid skill at {path}:\n{joined}")

    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    return Skill(
        name=str(fm.get("name") or path.stem),
        pack=pack,
        description=str(fm.get("description") or ""),
        body=body,
    )


def load_skill(name: str, *, pack: str | None = None) -> Skill:
    """Convenience: resolve + load a skill by name."""
    from streamtex.core.artifacts.loaders import load_artifact
    from streamtex.core.artifacts.spec import ArtifactKind

    return load_artifact(name, ArtifactKind.SKILL, pack=pack)
