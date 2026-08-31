"""PDF Export — convert StreamTeX HTML to PDF via Playwright (Chromium headless).

Requires the optional ``pdf`` extra::

    uv add "streamtex[pdf]"
    playwright install chromium
"""

import re
from dataclasses import dataclass
from enum import Enum
from html import escape as _attr_escape
from typing import Optional


class PdfMode(Enum):
    """PDF export mode controlling how slide breaks are handled."""

    CONTINUOUS = "continuous"
    """Remove all slide breaks — content flows continuously."""

    PAGINATED = "paginated"
    """Insert a PDF page break at each slide break and visible marker."""


@dataclass
class PdfConfig:
    """Configuration for PDF export.

    Example::

        from streamtex import PdfConfig, PdfMode

        config = PdfConfig(
            mode=PdfMode.PAGINATED,
            format="A4",
            landscape=True,
            content_width=80,
        )
    """

    mode: PdfMode = PdfMode.PAGINATED
    """How to handle slide breaks in the PDF."""

    format: str = "A4"
    """Page format: A4, Letter, A3, Legal, Tabloid, etc."""

    landscape: bool = True
    """Landscape orientation (default True for presentations)."""

    margin_top: str = "10mm"
    """Top margin (CSS value)."""

    margin_bottom: str = "10mm"
    """Bottom margin."""

    margin_left: str = "15mm"
    """Left margin."""

    margin_right: str = "15mm"
    """Right margin."""

    print_background: bool = True
    """Include background colors and gradients in the PDF."""

    scale: float = 1.0
    """Scale factor (0.1–2.0). 1.0 = 100%."""

    content_width: int = 100
    """Content width as percentage of the page (10–100).
    Similar to PageLayout(width=...) for on-screen display.
    80 means the content fills 80% of the page, centered with 10% padding each side.
    Background fills the full page regardless of this setting."""

    header_template: str = ""
    """HTML template for page header (Chromium print header format)."""

    footer_template: str = ""
    """HTML template for page footer (Chromium print footer format)."""

    page_numbers: bool = False
    """Add page numbers in the footer (e.g. '1 / 5')."""

    theme_bg: str = "#fff"
    """Background color for PDF margins/header/footer (read from Streamlit theme)."""

    theme_text: str = "#333"
    """Text color for page numbers (read from Streamlit theme)."""

    base_url: str = ""
    """Base URL for resolving the document's relative URLs at print time.

    ``export_pdf`` loads the HTML on ``about:blank`` — without a base,
    every relative ``src``/``poster``/CSS ``url()`` is dead and the media
    are missing from the PDF (issue #44).  When non-empty, a
    ``<base href>`` tag is injected right after ``<head>`` so Chromium
    resolves relative URLs against it (e.g. the running Streamlit server
    that serves ``app/static/...``); ``wait_until="networkidle"`` then
    waits for those loads.  Normalised to end with ``/``.

    Empty (default) = no injection, byte-identical HTML — the historical
    behaviour.  ``book.py`` fills this automatically with the running
    server's address for the "Download as..." panel and auto-exports."""


# ---------------------------------------------------------------------------
# Print CSS injection
# ---------------------------------------------------------------------------

_PRINT_CSS_CONTINUOUS = """
@media print {
    .stx-slide-break-rule { display: none !important; }
    .stx-slide-break-spacer { display: none !important; }
}
"""

_PRINT_CSS_PAGINATED = """
@media print {
    .stx-slide-break-rule { display: none !important; }
    .stx-slide-break-spacer {
        height: 0 !important;
        page-break-after: always;
        break-after: page;
    }
}
"""


def inject_print_css(html: str, mode: PdfMode) -> str:
    """Inject ``@media print`` rules into the HTML document.

    Args:
        html: Complete HTML document string.
        mode: Export mode (continuous or paginated).

    Returns:
        HTML with print CSS injected before ``</head>``.
    """
    css = _PRINT_CSS_CONTINUOUS if mode == PdfMode.CONTINUOUS else _PRINT_CSS_PAGINATED
    return html.replace("</head>", f"<style>{css}</style>\n</head>")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Conversion factors to millimetres
_UNIT_TO_MM = {"mm": 1.0, "cm": 10.0, "in": 25.4, "px": 0.264583, "pt": 0.352778}

# Standard page formats — (width_mm, height_mm) in portrait orientation.
# Formats marked (*) are presentation ratios stored in landscape directly;
# _page_dimensions_mm() handles the landscape flag for all entries.
_PAGE_FORMATS_MM: dict[str, tuple[float, float]] = {
    # Paper formats (portrait)
    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
    "A5": (148, 210),
    "A6": (105, 148),
    "Letter": (215.9, 279.4),
    "Legal": (215.9, 355.6),
    "Tabloid": (279.4, 431.8),
    "Ledger": (431.8, 279.4),
    # Presentation formats (landscape, 254mm = 10in reference height)
    "16:9": (338.7, 190.5),
    "16:10": (323.8, 202.4),
    "4:3": (270.9, 203.2),
}

# Screen DPI used by Chromium for CSS pixel conversion
_SCREEN_DPI = 96


def _parse_margin(value: str) -> float:
    """Parse a CSS margin string (e.g. '10mm', '0', '1in') to millimetres."""
    value = value.strip()
    if not value:
        return 0.0
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*(mm|cm|in|px|pt)?$", value)
    if not m:
        return 0.0
    num = float(m.group(1))
    unit = m.group(2) or "mm"
    return num * _UNIT_TO_MM.get(unit, 1.0)


# Formats natively supported by Playwright's `format` parameter.
_PLAYWRIGHT_NATIVE_FORMATS = {
    "a0", "a1", "a2", "a3", "a4", "a5", "a6",
    "letter", "legal", "tabloid", "ledger",
}

# Reference height for ratio-based formats (190.5mm ≈ 7.5in)
_RATIO_REF_HEIGHT_MM = 190.5


def _page_dimensions_mm(fmt: str, landscape: bool) -> tuple[float, float]:
    """Return (width_mm, height_mm) for a page format and orientation.

    Supports named formats (A4, Letter, 16:9, ...) and free-form ratios
    like ``"21:9"`` or ``"2.35:1"``.

    Args:
        fmt: Page format name or ratio (case-insensitive).
        landscape: If True, swap width and height for paper formats.
            Ratio-based formats (containing ``:``) are always landscape
            and ignore this flag.

    Returns:
        (width_mm, height_mm) tuple.

    Raises:
        ValueError: If the format is not recognized or the ratio is invalid.
    """
    # Case-insensitive lookup in known formats
    key = next((k for k in _PAGE_FORMATS_MM if k.lower() == fmt.lower()), None)
    if key is not None:
        w, h = _PAGE_FORMATS_MM[key]
        if landscape and ":" not in key:
            w, h = h, w
        return w, h

    # Free-form ratio: "W:H" (e.g. "21:9", "2.35:1")
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*:\s*([0-9]*\.?[0-9]+)\s*$", fmt)
    if m:
        rw, rh = float(m.group(1)), float(m.group(2))
        if rw <= 0 or rh <= 0:
            raise ValueError(f"Invalid ratio {fmt!r}: both values must be positive.")
        h = _RATIO_REF_HEIGHT_MM
        w = h * rw / rh
        return w, h

    raise ValueError(
        f"Unknown page format {fmt!r}. "
        f"Supported: {', '.join(_PAGE_FORMATS_MM.keys())} or a ratio like '16:9'."
    )


def _is_native_playwright_format(fmt: str) -> bool:
    """Return True if Playwright supports this format name directly."""
    return fmt.lower() in _PLAYWRIGHT_NATIVE_FORMATS


def _compute_viewport_width(
    fmt: str,
    landscape: bool,
    margin_left: str,
    margin_right: str,
    scale: float,
) -> int:
    """Compute the optimal viewport width in CSS pixels for PDF export.

    The viewport is sized so that the HTML content, once rendered at this
    width and scaled by ``scale``, fills the available page width exactly.

    Args:
        fmt: Page format (e.g. "A4").
        landscape: Landscape orientation.
        margin_left: Left margin (CSS value).
        margin_right: Right margin (CSS value).
        scale: Chromium print scale factor.

    Returns:
        Viewport width in pixels (integer, minimum 800).
    """
    page_w, _ = _page_dimensions_mm(fmt, landscape)
    available_mm = page_w - _parse_margin(margin_left) - _parse_margin(margin_right)
    available_px = available_mm / 25.4 * _SCREEN_DPI
    viewport_px = available_px / max(scale, 0.1)
    return max(int(round(viewport_px)), 800)


def _inject_content_width_css(html: str, content_width: int) -> str:
    """Inject CSS to control content width in the exported HTML for PDF.

    The exported HTML (from ``generate_full_html()``) wraps content in
    ``<div class="streamtex-page">`` — NOT Streamlit's ``.stMain`` classes.
    This function targets that actual class to ensure content fills the
    viewport (which is sized to match the PDF page).

    When content_width < 100, symmetric padding narrows the content while
    the body background remains full-bleed — same logic as
    ``PageLayout(width=...)`` for on-screen display.

    Args:
        html: Complete HTML document string.
        content_width: Percentage (10–100).

    Returns:
        HTML with layout CSS injected before ``</head>``.
    """
    cw = max(10, min(100, content_width))
    padding_pct = (100 - cw) / 2

    css = (
        f".streamtex-page {{"
        f" max-width: 100% !important;"
        f" width: 100% !important;"
        f" margin: 0 !important;"
        f" padding: {padding_pct:.1f}% !important;"
        f" box-sizing: border-box !important;"
        f"}}"
    )
    return html.replace("</head>", f"<style>{css}</style>\n</head>")


# ---------------------------------------------------------------------------
# TOC → PDF Bookmarks
# ---------------------------------------------------------------------------

# CSS for headings injected into the HTML for PDF outline generation.
# Chromium requires headings to remain in normal document flow to include
# them in the PDF outline tree.  Using ``position: absolute``, ``clip``,
# or ``overflow: hidden`` causes Chromium to skip the heading entirely.
# Instead we use near-zero font size with transparent color — the heading
# occupies no visual space but stays in flow for the outline parser.
_OUTLINE_HEADING_CSS = (
    ".stx-pdf-outline-heading {"
    " font-size: 0.1px;"
    " line-height: 0;"
    " margin: 0;"
    " padding: 0;"
    " color: transparent;"
    "}"
)


def _inject_toc_headings(html: str, toc: list[dict]) -> str:
    """Inject invisible ``<h1>``–``<h6>`` headings at TOC anchor positions.

    Chromium generates PDF bookmarks (outlines) from the heading hierarchy
    in the DOM.  StreamTeX does not use native ``<hN>`` tags — it renders
    styled ``<div>``/``<p>`` elements with ``id=`` anchors instead.

    This function finds each TOC anchor in the HTML and inserts a
    screen-reader-only ``<hN>`` element right after the opening tag,
    so Chromium sees a proper heading tree and builds the bookmark panel.

    Args:
        html: Complete HTML document string.
        toc: List of TOC entry dicts with ``key_anchor``, ``title``, ``level``.

    Returns:
        HTML with hidden headings injected and outline CSS added.
    """
    if not toc:
        return html

    injected = False
    for entry in toc:
        anchor = entry.get("key_anchor", "")
        title = entry.get("title", "")
        level = min(max(entry.get("level", 1), 1), 6)
        if not anchor or not title:
            continue

        # Find the element with id="<anchor>" and inject <hN> right after it.
        # Pattern: id='anchor' or id="anchor" followed by the rest of the tag.
        for quote in ('"', "'"):
            target = f"id={quote}{anchor}{quote}"
            if target not in html:
                continue
            # Inject the heading right after the closing > of the element
            # that carries the anchor id.
            idx = html.index(target)
            close_bracket = html.index(">", idx)
            heading = (
                f'<h{level} class="stx-pdf-outline-heading">'
                f'{title}</h{level}>'
            )
            html = html[:close_bracket + 1] + heading + html[close_bracket + 1:]
            injected = True
            break

    # Only add CSS if at least one heading was injected
    if injected:
        html = html.replace("</head>", f"<style>{_OUTLINE_HEADING_CSS}</style>\n</head>")

    return html


# ---------------------------------------------------------------------------
# Base URL injection (issue #44)
# ---------------------------------------------------------------------------

_BASE_TAG_RE = re.compile(r"<base[\s/>]", re.IGNORECASE)
_HEAD_OPEN_RE = re.compile(r"<head(?=[\s>])[^>]*>", re.IGNORECASE)
_HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)


def inject_base_href(html: str, base_url: str) -> str:
    """Inject ``<base href="{base_url}">`` right after ``<head>``.

    No-op when *base_url* is empty, when the document's head already
    declares a ``<base>`` (author's choice wins — the guard only scans
    the head section, so a literal ``<base`` in a body script or comment
    cannot block injection), or when there is no ``<head>`` to anchor to
    (matched case-insensitively, attributes tolerated).  The URL's PATH
    is normalised to end with ``/`` (URL resolution semantics: without
    it the last path segment would be dropped), its query/fragment are
    stripped (irrelevant to relative resolution), and the value is
    HTML-attribute escaped.
    """
    if not base_url:
        return html
    head_open = _HEAD_OPEN_RE.search(html)
    if not head_open:
        return html
    head_close = _HEAD_CLOSE_RE.search(html, head_open.end())
    head_section = html[head_open.end():
                        head_close.start() if head_close else len(html)]
    if _BASE_TAG_RE.search(head_section):
        return html
    from urllib.parse import urlsplit, urlunsplit
    try:
        parts = urlsplit(base_url)
        p = parts.path or "/"
        if not p.endswith("/"):
            p += "/"
        base_url = urlunsplit((parts.scheme, parts.netloc, p, "", ""))
    except ValueError:
        # A malformed configured base must never crash the export —
        # leave the HTML unchanged (historical behaviour).
        return html
    tag = f'<base href="{_attr_escape(base_url, quote=True)}">'
    return html[:head_open.end()] + tag + html[head_open.end():]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_pdf(
    html: str,
    output_path: Optional[str] = None,
    config: Optional[PdfConfig] = None,
    toc: Optional[list[dict]] = None,
) -> bytes:
    """Export an HTML document to PDF using Playwright (Chromium headless).

    Requires ``playwright`` to be installed (``uv add "streamtex[pdf]"``).
    On first use, run ``playwright install chromium`` to download the browser.

    The viewport width is automatically computed from the page format, margins,
    and scale so that the content fills the PDF page width exactly.  Use
    ``content_width`` (10–100%) to narrow the content area while keeping the
    background full-bleed (same logic as ``PageLayout(width=...)``).

    When ``toc`` is provided, invisible HTML headings are injected at the
    anchor positions and Chromium generates native PDF bookmarks (outlines)
    that appear in the reader's sidebar panel.

    Args:
        html: Complete HTML document (e.g. from ``generate_export_html()``).
        output_path: Optional file path to write the PDF. If None, PDF is
                     only returned as bytes.
        config: PDF configuration. Defaults to PdfConfig().
            Set ``theme_bg`` and ``theme_text`` on the config to match the
            current Streamlit theme (``book.py`` does this automatically).
        toc: Optional list of TOC entry dicts (from cache or ``toc_entries()``).
            Each dict must have ``key_anchor``, ``title``, and ``level`` keys.
            When provided, PDF bookmarks are generated from the TOC hierarchy.

    Returns:
        PDF content as bytes.

    Raises:
        ImportError: If playwright is not installed.
        RuntimeError: If Chromium is not installed.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "PDF export requires playwright. Install it with:\n"
            "  uv add \"streamtex[pdf]\"\n"
            "  playwright install chromium"
        ) from None

    cfg = config or PdfConfig()
    html = inject_print_css(html, cfg.mode)

    # Resolve relative media (src=, poster=, CSS url()) against the
    # configured base — issue #44.  No-op when base_url is empty.
    html = inject_base_href(html, cfg.base_url)

    # Inject content-width CSS if narrower than 100%
    html = _inject_content_width_css(html, cfg.content_width)

    # Inject TOC headings for PDF bookmark generation
    use_outline = False
    if toc:
        html = _inject_toc_headings(html, toc)
        use_outline = True

    text = cfg.theme_text

    # Page numbers footer (inline styles only — Chromium template parser is restrictive)
    footer = cfg.footer_template
    if cfg.page_numbers and not footer:
        footer = (
            f'<div style="font-size:18pt; font-weight:bold; width:100%; text-align:center;'
            f' color:{text}; margin:0; padding:0; line-height:1;">'
            '<span class="pageNumber"></span> / '
            '<span class="totalPages"></span>'
            '</div>'
        )

    header = cfg.header_template

    # Force minimum bottom margin when page_numbers is enabled
    # (Chromium renders footer template in the margin area — needs space)
    margin_bottom = cfg.margin_bottom
    if cfg.page_numbers and _parse_margin(margin_bottom) < 0.01:
        margin_bottom = "0.01mm"

    display_header_footer = bool(cfg.header_template or footer or cfg.page_numbers)

    # Compute viewport to match the PDF page width
    viewport_w = _compute_viewport_width(
        cfg.format, cfg.landscape, cfg.margin_left, cfg.margin_right, cfg.scale,
    )

    # Resolve page size: native Playwright format or explicit width/height
    if _is_native_playwright_format(cfg.format):
        page_size_kwargs = {"format": cfg.format, "landscape": cfg.landscape}
    else:
        # Custom format (16:9, 16:10, 4:3, or free-form ratio) → explicit mm
        w_mm, h_mm = _page_dimensions_mm(cfg.format, cfg.landscape)
        page_size_kwargs = {"width": f"{w_mm}mm", "height": f"{h_mm}mm"}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": viewport_w, "height": 900})
        page.set_content(html, wait_until="networkidle")

        pdf_bytes = page.pdf(
            **page_size_kwargs,
            print_background=cfg.print_background,
            scale=cfg.scale,
            margin={
                "top": cfg.margin_top,
                "bottom": margin_bottom,
                "left": cfg.margin_left,
                "right": cfg.margin_right,
            },
            display_header_footer=display_header_footer,
            header_template=header or "<span></span>",
            footer_template=footer or "<span></span>",
            outline=use_outline,
            tagged=use_outline,
        )
        browser.close()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
