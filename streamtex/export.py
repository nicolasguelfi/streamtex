"""HTML Export — self-contained HTML export for StreamTeX books.

Provides a dual-rendering pipeline: each content call goes to both
Streamlit (st.html) and an optional export buffer.  Context managers
(st_block, st_grid, st_list) push/pop wrapper tags so the exported
HTML reproduces the nesting structure with inline styles.
"""

import importlib.resources as resources
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import streamlit as st

if TYPE_CHECKING:
    from .pdf_export import PdfConfig

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
from .constants import PAGE_PADDING, PAGE_WIDTH


class ExportMode(Enum):
    """Controls when automatic file export happens."""

    ALWAYS = "always"
    """Auto-export to disk after every render."""

    MANUAL = "manual"
    """Show sidebar panel — user clicks Generate (default behaviour)."""

    NEVER = "never"
    """Disable export entirely (no buffer, no sidebar panel)."""


@dataclass
class ExportConfig:
    """Settings for the HTML export feature.

    Used in two ways:

    1. **Internal buffer config** (legacy) — passed by ``st_book()`` to
       ``reset_export_buffer()``.  Only ``enabled``, ``page_title``,
       ``page_width``, ``page_padding``, and ``zoom`` matter here.

    2. **Auto-export config** (new) — passed via ``st_book(exports=[...])``
       to describe one output file.  The fields ``format``, ``mode``,
       ``output_dir``, ``filename``, ``timestamp``, and ``pdf`` are used.
    """

    # --- Buffer / rendering fields (used internally by the export pipeline) ---
    enabled: bool = False
    page_title: str = "StreamTeX Export"
    page_width: str = PAGE_WIDTH
    page_padding: str = PAGE_PADDING
    zoom: float = 1.0

    # --- Auto-export fields (used by st_book exports=[...]) ---
    format: str = "html"
    """Output format: ``"html"`` or ``"pdf"``."""

    mode: ExportMode = ExportMode.ALWAYS
    """When to export: ``ALWAYS`` (auto), ``MANUAL`` (sidebar), ``NEVER``."""

    output_dir: str = "./exports"
    """Directory where exported files are written."""

    filename: str | None = None
    """Base filename (without extension).  Defaults to the book name."""

    timestamp: bool = False
    """Append ``-YYMMDD-HHMMSS`` to the filename."""

    pdf: "PdfConfig | None" = None
    """PDF configuration (only used when ``format="pdf"``)."""


def build_export_filename(config: "ExportConfig", base_name: str) -> str:
    """Build the full output path for an export config.

    Parameters
    ----------
    config : ExportConfig
        The export configuration describing format, filename, timestamp, etc.
    base_name : str
        Fallback name derived from the book title (used when ``config.filename``
        is None).

    Returns
    -------
    str
        Absolute path to the output file.
    """
    name = config.filename or base_name
    ext = "pdf" if config.format == "pdf" else "html"
    if config.timestamp:
        ts = datetime.now().strftime("%y%m%d-%H%M%S")
        name = f"{name}-{ts}"
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return str(out_dir / f"{name}.{ext}")


# ---------------------------------------------------------------------------
# Buffer with nesting stack
# ---------------------------------------------------------------------------

class HtmlExportBuffer:
    """Accumulates HTML fragments with push/pop support for nested wrappers.

    ``_stack`` is a list of levels.  Each level is a list of HTML strings.
    ``push_wrapper`` opens a new level; ``pop_wrapper`` collapses it back
    into the parent level wrapped in the given close tag.
    """

    def __init__(self, config: ExportConfig):
        self.config = config
        self._stack: list[list[str]] = [[]]  # root level

    def append(self, html_fragment: str) -> None:
        """Add a fragment to the current (innermost) level."""
        self._stack[-1].append(html_fragment)

    def push_wrapper(self, open_tag: str) -> None:
        """Open a new nesting level starting with *open_tag*."""
        self._stack.append([open_tag])

    def pop_wrapper(self, close_tag: str) -> None:
        """Close the current level and collapse it into its parent."""
        if len(self._stack) <= 1:
            return  # safety: never pop the root
        level = self._stack.pop()
        level.append(close_tag)
        self._stack[-1].append("\n".join(level))

    def get_body_html(self) -> str:
        """Return all accumulated HTML from the root level."""
        return "\n".join(self._stack[0])

    def reset(self) -> None:
        self._stack = [[]]

    def generate_full_html(self) -> str:
        """Produce a complete, self-contained HTML document."""
        body = self.get_body_html()
        css = _load_default_css()
        c = self.config
        bg = _get_theme_color("theme.backgroundColor", "#fff")
        text = _get_theme_color("theme.textColor", "#333")
        link = _get_theme_color("theme.primaryColor", "#1155cc")
        zoom_css = f"  zoom: {c.zoom};\n" if c.zoom != 1.0 else ""
        return (
            "<!DOCTYPE html>\n"
            f"<html lang=\"en\">\n<head>\n"
            f"<meta charset=\"UTF-8\">\n"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            f"<title>{c.page_title}</title>\n"
            f"<style>\n"
            f"*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}\n"
            f"body {{ font-family: Arial, Helvetica, sans-serif; background: {bg}; color: {text}; }}\n"
            f"a {{ color: {link}; }}\n"
            f"{css}\n"
            f".streamtex-page {{\n"
            f"  max-width: {c.page_width};\n"
            f"  margin: 0 auto;\n"
            f"  padding: {c.page_padding};\n"
            f"{zoom_css}"
            f"}}\n"
            f"</style>\n"
            f"</head>\n<body>\n"
            f"<div class=\"streamtex-page\">\n"
            f"{body}\n"
            f"</div>\n"
            f"</body>\n</html>\n"
        )


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _get_theme_color(option: str, fallback: str) -> str:
    """Read a Streamlit theme color from config, with fallback."""
    try:
        val = st.get_option(option)
        if val:
            return val
    except Exception:
        pass
    return fallback


def _load_default_css() -> str:
    """Load the default.css bundled with StreamTeX."""
    try:
        with resources.open_text("streamtex.static", "default.css") as f:
            return f.read()
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        current_dir = os.path.dirname(__file__)
        css_path = os.path.join(current_dir, "static", "default.css")
        try:
            with open(css_path) as f:
                return f.read()
        except FileNotFoundError:
            return ""


# ---------------------------------------------------------------------------
# Global singleton (same pattern as toc.py / marker.py)
# ---------------------------------------------------------------------------

_buffer: Optional[HtmlExportBuffer] = None


def reset_export_buffer(config: ExportConfig = None) -> None:
    """Initialise or reset the global export buffer."""
    global _buffer
    if config is None or not config.enabled:
        _buffer = None
        return
    if _buffer is not None:
        _buffer.config = config
        _buffer.reset()
    else:
        _buffer = HtmlExportBuffer(config)


def is_export_active() -> bool:
    """Return True when the export buffer is collecting fragments."""
    return _buffer is not None


def export_append(html: str) -> None:
    """Append *html* to the buffer (no-op when export is inactive)."""
    if _buffer is not None:
        _buffer.append(html)


def export_push_wrapper(open_tag: str) -> None:
    """Push a wrapper open-tag onto the nesting stack (no-op when inactive)."""
    if _buffer is not None:
        _buffer.push_wrapper(open_tag)


def export_pop_wrapper(close_tag: str) -> None:
    """Pop and close the current nesting level (no-op when inactive)."""
    if _buffer is not None:
        _buffer.pop_wrapper(close_tag)


def generate_export_html() -> Optional[str]:
    """Return the full HTML document, or None when export is inactive."""
    if _buffer is None:
        return None
    return _buffer.generate_full_html()


# ---------------------------------------------------------------------------
# Export-aware widget wrapper
# ---------------------------------------------------------------------------

@contextmanager
def st_export(fallback_html: str):
    """Wrap any st.* widget to include a static HTML fallback in the export."""
    yield
    export_append(fallback_html)  # no-op when buffer is None


# ---------------------------------------------------------------------------
# Dual render — the single bridge from content modules to st.html()
# ---------------------------------------------------------------------------

# Injected into iframes to force light-mode defaults (white background,
# black text) regardless of OS / browser dark-mode settings.
_LIGHT_SCHEME = "<style>:root{color-scheme:light}</style>"

# Injected into iframes (height > 0) to ensure consistent font rendering.
_IFRAME_BASE = "<style>body{font-family:Source Sans Pro,sans-serif;margin:0;}</style>"


def st_html(html: str, *, height: int = 0, light_bg: bool = False,
            scrolling: bool = False) -> None:
    """Send *html* to Streamlit **and** to the export buffer (if active).

    This is the **single bridge** for rendering raw HTML content in StreamTeX.
    Internal modules use ``_render`` (backward-compat alias); project blocks
    should import ``st_html`` from ``streamtex``.

    Parameters
    ----------
    height : int
        When > 0, use ``components.html()`` with an explicit pixel height
        instead of ``st.html()``.  This is required for content (e.g. SVG
        diagrams, bar charts) that cannot be auto-sized by the Shadow DOM
        iframe.  The iframe automatically gets ``font-family: Source Sans Pro``
        and ``margin: 0`` injected via ``_IFRAME_BASE``.
    light_bg : bool
        When True, inject ``color-scheme: light`` into the iframe so that
        diagram / image content renders on a white background even when the
        OS or browser is in dark mode.
    scrolling : bool
        When True and *height* > 0, enable scrolling inside the iframe.
    """
    live = f"{_LIGHT_SCHEME}{html}" if light_bg else html
    if height > 0:
        import streamlit.components.v1 as components

        live = f"{_IFRAME_BASE}{live}"
        components.html(live, height=height, scrolling=scrolling)
    else:
        st.html(live)
    if _buffer is not None:
        _buffer.append(html)
    from .search import record_if_active
    record_if_active(html)


_render = st_html  # backward-compat alias for internal modules
