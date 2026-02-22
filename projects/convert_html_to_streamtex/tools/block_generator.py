"""Generate StreamTeX Python block files from ParsedBlock structures.

Transforms the intermediate representation produced by html_parser.py
into complete, convention-compliant StreamTeX block code.

Generated blocks follow the project coding standards:
  - Standard imports header
  - BlockStyles class with color-mapping documentation
  - build() function with StreamTeX rendering calls
  - Correct use of st_write tuples for inline mixed-style text
  - st_grid for tables, st_list for lists, st_image for images
"""

from __future__ import annotations

import re

from tools.html_parser import ParsedBlock, ParsedElement, ParsedSpan
from tools.style_extractor import (
    get_family,
    map_color,
    map_font_size,
    map_heading,
    map_link_style,
    compose_style,
    is_default_color,
    COLOR_MAP,
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_block(parsed: ParsedBlock, image_registry: dict) -> str:
    """Generate a complete StreamTeX Python block file from *parsed*.

    Parameters
    ----------
    parsed : ParsedBlock
        Intermediate representation of a single HTML block.
    image_registry : dict
        Mapping of MD5 hashes to image metadata (name, originals).

    Returns
    -------
    str
        Full Python source code for the block file.
    """
    family = get_family(parsed.name)
    parts: list[str] = [
        _generate_imports(),
        "",
        _generate_block_styles(parsed),
        "",
        _generate_build(parsed, image_registry, family),
    ]
    # Ensure trailing newline
    return "\n".join(parts).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Import header
# ---------------------------------------------------------------------------


def _generate_imports() -> str:
    """Return the standard StreamTeX block import header."""
    return "\n".join([
        "import streamlit as st",
        "from streamtex import *",
        "import streamtex as stx",
        "from streamtex.styles import Style as ns, StyleGrid as sg",
        "from streamtex.enums import Tags as t, ListTypes as lt",
        "from shared.custom.styles import Styles as s",
    ])


# ---------------------------------------------------------------------------
# BlockStyles class
# ---------------------------------------------------------------------------


def _generate_block_styles(parsed: ParsedBlock) -> str:
    """Generate the ``BlockStyles`` class with a color-mapping comment.

    The class body is always ``pass`` (no local styles); all styling
    goes through the shared palette via ``s.project.*``.
    """
    # Build the color-mapping documentation lines.
    mapped_lines: list[str] = []
    dropped_lines: list[str] = []

    for color in sorted(parsed.all_colors):
        color_lower = color.lower()
        if is_default_color(color_lower):
            dropped_lines.append(color_lower)
        elif color_lower in COLOR_MAP:
            mapped_lines.append(f"{color_lower} -> {COLOR_MAP[color_lower]}")
        else:
            # Unknown color -- flag it for manual review.
            dropped_lines.append(f"{color_lower} (unmapped)")

    # Format the doc string.
    doc_parts = ['    """Local styles for this block.']
    if mapped_lines:
        doc_parts.append("")
        doc_parts.append("    Color mapping:")
        for line in mapped_lines:
            doc_parts.append(f"      {line}")
    if dropped_lines:
        doc_parts.append("    Dropped colors:")
        for line in dropped_lines:
            doc_parts.append(f"      {line}")
    doc_parts.append('    """')

    lines = [
        "class BlockStyles:",
        "\n".join(doc_parts),
        "    pass",
        "",
        "bs = BlockStyles",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# build() function
# ---------------------------------------------------------------------------


def _generate_build(
    parsed: ParsedBlock,
    image_registry: dict,
    family: str,
) -> str:
    """Generate the ``build()`` function body."""
    lines: list[str] = ["def build():"]
    body_lines: list[str] = []

    skip_leading_hr = True
    for elem in parsed.elements:
        # Skip <hr> at the very start of the document.
        if skip_leading_hr and elem.tag == "hr":
            continue
        skip_leading_hr = False

        elem_lines = _generate_element(elem, image_registry, family, indent=1)
        body_lines.extend(elem_lines)

    if not body_lines:
        lines.append("    pass")
    else:
        lines.extend(body_lines)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-element dispatch
# ---------------------------------------------------------------------------

# Tags that are headings.
_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

# Font-size thresholds for converting empty paragraphs to st_space.
_SPACE_SIZE_MAP = [
    (80, 5),
    (48, 4),
    (32, 3),
    (24, 2),
    (0, 1),
]


def _generate_element(
    elem: ParsedElement,
    image_registry: dict,
    family: str,
    indent: int,
) -> list[str]:
    """Generate code lines for a single ``ParsedElement``.

    Returns a list of indented source lines (strings).
    """
    tag = elem.tag.lower()

    # --- <hr> ---------------------------------------------------------------
    if tag == "hr":
        # Horizontal rules are generally skipped; if needed later, a
        # st_space could be emitted.  Currently we drop them.
        return []

    # --- <img> --------------------------------------------------------------
    if tag == "img":
        img_line = _generate_image(elem, image_registry, indent)
        return [img_line] if img_line else []

    # --- <table> ------------------------------------------------------------
    if tag == "table":
        return _generate_table(elem, image_registry, family, indent)

    # --- <ul> / <ol> --------------------------------------------------------
    if tag in ("ul", "ol"):
        return _generate_list(elem, family, indent)

    # --- Headings -----------------------------------------------------------
    if tag in _HEADING_TAGS:
        return _generate_heading(elem, family, indent)

    # --- <p> (paragraph) or generic inline element --------------------------
    if tag in ("p", "div", "span", ""):
        return _generate_paragraph(elem, image_registry, family, indent)

    # Fallback: try to render as paragraph.
    return _generate_paragraph(elem, image_registry, family, indent)


# ---------------------------------------------------------------------------
# Heading generation
# ---------------------------------------------------------------------------


def _generate_heading(
    elem: ParsedElement,
    family: str,
    indent: int,
) -> list[str]:
    """Generate an ``st_write`` call for a heading element."""
    prefix = "    " * indent
    heading_style = map_heading(elem.tag, family)

    # Determine the tag enum and TOC level.
    tag_num = elem.tag.lower().replace("h", "")
    tag_enum = f"t.h{tag_num}"

    # TOC registration: h1 -> absolute level "1", h2 -> relative "+1".
    # This is REQUIRED for the TOC and markers to work — tag alone is not enough.
    toc_lvl: str | None = None
    if tag_num == "1":
        toc_lvl = '"1"'       # Absolute level 1 (main TOC entry + marker target)
    elif tag_num == "2":
        toc_lvl = '"+1"'      # Relative level (sub-entry in TOC)

    # Collect color from spans (headings usually have one dominant color).
    color_style = _dominant_color(elem.spans)
    italic_part = _dominant_italic(elem.spans)

    # Compose the full style expression.
    style_parts = [heading_style]
    if color_style:
        style_parts.append(color_style)
    if italic_part:
        style_parts.append("s.italic")

    style_expr = " + ".join(style_parts)

    # Build the extra keyword arguments string.
    extra_args = f", tag={tag_enum}"
    if toc_lvl:
        extra_args += f", toc_lvl={toc_lvl}"

    # If there is a single span or all spans share the same style, emit a
    # simple st_write.  Otherwise use tuples for mixed inline styles.
    text_spans = [sp for sp in elem.spans if sp.text.strip()]
    if not text_spans:
        # Empty heading -> vertical space.
        return [f"{prefix}st_space(size=2)"]

    if _spans_share_style(text_spans):
        text = _join_span_texts(text_spans)
        return [f"{prefix}st_write({style_expr}, {_quote(text)}{extra_args})"]

    # Mixed inline styles inside the heading -> tuple form with tag + toc_lvl.
    return [_generate_write_call(elem.spans, family, indent, tag=tag_enum, toc_lvl=toc_lvl)]


# ---------------------------------------------------------------------------
# Paragraph generation
# ---------------------------------------------------------------------------


def _generate_paragraph(
    elem: ParsedElement,
    image_registry: dict,
    family: str,
    indent: int,
) -> list[str]:
    """Generate code for a ``<p>`` or similar inline container."""
    prefix = "    " * indent

    # Check for embedded image inside paragraph.
    if elem.image_src:
        img_line = _generate_image(elem, image_registry, indent)
        return [img_line] if img_line else []

    # Check for empty paragraph (used as vertical spacer in Google Docs).
    text_spans = [sp for sp in elem.spans if sp.text.strip()]
    if not text_spans:
        size = _empty_para_space_size(elem)
        return [f"{prefix}st_space(size={size})"]

    # Single span paragraph -- simple st_write.
    if len(text_spans) == 1:
        sp = text_spans[0]
        style_expr = _span_style_expr(sp, family)
        if sp.link:
            return [
                f"{prefix}st_write({style_expr}, {_quote(sp.text)}, "
                f"link={_quote(sp.link)})"
            ]
        return [f"{prefix}st_write({style_expr}, {_quote(sp.text)})"]

    # Multiple spans -- use tuple form via _generate_write_call.
    return [_generate_write_call(elem.spans, family, indent)]


# ---------------------------------------------------------------------------
# st_write with tuples (mixed inline styles)
# ---------------------------------------------------------------------------


def _generate_write_call(
    spans: list[ParsedSpan],
    family: str,
    indent: int,
    tag: str | None = None,
    toc_lvl: str | None = None,
) -> str:
    """Generate a single ``st_write()`` call with tuple arguments.

    Each span becomes a ``(style, "text")`` or ``(style, "text", link)``
    tuple argument.  The first positional argument is a base style that
    sets the dominant font size for the paragraph.
    """
    prefix = "    " * indent

    # Filter out whitespace-only spans that carry no meaning.
    meaningful = [sp for sp in spans if sp.text.strip() or sp.text == " "]
    if not meaningful:
        return f"{prefix}st_space(size=1)"

    # Determine a base / paragraph style from the dominant font size.
    base_style = _paragraph_base_style(meaningful, family)

    # Build tuple arguments.
    tuple_args: list[str] = []
    for sp in meaningful:
        s_expr = _span_color_and_decoration_expr(sp, family)
        if sp.link:
            link_style = map_link_style(sp.font_size, family)
            if s_expr:
                combined = f"{link_style} + {s_expr}"
            else:
                combined = link_style
            tuple_args.append(f"({combined}, {_quote(sp.text)}, {_quote(sp.link)})")
        elif s_expr:
            tuple_args.append(f"({s_expr}, {_quote(sp.text)})")
        else:
            # Plain text inheriting the base style.
            tuple_args.append(_quote(sp.text))

    # Optional keyword arguments for TOC/tag registration.
    kw_suffix = ""
    if tag:
        kw_suffix += f", tag={tag}"
    if toc_lvl:
        kw_suffix += f", toc_lvl={toc_lvl}"

    # If only one tuple and it has no extra style, simplify.
    if len(tuple_args) == 1 and not tuple_args[0].startswith("("):
        return f"{prefix}st_write({base_style}, {tuple_args[0]}{kw_suffix})"

    joined = ", ".join(tuple_args)
    call = f"{prefix}st_write({base_style}, {joined}{kw_suffix})"

    # If the line is very long, wrap it for readability.
    if len(call) > 100:
        inner = f",\n{prefix}    ".join(tuple_args)
        kw_lines = ""
        if tag:
            kw_lines += f"\n{prefix}    tag={tag},"
        if toc_lvl:
            kw_lines += f"\n{prefix}    toc_lvl={toc_lvl},"
        call = f"{prefix}st_write(\n{prefix}    {base_style},\n{prefix}    {inner},{kw_lines}\n{prefix})"

    return call


# ---------------------------------------------------------------------------
# Table generation (st_grid)
# ---------------------------------------------------------------------------


def _generate_table(
    elem: ParsedElement,
    image_registry: dict,
    family: str,
    indent: int,
) -> list[str]:
    """Generate ``st_grid`` code for a ``<table>`` element."""
    prefix = "    " * indent
    inner_prefix = "    " * (indent + 1)
    cell_prefix = "    " * (indent + 2)

    rows = elem.rows
    if not rows:
        return []

    # Determine number of columns from the widest row.
    num_cols = max(len(row) for row in rows)

    # Family-aware style references.
    fam = "pres" if family == "pres" else "doc"
    grid_gap = f"s.project.{fam}.grids.gap"
    header_style = f"s.project.{fam}.tables.header"
    cell_style = f"s.project.{fam}.tables.cell"

    lines: list[str] = []
    lines.append(
        f"{prefix}with st_grid(cols={num_cols}, "
        f"grid_style={grid_gap}) as g:"
    )

    for row_idx, row in enumerate(rows):
        if row_idx == 0 and _row_looks_like_header(row):
            # First row as header.
            for cell_elem in row:
                lines.append(f"{inner_prefix}with g.cell():")
                cell_lines = _generate_cell_content(
                    cell_elem, image_registry, family, indent + 2,
                    style_override=header_style,
                )
                lines.extend(cell_lines)
        else:
            for cell_elem in row:
                lines.append(f"{inner_prefix}with g.cell():")
                cell_lines = _generate_cell_content(
                    cell_elem, image_registry, family, indent + 2,
                    style_override=cell_style,
                )
                lines.extend(cell_lines)

    return lines


def _generate_cell_content(
    cell_elem: ParsedElement,
    image_registry: dict,
    family: str,
    indent: int,
    style_override: str | None = None,
) -> list[str]:
    """Generate content lines for a single table cell.

    If *style_override* is given, it replaces the computed paragraph style.
    """
    prefix = "    " * indent

    # Cell may contain sub-elements (children).
    if cell_elem.children:
        result: list[str] = []
        for child in cell_elem.children:
            result.extend(
                _generate_element(child, image_registry, family, indent)
            )
        return result if result else [f"{prefix}pass"]

    # Cell with direct spans.
    text_spans = [sp for sp in cell_elem.spans if sp.text.strip()]
    if not text_spans:
        return [f"{prefix}pass"]

    if len(text_spans) == 1:
        sp = text_spans[0]
        color_expr = _span_color_and_decoration_expr(sp, family)
        if style_override and color_expr:
            style_expr = f"{style_override} + {color_expr}"
        elif style_override:
            style_expr = style_override
        elif color_expr:
            style_expr = color_expr
        else:
            style_expr = _span_style_expr(sp, family)

        if sp.link:
            return [
                f"{prefix}st_write({style_expr}, {_quote(sp.text)}, "
                f"link={_quote(sp.link)})"
            ]
        return [f"{prefix}st_write({style_expr}, {_quote(sp.text)})"]

    # Multiple spans in cell.
    base = style_override or _paragraph_base_style(text_spans, family)
    tuple_args: list[str] = []
    for sp in text_spans:
        s_expr = _span_color_and_decoration_expr(sp, family)
        if sp.link:
            link_s = map_link_style(sp.font_size, family)
            combined = f"{link_s} + {s_expr}" if s_expr else link_s
            tuple_args.append(
                f"({combined}, {_quote(sp.text)}, {_quote(sp.link)})"
            )
        elif s_expr:
            tuple_args.append(f"({s_expr}, {_quote(sp.text)})")
        else:
            tuple_args.append(_quote(sp.text))

    joined = ", ".join(tuple_args)
    return [f"{prefix}st_write({base}, {joined})"]


def _row_looks_like_header(row: list[ParsedElement]) -> bool:
    """Heuristic: a row is likely a header if most cells are bold."""
    bold_count = sum(
        1 for cell in row
        if cell.spans and all(sp.bold for sp in cell.spans if sp.text.strip())
    )
    return bold_count > len(row) / 2


# ---------------------------------------------------------------------------
# List generation (st_list)
# ---------------------------------------------------------------------------


def _generate_list(
    elem: ParsedElement,
    family: str,
    indent: int,
) -> list[str]:
    """Generate ``st_list`` code for ``<ul>`` or ``<ol>`` elements."""
    prefix = "    " * indent
    inner_prefix = "    " * (indent + 1)
    item_prefix = "    " * (indent + 2)

    list_type = "lt.ordered" if elem.tag.lower() == "ol" else "lt.unordered"
    fam = "pres" if family == "pres" else "doc"
    item_style = f"s.project.{fam}.lists.item"

    lines: list[str] = []
    lines.append(
        f"{prefix}with st_list(list_type={list_type}, "
        f"li_style={item_style}) as lst:"
    )

    for child in elem.children:
        lines.append(f"{inner_prefix}with lst.item():")
        # Each child is a <li> ParsedElement.
        text_spans = [sp for sp in child.spans if sp.text.strip()]
        if not text_spans:
            lines.append(f"{item_prefix}pass")
            continue

        if len(text_spans) == 1:
            sp = text_spans[0]
            s_expr = _span_color_and_decoration_expr(sp, family)
            if sp.link:
                link_s = map_link_style(sp.font_size, family)
                combined = f"{link_s} + {s_expr}" if s_expr else link_s
                lines.append(
                    f"{item_prefix}st_write({combined}, "
                    f"{_quote(sp.text)}, link={_quote(sp.link)})"
                )
            elif s_expr:
                lines.append(
                    f"{item_prefix}st_write({s_expr}, {_quote(sp.text)})"
                )
            else:
                lines.append(f"{item_prefix}st_write({_quote(sp.text)})")
        else:
            # Mixed styles in a single list item -> tuple form.
            write_line = _generate_write_call(child.spans, family, indent + 2)
            lines.append(write_line)

        # Handle nested lists.
        for sub in child.children:
            if sub.tag.lower() in ("ul", "ol"):
                lines.extend(_generate_list(sub, family, indent + 2))

    return lines


# ---------------------------------------------------------------------------
# Image generation (st_image)
# ---------------------------------------------------------------------------


def _generate_image(
    elem: ParsedElement,
    image_registry: dict,
    indent: int,
) -> str:
    """Generate an ``st_image`` call for an ``<img>`` element.

    Uses st_image defaults (width="100%", height="auto") for proportional
    display.  No absolute pixel dimensions from HTML.
    """
    prefix = "    " * indent
    src = elem.image_src
    if not src:
        return ""

    resolved_name = _resolve_image_name(src, "", image_registry)
    return f'{prefix}st_image(uri="{resolved_name}")'


def _resolve_image_name(
    original_src: str,
    block_name: str,
    image_registry: dict,
) -> str:
    """Look up the semantic image name from the registry.

    The *image_registry* maps MD5 hashes to metadata dicts::

        {
            "md5hash": {
                "name": "diagram_cnn_architecture-layers.png",
                "originals": [
                    {"block": "bck_deep_learning_part_2", "file": "image1.png"}
                ]
            }
        }

    We search for an entry whose ``originals`` list contains a match for
    (*block_name*, *original_src*).  If found, return the entry's ``name``.
    Otherwise fall back to the basename of *original_src*.
    """
    # Extract just the filename portion from the src path.
    src_filename = original_src.rsplit("/", 1)[-1] if "/" in original_src else original_src

    for _hash, meta in image_registry.items():
        originals = meta.get("originals", [])
        for orig in originals:
            orig_file = orig.get("file", "")
            orig_block = orig.get("block", "")
            # Match by file name.  If block_name is provided, also match block.
            if orig_file == src_filename:
                if not block_name or orig_block == block_name:
                    return meta.get("name", src_filename)
            # Also try matching against the full original_src.
            if orig_file == original_src:
                if not block_name or orig_block == block_name:
                    return meta.get("name", src_filename)

    # Fallback: if block_name is provided, try a second pass matching just
    # the block name (in case file names differ slightly).
    if block_name:
        for _hash, meta in image_registry.items():
            originals = meta.get("originals", [])
            for orig in originals:
                if orig.get("block", "") == block_name:
                    return meta.get("name", src_filename)

    # No match found -- return the raw filename.
    return src_filename


# ---------------------------------------------------------------------------
# Style expression helpers
# ---------------------------------------------------------------------------


def _span_style_expr(span: ParsedSpan, family: str) -> str:
    """Build a full style expression string for a single span.

    Combines font-size, color, bold, italic, underline, and link decorations.
    """
    parts: list[str] = []

    # Font size -> paragraph style.
    if span.font_size:
        size_style = map_font_size(span.font_size, family)
        if size_style:
            parts.append(size_style)
    else:
        # Default body style for the family.
        fam = "pres" if family == "pres" else "doc"
        parts.append(f"s.project.{fam}.paragraphs.p_body")

    # Color.
    if span.color and not is_default_color(span.color):
        color_style = map_color(span.color)
        if color_style:
            parts.append(color_style)

    # Bold / Italic.
    if span.bold:
        parts.append("s.bold")
    if span.italic:
        parts.append("s.italic")

    return " + ".join(parts) if parts else "s.project.pres.paragraphs.p_body"


def _span_color_and_decoration_expr(span: ParsedSpan, family: str) -> str:
    """Build a style expression for color and text decorations only.

    Does NOT include font-size (that belongs in the base / paragraph style).
    Used when composing tuple arguments inside ``st_write(base, (color, text))``.
    """
    parts: list[str] = []

    if span.color and not is_default_color(span.color):
        color_style = map_color(span.color)
        if color_style:
            parts.append(color_style)

    if span.bold:
        parts.append("s.bold")
    if span.italic:
        parts.append("s.italic")

    return " + ".join(parts)


def _paragraph_base_style(spans: list[ParsedSpan], family: str) -> str:
    """Determine the base paragraph style from the dominant font size."""
    fam = "pres" if family == "pres" else "doc"

    # Collect all font sizes.
    sizes: list[str] = [sp.font_size for sp in spans if sp.font_size]
    if not sizes:
        return f"s.project.{fam}.paragraphs.p_body"

    # Use the most common (or largest) font size as the base.
    dominant = max(sizes, key=lambda sz: _parse_pt(sz))
    mapped = map_font_size(dominant, family)
    return mapped or f"s.project.{fam}.paragraphs.p_body"


def _dominant_color(spans: list[ParsedSpan]) -> str | None:
    """Return the mapped color style for the most common non-default color."""
    colors = [
        sp.color for sp in spans
        if sp.color and not is_default_color(sp.color) and sp.text.strip()
    ]
    if not colors:
        return None
    # Most frequent color.
    dominant = max(set(colors), key=colors.count)
    return map_color(dominant)


def _dominant_bold(spans: list[ParsedSpan]) -> bool:
    """Return True if the majority of text-bearing spans are bold."""
    text_spans = [sp for sp in spans if sp.text.strip()]
    if not text_spans:
        return False
    return sum(1 for sp in text_spans if sp.bold) > len(text_spans) / 2


def _dominant_italic(spans: list[ParsedSpan]) -> bool:
    """Return True if the majority of text-bearing spans are italic."""
    text_spans = [sp for sp in spans if sp.text.strip()]
    if not text_spans:
        return False
    return sum(1 for sp in text_spans if sp.italic) > len(text_spans) / 2


def _spans_share_style(spans: list[ParsedSpan]) -> bool:
    """Return True if all spans share the same color, bold, and italic."""
    if len(spans) <= 1:
        return True
    first = spans[0]
    return all(
        sp.color == first.color
        and sp.bold == first.bold
        and sp.italic == first.italic
        and sp.link == first.link
        for sp in spans[1:]
    )


def _join_span_texts(spans: list[ParsedSpan]) -> str:
    """Concatenate the text of multiple spans into one string."""
    return "".join(sp.text for sp in spans)


# ---------------------------------------------------------------------------
# Empty paragraph -> st_space sizing
# ---------------------------------------------------------------------------


def _empty_para_space_size(elem: ParsedElement) -> int:
    """Estimate ``st_space(size=N)`` from an empty paragraph's font size.

    Large font-size empty paragraphs in Google Docs exports are used as
    visual spacers.  We map them proportionally.
    """
    # Try to get font size from the first span (even if text is empty).
    for sp in elem.spans:
        if sp.font_size:
            pt = _parse_pt(sp.font_size)
            for threshold, size in _SPACE_SIZE_MAP:
                if pt >= threshold:
                    return size
    return 1


def _parse_pt(size_str: str) -> float:
    """Parse a CSS size string like ``"48pt"`` or ``"24px"`` to a float in pt."""
    if not size_str:
        return 0.0
    size_str = size_str.strip().lower()
    match = re.match(r"([\d.]+)\s*(pt|px|em|rem|%)?", size_str)
    if not match:
        return 0.0
    value = float(match.group(1))
    unit = match.group(2) or "pt"
    if unit == "px":
        # Rough conversion: 1pt ~ 1.333px.
        return value / 1.333
    if unit in ("em", "rem"):
        return value * 12  # Assume base 12pt.
    if unit == "%":
        return value * 12 / 100
    return value


# ---------------------------------------------------------------------------
# String quoting
# ---------------------------------------------------------------------------


# Characters to strip from Google Docs exports (render as squares).
_STRIP_CHARS = {
    "\u200b": "",      # zero-width space
    "\u2028": " ",     # line separator -> space
    "\u202f": " ",     # narrow no-break space -> space
    "\ue907": "",      # Google Docs icon font (private use area)
    "\ufe0f": "",      # variation selector-16 (emoji presentation)
}


def _clean_text(text: str) -> str:
    """Clean problematic Unicode characters from Google Docs exports."""
    for char, replacement in _STRIP_CHARS.items():
        text = text.replace(char, replacement)
    return text


def _quote(text: str) -> str:
    """Return a safely quoted Python string literal.

    Uses double quotes by default.  Falls back to triple-quotes if the
    text contains both single and double quotes plus newlines.
    Cleans problematic Unicode characters first.
    """
    if text is None:
        return '""'

    text = _clean_text(text)

    # Escape backslashes first, then double quotes.
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')

    # If the string contains newlines, use triple-double-quotes.
    if "\n" in escaped:
        # For triple-quotes, un-escape internal double quotes (they are safe
        # inside triple-quoted strings unless there are 3+ consecutive).
        inner = text.replace("\\", "\\\\")
        # Ensure no triple-double-quote sequence inside.
        inner = inner.replace('"""', '""\\"')
        return f'"""{inner}"""'

    return f'"{escaped}"'
