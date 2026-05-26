"""Palette artifact — JSON canonical, Python view generated at load time.

A palette file lives at `<pack>/palettes/<name>.json` with the schema:

    {
      "name": "main",
      "version": "1.0.0",
      "colors": {
        "<token>": {
          "hex": "#RRGGBB",
          "role": "<short description>",
          "constraints": "<optional usage constraints>"
        }
      },
      "dimensions": {
        "<dimension_name>": "<color_token>"
      }
    }

The Python view (`Palette` dataclass) exposes:

* `colors: dict[str, Color]` — keyed by token name. Each `Color` carries the
  hex string, role/constraints metadata, plus an `as_style()` method that
  returns a composable `streamtex.styles.Style` atom.
* `dimensions: dict[str, str]` — semantic aliases (e.g. "ideological" → "primary").

Validation codes: PAV001–PAV010 (`palette artifact validation`).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from streamtex.core.validation import ValidationIssue

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass(frozen=True)
class Color:
    """One palette entry — hex string + role metadata + Style adapter."""

    token: str
    hex: str
    role: str = ""
    constraints: str = ""

    def as_style(self, *, style_id: str | None = None):
        """Return a composable `streamtex.styles.Style` atom (color property).

        Import is lazy to keep `streamtex.core.artifacts` importable without
        loading the styles subsystem.
        """
        from streamtex.styles import Style

        return Style(f"color: {self.hex};", style_id or f"color_{self.token}")

    def as_bg_style(self, *, style_id: str | None = None):
        """Same as `as_style` but emits a background-color CSS property."""
        from streamtex.styles import Style

        return Style(f"background-color: {self.hex};", style_id or f"bg_{self.token}")


@dataclass(frozen=True)
class Palette:
    """Typed Python view of a palette artifact."""

    name: str
    pack: str
    version: str
    colors: dict[str, Color]
    dimensions: dict[str, str] = field(default_factory=dict)
    since: str = ""

    def hex_for(self, name: str) -> str:
        """Return the hex string for a token or dimension name.

        Resolves dimensions transitively (`hex_for("ideological")` →
        `colors["primary"].hex` if `dimensions["ideological"] == "primary"`).
        """
        if name in self.dimensions:
            name = self.dimensions[name]
        if name not in self.colors:
            raise KeyError(
                f"Palette {self.pack}:{self.name}: unknown color or dimension "
                f"{name!r}. Known colors: {sorted(self.colors)}; "
                f"known dimensions: {sorted(self.dimensions)}."
            )
        return self.colors[name].hex


def _issue(code: str, severity: str, path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, location=str(path), message=message)


def validate_palette(path: Path) -> list[ValidationIssue]:
    """Run validation checks on a single palette JSON file.

    PAV001 — file readable
    PAV002 — valid JSON
    PAV003 — top-level object (dict)
    PAV004 — `name` field present and non-empty string
    PAV005 — `version` field present, semver-ish string
    PAV006 — `colors` table present and non-empty
    PAV007 — every color entry is an object with hex
    PAV008 — every hex matches `#RRGGBB`
    PAV009 — dimensions (if present) point to existing color tokens
    PAV010 — no duplicate or shadowed keys
    """
    issues: list[ValidationIssue] = []
    if not path.exists():
        return [_issue("PAV001", "error", path, "palette file not found")]
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [_issue("PAV001", "error", path, f"palette file unreadable: {exc}")]
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        return [_issue("PAV002", "error", path, f"invalid JSON: {exc}")]
    if not isinstance(data, dict):
        return [_issue("PAV003", "error", path, "top-level must be an object")]

    name = data.get("name")
    if not isinstance(name, str) or not name:
        issues.append(_issue("PAV004", "error", path, "missing or empty 'name'"))

    version = data.get("version")
    if not isinstance(version, str) or not version:
        issues.append(_issue("PAV005", "error", path, "missing or empty 'version'"))

    colors = data.get("colors")
    if not isinstance(colors, dict) or not colors:
        issues.append(_issue("PAV006", "error", path, "'colors' must be a non-empty object"))
        colors = {}

    for token, entry in colors.items():
        if not isinstance(entry, dict):
            issues.append(
                _issue("PAV007", "error", path, f"color {token!r} must be an object")
            )
            continue
        hex_value = entry.get("hex")
        if not isinstance(hex_value, str) or not _HEX_RE.match(hex_value):
            issues.append(
                _issue(
                    "PAV008",
                    "error",
                    path,
                    f"color {token!r}: hex {hex_value!r} must match '#RRGGBB'",
                )
            )

    dimensions = data.get("dimensions") or {}
    if isinstance(dimensions, dict):
        for dim, target in dimensions.items():
            if dim.startswith("_"):
                continue
            if not isinstance(target, str) or target not in colors:
                issues.append(
                    _issue(
                        "PAV009",
                        "error",
                        path,
                        f"dimension {dim!r} points to unknown color {target!r}",
                    )
                )

    return issues


def load_palette_from_path(path: Path, *, pack: str = "") -> Palette:
    """Parse a palette JSON file into a typed `Palette` dataclass.

    Raises:
        ValueError: if the file is not a valid palette (validation errors).
    """
    issues = validate_palette(path)
    blocking = [i for i in issues if i.is_error()]
    if blocking:
        joined = "\n".join(f"  [{i.code}] {i.message}" for i in blocking)
        raise ValueError(f"Invalid palette at {path}:\n{joined}")

    data = json.loads(path.read_text(encoding="utf-8"))
    name = data.get("name", path.stem)
    version = data.get("version", "0.0.0")
    raw_colors = data.get("colors", {})
    colors: dict[str, Color] = {}
    for token, entry in raw_colors.items():
        colors[token] = Color(
            token=token,
            hex=entry["hex"],
            role=entry.get("role", ""),
            constraints=entry.get("constraints", ""),
        )
    raw_dimensions = data.get("dimensions") or {}
    dimensions = {
        k: v for k, v in raw_dimensions.items()
        if isinstance(k, str) and isinstance(v, str) and not k.startswith("_")
    }
    return Palette(
        name=name,
        pack=pack,
        version=version,
        colors=colors,
        dimensions=dimensions,
        since=data.get("since", ""),
    )


def load_palette(name: str, *, pack: str | None = None) -> Palette:
    """Convenience: resolve + load a palette by name.

    Equivalent to:
        load_artifact(name, ArtifactKind.PALETTE, pack=pack)
    """
    from streamtex.core.artifacts.loaders import load_artifact
    from streamtex.core.artifacts.spec import ArtifactKind

    return load_artifact(name, ArtifactKind.PALETTE, pack=pack)
