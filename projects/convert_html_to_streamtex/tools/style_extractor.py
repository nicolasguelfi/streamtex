"""Map CSS inline values from parsed HTML to StreamTeX style expressions.

Two style families:
  - Presentation ("pres"): for ``bck_*`` blocks (slides, large text)
  - Document ("doc"): for ``bckcp_*`` blocks (course-pack, compact reading)

The family is inferred from the block name prefix.

Every public function returns a **Python code string** (e.g.
``"s.project.colors.navy_blue + s.bold"``) that can be pasted straight
into a StreamTeX block file.
"""

from __future__ import annotations

# ============================================================
# COLOR MAP  (54 HTML hex colours -> ~15 project colour styles)
# ============================================================

COLOR_MAP: dict[str, str] = {
    # --- greens ---
    "#274e13": "s.project.colors.forest_green",
    "#2f5a1b": "s.project.colors.forest_green",
    "#37761c": "s.project.colors.olive_green",
    "#188037": "s.project.colors.olive_green",
    "#6aa84f": "s.project.colors.light_green",
    "#93c47d": "s.project.colors.light_green",
    # --- blues ---
    "#0000ff": "s.project.colors.link_blue",
    "#1155cc": "s.project.colors.link_blue",
    "#0b5394": "s.project.colors.navy_blue",
    "#1b4587": "s.project.colors.navy_blue",
    "#063763": "s.project.colors.navy_blue",
    "#3d85c6": "s.project.colors.sky_blue",
    "#3c78d8": "s.project.colors.sky_blue",
    # --- teals ---
    "#134f5c": "s.project.colors.teal",
    "#0c343d": "s.project.colors.teal",
    "#45818e": "s.project.colors.teal",
    # --- reds ---
    "#ff0000": "s.project.colors.bright_red",
    "#cc0000": "s.project.colors.bright_red",
    "#980000": "s.project.colors.bright_red",
    "#990000": "s.project.colors.bright_red",
    "#660000": "s.project.colors.deep_red",
    "#5b0f00": "s.project.colors.deep_red",
    "#85200c": "s.project.colors.deep_red",
    "#e06666": "s.project.colors.salmon",
    "#ea9999": "s.project.colors.salmon",
    "#cc4125": "s.project.colors.salmon",
    "#a61b00": "s.project.colors.salmon",
    # --- oranges ---
    "#ff9900": "s.project.colors.orange",
    "#ffa500": "s.project.colors.orange",
    "#e69137": "s.project.colors.orange",
    "#b45f06": "s.project.colors.burnt_orange",
    "#783e04": "s.project.colors.burnt_orange",
    "#a65704": "s.project.colors.burnt_orange",
    # --- golds ---
    "#7f6000": "s.project.colors.gold",
    "#be9000": "s.project.colors.gold",
    "#947e01": "s.project.colors.gold",
    # --- purples ---
    "#9900ff": "s.project.colors.purple",
    "#674ea7": "s.project.colors.purple",
    "#20124d": "s.project.colors.dark_purple",
    "#351b75": "s.project.colors.dark_purple",
    "#731b47": "s.project.colors.dark_purple",
    "#4c1130": "s.project.colors.dark_purple",
    "#a64d78": "s.project.colors.dark_purple",
    # --- grays ---
    "#434343": "s.project.colors.gray",
    "#666666": "s.project.colors.gray",
    "#999999": "s.project.colors.gray",
}

# Colours that the Streamlit theme controls (never hardcode these).
DEFAULT_COLORS: set[str] = {
    "#000000",
    "#ffffff",
    "#222222",
    "#d9d9d9",
    "#00ff00",
    "#87ff01",
    "#ff00ff",
}

# ============================================================
# SIZE MAPS — one per family
# ============================================================

# Presentation sizes (slides): boundaries -> project paragraph style
# Maps HTML font sizes to reasonable presentation styles.
# Checked from largest to smallest so the first match wins.
_PRES_SIZE_BRACKETS: list[tuple[int, str]] = [
    (36, "s.project.pres.paragraphs.p_xl"),    # 36pt+ (was Giant/Huge)
    (28, "s.project.pres.paragraphs.p_lg"),    # 28-35pt (was huge/LARGE)
    (24, "s.project.pres.paragraphs.p_md"),    # 24-27pt (was Large)
    (20, "s.project.pres.paragraphs.p_sm"),    # 20-23pt (was large)
    (0,  "s.project.pres.paragraphs.p_body"),  # 0-19pt (was big/medium)
]

# Document sizes (reading): boundaries -> style expression
_DOC_SIZE_BRACKETS: list[tuple[int, str]] = [
    (20, "s.project.doc.paragraphs.p_lg"),    # 20pt+
    (16, "s.project.doc.paragraphs.p_md"),    # 16-19pt
    (14, "s.project.doc.paragraphs.p_sm"),    # 14-15pt
    (0,  "s.project.doc.paragraphs.p_body"),  # 0-13pt
]

# ============================================================
# HEADING MAPS — one per family
# ============================================================

_PRES_HEADING_MAP: dict[str, str] = {
    "h1": "s.project.pres.titles.h1",
    "h2": "s.project.pres.titles.h2",
    "h3": "s.project.pres.titles.h3",
    "h4": "s.project.pres.titles.h4",
    "h5": "s.project.pres.titles.h5",
    "h6": "s.project.pres.titles.h6",
}

_DOC_HEADING_MAP: dict[str, str] = {
    "h1": "s.project.doc.titles.h1",
    "h2": "s.project.doc.titles.h2",
    "h3": "s.project.doc.titles.h3",
    "h4": "s.project.doc.titles.h4",
    "h5": "s.project.doc.titles.h5",
    "h6": "s.project.doc.titles.h6",
}

# ============================================================
# LINK SIZE MAPS — one per family
# ============================================================

# Presentation link sizes: boundary -> style expression
_PRES_LINK_BRACKETS: list[tuple[int, str]] = [
    (28, "s.project.pres.links.link_lg"),    # 28pt+
    (24, "s.project.pres.links.link_md"),    # 24-27pt
    (20, "s.project.pres.links.link_sm"),    # 20-23pt
    (16, "s.project.pres.links.link_body"),  # 16-19pt
    (0,  "s.project.pres.links.default"),    # <16pt
]

# Document link sizes: boundary -> style expression
_DOC_LINK_BRACKETS: list[tuple[int, str]] = [
    (20, "s.project.doc.links.link_lg"),    # 20pt+
    (16, "s.project.doc.links.link_md"),    # 16-19pt
    (12, "s.project.doc.links.link_body"),  # 12-15pt
    (0,  "s.project.doc.links.default"),    # <12pt
]


# ============================================================
# PUBLIC API
# ============================================================


def get_family(block_name: str) -> str:
    """Return ``"pres"`` or ``"doc"`` based on the block-name prefix.

    * ``bckcp_*`` -> ``"doc"``  (course-pack / document)
    * everything else (``bck_*``) -> ``"pres"`` (presentation / slides)
    """
    if block_name.startswith("bckcp_"):
        return "doc"
    return "pres"


def is_default_color(hex_color: str) -> bool:
    """Return True when *hex_color* is theme-controlled and must NOT be hardcoded."""
    return hex_color.lower() in DEFAULT_COLORS


def map_color(hex_color: str) -> str | None:
    """Map an HTML hex colour to a project colour style expression.

    Returns ``None`` when the colour is in :data:`DEFAULT_COLORS` (theme-
    controlled) or when no mapping exists in :data:`COLOR_MAP`.
    """
    normalised = hex_color.lower()
    if is_default_color(normalised):
        return None
    return COLOR_MAP.get(normalised)


def map_font_size(size_pt: int | str, family: str) -> str | None:
    """Map a font-size (in ``pt``) to the closest StreamTeX size style.

    Parameters
    ----------
    size_pt:
        Font size in points parsed from the inline CSS.
        Accepts int (e.g. 48) or string (e.g. "48pt", "48").
    family:
        ``"pres"`` or ``"doc"`` (see :func:`get_family`).

    Returns ``None`` only when *size_pt* is negative (invalid input).
    """
    if isinstance(size_pt, str):
        size_pt = int("".join(c for c in size_pt if c.isdigit()) or "0")
    if size_pt < 0:
        return None
    brackets = _PRES_SIZE_BRACKETS if family == "pres" else _DOC_SIZE_BRACKETS
    for threshold, style_expr in brackets:
        if size_pt >= threshold:
            return style_expr
    # Fallback (should not happen since last bracket starts at 0)
    return brackets[-1][1]


def map_heading(tag: str, family: str) -> str:
    """Return the heading style expression for an HTML heading tag.

    Parameters
    ----------
    tag:
        Lowercase HTML tag: ``"h1"`` .. ``"h6"``.
    family:
        ``"pres"`` or ``"doc"``.
    """
    heading_map = _PRES_HEADING_MAP if family == "pres" else _DOC_HEADING_MAP
    return heading_map.get(tag, heading_map["h6"])


def map_link_style(font_size_pt: int | str | None, family: str) -> str:
    """Return the link style expression with an appropriate size.

    When *font_size_pt* is ``None`` the default (unsized) link style is
    returned so the link inherits the surrounding font-size.

    Parameters
    ----------
    font_size_pt:
        The font-size of the surrounding context (in pt), or ``None``.
        Accepts int (e.g. 48) or string (e.g. "48pt", "48").
    family:
        ``"pres"`` or ``"doc"``.
    """
    brackets = _PRES_LINK_BRACKETS if family == "pres" else _DOC_LINK_BRACKETS
    if font_size_pt is None:
        # Return the smallest / default link style
        return brackets[-1][1]
    if isinstance(font_size_pt, str):
        font_size_pt = int("".join(c for c in font_size_pt if c.isdigit()) or "0")
    for threshold, style_expr in brackets:
        if font_size_pt >= threshold:
            return style_expr
    return brackets[-1][1]


def compose_style(
    color: str | None,
    size: str | None,
    bold: bool,
    italic: bool,
) -> str:
    """Combine style fragments into a single ``" + "``-joined expression.

    Each non-``None`` / non-``False`` argument contributes one term.
    Returns an empty string when nothing applies (caller can then omit
    the style argument altogether).

    Examples
    --------
    >>> compose_style("s.project.colors.navy_blue", "s.Large", True, False)
    's.project.colors.navy_blue + s.Large + s.bold'

    >>> compose_style(None, "s.big", False, True)
    's.big + s.italic'

    >>> compose_style(None, None, False, False)
    ''
    """
    parts: list[str] = []
    if color is not None:
        parts.append(color)
    if size is not None:
        parts.append(size)
    if bold:
        parts.append("s.bold")
    if italic:
        parts.append("s.italic")
    return " + ".join(parts)
