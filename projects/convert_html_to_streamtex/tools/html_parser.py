"""
HTML parser for converting Google Docs HTML exports to an intermediate structure.

Parses index.html files from exports/html/{block_name}/ directories and produces
ParsedBlock objects containing structured element data (headings, paragraphs, images,
tables, lists) with inline style extraction (colors, font sizes, bold/italic/underline).

Usage:
    from tools.html_parser import parse_html
    from pathlib import Path

    block = parse_html(Path("exports/html/bck_example/index.html"))
    print(block.name)                # "bck_example"
    print(block.all_colors)          # {"#274e13", "#1155cc", ...}
    print(block.estimated_complexity) # "simple" | "medium" | "complex"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ParsedSpan:
    """A styled text fragment extracted from the HTML."""

    text: str
    color: str | None = None
    font_size: str | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    link: str | None = None


@dataclass
class ParsedElement:
    """A parsed HTML element (heading, paragraph, image, table, list, etc.)."""

    tag: str  # h1-h6, p, img, table, ul, ol, hr, empty_space
    spans: list[ParsedSpan] = field(default_factory=list)
    children: list[ParsedElement] = field(default_factory=list)
    image_src: str | None = None
    image_width: str | None = None
    image_height: str | None = None
    rows: list[list[ParsedElement]] = field(default_factory=list)  # for tables


@dataclass
class ParsedBlock:
    """The complete parsed result for one HTML block file."""

    name: str
    elements: list[ParsedElement] = field(default_factory=list)
    all_colors: set[str] = field(default_factory=set)
    all_font_sizes: set[str] = field(default_factory=set)
    all_images: list[str] = field(default_factory=list)
    has_tables: bool = False
    has_lists: bool = False
    estimated_complexity: str = "simple"


# ---------------------------------------------------------------------------
# Style attribute parsing
# ---------------------------------------------------------------------------

_STYLE_RE = re.compile(r"([a-zA-Z\-]+)\s*:\s*([^;]+)")


def _extract_inline_styles(style_attr: str | None) -> dict[str, str]:
    """Parse a CSS inline ``style`` attribute into a dict.

    Example::

        >>> _extract_inline_styles("color:#fff;font-size:12pt")
        {"color": "#fff", "font-size": "12pt"}
    """
    if not style_attr:
        return {}
    return {m.group(1).strip(): m.group(2).strip() for m in _STYLE_RE.finditer(style_attr)}


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

def _is_empty_spacing(element: Tag) -> bool:
    """Return True when *element* is an empty block used only for vertical spacing.

    Google Docs inserts ``<p><span style="font-size:42pt">\\n</span></p>`` or bare
    ``<p></p>`` to create visual gaps between content.  Empty headings
    (``<h2><span style="font-size:80pt">\\n</span></h2>``) are also used for spacing.
    These carry no meaningful text (only whitespace / zero-width characters).
    """
    _SPACING_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6"}
    if element.name not in _SPACING_TAGS:
        return False
    # If the paragraph contains an image it is NOT empty spacing
    if element.find("img"):
        return False
    # If the paragraph contains a link with real text it is NOT empty spacing
    for a_tag in element.find_all("a"):
        link_text = a_tag.get_text(strip=True)
        # Google Docs uses "_" as a tiny placeholder for link anchors; treat as spacing
        if link_text and link_text != "_":
            return False
    text = element.get_text()
    # Strip whitespace AND zero-width space (U+200B)
    stripped = text.replace("\u200b", "").strip()
    return len(stripped) == 0


def _get_spacing_font_size(element: Tag) -> str | None:
    """Extract the font-size from an empty spacing element if present.

    Returns the font-size string (e.g. ``"42pt"``) or None.
    """
    span = element.find("span")
    if span:
        styles = _extract_inline_styles(span.get("style"))
        return styles.get("font-size")
    return None


# ---------------------------------------------------------------------------
# Inline text / span extraction
# ---------------------------------------------------------------------------

def _is_bold_tag(tag: Tag) -> bool:
    """Return True if the tag itself conveys bold (``<b>`` or ``<strong>``)."""
    return tag.name in ("b", "strong")


def _is_italic_tag(tag: Tag) -> bool:
    """Return True if the tag itself conveys italic (``<i>`` or ``<em>``)."""
    return tag.name in ("i", "em")


def _is_underline_tag(tag: Tag) -> bool:
    """Return True if the tag itself conveys underline (``<u>``)."""
    return tag.name == "u"


@dataclass
class _InlineContext:
    """Inherited formatting state while walking inline nodes."""

    bold: bool = False
    italic: bool = False
    underline: bool = False
    link: str | None = None
    color: str | None = None
    font_size: str | None = None


def _collect_spans(node: Tag | NavigableString, ctx: _InlineContext) -> list[ParsedSpan]:
    """Recursively walk *node* collecting ``ParsedSpan`` objects.

    The *ctx* carries inherited formatting from parent elements so that
    ``<b><span style="color:red">text</span></b>`` correctly marks the span as bold.
    """
    results: list[ParsedSpan] = []

    if isinstance(node, NavigableString):
        text = str(node)
        # Skip pure-whitespace strings that are just newlines between tags
        if text.strip() or text == " ":
            clean = text.replace("\n", " ")
            if clean:
                results.append(ParsedSpan(
                    text=clean,
                    color=ctx.color,
                    font_size=ctx.font_size,
                    bold=ctx.bold,
                    italic=ctx.italic,
                    underline=ctx.underline,
                    link=ctx.link,
                ))
        return results

    if not isinstance(node, Tag):
        return results

    # Skip <img> tags -- they are handled at the element level
    if node.name == "img":
        return results

    # Build a child context inheriting from parent
    child_ctx = _InlineContext(
        bold=ctx.bold,
        italic=ctx.italic,
        underline=ctx.underline,
        link=ctx.link,
        color=ctx.color,
        font_size=ctx.font_size,
    )

    # Update from tag semantics
    if _is_bold_tag(node):
        child_ctx.bold = True
    if _is_italic_tag(node):
        child_ctx.italic = True
    if _is_underline_tag(node):
        child_ctx.underline = True

    # Update from <a> tag
    if node.name == "a":
        href = node.get("href")
        if href:
            child_ctx.link = str(href)

    # Update from inline style (on <span> or any element with a style attr)
    styles = _extract_inline_styles(node.get("style"))
    if "color" in styles:
        child_ctx.color = styles["color"]
    if "font-size" in styles:
        child_ctx.font_size = styles["font-size"]
    if styles.get("font-weight") in ("bold", "700", "800", "900"):
        child_ctx.bold = True
    if styles.get("font-style") == "italic":
        child_ctx.italic = True
    if "underline" in styles.get("text-decoration", ""):
        child_ctx.underline = True

    # Recurse into children
    for child in node.children:
        results.extend(_collect_spans(child, child_ctx))

    return results


def _clean_spans(spans: list[ParsedSpan]) -> list[ParsedSpan]:
    """Post-process span list: strip trailing whitespace-only spans, skip empty ones."""
    cleaned: list[ParsedSpan] = []
    for span in spans:
        # Skip completely empty spans
        if not span.text:
            continue
        # Skip spans that are only whitespace / zero-width space
        stripped = span.text.replace("\u200b", "").strip()
        if not stripped:
            # Keep single-space spans as they may be intentional separators
            if span.text == " " and cleaned:
                cleaned.append(span)
            continue
        cleaned.append(span)

    # Remove trailing whitespace-only spans
    while cleaned and not cleaned[-1].text.strip():
        cleaned.pop()

    return cleaned


# ---------------------------------------------------------------------------
# Image extraction from an element
# ---------------------------------------------------------------------------

def _extract_images(element: Tag) -> list[tuple[str, str | None, str | None]]:
    """Return a list of (src, width, height) for all ``<img>`` tags in *element*."""
    images = []
    for img in element.find_all("img"):
        src = img.get("src", "")
        styles = _extract_inline_styles(img.get("style"))
        width = styles.get("width")
        height = styles.get("height")
        images.append((str(src), width, height))
    return images


# ---------------------------------------------------------------------------
# Element parsing
# ---------------------------------------------------------------------------

_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_LIST_TAGS = {"ul", "ol"}


def _parse_table(table_tag: Tag, context: _ParseContext) -> ParsedElement:
    """Parse a ``<table>`` element into a ParsedElement with rows of cells."""
    rows: list[list[ParsedElement]] = []
    for tr in table_tag.find_all("tr", recursive=False):
        row: list[ParsedElement] = []
        for td in tr.find_all(["td", "th"], recursive=False):
            cell_elem = _parse_content_element(td, context, override_tag="p")
            row.append(cell_elem)
        if row:
            rows.append(row)
    context.has_tables = True
    return ParsedElement(tag="table", rows=rows)


def _parse_list(list_tag: Tag, context: _ParseContext) -> ParsedElement:
    """Parse ``<ul>`` or ``<ol>`` into a ParsedElement with children."""
    tag_name = list_tag.name  # "ul" or "ol"
    children: list[ParsedElement] = []
    for child in list_tag.children:
        if not isinstance(child, Tag):
            continue
        if child.name == "li":
            li_elem = _parse_content_element(child, context, override_tag="li")
            # Check for nested lists inside this <li>
            for nested in child.find_all(["ul", "ol"], recursive=False):
                nested_list = _parse_list(nested, context)
                li_elem.children.append(nested_list)
            children.append(li_elem)
        elif child.name in _LIST_TAGS:
            # Nested list directly under parent list (Google Docs does this)
            nested_list = _parse_list(child, context)
            children.append(nested_list)
    context.has_lists = True
    return ParsedElement(tag=tag_name, children=children)


def _parse_content_element(
    element: Tag,
    context: _ParseContext,
    override_tag: str | None = None,
) -> ParsedElement:
    """Parse a content element (heading, paragraph, list item, table cell).

    Extracts inline spans and images.  The *override_tag* lets callers
    set a specific tag name (e.g. ``"li"`` or ``"p"`` for table cells).
    """
    tag = override_tag or element.name

    # Collect inline spans
    inline_ctx = _InlineContext()
    raw_spans = _collect_spans(element, inline_ctx)
    spans = _clean_spans(raw_spans)

    # Collect images
    images = _extract_images(element)

    # Track colors and font sizes
    for span in spans:
        if span.color:
            context.all_colors.add(span.color)
        if span.font_size:
            context.all_font_sizes.add(span.font_size)

    # If there is exactly one image and no meaningful text, return as an img element
    if len(images) == 1 and not any(s.text.strip() for s in spans):
        src, width, height = images[0]
        context.all_images.append(src)
        return ParsedElement(
            tag="img",
            image_src=src,
            image_width=width,
            image_height=height,
        )

    # If there are images mixed with text, create the element with spans AND
    # attach image info.  For multiple images, use the first one as primary.
    result = ParsedElement(tag=tag, spans=spans)
    if images:
        src, width, height = images[0]
        result.image_src = src
        result.image_width = width
        result.image_height = height
        for src_item, _, _ in images:
            context.all_images.append(src_item)

    return result


@dataclass
class _ParseContext:
    """Mutable context accumulating metadata during parsing."""

    all_colors: set[str] = field(default_factory=set)
    all_font_sizes: set[str] = field(default_factory=set)
    all_images: list[str] = field(default_factory=list)
    has_tables: bool = False
    has_lists: bool = False


def _parse_element(element: Tag, context: _ParseContext) -> ParsedElement | None:
    """Parse a single top-level element from the ``<body>``.

    Returns None for elements that should be skipped (e.g. pure whitespace).
    """
    if not isinstance(element, Tag):
        return None

    tag = element.name

    # --- Horizontal rule ---
    if tag == "hr":
        return ParsedElement(tag="hr")

    # --- Empty spacing detection ---
    if tag == "p" and _is_empty_spacing(element):
        font_size = _get_spacing_font_size(element)
        if font_size:
            context.all_font_sizes.add(font_size)
        return ParsedElement(
            tag="empty_space",
            spans=[ParsedSpan(text="", font_size=font_size)] if font_size else [],
        )

    # --- Headings ---
    if tag in _HEADING_TAGS:
        # Empty headings (Google Docs uses them for spacing too)
        if _is_empty_spacing(element):
            font_size = _get_spacing_font_size(element)
            if font_size:
                context.all_font_sizes.add(font_size)
            return ParsedElement(
                tag="empty_space",
                spans=[ParsedSpan(text="", font_size=font_size)] if font_size else [],
            )
        return _parse_content_element(element, context)

    # --- Paragraphs ---
    if tag == "p":
        return _parse_content_element(element, context)

    # --- Lists ---
    if tag in _LIST_TAGS:
        return _parse_list(element, context)

    # --- Tables ---
    if tag == "table":
        return _parse_table(element, context)

    # --- Images at top level (rare, but possible) ---
    if tag == "img":
        styles = _extract_inline_styles(element.get("style"))
        src = str(element.get("src", ""))
        width = styles.get("width")
        height = styles.get("height")
        context.all_images.append(src)
        return ParsedElement(
            tag="img",
            image_src=src,
            image_width=width,
            image_height=height,
        )

    # Unknown tags: skip
    return None


# ---------------------------------------------------------------------------
# Complexity estimation
# ---------------------------------------------------------------------------

def _estimate_complexity(block: ParsedBlock) -> str:
    """Estimate block complexity as ``"simple"``, ``"medium"``, or ``"complex"``.

    Heuristics:
    - ``complex``: has tables AND images, or >30 elements, or >10 images
    - ``medium``: has tables OR images OR lists, or >15 elements
    - ``simple``: everything else
    """
    n_elements = len(block.elements)
    n_images = len(block.all_images)

    if (block.has_tables and n_images > 0) or n_elements > 30 or n_images > 10:
        return "complex"
    if block.has_tables or n_images > 0 or block.has_lists or n_elements > 15:
        return "medium"
    return "simple"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_html(html_path: Path) -> ParsedBlock:
    """Parse a Google Docs HTML export into a ``ParsedBlock``.

    Parameters
    ----------
    html_path:
        Path to the ``index.html`` file, typically at
        ``exports/html/{block_name}/index.html``.

    Returns
    -------
    ParsedBlock
        Structured intermediate representation of the HTML content.

    Raises
    ------
    FileNotFoundError
        If *html_path* does not exist.
    ValueError
        If the HTML has no ``<body>`` element.
    """
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    html_content = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    body = soup.find("body")
    if body is None:
        raise ValueError(f"No <body> element found in {html_path}")

    # Derive the block name from the parent directory
    block_name = html_path.parent.name

    context = _ParseContext()
    elements: list[ParsedElement] = []

    for child in body.children:
        if not isinstance(child, Tag):
            continue
        parsed = _parse_element(child, context)
        if parsed is not None:
            elements.append(parsed)

    block = ParsedBlock(
        name=block_name,
        elements=elements,
        all_colors=context.all_colors,
        all_font_sizes=context.all_font_sizes,
        all_images=context.all_images,
        has_tables=context.has_tables,
        has_lists=context.has_lists,
    )
    block.estimated_complexity = _estimate_complexity(block)

    return block


# ---------------------------------------------------------------------------
# CLI helper (for quick testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run python -m tools.html_parser <path/to/index.html>")
        sys.exit(1)

    path = Path(sys.argv[1])
    result = parse_html(path)

    print(f"Block: {result.name}")
    print(f"Elements: {len(result.elements)}")
    print(f"Colors: {sorted(result.all_colors)}")
    print(f"Font sizes: {sorted(result.all_font_sizes)}")
    print(f"Images: {result.all_images}")
    print(f"Has tables: {result.has_tables}")
    print(f"Has lists: {result.has_lists}")
    print(f"Complexity: {result.estimated_complexity}")
    print()

    for i, elem in enumerate(result.elements):
        if elem.tag == "empty_space":
            fs = elem.spans[0].font_size if elem.spans else "?"
            print(f"  [{i}] empty_space (font-size: {fs})")
        elif elem.tag == "hr":
            print(f"  [{i}] hr")
        elif elem.tag == "img":
            print(f"  [{i}] img src={elem.image_src} ({elem.image_width} x {elem.image_height})")
        elif elem.tag == "table":
            print(f"  [{i}] table ({len(elem.rows)} rows)")
            for ri, row in enumerate(elem.rows):
                cells_preview = " | ".join(
                    " ".join(s.text.strip() for s in cell.spans)[:30]
                    for cell in row
                )
                print(f"        row {ri}: {cells_preview}")
        elif elem.tag in ("ul", "ol"):
            print(f"  [{i}] {elem.tag} ({len(elem.children)} items)")
            for ci, child in enumerate(elem.children):
                text_preview = " ".join(s.text.strip() for s in child.spans)[:60]
                print(f"        item {ci}: {text_preview}")
        else:
            text_preview = " ".join(s.text.strip() for s in elem.spans)[:80]
            n_spans = len(elem.spans)
            img_note = f" +img:{elem.image_src}" if elem.image_src else ""
            print(f"  [{i}] {elem.tag} ({n_spans} spans{img_note}): {text_preview}")
