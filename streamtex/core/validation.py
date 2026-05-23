"""Validation API for the reuse architecture.

Each validate_* function returns a list of ValidationIssue objects (empty list
means "fully conformant"). Error codes follow the families documented in
PLAN.md §5.5 and §28.1:

* CV001-CV011  — component validation
* DV001-DV006  — design system validation
* KV001-KV005  — kit validation
* PV001-PV010  — pack validation
* BV001-BV002  — bundles_required cross-check

Severity is "error", "warning" or "info"; callers usually surface errors only.
"""

from __future__ import annotations

import inspect
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

from streamtex.core.contracts import (
    REQUIRED_BUNDLES,
    ComponentMeta,
    DesignSystemProtocol,
)

Severity = Literal["error", "warning", "info"]


@dataclass
class ValidationIssue:
    code: str
    severity: Severity
    location: str
    message: str

    def is_error(self) -> bool:
        return self.severity == "error"


_REQUIRED_DOCSTRING_SECTIONS: tuple[str, ...] = (
    "Visual",
    "Structure",
    "Styling rules",
    "Extrapolation rules",
    "When to use",
    "When NOT to use",
    "Design system bundles required",
)

_EXTRAPOLATION_SUBSECTIONS: tuple[str, ...] = (
    "INVARIANTS",
    "PARAMS",
    "INTERDITS",
)


def _has_section(docstring: str, name: str) -> bool:
    pattern = rf"(?im)^\s*#+\s*{re.escape(name)}\b"
    return re.search(pattern, docstring) is not None


def _count_bullets_after(docstring: str, name: str) -> int:
    """Crude bullet counter for the section identified by name."""
    pattern = rf"(?im)^\s*#+\s*{re.escape(name)}\b[^\n]*\n(.+?)(?=^\s*#+\s|\Z)"
    m = re.search(pattern, docstring, re.DOTALL)
    if not m:
        return 0
    body = m.group(1)
    return len(re.findall(r"(?m)^\s*[-*]\s+\S", body))


def validate_component(mod: ModuleType) -> list[ValidationIssue]:
    """Verify a Python module conforms to the component contract.

    See PLAN.md §5.5 for the full check list. Returns [] for a clean module.
    """
    issues: list[ValidationIssue] = []
    location_base = getattr(mod, "__name__", "<unknown_module>")

    # CV001 — module docstring present
    doc = getattr(mod, "__doc__", None)
    if not doc or not doc.strip():
        issues.append(
            ValidationIssue(
                "CV001",
                "error",
                location_base,
                "Module docstring is missing (required for component spec).",
            )
        )
        doc = ""

    # CV002 — required sections
    for section in _REQUIRED_DOCSTRING_SECTIONS:
        if not _has_section(doc, section):
            issues.append(
                ValidationIssue(
                    "CV002",
                    "error",
                    location_base,
                    f"Docstring section '## {section}' is missing.",
                )
            )

    # CV004 — __component_meta__ present and well-shaped
    meta: Any = getattr(mod, "__component_meta__", None)
    if not isinstance(meta, dict):
        issues.append(
            ValidationIssue(
                "CV004",
                "error",
                location_base,
                "__component_meta__ missing or not a dict.",
            )
        )
        return issues

    required_meta_keys = (
        "name",
        "description",
        "tags",
        "extrapolable",
        "since",
        "bundles_required",
        "granularity",
    )
    for key in required_meta_keys:
        if key not in meta:
            issues.append(
                ValidationIssue(
                    "CV004",
                    "error",
                    f"{location_base}.__component_meta__",
                    f"Missing key '{key}'.",
                )
            )
    if "granularity" in meta and meta["granularity"] not in (
        "primitive",
        "composition",
        "block",
    ):
        issues.append(
            ValidationIssue(
                "CV004",
                "error",
                f"{location_base}.__component_meta__",
                f"granularity must be primitive|composition|block, got {meta['granularity']!r}.",
            )
        )

    # CV003 — extrapolable implies INVARIANTS/PARAMS/INTERDITS each with ≥ 2 items
    if meta.get("extrapolable") is True:
        for sub in _EXTRAPOLATION_SUBSECTIONS:
            if not _has_section(doc, sub):
                issues.append(
                    ValidationIssue(
                        "CV003",
                        "error",
                        location_base,
                        f"extrapolable=True but '{sub}' section is missing.",
                    )
                )
            elif _count_bullets_after(doc, sub) < 2:
                issues.append(
                    ValidationIssue(
                        "CV003",
                        "error",
                        location_base,
                        f"Section '{sub}' requires ≥ 2 bullet items.",
                    )
                )

    # CV005 — meta.name == file name (when discoverable)
    name = meta.get("name")
    file_path = getattr(mod, "__file__", None)
    if name and file_path:
        expected = Path(file_path).stem
        if expected != name:
            issues.append(
                ValidationIssue(
                    "CV005",
                    "error",
                    location_base,
                    f"__component_meta__['name']={name!r} does not match file stem {expected!r}.",
                )
            )

    # CV006 — a public function with the same name exists
    func: Any = getattr(mod, name, None) if isinstance(name, str) else None
    if not callable(func):
        issues.append(
            ValidationIssue(
                "CV006",
                "error",
                location_base,
                f"No public function named '{name}' found in module.",
            )
        )
    else:
        # CV007 — only keyword-only arguments
        try:
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ):
                    issues.append(
                        ValidationIssue(
                            "CV007",
                            "error",
                            f"{location_base}.{name}",
                            f"Parameter '{param_name}' must be keyword-only (use *).",
                        )
                    )
                    break
        except (TypeError, ValueError):
            # inspect.signature() raises TypeError on some builtins / C-extensions
            # and ValueError if the signature is malformed. Both are acceptable —
            # we simply skip the CV007 keyword-only check for that callable.
            pass

        # CV011 — public function has its own docstring (info)
        if not (func.__doc__ or "").strip():
            issues.append(
                ValidationIssue(
                    "CV011",
                    "info",
                    f"{location_base}.{name}",
                    "Public function has no docstring (recommended).",
                )
            )

    # CV008 — bundles_required entries are "<bundle>.<attr>" syntactically
    for entry in meta.get("bundles_required", []) or []:
        if not isinstance(entry, str) or "." not in entry:
            issues.append(
                ValidationIssue(
                    "CV008",
                    "error",
                    f"{location_base}.__component_meta__",
                    f"bundles_required entry {entry!r} is not of the form '<bundle>.<attr>'.",
                )
            )

    # CV009 — When to use / When NOT to use 2-6 items (warning)
    for section in ("When to use", "When NOT to use"):
        count = _count_bullets_after(doc, section)
        if count and not (2 <= count <= 6):
            issues.append(
                ValidationIssue(
                    "CV009",
                    "warning",
                    location_base,
                    f"Section '{section}' has {count} items (recommended 2-6).",
                )
            )

    # CV010 — tags unique and snake_case (warning)
    tags = meta.get("tags") or []
    if isinstance(tags, list):
        if len(set(tags)) != len(tags):
            issues.append(
                ValidationIssue(
                    "CV010",
                    "warning",
                    f"{location_base}.__component_meta__",
                    "tags are not unique.",
                )
            )
        for tag in tags:
            if not isinstance(tag, str) or not re.fullmatch(r"[a-z0-9_]+", tag):
                issues.append(
                    ValidationIssue(
                        "CV010",
                        "warning",
                        f"{location_base}.__component_meta__",
                        f"tag {tag!r} is not snake_case.",
                    )
                )

    return issues


def validate_design_system(mod: ModuleType) -> list[ValidationIssue]:
    """Verify a Python module exposes a conforming DesignSystem class."""
    issues: list[ValidationIssue] = []
    location_base = getattr(mod, "__name__", "<unknown_module>")

    ds = getattr(mod, "DesignSystem", None)
    if ds is None:
        issues.append(
            ValidationIssue(
                "DV001",
                "error",
                location_base,
                "Module does not export a 'DesignSystem' class.",
            )
        )
        return issues

    # DV002 — runtime check against the Protocol
    if not isinstance(ds, type):
        issues.append(
            ValidationIssue(
                "DV002",
                "error",
                f"{location_base}.DesignSystem",
                "DesignSystem must be a class.",
            )
        )
        return issues

    # We attribute-check rather than isinstance(...) because protocols on
    # classes don't always cooperate with runtime_checkable when subclasses
    # use ClassVar. The contract is "attributes are present".
    for bundle_name in REQUIRED_BUNDLES:
        if not hasattr(ds, bundle_name):
            issues.append(
                ValidationIssue(
                    "DV003",
                    "error",
                    f"{location_base}.DesignSystem",
                    f"Required bundle '{bundle_name}' is missing.",
                )
            )

    # DV002 (cont.) — Protocol check is best-effort, classed as warning
    try:
        if not isinstance(ds, DesignSystemProtocol):
            issues.append(
                ValidationIssue(
                    "DV002",
                    "warning",
                    f"{location_base}.DesignSystem",
                    "Class does not satisfy DesignSystemProtocol (runtime isinstance check).",
                )
            )
    except TypeError:
        # Some Protocol subclasses are not runtime-checkable in older Pythons
        pass

    # DV005 — module docstring describes the design system
    if not (mod.__doc__ or "").strip():
        issues.append(
            ValidationIssue(
                "DV005",
                "warning",
                location_base,
                "Module has no docstring (recommended for design systems).",
            )
        )

    return issues


def validate_kit(path: Path) -> list[ValidationIssue]:
    """Validate a kit TOML file against KitManifest schema."""
    issues: list[ValidationIssue] = []
    location = str(path)

    if not path.exists():
        issues.append(ValidationIssue("KV001", "error", location, "Kit file does not exist."))
        return issues

    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        issues.append(
            ValidationIssue("KV002", "error", location, f"Kit TOML parse error: {exc}")
        )
        return issues

    kit = data.get("kit") or data
    for field in ("name", "description", "since"):
        if field not in kit:
            issues.append(
                ValidationIssue(
                    "KV003",
                    "error",
                    location,
                    f"Missing field '{field}' in kit manifest.",
                )
            )

    if "design_system" not in kit:
        issues.append(
            ValidationIssue("KV004", "error", location, "Missing [design_system] section.")
        )
    else:
        ds_ref = kit["design_system"]
        if not isinstance(ds_ref, dict) or "ref" not in ds_ref:
            issues.append(
                ValidationIssue(
                    "KV004",
                    "error",
                    location,
                    "[design_system] must contain a 'ref' field.",
                )
            )

    components = kit.get("components")
    if components is None or not (components.get("include") if isinstance(components, dict) else None):
        issues.append(
            ValidationIssue(
                "KV005",
                "error",
                location,
                "[components.include] must be a non-empty list.",
            )
        )

    return issues


# ---------------------------------------------------------------------------
# Pack manifest validation (PV001-PV010)
# ---------------------------------------------------------------------------

_SEMVER_RE = re.compile(r"^\d+\.\d+(\.\d+)?$")


def _supported_manifest_format(value: str) -> bool:
    """Track streamtex 0.7.x accepts manifest formats 0.1.y and 0.2.y."""
    m = re.match(r"^0\.(\d+)(?:\.\d+)?$", value or "")
    if not m:
        return False
    return int(m.group(1)) in (1, 2)


def validate_pack(path: Path) -> list[ValidationIssue]:
    """Validate a pack directory or its _pack_manifest.toml.

    Accepts either a directory containing `_pack_manifest.toml` at its root, or
    a direct path to that file.
    """
    issues: list[ValidationIssue] = []
    if path.is_dir():
        manifest_path = path / "_pack_manifest.toml"
    else:
        manifest_path = path
    location = str(manifest_path)

    if not manifest_path.exists():
        issues.append(
            ValidationIssue("PV001", "error", location, "_pack_manifest.toml is missing.")
        )
        return issues

    try:
        with manifest_path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        issues.append(
            ValidationIssue("PV001", "error", location, f"Pack manifest parse error: {exc}")
        )
        return issues

    manifest_section = data.get("manifest")
    if not isinstance(manifest_section, dict) or "format" not in manifest_section:
        issues.append(
            ValidationIssue(
                "PV002",
                "error",
                location,
                "[manifest] section with field 'format' is required (Q16).",
            )
        )
    else:
        fmt = manifest_section["format"]
        if not isinstance(fmt, str) or not _SEMVER_RE.match(fmt):
            issues.append(
                ValidationIssue(
                    "PV003",
                    "error",
                    location,
                    f"manifest.format {fmt!r} is not a valid semver.",
                )
            )
        else:
            if fmt.startswith("0."):
                issues.append(
                    ValidationIssue(
                        "PV004",
                        "warning",
                        location,
                        f"manifest.format={fmt} is pre-1.0 (mouvant during 0.7.x).",
                    )
                )
            if not _supported_manifest_format(fmt):
                issues.append(
                    ValidationIssue(
                        "PV005",
                        "error",
                        location,
                        f"manifest.format={fmt} not supported by current streamtex (0.1.y or 0.2.y expected).",
                    )
                )

    pack_section = data.get("pack")
    if not isinstance(pack_section, dict):
        issues.append(
            ValidationIssue(
                "PV006", "error", location, "[pack] section is required."
            )
        )
    else:
        for field in ("name", "version", "author", "license", "streamtex_compat"):
            if field not in pack_section:
                issues.append(
                    ValidationIssue(
                        "PV006",
                        "error",
                        location,
                        f"[pack].{field} is required.",
                    )
                )

        compat = pack_section.get("streamtex_compat")
        if compat and not isinstance(compat, str):
            issues.append(
                ValidationIssue(
                    "PV007",
                    "error",
                    location,
                    "streamtex_compat must be a PEP 440 specifier string.",
                )
            )

    entrypoint = data.get("entrypoint") or (data.get("pack", {}) or {}).get("entrypoint")
    if not isinstance(entrypoint, dict) or "module" not in entrypoint:
        issues.append(
            ValidationIssue(
                "PV008",
                "error",
                location,
                "[entrypoint] (or [pack.entrypoint]) with 'module' is required.",
            )
        )

    # PV009 — at least 1 component or design system findable on disk
    if path.is_dir():
        components_dir = path / "components"
        ds_dir = path / "design_systems"
        found = False
        if components_dir.exists() and any(components_dir.glob("*.py")):
            found = True
        if ds_dir.exists() and any(ds_dir.glob("*/__init__.py")):
            found = True
        if not found:
            issues.append(
                ValidationIssue(
                    "PV009",
                    "error",
                    location,
                    "No components/ or design_systems/ artifacts found in pack.",
                )
            )

    return issues


# ---------------------------------------------------------------------------
# Bundles required cross-check (BV001-BV002 — Q2)
# ---------------------------------------------------------------------------


def validate_bundles_required(
    component_meta: ComponentMeta,
    design_system: type,
) -> list[ValidationIssue]:
    """Verify every bundles_required entry resolves on the active design system.

    Entries are "<bundle>.<attr>". A missing bundle yields BV001; a missing
    attribute on an existing bundle yields BV002.
    """
    issues: list[ValidationIssue] = []
    comp_name = component_meta.get("name", "<unknown>")
    for entry in component_meta.get("bundles_required", []) or []:
        if not isinstance(entry, str) or "." not in entry:
            continue
        bundle, attr = entry.split(".", 1)
        bundle_obj = getattr(design_system, bundle, None)
        if bundle_obj is None:
            issues.append(
                ValidationIssue(
                    "BV001",
                    "error",
                    f"<component:{comp_name}>",
                    f"Design system is missing bundle '{bundle}' required by component '{comp_name}'.",
                )
            )
            continue
        if not hasattr(bundle_obj, attr):
            issues.append(
                ValidationIssue(
                    "BV002",
                    "error",
                    f"<component:{comp_name}>",
                    f"Bundle '{bundle}' is missing attribute '{attr}' required by component '{comp_name}'.",
                )
            )
    return issues


__all__ = [
    "ValidationIssue",
    "validate_component",
    "validate_design_system",
    "validate_kit",
    "validate_pack",
    "validate_bundles_required",
]
