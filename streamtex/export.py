"""HTML Export — self-contained HTML export for StreamTeX books.

Provides a dual-rendering pipeline: each content call goes to both
Streamlit (st.html) and an optional export buffer.  Context managers
(st_block, st_grid, st_list) push/pop wrapper tags so the exported
HTML reproduces the nesting structure with inline styles.
"""

import base64
import hashlib
import importlib.resources as resources
import io
import os
import re
import zipfile
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


class AssetMode(Enum):
    """Controls how media assets are stored in HTML exports."""

    EMBEDDED = "embedded"
    """Base64 data URIs inline in the HTML (legacy, single file)."""

    EXTERNAL = "external"
    """Assets saved to a ``data/`` folder, HTML uses relative paths (ZIP download)."""


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

    asset_mode: AssetMode = AssetMode.EXTERNAL
    """How media assets are stored: ``EMBEDDED`` (base64) or ``EXTERNAL`` (files in data/)."""


# ---------------------------------------------------------------------------
# Asset collector — extracts and deduplicates media from HTML
# ---------------------------------------------------------------------------

# Regex matching data URIs in src="..." or src='...' attributes
_DATA_URI_RE = re.compile(
    r"""(src\s*=\s*["'])"""          # group 1: src=" or src='
    r"""(data:([^;]+);base64,"""     # group 2: full data URI start, group 3: mime
    r"""([A-Za-z0-9+/=\s]+))"""      # group 4: base64 payload
    r"""(["'])""",                    # group 5: closing quote
    re.DOTALL,
)

# Map MIME types to asset subdirectories
_MIME_TO_SUBDIR = {
    "image": "images",
    "audio": "audio",
    "video": "video",
}

# Map MIME types to file extensions
_MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/x-icon": ".ico",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/ogg": ".ogg",
    "audio/flac": ".flac",
    "audio/aac": ".aac",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/ogg": ".ogv",
}


@dataclass
class _AssetEntry:
    """An extracted media asset."""
    data: bytes
    mime: str
    relative_path: str  # e.g. "data/images/a1b2c3d4.png"


class AssetCollector:
    """Collects media assets during export and deduplicates by content hash."""

    def __init__(self) -> None:
        self._assets: dict[str, _AssetEntry] = {}  # content hash → entry
        self._data_uri_to_path: dict[str, str] = {}  # full data URI → relative path

    @property
    def assets(self) -> dict[str, _AssetEntry]:
        return self._assets

    def register_data_uri(self, data_uri: str) -> str:
        """Register a ``data:<mime>;base64,...`` URI and return the relative path.

        If the same content was already registered, returns the existing path
        (deduplication by SHA-256).
        """
        if data_uri in self._data_uri_to_path:
            return self._data_uri_to_path[data_uri]

        # Parse the data URI
        m = re.match(r"data:([^;]+);base64,(.*)", data_uri, re.DOTALL)
        if not m:
            return data_uri  # not a data URI, return unchanged
        mime = m.group(1)
        b64_payload = m.group(2).strip()

        try:
            raw = base64.b64decode(b64_payload)
        except Exception:
            return data_uri

        return self._register_bytes(raw, mime, data_uri)

    def register_file(self, file_path: str, mime: str) -> str:
        """Register a local file and return the relative path."""
        try:
            with open(file_path, "rb") as f:
                raw = f.read()
        except OSError:
            return file_path
        # Use original filename as hint
        original_name = os.path.basename(file_path)
        return self._register_bytes(raw, mime, _original_name=original_name)

    def register_bytes(self, raw: bytes, mime: str) -> str:
        """Register raw bytes and return the relative path."""
        return self._register_bytes(raw, mime)

    def _register_bytes(self, raw: bytes, mime: str,
                        data_uri: str | None = None,
                        _original_name: str = "") -> str:
        content_hash = hashlib.sha256(raw).hexdigest()[:12]

        if content_hash in self._assets:
            path = self._assets[content_hash].relative_path
            if data_uri:
                self._data_uri_to_path[data_uri] = path
            return path

        # Determine subdirectory and extension
        media_type = mime.split("/")[0] if "/" in mime else "image"
        subdir = _MIME_TO_SUBDIR.get(media_type, "other")
        ext = _MIME_TO_EXT.get(mime, "")
        if not ext and _original_name:
            _, ext = os.path.splitext(_original_name)
        if not ext:
            ext = ".bin"

        # Use original name if available, otherwise hash-based name
        if _original_name:
            stem = os.path.splitext(_original_name)[0]
            filename = f"{stem}_{content_hash[:6]}{ext}"
        else:
            filename = f"{content_hash}{ext}"

        relative_path = f"data/{subdir}/{filename}"

        entry = _AssetEntry(data=raw, mime=mime, relative_path=relative_path)
        self._assets[content_hash] = entry
        if data_uri:
            self._data_uri_to_path[data_uri] = relative_path
        return relative_path

    def rewrite_html(self, html: str) -> str:
        """Replace all base64 data URIs in *html* with relative asset paths."""
        def _replace(match):
            prefix = match.group(1)    # src="
            data_uri = match.group(2)  # data:...;base64,...
            quote = match.group(5)     # closing quote
            path = self.register_data_uri(f"{data_uri}")
            return f"{prefix}{path}{quote}"
        return _DATA_URI_RE.sub(_replace, html)

    def to_zip(self, html: str, base_name: str) -> bytes:
        """Create a ZIP containing the HTML file and all assets in data/.

        The HTML has all data URIs replaced with relative paths.
        """
        rewritten = self.rewrite_html(html)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{base_name}/{base_name}.html", rewritten)
            for entry in self._assets.values():
                zf.writestr(f"{base_name}/{entry.relative_path}", entry.data)
        buf.seek(0)
        return buf.getvalue()

    def write_to_disk(self, html: str, output_dir: str, base_name: str) -> str:
        """Write HTML + assets to disk. Returns the HTML file path."""
        rewritten = self.rewrite_html(html)
        out = Path(output_dir) / base_name
        out.mkdir(parents=True, exist_ok=True)
        html_path = out / f"{base_name}.html"
        html_path.write_text(rewritten, encoding="utf-8")
        for entry in self._assets.values():
            asset_path = out / entry.relative_path
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            asset_path.write_bytes(entry.data)
        return str(html_path)

    def reset(self) -> None:
        self._assets.clear()
        self._data_uri_to_path.clear()


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
    """Read a Streamlit theme color from config, with fallback.

    When ``theme.base`` is ``"dark"`` but individual colors are not set,
    use Streamlit's dark-mode defaults instead of light-mode fallbacks.
    """
    try:
        val = st.get_option(option)
        if val:
            return val
    except Exception:
        pass
    # Detect dark theme base and provide matching defaults
    try:
        base = st.get_option("theme.base")
        if base == "dark":
            _dark_defaults = {
                "theme.backgroundColor": "#0e1117",
                "theme.textColor": "#fafafa",
                "theme.primaryColor": "#ff4b4b",
            }
            return _dark_defaults.get(option, fallback)
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
_asset_collector: Optional[AssetCollector] = None


def reset_export_buffer(config: ExportConfig = None) -> None:
    """Initialise or reset the global export buffer."""
    global _buffer, _asset_collector
    if config is None or not config.enabled:
        _buffer = None
        _asset_collector = None
        return
    if _buffer is not None:
        _buffer.config = config
        _buffer.reset()
    else:
        _buffer = HtmlExportBuffer(config)
    # Always reset the asset collector
    if config.asset_mode == AssetMode.EXTERNAL:
        _asset_collector = AssetCollector()
    else:
        _asset_collector = None


def is_export_active() -> bool:
    """Return True when the export buffer is collecting fragments."""
    return _buffer is not None


def get_asset_collector() -> Optional[AssetCollector]:
    """Return the global asset collector, or None when assets are embedded."""
    return _asset_collector


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
