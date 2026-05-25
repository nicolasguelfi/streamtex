"""Typed loader dispatch for the generic artifact engine.

`load_artifact(name, kind, *, pack=None)` resolves the artifact via the engine
discovery layer, then loads its typed view (a `dataclass` or TypedDict-shaped
object) by delegating to the per-category module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from streamtex.core.artifacts.discovery import resolve_artifact
from streamtex.core.artifacts.spec import ArtifactKind


def load_artifact(
    name: str,
    kind: ArtifactKind,
    *,
    pack: str | None = None,
    stx_toml_path: Path | None = None,
) -> Any:
    """Load the typed Python view of an artifact.

    Args:
        name: artifact name (slug).
        kind: which category.
        pack: optional pack name filter (use to disambiguate when more than
            one pack declares the same name).
        stx_toml_path: optional project stx.toml path for discovery.

    Returns:
        The kind-specific dataclass/TypedDict (e.g. `Palette` for
        ArtifactKind.PALETTE). See per-category module for the exact type.

    Raises:
        ArtifactResolutionError: if the artifact is not found.
    """
    discovered = resolve_artifact(
        name,
        kind,
        prefer=[pack] if pack else None,
        stx_toml_path=stx_toml_path,
    )
    if kind == ArtifactKind.PALETTE:
        from streamtex.core.artifacts.palette import load_palette_from_path

        return load_palette_from_path(discovered.path, pack=discovered.pack)
    if kind == ArtifactKind.AI_PROMPT:
        from streamtex.core.artifacts.ai_prompt import load_ai_prompt_from_path

        return load_ai_prompt_from_path(discovered.path, pack=discovered.pack)
    raise NotImplementedError(
        f"load_artifact does not yet support kind={kind.value!r}; "
        "the per-category loader has not been registered."
    )
