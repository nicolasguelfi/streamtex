"""Agent artifact — Claude Code agent definition, pack-scoped.

Same shape as a skill: markdown with Claude Code frontmatter. The semantic
difference is purely consumer-side — Claude Code interprets agents and
skills differently. From the pack's point of view, both are pack-scoped
markdown blobs with ``name`` + ``description``.

Filesystem convention: ``<pack>/agents/<name>.md``

Validation codes: AGV001-AGV010 (agent validation).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from streamtex.core.artifacts._frontmatter import split_frontmatter
from streamtex.core.validation import ValidationIssue

_REQUIRED_FIELDS = ("name", "description")


@dataclass(frozen=True)
class Agent:
    """Typed view of a Claude Code agent artifact."""

    name: str
    pack: str
    description: str
    body: str

    @property
    def namespaced_name(self) -> str:
        return f"{self.pack}:{self.name}"

    @property
    def install_filename(self) -> str:
        pack_slug = self.pack.replace("streamtex-pack-", "").replace("-", "_")
        return f"{pack_slug}__{self.name}.md"


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_agent(path: Path) -> list[ValidationIssue]:
    """Run validation checks on a single agent markdown file.

    AGV001 — file readable
    AGV002 — has YAML frontmatter
    AGV003 — required fields present
    AGV004 — body is non-trivial (≥ 100 chars)
    """
    issues: list[ValidationIssue] = []
    if not path.exists() or not path.is_file():
        return [_issue("AGV001", "error", path, "agent file not found")]
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [_issue("AGV001", "error", path, f"unreadable: {exc}")]

    if not text.startswith("---"):
        issues.append(_issue("AGV002", "error", path, "missing YAML frontmatter"))
        return issues

    fm, body = split_frontmatter(text)
    for key in _REQUIRED_FIELDS:
        if key not in fm or fm[key] in (None, ""):
            issues.append(_issue("AGV003", "error", path, f"missing required field '{key}'"))

    if len(body.strip()) < 100:
        issues.append(_issue("AGV004", "warning", path, "agent body suspiciously short (< 100 chars)"))

    return issues


def load_agent_from_path(path: Path, *, pack: str = "") -> Agent:
    """Parse an agent markdown file into a typed `Agent` dataclass."""
    issues = validate_agent(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid agent at {path}:\n{joined}")

    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    return Agent(
        name=str(fm.get("name") or path.stem),
        pack=pack,
        description=str(fm.get("description") or ""),
        body=body,
    )


def load_agent(name: str, *, pack: str | None = None) -> Agent:
    """Convenience: resolve + load an agent by name."""
    from streamtex.core.artifacts.loaders import load_artifact
    from streamtex.core.artifacts.spec import ArtifactKind

    return load_artifact(name, ArtifactKind.AGENT, pack=pack)
