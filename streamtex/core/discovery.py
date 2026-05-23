"""Discovery: enumerate packs / components / kits at runtime.

Two layers of discovery cooperate:

* `entry_points()` — Python's standard mechanism. Packs declare a
  `streamtex.packs` entry point pointing at their root module.
* `stx.toml` `[[packs]]` — the project's explicit declaration; the order of
  entries determines default resolution priority (overridable via
  `[resolution].prefer`).

The five lifecycle states (§5.6bis) — Nominal, Drift install, Indirect,
Manifest broken, Collision — are surfaced via the PR002/PR003/PR004 error
codes raised here.
"""

from __future__ import annotations

import importlib
import sys
import tomllib
from dataclasses import dataclass, field
from importlib import metadata as _metadata
from pathlib import Path
from types import ModuleType
from typing import Any

from streamtex.core import contracts

# ---------------------------------------------------------------------------
# Exceptions (§28.1 hierarchy)
# ---------------------------------------------------------------------------


class ReuseArchitectureError(Exception):
    """Base error for the reuse architecture subsystem.

    Subclasses carry a `code` attribute that maps to the documented error
    codes (PR001-PR004 for pack resolution, PV* for manifest, BV* for
    bundles).
    """

    code: str = "RA000"


class PackResolutionError(ReuseArchitectureError):
    code = "PR000"


class KitResolutionError(ReuseArchitectureError):
    code = "PR000"


class PackManifestError(ReuseArchitectureError):
    code = "PR003"


class ComponentValidationError(ReuseArchitectureError):
    code = "CV000"


class BundleMissingError(ReuseArchitectureError):
    code = "BV001"


# ---------------------------------------------------------------------------
# Discovered artifacts
# ---------------------------------------------------------------------------


@dataclass
class DiscoveredArtifact:
    pack_name: str
    artifact_type: str  # component | design_system | cli_template | project_blueprint | kit
    name: str
    module: ModuleType | None = None
    path: Path | None = None


@dataclass
class DiscoveredPack:
    """Result of discover_packs — describes a pack's full lifecycle state."""

    name: str
    state: str  # nominal | drift_install | indirect | manifest_broken | collision
    declared: bool
    installed: bool
    manifest: contracts.PackManifest | None = None
    entry_point_module: str | None = None
    stx_toml_entry: contracts.StxTomlPackEntry | None = None
    indirect: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class TraceEntry:
    """Audit trail entry surfaced via `stx pack list --trace`.

    Each transition is recorded as a TraceEntry so users can diagnose why a
    pack ended up in a given lifecycle state.
    """

    pack_name: str
    transition: str  # declared | installed | manifest_ok | included | skipped
    detail: str = ""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _read_stx_toml(stx_toml_path: Path | None) -> dict[str, Any]:
    if stx_toml_path is None or not stx_toml_path.exists():
        return {}
    with stx_toml_path.open("rb") as fh:
        return tomllib.load(fh) or {}


def _stx_toml_packs(data: dict[str, Any]) -> list[contracts.StxTomlPackEntry]:
    raw = data.get("packs") or []
    if isinstance(raw, list):
        return [entry for entry in raw if isinstance(entry, dict)]
    return []


def _entry_points_by_pack() -> dict[str, list[_metadata.EntryPoint]]:
    grouped: dict[str, list[_metadata.EntryPoint]] = {}
    try:
        eps = _metadata.entry_points(group="streamtex.packs")
    except TypeError:  # Python < 3.10 API fallback
        eps = _metadata.entry_points().get("streamtex.packs", [])  # type: ignore[union-attr]
    for ep in eps:
        grouped.setdefault(ep.name, []).append(ep)
    return grouped


def _import_pack_module(module_name: str) -> ModuleType:
    try:
        return importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001 — propagated as ReuseArchitectureError
        err = PackManifestError(f"Failed to import pack module '{module_name}': {exc}")
        err.code = "PR003"
        raise err from exc


def _load_pack_manifest(mod: ModuleType) -> contracts.PackManifest:
    base = Path(getattr(mod, "__file__", "")).resolve().parent
    manifest_path = base / "_pack_manifest.toml"
    if not manifest_path.exists():
        err = PackManifestError(f"Pack '{mod.__name__}' has no _pack_manifest.toml.")
        err.code = "PR003"
        raise err
    with manifest_path.open("rb") as fh:
        data = tomllib.load(fh)
    return data  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def discover_packs(
    stx_toml_path: Path | None = None,
    *,
    trace: list[TraceEntry] | None = None,
) -> list[DiscoveredPack]:
    """Enumerate packs visible to the current project.

    The five lifecycle states (§5.6bis) are surfaced as ``state`` values:

    * ``nominal`` — declared in stx.toml AND installed AND manifest OK.
    * ``drift_install`` — declared but no matching entry point. PR002.
    * ``indirect`` — entry point present but not declared in stx.toml.
    * ``manifest_broken`` — installed but manifest fails to load. PR003.
    * ``collision`` — same name declared more than once. PR004 (raised).
    """
    data = _read_stx_toml(stx_toml_path)
    declared_entries = _stx_toml_packs(data)
    ep_groups = _entry_points_by_pack()

    # Detect collisions first
    for name, eps in ep_groups.items():
        if len(eps) > 1:
            err = PackResolutionError(
                f"Pack name '{name}' is declared by {len(eps)} packages "
                "in entry-points. Set [resolution].prefer in stx.toml to disambiguate."
            )
            err.code = "PR004"
            raise err

    result: list[DiscoveredPack] = []
    seen_names: set[str] = set()

    for entry in declared_entries:
        name = entry.get("name") or ""
        if not name:
            # git / pypi packs may omit name — derive from ref when possible
            ref = entry.get("ref") or entry.get("constraint") or "<unnamed>"
            name = ref.rstrip("/").split("/")[-1]
        if trace is not None:
            trace.append(TraceEntry(name, "declared"))
        seen_names.add(name)

        eps = ep_groups.get(name, [])
        if not eps:
            result.append(
                DiscoveredPack(
                    name=name,
                    state="drift_install",
                    declared=True,
                    installed=False,
                    stx_toml_entry=entry,
                    issues=[f"PR002: entry point for pack '{name}' not found in environment."],
                )
            )
            if trace is not None:
                trace.append(TraceEntry(name, "skipped", "no entry point"))
            continue

        ep = eps[0]
        try:
            mod = _import_pack_module(ep.value)
            manifest = _load_pack_manifest(mod)
        except PackManifestError as err:
            result.append(
                DiscoveredPack(
                    name=name,
                    state="manifest_broken",
                    declared=True,
                    installed=True,
                    entry_point_module=ep.value,
                    stx_toml_entry=entry,
                    issues=[f"{err.code}: {err}"],
                )
            )
            if trace is not None:
                trace.append(TraceEntry(name, "skipped", "manifest broken"))
            continue

        result.append(
            DiscoveredPack(
                name=name,
                state="nominal",
                declared=True,
                installed=True,
                manifest=manifest,
                entry_point_module=ep.value,
                stx_toml_entry=entry,
            )
        )
        if trace is not None:
            trace.append(TraceEntry(name, "installed"))
            trace.append(TraceEntry(name, "manifest_ok"))
            trace.append(TraceEntry(name, "included"))

    # Indirect packs: entry point present, not declared in stx.toml
    for ep_name, eps in ep_groups.items():
        if ep_name in seen_names:
            continue
        ep = eps[0]
        try:
            mod = _import_pack_module(ep.value)
            manifest = _load_pack_manifest(mod)
        except PackManifestError:
            continue
        result.append(
            DiscoveredPack(
                name=ep_name,
                state="indirect",
                declared=False,
                installed=True,
                indirect=True,
                manifest=manifest,
                entry_point_module=ep.value,
            )
        )
        if trace is not None:
            trace.append(TraceEntry(ep_name, "installed", "indirect"))

    return result


def get_primary_local_pack(stx_toml_path: Path | None = None) -> dict[str, Any] | None:
    """Return the [[packs]] entry with type='local' and primary=true, or None.

    Raises PackResolutionError(PR005) if 2+ entries have primary=true.
    """
    data = _read_stx_toml(stx_toml_path)
    locals_primary = [
        entry
        for entry in _stx_toml_packs(data)
        if entry.get("type") == "local" and entry.get("primary") is True
    ]
    if len(locals_primary) > 1:
        err = PackResolutionError(
            f"Found {len(locals_primary)} local packs with primary=true; expected exactly one."
        )
        err.code = "PR005"
        raise err
    return locals_primary[0] if locals_primary else None


def discover_components(packs: list[DiscoveredPack]) -> list[DiscoveredArtifact]:
    """Enumerate every component visible across the given packs."""
    out: list[DiscoveredArtifact] = []
    for pack in packs:
        if pack.state not in ("nominal", "indirect"):
            continue
        mod_name = pack.entry_point_module
        if not mod_name:
            continue
        try:
            mod = importlib.import_module(mod_name)
        except Exception:  # noqa: BLE001
            continue
        components_dir = Path(getattr(mod, "__file__", "")).resolve().parent / "components"
        if not components_dir.exists():
            continue
        for py in sorted(components_dir.glob("*.py")):
            if py.name == "__init__.py":
                continue
            comp_module_name = f"{mod_name}.components.{py.stem}"
            try:
                comp_mod = importlib.import_module(comp_module_name)
            except Exception:  # noqa: BLE001
                continue
            meta = getattr(comp_mod, "__component_meta__", None)
            name = meta.get("name") if isinstance(meta, dict) else py.stem
            out.append(
                DiscoveredArtifact(
                    pack_name=pack.name,
                    artifact_type="component",
                    name=name or py.stem,
                    module=comp_mod,
                    path=py,
                )
            )
    return out


def resolve_component(
    name: str,
    packs: list[DiscoveredPack],
    prefer: list[str] | None = None,
) -> DiscoveredArtifact:
    """Resolve a component name using the given pack list and prefer order.

    `prefer` is a sort key, not a filter (§5.6bis). Packs absent from `prefer`
    keep their relative order from `packs`.
    """
    artifacts = [a for a in discover_components(packs) if a.name == name]
    if not artifacts:
        err = PackResolutionError(f"Component '{name}' not found in any installed pack.")
        err.code = "PR006"
        raise err

    if prefer:
        prefer_index = {pack_name: idx for idx, pack_name in enumerate(prefer)}

        def sort_key(art: DiscoveredArtifact) -> tuple[int, int]:
            primary = prefer_index.get(art.pack_name, len(prefer))
            secondary = next(
                (idx for idx, p in enumerate(packs) if p.name == art.pack_name), 999
            )
            return (primary, secondary)

        artifacts.sort(key=sort_key)

    return artifacts[0]


def get_bundle_attr(bundle: Any, attr_name: str, component_name: str) -> Any:
    """Access ``bundle.<attr_name>`` with an enriched error message on miss.

    Components should use this in place of bare getattr() so that, when a
    runtime swap of the design system invalidates a bundle reference, the
    user gets a clear diagnostic pointing them at `stx validate`.
    """
    if not hasattr(bundle, attr_name):
        err = BundleMissingError(
            f"Component '{component_name}' needs bundle attribute "
            f"'{attr_name}' but active design system doesn't provide it. "
            "Run `stx validate` to diagnose."
        )
        err.code = "BV001"
        raise err
    return getattr(bundle, attr_name)


# Reserved for future use — currently a stub
def reload_pack(name: str) -> None:  # pragma: no cover — intentionally minimal
    """Force re-import of a pack's modules. Used by `stx pack sync`."""
    prefix = f"{name}."
    for module_name in list(sys.modules):
        if module_name == name or module_name.startswith(prefix):
            del sys.modules[module_name]


__all__ = [
    "ReuseArchitectureError",
    "PackResolutionError",
    "KitResolutionError",
    "PackManifestError",
    "ComponentValidationError",
    "BundleMissingError",
    "DiscoveredArtifact",
    "DiscoveredPack",
    "TraceEntry",
    "discover_packs",
    "discover_components",
    "resolve_component",
    "get_primary_local_pack",
    "get_bundle_attr",
    "reload_pack",
]
