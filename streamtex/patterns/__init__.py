"""Public API for the streamtex-patterns subsystem.

This package implements the business logic behind ``stx patterns ...``
commands.  The CLI adapter lives in :mod:`streamtex.cli.patterns_cmd`.

Exposes:
    - The exception hierarchy used across all pattern operations.
    - Public dataclasses for resolved sources, presets, manifest records,
      and drift reports.
    - The schema version of ``.patterns-meta.json``.
"""

from __future__ import annotations

__all__ = [
    "__version_schema__",
    "PatternError",
    "SourceNotFoundError",
    "PresetError",
    "ManifestError",
    "ValidationError",
    "DriftError",
    "MetaError",
]

__version_schema__: int = 1
"""Schema version embedded in ``.patterns-meta.json``."""


# --- Exception hierarchy ---------------------------------------------------

class PatternError(Exception):
    """Base class for all errors raised by the patterns subsystem."""


class SourceNotFoundError(PatternError):
    """Raised when the patterns source repo cannot be resolved (R4 exhausted)."""


class PresetError(PatternError):
    """Raised when a preset is malformed, missing, or has cyclic ``extends``."""


class ManifestError(PatternError):
    """Raised when ``manifest.toml`` or pattern frontmatter cannot be parsed."""


class MetaError(PatternError):
    """Raised when ``.patterns-meta.json`` is missing or malformed."""


class ValidationError(PatternError):
    """Raised when a pattern file fails A2 validation.

    Attributes:
        name: Pattern name (file stem).
        issues: Concrete blocking issues found during validation.
    """

    def __init__(self, name: str, issues: list[str]) -> None:
        self.name = name
        self.issues = list(issues)
        super().__init__(f"{name}: {len(self.issues)} issue(s)")


class DriftError(PatternError):
    """Raised when install/update detects drift that cannot be safely resolved.

    Attributes:
        name: Pattern name involved.
        action_hint: Suggested CLI action for the user.
    """

    def __init__(self, name: str, action_hint: str) -> None:
        self.name = name
        self.action_hint = action_hint
        super().__init__(f"drift detected for '{name}': {action_hint}")
