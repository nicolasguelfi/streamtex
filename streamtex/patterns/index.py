"""Regenerate ``_pattern_library.md`` from installed pattern frontmatters."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from .manifest import Frontmatter, parse_frontmatter, split_frontmatter

logger = logging.getLogger(__name__)

INDEX_FILENAME = "_pattern_library.md"
BEGIN_AUTO = "<!-- BEGIN AUTO -->"
END_AUTO = "<!-- END AUTO -->"

_AUTO_BLOCK_RE = re.compile(
    re.escape(BEGIN_AUTO) + r".*?" + re.escape(END_AUTO),
    re.DOTALL,
)


def _scan_patterns(target: Path) -> list[tuple[Path, Frontmatter | None]]:
    """Walk *target* for all ``*.md`` patterns (skipping leading-underscore + drafts)."""
    out: list[tuple[Path, Frontmatter | None]] = []
    if not target.is_dir():
        return out
    for path in sorted(target.iterdir()):
        if not path.is_file() or path.suffix != ".md":
            continue
        if path.name.startswith("_"):
            continue
        if path.parent.name == "_drafts":
            continue
        try:
            text = path.read_text(encoding="utf-8")
            yaml, _ = split_frontmatter(text)
            fm = parse_frontmatter(yaml)
        except Exception as exc:
            logger.warning("skipping %s in index: %s", path, exc)
            out.append((path, None))
            continue
        out.append((path, fm))
    return out


def _build_auto_section(target: Path) -> str:
    """Build the markdown table embedded between AUTO markers."""
    rows = []
    for _, fm in _scan_patterns(target):
        if fm is None:
            continue
        tags_str = ", ".join(fm.tags) if fm.tags else "—"
        extra = "yes" if fm.extrapolable else "no"
        # escape pipes inside description
        desc = fm.description.replace("|", "\\|")
        rows.append(f"| {fm.name} | {desc} | {tags_str} | {extra} |")

    rows.sort()
    body = "\n".join(rows) if rows else "| _(no patterns installed)_ |  |  |  |"
    return (
        "## Patterns disponibles\n\n"
        "| Name | Description | Tags | Extrapolable |\n"
        "|---|---|---|---|\n"
        f"{body}\n"
    )


def _initial_index_template(auto: str) -> str:
    return (
        "# Pattern library\n\n"
        "Locally installed StreamTeX patterns. The table below is regenerated\n"
        "by `stx patterns install/update/sync`.\n\n"
        f"{BEGIN_AUTO}\n\n{auto}\n{END_AUTO}\n"
    )


def regenerate_index(target: Path) -> Path:
    """(Re)write ``_pattern_library.md`` in *target*, preserving manual content."""
    target = Path(target)
    auto = _build_auto_section(target)
    index_path = target / INDEX_FILENAME

    if not index_path.exists():
        target.mkdir(parents=True, exist_ok=True)
        index_path.write_text(_initial_index_template(auto), encoding="utf-8")
        return index_path

    content = index_path.read_text(encoding="utf-8")
    new_block = f"{BEGIN_AUTO}\n\n{auto}\n{END_AUTO}"

    if BEGIN_AUTO in content and END_AUTO in content:
        content = _AUTO_BLOCK_RE.sub(new_block, content, count=1)
    else:
        # Inject after first H1 if any, else at the top.
        h1 = re.search(r"^(#\s.+)$", content, re.MULTILINE)
        if h1:
            insert_at = h1.end()
            content = (
                content[:insert_at]
                + "\n\n"
                + new_block
                + "\n"
                + content[insert_at:]
            )
        else:
            content = new_block + "\n\n" + content

    index_path.write_text(content, encoding="utf-8")
    return index_path
