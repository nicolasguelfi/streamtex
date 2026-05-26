"""Discovery of artifacts across the installed pack ecosystem.

Walks the entry-points-registered packs, reads each pack's `_pack_manifest.toml`
to learn which categories it declares under `[pack.data]`, then enumerates the
artifact files/dirs on disk. No content is loaded at this stage.
"""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

from streamtex.core import discovery as _pack_discovery
from streamtex.core.artifacts.spec import (
    KIND_FS,
    KIND_MANIFEST_KEY,
    ArtifactKind,
    DiscoveredArtifact,
)


class ArtifactResolutionError(Exception):
    """Raised when `resolve_artifact` cannot pick a unique winner."""

    code: str = "AR000"


def _pack_root(pack: _pack_discovery.DiscoveredPack) -> Path | None:
    """Resolve the on-disk root of a discovered pack via its entry-point module."""
    module_name = pack.entry_point_module
    if not module_name:
        return None
    try:
        mod = importlib.import_module(module_name)
    except Exception:
        return None
    file = getattr(mod, "__file__", None)
    if not file:
        return None
    return Path(file).resolve().parent


def _read_pack_data_section(pack: _pack_discovery.DiscoveredPack) -> dict:
    """Return the `[pack.data]` table from the pack manifest, or empty dict.

    Format 0.1 packs (no [pack.data]) yield {} — they have no data-first
    artifacts to enumerate.
    """
    root = _pack_root(pack)
    if root is None:
        return {}
    manifest_path = root / "_pack_manifest.toml"
    if not manifest_path.exists():
        return {}
    try:
        data = tomllib.loads(manifest_path.read_text())
    except tomllib.TOMLDecodeError:
        return {}
    pack_table = data.get("pack", {})
    if isinstance(pack_table, dict):
        data_section = pack_table.get("data", {})
        if isinstance(data_section, dict):
            return data_section
    return {}


def _scan_pack_artifacts(
    pack: _pack_discovery.DiscoveredPack,
    kind: ArtifactKind,
) -> list[DiscoveredArtifact]:
    """Enumerate artifacts of `kind` declared by `pack`."""
    root = _pack_root(pack)
    if root is None:
        return []

    data_section = _read_pack_data_section(pack)
    manifest_key = KIND_MANIFEST_KEY[kind]
    declared = data_section.get(manifest_key, [])
    if not isinstance(declared, list):
        return []

    subdir_name, ext = KIND_FS[kind]
    subdir = root / subdir_name
    if not subdir.exists():
        return []

    out: list[DiscoveredArtifact] = []
    for entry in declared:
        if not isinstance(entry, str) or not entry:
            continue
        if ext is None:
            # Subdir-based artifact (ai_prompt, asset, integration)
            target = subdir / entry
            if target.exists() and target.is_dir():
                out.append(
                    DiscoveredArtifact(
                        name=entry, kind=kind, pack=pack.name, path=target
                    )
                )
            elif kind == ArtifactKind.ASSET and target.name == "assets":
                # Special case: assets/ as a whole, declared with "assets" or empty
                pass
        else:
            target = subdir / f"{entry}{ext}"
            if target.exists() and target.is_file():
                out.append(
                    DiscoveredArtifact(
                        name=entry, kind=kind, pack=pack.name, path=target
                    )
                )
    return out


def discover_artifacts(
    kind: ArtifactKind,
    *,
    pack: str | None = None,
    stx_toml_path: Path | None = None,
) -> list[DiscoveredArtifact]:
    """Enumerate all artifacts of `kind` from installed packs.

    Args:
        kind: which artifact category to enumerate.
        pack: optional pack name filter — return only artifacts from this pack.
        stx_toml_path: optional path to a project stx.toml to use for pack
            discovery (cf. `streamtex.core.discovery.discover_packs`).

    Returns:
        list of `DiscoveredArtifact`, possibly empty. Order: packs first by
        `stx.toml` order, then by alphabetical artifact name within each pack.
    """
    packs = _pack_discovery.discover_packs(stx_toml_path=stx_toml_path)
    out: list[DiscoveredArtifact] = []
    for p in packs:
        if pack is not None and p.name != pack:
            continue
        out.extend(_scan_pack_artifacts(p, kind))
    return out


def resolve_artifact(
    name: str,
    kind: ArtifactKind,
    *,
    prefer: list[str] | None = None,
    stx_toml_path: Path | None = None,
) -> DiscoveredArtifact:
    """Return the unique artifact `(kind, name)` honoring resolution preference.

    If multiple packs declare an artifact with the same name and kind, the
    `prefer` list (defaults to project stx.toml `[resolution].prefer`) decides;
    if none matches, the first-discovered wins.

    Raises:
        ArtifactResolutionError: if no artifact `(kind, name)` is found.
    """
    candidates = discover_artifacts(kind, stx_toml_path=stx_toml_path)
    matches = [c for c in candidates if c.name == name]
    if not matches:
        err = ArtifactResolutionError(
            f"No artifact of kind '{kind.value}' named '{name}' found across "
            f"installed packs."
        )
        err.code = "AR001"
        raise err
    if len(matches) == 1:
        return matches[0]
    if prefer:
        for preferred_pack in prefer:
            for m in matches:
                if m.pack == preferred_pack:
                    return m
    return matches[0]
