"""Validation dispatch for the generic artifact engine.

`validate_artifact(path, kind)` dispatches on the kind to the per-category
validator. Each per-category validator is owned by its sibling module
(`palette.py::validate_palette`, etc.) and returns a list of
`ValidationIssue` from `streamtex.core.validation`.
"""

from __future__ import annotations

from pathlib import Path

from streamtex.core.artifacts.spec import ArtifactKind
from streamtex.core.validation import ValidationIssue


def validate_artifact(path: Path, kind: ArtifactKind) -> list[ValidationIssue]:
    """Validate a single artifact at `path`, dispatching on `kind`.

    Lazy imports per-category modules so adding a new kind only touches that
    module + the spec enum + this dispatch table.
    """
    if kind == ArtifactKind.PALETTE:
        from streamtex.core.artifacts.palette import validate_palette

        return validate_palette(path)
    if kind == ArtifactKind.AI_PROMPT:
        from streamtex.core.artifacts.ai_prompt import validate_ai_prompt

        return validate_ai_prompt(path)
    if kind == ArtifactKind.ARCHETYPE:
        from streamtex.core.artifacts.archetype import validate_archetype

        return validate_archetype(path)
    if kind == ArtifactKind.GUIDELINE:
        from streamtex.core.artifacts.guideline import validate_guideline

        return validate_guideline(path)
    if kind == ArtifactKind.SKILL:
        from streamtex.core.artifacts.skill import validate_skill

        return validate_skill(path)
    if kind == ArtifactKind.AGENT:
        from streamtex.core.artifacts.agent import validate_agent

        return validate_agent(path)
    if kind == ArtifactKind.ASSET:
        from streamtex.core.artifacts.asset import validate_asset

        return validate_asset(path)
    if kind == ArtifactKind.INTEGRATION:
        from streamtex.core.artifacts.integration import validate_integration

        return validate_integration(path)
    return []
