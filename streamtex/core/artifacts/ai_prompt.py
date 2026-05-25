"""AI prompt artifact — prefix + per-orientation suffixes as plain text.

An AI prompt lives at `<pack>/ai_prompts/<name>/`:

    ai_prompts/
    └── scene_generation/
        ├── prefix.txt              (required)
        ├── suffix-landscape.txt    (≥ 1 required across landscape/portrait/square)
        ├── suffix-portrait.txt
        └── suffix-square.txt

The Python view (`AIPrompt`) exposes:

* `prefix: str` — the canonical context paragraph.
* `suffixes: dict[str, str]` — keyed by orientation ("landscape", "portrait",
  "square"). At least one key is guaranteed by validation.

Validation codes: APV001–APV010 (`AI prompt validation`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from streamtex.core.validation import ValidationIssue

_SUPPORTED_ORIENTATIONS: tuple[str, ...] = ("landscape", "portrait", "square")
_SUFFIX_RE = re.compile(r"^suffix-(?P<orient>[a-z]+)\.txt$")


@dataclass(frozen=True)
class AIPrompt:
    """Typed view of an AI prompt artifact."""

    name: str
    pack: str
    prefix: str
    suffixes: dict[str, str] = field(default_factory=dict)

    def compose(self, *, orientation: str = "landscape", scene: str = "") -> str:
        """Assemble a complete prompt: prefix + scene + suffix(orientation)."""
        if orientation not in self.suffixes:
            available = ", ".join(sorted(self.suffixes)) or "(none)"
            raise KeyError(
                f"AI prompt {self.pack}:{self.name}: orientation "
                f"{orientation!r} not declared. Available: {available}"
            )
        parts = [self.prefix.strip()]
        if scene:
            parts.append(scene.strip())
        parts.append(self.suffixes[orientation].strip())
        return "\n\n".join(parts)


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_ai_prompt(path: Path) -> list[ValidationIssue]:
    """Run validation checks on a single AI prompt directory.

    APV001 — directory exists
    APV002 — `prefix.txt` present and non-empty
    APV003 — at least one `suffix-<orientation>.txt` present
    APV004 — every suffix orientation is in the supported set
    APV005 — no empty suffix file
    APV006 — no unknown files at the artifact root (warning)
    """
    issues: list[ValidationIssue] = []
    if not path.exists() or not path.is_dir():
        return [_issue("APV001", "error", path, "AI prompt directory not found")]

    prefix_path = path / "prefix.txt"
    if not prefix_path.exists() or not prefix_path.is_file():
        issues.append(_issue("APV002", "error", path, "prefix.txt is required"))
    else:
        try:
            content = prefix_path.read_text(encoding="utf-8").strip()
            if not content:
                issues.append(_issue("APV002", "error", prefix_path, "prefix.txt is empty"))
        except Exception as exc:
            issues.append(_issue("APV002", "error", prefix_path, f"unreadable: {exc}"))

    found_orientations: list[str] = []
    for child in sorted(path.iterdir()):
        if child.name == "prefix.txt":
            continue
        m = _SUFFIX_RE.match(child.name)
        if m:
            orient = m.group("orient")
            if orient not in _SUPPORTED_ORIENTATIONS:
                issues.append(
                    _issue(
                        "APV004",
                        "error",
                        child,
                        f"unsupported orientation {orient!r}; supported: "
                        f"{', '.join(_SUPPORTED_ORIENTATIONS)}",
                    )
                )
                continue
            found_orientations.append(orient)
            try:
                if not child.read_text(encoding="utf-8").strip():
                    issues.append(_issue("APV005", "error", child, "suffix file is empty"))
            except Exception as exc:
                issues.append(_issue("APV005", "error", child, f"unreadable: {exc}"))
        else:
            issues.append(
                _issue(
                    "APV006",
                    "warning",
                    child,
                    f"unexpected file {child.name!r} in AI prompt directory",
                )
            )

    if not found_orientations:
        issues.append(
            _issue(
                "APV003",
                "error",
                path,
                "at least one suffix-<orientation>.txt is required "
                f"({', '.join(_SUPPORTED_ORIENTATIONS)})",
            )
        )

    return issues


def load_ai_prompt_from_path(path: Path, *, pack: str = "") -> AIPrompt:
    """Parse an AI prompt directory into a typed `AIPrompt` dataclass.

    Raises:
        ValueError: if validation finds blocking errors.
    """
    issues = validate_ai_prompt(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid AI prompt at {path}:\n{joined}")

    prefix = (path / "prefix.txt").read_text(encoding="utf-8").strip()
    suffixes: dict[str, str] = {}
    for child in sorted(path.iterdir()):
        m = _SUFFIX_RE.match(child.name)
        if not m:
            continue
        orient = m.group("orient")
        if orient in _SUPPORTED_ORIENTATIONS:
            suffixes[orient] = child.read_text(encoding="utf-8").strip()
    return AIPrompt(name=path.name, pack=pack, prefix=prefix, suffixes=suffixes)


def load_ai_prompt(name: str, *, pack: str | None = None) -> AIPrompt:
    """Convenience: resolve + load an AI prompt by name."""
    from streamtex.core.artifacts.loaders import load_artifact
    from streamtex.core.artifacts.spec import ArtifactKind

    return load_artifact(name, ArtifactKind.AI_PROMPT, pack=pack)
