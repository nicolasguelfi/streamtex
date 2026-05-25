"""Generic artifact engine for StreamTeX packs (manifest format 0.2+).

A pack can ship multiple categories of reusable artifacts: data-first (palettes,
AI prompts), structured documentation (archetypes, guidelines), Claude Code
assets (skills, agents), binary resources (assets), and integration recipes for
third-party frameworks.

This module provides the **one** generic engine that all categories share:

* `ArtifactKind` — enum of supported categories.
* `DiscoveredArtifact` — uniform record returned by discovery.
* `discover_artifacts(kind, *, pack=None)` — enumerate across the installed
  pack ecosystem.
* `resolve_artifact(name, kind, *, prefer=None)` — pick one in case of
  cross-pack collision.
* `validate_artifact(path, kind)` — return ValidationIssue list for a single
  artifact file/dir.
* `load_artifact(name, kind, *, pack=None)` — return the typed Python view
  of an artifact (dispatches on kind).

Per-category contracts (TypedDict + validator + loader) live in sibling
modules: `palette.py`, `ai_prompt.py`, `archetype.py`, `guideline.py`,
`skill.py`, `agent.py`, `asset.py`, `integration.py`.

The engine is **additive** on top of the format-0.1 mechanism: packs without
a `[pack.data]` section in their manifest are unaffected.
"""

from streamtex.core.artifacts.spec import (
    ArtifactKind,
    ArtifactSpec,
    DiscoveredArtifact,
)
from streamtex.core.artifacts.discovery import (
    discover_artifacts,
    resolve_artifact,
)
from streamtex.core.artifacts.validation import validate_artifact
from streamtex.core.artifacts.loaders import load_artifact
from streamtex.core.artifacts.install import (
    InstallReport,
    install_claude_artifact,
    list_claude_artifacts_for_pack,
    uninstall_claude_artifact,
)

__all__ = [
    "ArtifactKind",
    "ArtifactSpec",
    "DiscoveredArtifact",
    "InstallReport",
    "discover_artifacts",
    "resolve_artifact",
    "validate_artifact",
    "load_artifact",
    "install_claude_artifact",
    "list_claude_artifacts_for_pack",
    "uninstall_claude_artifact",
]
