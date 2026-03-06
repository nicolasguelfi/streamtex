"""PDF Export — convert StreamTeX HTML to PDF via Playwright (Chromium headless).

Requires the optional ``pdf`` extra::

    uv add "streamtex[pdf]"
    playwright install chromium
"""

from dataclasses import dataclass
from enum import Enum
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

    header_template: str = ""
    """HTML template for page header (Chromium print header format)."""

    footer_template: str = ""
    """HTML template for page footer (Chromium print footer format)."""

    page_numbers: bool = False
    """Add page numbers in the footer (e.g. '1 / 5')."""


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
# Public API
# ---------------------------------------------------------------------------

def export_pdf(
    html: str,
    output_path: Optional[str] = None,
    config: Optional[PdfConfig] = None,
) -> bytes:
    """Export an HTML document to PDF using Playwright (Chromium headless).

    Requires ``playwright`` to be installed (``uv add "streamtex[pdf]"``).
    On first use, run ``playwright install chromium`` to download the browser.

    Args:
        html: Complete HTML document (e.g. from ``generate_export_html()``).
        output_path: Optional file path to write the PDF. If None, PDF is
                     only returned as bytes.
        config: PDF configuration. Defaults to PdfConfig().

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

    # Page numbers footer
    footer = cfg.footer_template
    if cfg.page_numbers and not footer:
        footer = (
            '<div style="font-size:10px; width:100%; text-align:center;">'
            '<span class="pageNumber"></span> / <span class="totalPages"></span>'
            '</div>'
        )

    display_header_footer = bool(cfg.header_template or footer or cfg.page_numbers)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")

        pdf_bytes = page.pdf(
            format=cfg.format,
            landscape=cfg.landscape,
            print_background=cfg.print_background,
            scale=cfg.scale,
            margin={
                "top": cfg.margin_top,
                "bottom": cfg.margin_bottom,
                "left": cfg.margin_left,
                "right": cfg.margin_right,
            },
            display_header_footer=display_header_footer,
            header_template=cfg.header_template or "<span></span>",
            footer_template=footer or "<span></span>",
        )
        browser.close()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
