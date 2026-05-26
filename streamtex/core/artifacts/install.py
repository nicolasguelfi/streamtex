"""Lifecycle hooks: install pack-shipped skills/agents into a project's
`.claude/custom/` directory.

Called by:
- `stx artifact install <name> --kind skill|agent` (manual install)
- `stx pack add <pack>` (Phase 4 — auto with confirmation prompt)

Design constraints (EAR-4):
- Confirmation prompt by default ; flag `--yes` to skip
- Namespaced filename `<pack_slug>__<name>.md` to avoid collisions
- Never read-only — users may edit their installed copy
- Symmetric uninstall via `stx pack remove`
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from streamtex.core.artifacts.discovery import discover_artifacts, resolve_artifact
from streamtex.core.artifacts.spec import ArtifactKind


@dataclass
class InstallReport:
    """Result of installing one Claude artifact into a project."""

    pack: str
    name: str
    kind: ArtifactKind
    source: Path
    destination: Path
    action: str  # "installed" | "skipped" | "overwritten"


def _target_subdir(kind: ArtifactKind) -> str:
    if kind == ArtifactKind.SKILL:
        return "skills"
    if kind == ArtifactKind.AGENT:
        return "agents"
    raise ValueError(f"Unsupported kind for project install: {kind!r}")


def _pack_slug(pack_name: str) -> str:
    return pack_name.replace("streamtex-pack-", "").replace("-", "_")


def install_claude_artifact(
    name: str,
    kind: ArtifactKind,
    project_dir: Path,
    *,
    pack: str | None = None,
    overwrite: bool = False,
) -> InstallReport:
    """Copy one skill/agent into `<project_dir>/.claude/custom/<subdir>/`.

    Args:
        name: artifact slug.
        kind: must be SKILL or AGENT (other kinds are not installed in
            `.claude/custom/`).
        project_dir: project root containing (or about to contain) `.claude/`.
        pack: optional disambiguation when multiple packs ship the same name.
        overwrite: if False and target exists, skip (action="skipped").

    Returns:
        InstallReport describing what happened.
    """
    discovered = resolve_artifact(
        name, kind, prefer=[pack] if pack else None
    )
    subdir = _target_subdir(kind)
    pack_slug = _pack_slug(discovered.pack)
    target_dir = project_dir / ".claude" / "custom" / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{pack_slug}__{discovered.name}.md"

    action = "installed"
    if target.exists():
        if not overwrite:
            return InstallReport(
                pack=discovered.pack,
                name=discovered.name,
                kind=kind,
                source=discovered.path,
                destination=target,
                action="skipped",
            )
        action = "overwritten"

    target.write_bytes(discovered.path.read_bytes())
    return InstallReport(
        pack=discovered.pack,
        name=discovered.name,
        kind=kind,
        source=discovered.path,
        destination=target,
        action=action,
    )


def list_claude_artifacts_for_pack(pack_name: str) -> list[tuple[ArtifactKind, str]]:
    """Return all `(kind, name)` pairs for skills + agents shipped by a pack.

    Used by `stx pack add` (Phase 4) to know what to offer for install.
    """
    out: list[tuple[ArtifactKind, str]] = []
    for kind in (ArtifactKind.SKILL, ArtifactKind.AGENT):
        for art in discover_artifacts(kind, pack=pack_name):
            out.append((kind, art.name))
    return out


def uninstall_claude_artifact(
    pack_name: str,
    name: str,
    kind: ArtifactKind,
    project_dir: Path,
) -> bool:
    """Remove a previously installed pack-skill/agent from a project.

    Returns True if removed, False if file was not present.
    """
    pack_slug = _pack_slug(pack_name)
    target = project_dir / ".claude" / "custom" / _target_subdir(kind) / f"{pack_slug}__{name}.md"
    if target.exists():
        target.unlink()
        return True
    return False
