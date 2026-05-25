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
    # Other kinds will be added in subsequent phases (archetype, guideline,
    # skill, agent, asset, integration). For now return empty — the file
    # exists check is done at discovery time.
    return []
