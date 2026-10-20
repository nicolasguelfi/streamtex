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
import logging
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

from .constants import PAGE_PADDING, PAGE_WIDTH

if TYPE_CHECKING:
    from .pdf_export import PdfConfig

logger = logging.getLogger(__name__)


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
    """Base64 data URIs inline in the HTML (single file)."""

    EXTERNAL = "external"
    """Assets saved to a ``data/`` folder, HTML uses relative paths (ZIP download)."""


@dataclass
class ExportConfig:
    """Settings for the HTML export feature.

    Used in two ways:

    1. **Internal buffer config** — passed by ``st_book()`` to
       ``reset_export_buffer()``.  Only ``enabled``, ``page_title``,
       ``page_width``, ``page_padding``, and ``zoom`` matter here.

    2. **Auto-export config** — passed via ``st_book(exports=[...])``
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

    theme_bg: str | None = None
    """Override background color for the exported HTML (e.g. ``"#0e1117"`` for dark).
    When set, takes precedence over Streamlit theme detection."""

    theme_text: str | None = None
    """Override text color for the exported HTML (e.g. ``"#fafafa"`` for dark)."""

    theme_primary: str | None = None
    """Override link/primary color for the exported HTML."""

    lang: str = "en"
    """BCP 47 language tag written to the ``<html lang>`` attribute of the
    exported document (``"en"``, ``"fr"``, ``"de-CH"``...). One static export
    per language passes its own value here — the CLI resolves it from
    ``stx export html --lang`` or the ``STX_LANG`` environment variable."""


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


_SERVED_ATTR_RE = re.compile(r'((?:src|poster)=")(app/static/[^"]+)(")')


def materialize_served_media(html: str,
                             collector: Optional[AssetCollector] = None,
                             project_root: Optional[str] = None) -> str:
    """Post-pass on EXPORT HTML: make server-relative media self-contained.

    The "served, never inlined" pattern (``configure_image_path``) emits
    ``src="app/static/..."`` URLs that only a running server resolves —
    a downloaded export opened over ``file://`` shows broken media
    (issue #48).  This rewrites ``src=``/``poster=`` attributes starting
    with ``app/static/`` by locating the bytes on disk:

    1. the ``configure_image_path`` base + ``fs_root`` (the same
       resolution ``crop=`` uses — ``image_crop._find_served_file``);
    2. Streamlit's ``app/static`` serving convention (app static dir);
    3. ``<project_root>/static/`` when *project_root* is given
       (headless CLI export, where the script context is absent).

    With a *collector* (``AssetMode.EXTERNAL``) the file is registered
    (SHA-256 dedup) and the attribute points into ``data/``; without
    one (``EMBEDDED``) it becomes a base64 data URI.  An unresolvable
    reference is left unchanged (deployments serving ``/app/static/``
    keep working) with one warning per path.  The live render is
    untouched — this runs on the export copy only.  CSS ``url()``
    references are not covered.
    """
    if "app/static/" not in html:
        return html
    import logging
    import mimetypes

    from .image import _static_image_base
    from .image_crop import _app_static_dir, _find_served_file

    log = logging.getLogger(__name__)
    warned: set = set()

    def _safe_rel(rel: str) -> bool:
        """Pure descending relative path — no traversal, no absolute."""
        if not rel or os.path.isabs(rel) or "\\" in rel:
            return False
        return ".." not in rel.split("/")

    def _contained(path: str, root: str) -> bool:
        try:
            return os.path.realpath(path).startswith(
                os.path.realpath(root) + os.sep)
        except OSError:  # pragma: no cover — filesystem drift
            return False

    def _locate(value: str) -> str:
        rest = value[len("app/static/"):]
        if not _safe_rel(rest):
            return ""
        base = _static_image_base or ""
        if base and value.startswith(base + "/"):
            sub = value[len(base) + 1:]
            if _safe_rel(sub):
                p = _find_served_file(sub)
                if p:
                    return p
        try:
            root = _app_static_dir()
            p = os.path.join(root, rest)
            if os.path.isfile(p) and _contained(p, root):
                return p
        except Exception:  # pragma: no cover — script-context drift
            pass
        if project_root:
            root = os.path.join(project_root, "static")
            p = os.path.join(root, rest)
            if os.path.isfile(p) and _contained(p, root):
                return p
        return ""

    def _replace(m):
        prefix, value, quote = m.group(1), m.group(2), m.group(3)
        file_path = _locate(value)
        if not file_path:
            if value not in warned:
                warned.add(value)
                log.warning(
                    "Export: served media not found on disk, left as-is: %s",
                    value)
            return m.group(0)
        mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        if collector is not None:
            new = collector.register_file(file_path, mime)
            if new == file_path:
                # register_file returns its input on read failure — do
                # NOT write an absolute filesystem path into the export.
                return m.group(0)
        else:
            try:
                with open(file_path, "rb") as f:
                    raw = f.read()
            except OSError:
                return m.group(0)
            new = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
        return f"{prefix}{new}{quote}"

    return _SERVED_ATTR_RE.sub(_replace, html)


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
        # ExportConfig > the session's theme (kept by st_book, as the PDF
        # uses it; a runtime light/dark toggle will write there, #20) > config.
        bg = (c.theme_bg or _session_theme_color("_stx_theme_bg")
              or _get_theme_color("theme.backgroundColor", "#fff"))
        text = (c.theme_text or _session_theme_color("_stx_theme_text")
                or _get_theme_color("theme.textColor", "#333"))
        link = c.theme_primary or _get_theme_color("theme.primaryColor", "#1155cc")
        zoom_css = f"  zoom: {c.zoom};\n" if c.zoom != 1.0 else ""
        return (
            "<!DOCTYPE html>\n"
            f"<html lang=\"{_escape_lang(c.lang)}\">\n<head>\n"
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
            f"/* Mirror Streamlit stVerticalBlock: all children stretch to full width */\n"
            f".stx-block > * {{ align-self: stretch; }}\n"
            f"</style>\n"
            f"</head>\n<body>\n"
            f"<div class=\"streamtex-page\">\n"
            f"{body}\n"
            f"</div>\n"
            f"{_LIST_INSIDE_JS}\n"
            f"{_video_stage_js(body)}"
            f"</body>\n</html>\n"
        )


# ---------------------------------------------------------------------------
# Marker mode in the export — the twin of `.stx-list-item--inside` live
# ---------------------------------------------------------------------------
# Until 0.7.33 the exported document carried `ol, ul { text-align: left; }`,
# the export twin of the inline `text-align: left` the live list root used to
# force: it made a centred page or block unable to centre its lists, exactly
# the defect 0.7.33 fixed on the live side only.  The rule is gone, so lists
# inherit `text-align` like every other element.
#
# `list-style-position` does not follow `text-align` on its own, though, and no
# selector can match on an INHERITED value — which is why this runs in the
# document instead of in the stylesheet.  It is the same rule the marker
# observer applies live, resolved by the same engine: a list whose effective
# alignment is `center` or `right` takes its marker inside the line.  A list
# that declares `text_align=` already carries the property inline from
# `_list_export_css`, so this only ever adds what inheritance implied.
#
# Moving the marker inside is not enough on its own (#112): an exported item is
# `<li><div class="stx-el">text</div>…</li>`, and that `div` is a block, so the
# marker stood alone on its line and the text started below it.  The live
# inside-mode rules (`stx_global.css`) render the item's FIRST element inline;
# the script does the same here, for every list whose marker is inside —
# declared or implied.  Only that first element and its text wrapper become
# inline: a nested list, a second paragraph or a layout block stays a block.
#
# The marker itself is drawn the live way too (#112, A'): the browser's inside
# marker is about 1.3 em wide, the live `::before` is a box of
# `--stx-list-marker-width` (1.2rem), right-aligned, followed by
# `--stx-list-marker-gap` (0.5rem).  `list.py` writes the live symbol on each
# exported item (`data-stx-marker`, or `data-stx-marker-counter` for an
# ordered list); the script puts it in a span with those metrics and hides the
# native marker.  An item without the attribute keeps the native marker, and
# an outside-mode list (left-aligned) is untouched.
_LIST_INSIDE_JS = (
    "<script>\n"
    "(function () {\n"
    "  var INSIDE = { center: 1, right: 1, end: 1 };\n"
    "  var TEXT = /^(P|H[1-6])$/;\n"
    "  var PHRASING = /^(SPAN|A|B|I|EM|STRONG|CODE|SUB|SUP|SMALL|MARK|BR)$/;\n"
    "  function textOnly(e) {\n"
    "    for (var k = 0; k < e.children.length; k++) {\n"
    "      if (!PHRASING.test(e.children[k].tagName)) return false;\n"
    "    }\n"
    "    return true;\n"
    "  }\n"
    "  function roman(n) {\n"
    "    var v = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1];\n"
    "    var r = ['m', 'cm', 'd', 'cd', 'c', 'xc', 'l', 'xl', 'x', 'ix', 'v', 'iv', 'i'];\n"
    "    var out = '';\n"
    "    for (var k = 0; k < v.length; k++) { while (n >= v[k]) { out += r[k]; n -= v[k]; } }\n"
    "    return out;\n"
    "  }\n"
    "  function alpha(n) {\n"
    "    var out = '';\n"
    "    while (n > 0) { n--; out = String.fromCharCode(97 + n % 26) + out; n = Math.floor(n / 26); }\n"
    "    return out;\n"
    "  }\n"
    "  function counter(style, n) {\n"
    "    if (style === 'lower-roman') return roman(n);\n"
    "    if (style === 'upper-roman') return roman(n).toUpperCase();\n"
    "    if (style === 'lower-alpha' || style === 'lower-latin') return alpha(n);\n"
    "    if (style === 'upper-alpha' || style === 'upper-latin') return alpha(n).toUpperCase();\n"
    "    return String(n);\n"
    "  }\n"
    "  function marker(li, n) {\n"
    "    var sym = li.getAttribute('data-stx-marker');\n"
    "    var cnt = li.getAttribute('data-stx-marker-counter');\n"
    "    if (sym === null && cnt === null) return false;\n"
    "    var m = document.createElement('span');\n"
    "    m.className = 'stx-li-marker';\n"
    "    m.setAttribute('aria-hidden', 'true');\n"
    "    m.textContent = sym !== null ? sym : counter(cnt, n) + '.';\n"
    "    m.style.display = 'inline-block';\n"
    "    m.style.minWidth = '1.2rem';\n"
    "    m.style.marginInlineEnd = '0.5rem';\n"
    "    m.style.textAlign = 'right';\n"
    "    li.insertBefore(m, li.firstChild);\n"
    "    var gap = m.nextSibling;\n"
    "    if (gap && gap.nodeType === 3 && !gap.textContent.trim()) gap.remove();\n"
    "    return true;\n"
    "  }\n"
    "  function inlineFirst(list) {\n"
    "    var n = 0, drawn = false;\n"
    "    for (var j = 0; j < list.children.length; j++) {\n"
    "      var li = list.children[j];\n"
    "      if (li.tagName !== 'LI') continue;\n"
    "      n++;\n"
    "      var first = li.firstElementChild, zooms = [];\n"
    "      if (marker(li, n)) drawn = true;\n"
    "      while (first && first.classList.contains('stx-zoom')) {\n"  # st_zoom around the text (#112)
    "        zooms.push(first); first = first.firstElementChild;\n"
    "      }\n"
    "      if (!first || !first.classList.contains('stx-el')) continue;\n"
    "      var inner = first.firstElementChild;\n"
    "      if (inner && !PHRASING.test(inner.tagName)) {\n"
    "        if (!(TEXT.test(inner.tagName) || inner.tagName === 'DIV') || !textOnly(inner)) continue;\n"
    "        inner.style.display = 'inline';\n"
    "      }\n"
    "      first.style.display = 'inline';\n"
    "      for (var z = 0; z < zooms.length; z++) zooms[z].style.display = 'inline';\n"
    "    }\n"
    "    if (drawn) list.style.listStyleType = 'none';\n"
    "  }\n"
    "  function apply() {\n"
    "    var lists = document.querySelectorAll('ul, ol');\n"
    "    for (var i = 0; i < lists.length; i++) {\n"
    "      var el = lists[i];\n"
    "      if (!el.style.listStylePosition && INSIDE[getComputedStyle(el).textAlign]) {\n"
    "        el.style.listStylePosition = 'inside';\n"
    "      }\n"
    "      if (el.style.listStylePosition === 'inside') inlineFirst(el);\n"
    "    }\n"
    "  }\n"
    "  if (document.readyState === 'loading') {\n"
    "    document.addEventListener('DOMContentLoaded', apply);\n"
    "  } else { apply(); }\n"
    "})();\n"
    "</script>"
)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _escape_lang(lang: str | None) -> str:
    """Return a safe ``<html lang>`` value — a BCP 47-looking tag or ``"en"``.

    Anything that is not letters/digits/hyphens (an injection attempt, an
    empty string, ``None``) falls back to ``"en"`` rather than breaking the
    document head.
    """
    if isinstance(lang, str) and re.fullmatch(r"[A-Za-z]{2,8}(-[A-Za-z0-9]{1,8})*", lang):
        return lang
    return "en"


def _session_theme_color(key: str) -> str | None:
    """A theme colour ``st_book`` keeps in session state, or None (no session)."""
    try:
        value = st.session_state.get(key)
    except Exception:  # noqa: BLE001 — outside a Streamlit session
        return None
    return value if isinstance(value, str) and value else None


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
        logger.debug("Failed to read Streamlit theme option '%s'", option, exc_info=True)
    # Detect dark theme base and provide matching defaults.  The values
    # below mirror what Streamlit 1.56's frontend resolves for a project
    # that declares only ``base = "dark"`` — they are NOT defined as
    # constants in the Streamlit package (the theme provider computes
    # them in React), so we encode them here so the static export stays
    # visually aligned with the live app.  Update these when bumping the
    # Streamlit baseline.
    try:
        base = st.get_option("theme.base")
        if base == "dark":
            _dark_defaults = {
                "theme.backgroundColor": "#0e1117",
                "theme.textColor": "#fafafa",
                "theme.primaryColor": "#ff4b4b",
                # Sidebar background (= Streamlit ``secondaryBackgroundColor``
                # when no per-sidebar override is set).
                "theme.secondaryBackgroundColor": "#1C1E1F",
                # Default link colour in dark theme.
                "theme.linkColor": "#43A9FB",
            }
            return _dark_defaults.get(option, fallback)
    except Exception:
        logger.debug("Failed to detect dark theme base", exc_info=True)
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


# ---------------------------------------------------------------------------
# Cache-build flag — lets interactive-only widgets skip rendering
# ---------------------------------------------------------------------------

_cache_building: bool = False


def set_cache_building(value: bool) -> None:
    """Set the cache-building flag (called by ``_build_page_cache``)."""
    global _cache_building
    _cache_building = value


def is_cache_building() -> bool:
    """Return True when ``_build_page_cache`` is rendering blocks."""
    return _cache_building


def get_asset_collector() -> Optional[AssetCollector]:
    """Return the global asset collector, or None when assets are embedded."""
    return _asset_collector


#: Page sentinels in the export (#106): ``<!--stx-page:N-->`` marks where
#: page N of the page map starts, so a paginated HTML export can cut the
#: document. Only inserted when a paginated export is requested.
PAGE_SENTINEL = "<!--stx-page:{n}-->"
_PAGE_SENTINEL_RE = re.compile(r"<!--stx-page:(\d+)-->\n?")


def export_root_position() -> Optional[int]:
    """Number of top-level fragments, or ``None`` inside an open wrapper / no buffer."""
    if _buffer is None or len(_buffer._stack) != 1:
        return None
    return len(_buffer._stack[0])


def export_insert_root(pos: int, html: str) -> None:
    """Insert *html* as a top-level fragment at *pos* (page sentinels)."""
    if _buffer is not None:
        _buffer._stack[0].insert(pos, html)


def strip_page_sentinels(html: str) -> str:
    """The document without its page sentinels (the continuous export)."""
    return _PAGE_SENTINEL_RE.sub("", html)


_MARKER_DIV_RE = re.compile(r'class="streamtex-marker" data-marker-index="(\d+)"')
_IMG_TAG_RE = re.compile(r"<img\b(?![^>]*\bloading=)", re.IGNORECASE)


def lazy_load_images(html: str, markers: Optional[list] = None) -> str:
    """An HTML export whose images load as the reader nears them (#115).

    The images of the document's first slide (before its second stop
    marker) load at once, every later ``<img>`` gets ``loading="lazy"
    decoding="async"``.  Without a second stop, a document of one slide
    keeps all its images, and a document without markers its first image
    only.  An ``<img>`` that already has ``loading=`` is left as is.  For
    the export copies only: the live page and the PDF (printed from a copy
    without it) are unchanged.  *markers* (``cache["markers"]``) tells the
    stops apart; without it every marker counts as a stop.
    """
    stops = None if not markers else {m["index"] for m in markers if m.get("stop", True)}
    seen = [m.start() for m in _MARKER_DIV_RE.finditer(html)
            if stops is None or int(m.group(1)) in stops]
    if len(seen) >= 2:
        cut = seen[1]
    elif seen:
        return html
    else:
        first = _IMG_TAG_RE.search(html)
        if first is None:
            return html
        cut = first.end()
    return html[:cut] + _IMG_TAG_RE.sub('<img loading="lazy" decoding="async"', html[cut:])


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


def apply_view_to_export_html(html: str, *, built_view: Optional[tuple] = None,
                              page_width: str, zoom: float) -> str:
    """Give an already generated export the current view's page width and zoom.

    The full-book HTML is built once per session; when the view changed
    since (*built_view* = ``(page_width, zoom)`` it was built with), a later
    rule on ``.streamtex-page`` replaces the old values (#110). Blocks never
    read the view's width or zoom, only this page rule does, so no rebuild
    is needed. Unchanged when the view is the same.
    """
    if built_view is not None and tuple(built_view) == (page_width, zoom):
        return html
    css = f".streamtex-page {{ max-width: {page_width}; zoom: {zoom:g}; }}"
    return html.replace("</head>", f"<style>{css}</style>\n</head>", 1)


def _video_stage_js(body: str) -> str:
    """The video stage script (#56), once, when the page has a staged video."""
    if "stx-video-marker" not in body:
        return ""
    path = os.path.join(os.path.dirname(__file__), "static", "js", "stx_video.js")
    with open(path, encoding="utf-8") as f:
        return f"<script>\n{f.read()}</script>\n"


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
        When > 0, use ``st.iframe()`` with an explicit pixel height
        instead of ``st.html()``.  This is required for content (e.g. SVG
        diagrams, bar charts) that cannot be auto-sized by the Shadow DOM
        iframe.  The iframe automatically gets ``font-family: Source Sans Pro``
        and ``margin: 0`` injected via ``_IFRAME_BASE``.
    light_bg : bool
        When True, inject ``color-scheme: light`` into the iframe so that
        diagram / image content renders on a white background even when the
        OS or browser is in dark mode.
    scrolling : bool
        **No-op.**  ``st.iframe`` (Streamlit ≥ 1.56) has no explicit
        ``scrolling`` parameter; the iframe shows native scrollbars when
        its content overflows the configured *height*.  Pass
        ``scrolling=True`` or ``scrolling=False``
        without effect — kept in the signature to avoid breaking callers.
    """
    from . import pagewalk
    if pagewalk.muted():
        return          # content of another page: neither drawn nor exported (#121)
    # Section-level horizontal spacing + zoom: wrap each fragment
    from .spacing import get_section_horizontal, get_section_zoom
    _sh = get_section_horizontal()
    _sz = get_section_zoom()
    _parts = []
    if _sh is not None:
        if _sh.left:
            _parts.append(f"margin-left: {_sh.left};")
        if _sh.right:
            _parts.append(f"margin-right: {_sh.right};")
    if _sz is not None:
        _parts.append(f"zoom: {_sz / 100};")
    if _parts:
        html = f'<div style="{" ".join(_parts)}">{html}</div>'

    live = f"{_LIGHT_SCHEME}{html}" if light_bg else html
    if height > 0:
        live = f"{_IFRAME_BASE}{live}"
        st.iframe(live, height=height)
    else:
        st.html(live)
    if _buffer is not None:
        _buffer.append(f'<div class="stx-el" style="align-self:stretch">{html}</div>')
    from .search import record_if_active
    record_if_active(html)


_render = st_html  # backward-compat alias for internal modules
