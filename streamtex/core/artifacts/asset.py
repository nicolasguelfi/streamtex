"""Asset artifact — binary resources (logos, fonts, images, …) with a manifest.

Filesystem convention: ``<pack>/assets/_manifest.toml`` + the binary files
themselves. The manifest lists every shipped asset with its kind and
license:

    [[assets]]
    path = "logos/gse-logo.svg"
    kind = "logo"
    license = "BUSL-1.1"
    sha256 = "<optional>"

The asset "name" in the [pack.data] section is the bundle name (typically
just "assets"), pointing at the manifest. Individual asset paths are
enumerated via the manifest entries.

Validation codes: ASV001-ASV010 (asset validation).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from streamtex.core.validation import ValidationIssue

_VALID_KINDS = {"logo", "font", "image", "icon", "audio", "video", "data", "other"}


@dataclass(frozen=True)
class AssetEntry:
    """One entry in an asset manifest."""

    path: str
    kind: str
    license: str
    sha256: str = ""


@dataclass(frozen=True)
class AssetBundle:
    """Typed view of a pack's ``assets/`` bundle (loaded from _manifest.toml)."""

    name: str
    pack: str
    root: Path
    entries: list[AssetEntry] = field(default_factory=list)

    def resolve(self, asset_path: str) -> Path:
        return self.root / asset_path


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_asset(path: Path) -> list[ValidationIssue]:
    """Validate an asset bundle directory (or its `_manifest.toml`).

    ASV001 — directory or manifest path exists
    ASV002 — _manifest.toml parseable
    ASV003 — [[assets]] entries are objects with path + kind + license
    ASV004 — kinds within the supported set (warning if not)
    ASV005 — each declared path exists on disk
    """
    issues: list[ValidationIssue] = []
    if path.is_dir():
        manifest = path / "_manifest.toml"
        root = path
    else:
        manifest = path
        root = path.parent
    if not manifest.exists():
        return [_issue("ASV001", "error", manifest, "asset manifest not found")]
    try:
        data = tomllib.loads(manifest.read_text())
    except tomllib.TOMLDecodeError as exc:
        return [_issue("ASV002", "error", manifest, f"manifest parse error: {exc}")]

    entries = data.get("assets") or []
    if not isinstance(entries, list) or not entries:
        issues.append(_issue("ASV003", "warning", manifest, "[[assets]] is empty or missing"))

    for entry in entries:
        if not isinstance(entry, dict):
            issues.append(_issue("ASV003", "error", manifest, f"entry must be a table: {entry!r}"))
            continue
        for field_name in ("path", "kind", "license"):
            if not entry.get(field_name):
                issues.append(
                    _issue("ASV003", "error", manifest, f"asset entry missing '{field_name}'")
                )
        kind = entry.get("kind")
        if isinstance(kind, str) and kind not in _VALID_KINDS:
            issues.append(
                _issue(
                    "ASV004",
                    "warning",
                    manifest,
                    f"kind {kind!r} not in {{{', '.join(sorted(_VALID_KINDS))}}}",
                )
            )
        rel_path = entry.get("path")
        if isinstance(rel_path, str):
            on_disk = root / rel_path
            if not on_disk.exists():
                issues.append(
                    _issue("ASV005", "error", manifest, f"asset file not found: {rel_path}")
                )

    return issues


def load_asset_bundle_from_path(path: Path, *, pack: str = "") -> AssetBundle:
    """Parse an asset bundle directory into a typed AssetBundle."""
    issues = validate_asset(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid asset bundle at {path}:\n{joined}")

    if path.is_dir():
        manifest = path / "_manifest.toml"
        root = path
    else:
        manifest = path
        root = path.parent
    data = tomllib.loads(manifest.read_text())
    entries = [
        AssetEntry(
            path=e["path"],
            kind=e["kind"],
            license=e["license"],
            sha256=e.get("sha256", ""),
        )
        for e in (data.get("assets") or [])
        if isinstance(e, dict) and e.get("path")
    ]
    return AssetBundle(name=root.name, pack=pack, root=root, entries=entries)
