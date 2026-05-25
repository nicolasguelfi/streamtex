"""Shared types for the generic artifact engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol, runtime_checkable


class ArtifactKind(str, Enum):
    """Supported artifact categories under `[pack.data]` (manifest 0.2+)."""

    PALETTE = "palette"
    AI_PROMPT = "ai_prompt"
    ARCHETYPE = "archetype"
    GUIDELINE = "guideline"
    SKILL = "skill"
    AGENT = "agent"
    ASSET = "asset"
    INTEGRATION = "integration"


# Per-kind filesystem conventions: (subdir, file_extension OR None for dirs)
KIND_FS: dict[ArtifactKind, tuple[str, str | None]] = {
    ArtifactKind.PALETTE: ("palettes", ".json"),
    ArtifactKind.AI_PROMPT: ("ai_prompts", None),       # subdir per prompt
    ArtifactKind.ARCHETYPE: ("archetypes", ".md"),
    ArtifactKind.GUIDELINE: ("guidelines", ".md"),
    ArtifactKind.SKILL: ("skills", ".md"),
    ArtifactKind.AGENT: ("agents", ".md"),
    ArtifactKind.ASSET: ("assets", None),               # whole dir + _manifest.toml
    ArtifactKind.INTEGRATION: ("integrations", None),   # subdir per framework
}


# Per-kind manifest keys under [pack.data]
KIND_MANIFEST_KEY: dict[ArtifactKind, str] = {
    ArtifactKind.PALETTE: "palettes",
    ArtifactKind.AI_PROMPT: "ai_prompts",
    ArtifactKind.ARCHETYPE: "archetypes",
    ArtifactKind.GUIDELINE: "guidelines",
    ArtifactKind.SKILL: "skills",
    ArtifactKind.AGENT: "agents",
    ArtifactKind.ASSET: "assets",
    ArtifactKind.INTEGRATION: "integrations",
}


@runtime_checkable
class ArtifactSpec(Protocol):
    """Minimal common shape of a typed artifact loaded from disk.

    Each category extends this with its own fields (palette has `colors`,
    archetype has `composition`, etc.).
    """

    name: str
    pack: str
    kind: ArtifactKind
    since: str  # ISO date "YYYY-MM-DD"


@dataclass(frozen=True)
class DiscoveredArtifact:
    """Uniform record returned by `discover_artifacts`.

    Carries enough metadata to locate the artifact on disk without yet loading
    its content — keeps discovery cheap and side-effect-free.
    """

    name: str
    kind: ArtifactKind
    pack: str
    path: Path

    def __repr__(self) -> str:
        return f"DiscoveredArtifact({self.pack}:{self.name}, kind={self.kind.value})"
