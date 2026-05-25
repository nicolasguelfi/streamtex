"""Minimal YAML frontmatter parser shared by archetype/guideline/skill/agent.

Supports the standard convention: a file starting with `---` opens a YAML block
that ends at the next `---` line. We parse a deliberately tiny subset of YAML
(scalars, inline lists, multi-line lists) to avoid pulling in PyYAML as a
runtime dependency of streamtex core.

For richer frontmatter needs (anchors, references, multi-line strings beyond
inline), packs may use full YAML — they just need PyYAML installed and parse
manually before calling our validators.
"""

from __future__ import annotations

import re
from typing import Any

_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(?P<fm>.*?)\n---\s*\n(?P<body>.*)$",
    re.DOTALL,
)


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown file into (frontmatter dict, body text).

    If no frontmatter block is found, returns ({}, original_text).
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm = _parse_simple_yaml(m.group("fm"))
    return fm, m.group("body")


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a tiny YAML subset (scalars + inline lists + indented lists)."""
    out: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, raw_value = line.partition(":")
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value == "":
            # Multi-line list: collect "- item" lines that follow
            collected: list[str] = []
            j = i + 1
            while j < len(lines) and (lines[j].startswith("  ") or lines[j].strip().startswith("-")):
                stripped = lines[j].strip()
                if stripped.startswith("-"):
                    collected.append(_coerce(stripped[1:].strip()))
                j += 1
            if collected:
                out[key] = collected
            i = j
            continue
        if raw_value.startswith("[") and raw_value.endswith("]"):
            inner = raw_value[1:-1].strip()
            if inner:
                out[key] = [_coerce(p.strip()) for p in inner.split(",")]
            else:
                out[key] = []
        else:
            out[key] = _coerce(raw_value)
        i += 1
    return out


def _coerce(value: str) -> Any:
    """Coerce a scalar string into bool/int/None/str."""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in ("null", "none", "~", ""):
        return None
    if value.lstrip("-").isdigit():
        try:
            return int(value)
        except ValueError:
            pass
    return value
