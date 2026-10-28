import ast
import contextlib
import copy
import functools
import hashlib
import importlib.resources as resources
import importlib.util
import itertools
import json
import logging
import os
import sys
import sysconfig
import threading
import time
import types
import weakref
from contextvars import ContextVar

import streamlit as st
from streamlit.delta_generator import DeltaGenerator as Delta
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

from . import pagewalk as _pagewalk
from . import toc as _toc_mod
from .auth import _password_gate
from .banner import BannerConfig, BannerMode, _render_banner, _render_loop_banner
from .browser import st_chrome_banner
from .code import add_wrap_all_option
from .enums import Tags
from .export import (
    PAGE_SENTINEL,
    ExportConfig,
    ExportMode,
    apply_view_to_export_html,
    build_export_filename,
    export_insert_root,
    export_root_position,
    generate_export_html,
    get_asset_collector,
    is_export_active,
    reset_export_buffer,
    set_cache_building,
)
from .loading import inject_loading_overlay, remove_loading_overlay, update_loading_progress
from .marker import (
    MarkerConfig,
    annotate_marker_numbers,
    inject_marker_navigation,
    is_listed,
    is_stop,
    marker_entries,
    marker_row_text,
    marker_slide_boundary,
    normalize_marker_entries,
    reset_marker_registry,
    stop_count,
)
from .marker_runtime import inject_marker_runtime
from .pdf_export import PdfConfig
from .presentation import get_presentation_config, presentation_page_scrolls, st_presentation_footer
from .presentation_profile import (
    _ACTIVE_PROFILE_KEY,
    PresentationProfile,
    ViewMode,
    apply_profile,
    build_default_profile,
    is_profile_modified,
)
from .printing import (
    PRINT_KEY,
    PrintConfig,
    apply_html_print_rule,
    get_print_state,
    notice_html,
    print_block_css,
    print_state,
)
from .search import generate_search_input_html, generate_search_script, start_collector, stop_collector
from .slide import add_slide_break_options
from .space import st_br, st_space
from .spacing import (
    mark_block_top_injected,
    reset_block_spacing,
    resolve_block_spacing,
    set_active_profile,
)
from .styles import Style
from .toc import NumberingMode, TOCConfig, reset_toc_registry, toc_entries
from .utils import inject_link_preview_scaffold
from .write import st_write
from .zoom import _PAGE_WIDTH_KEY, _ZOOM_KEY, add_zoom_options

logger = logging.getLogger(__name__)

# Warmup mode flag — set by CLI ``stx cache warmup`` for headless cache build.
_warmup_mode = False

#: Blocks that raised during a warmup run, as ``(block, error)`` pairs: the
#: block is the innermost inclusion that raised. ``stx export html`` reads it
#: to fail instead of writing a partial page (#134).
_warmup_errors: list[tuple[str, str]] = []

#: Set by ``stx export html`` for a paginated export (#106): the cache build
#: marks where each page starts in the export buffer.
_export_page_sentinels = False

#: The HTML export mode the module asks for: "continuous", "paginated" or
#: "both" (#106) — set by st_book, read by ``stx export html``.
_html_export_mode = "continuous"

#: ``stx export html --up-to-slide N`` (#146): the build stops after the entry
#: that holds the N-th stop (the slide counter's N); later entries never run,
#: so nothing of them reaches the export. The build then records what it kept
#: in ``_warmup_limit_result``: ``{"up_to_slide", "last_slide", "entries",
#: "stops"}`` (``stops``: the stops of the kept entries).
_warmup_up_to_slide: int | None = None
_warmup_limit_result: dict | None = None
HTML_EXPORT_MODES = ("continuous", "paginated", "both")

# Optional ExportConfig for headless export — set by CLI ``stx export html``.
# When set (not None) during warmup, _warmup_build_cache will activate the
# export buffer so the full-book HTML is captured alongside the cache.
_warmup_export_config: "ExportConfig | None" = None

# Counter for unique section CSS class names (Phase 2/3)
_block_css_counter = 0


def _inject_block_horizontal_css(block_spacing) -> None:
    """Inject a scoped CSS override for block-level horizontal spacing.

    Uses a unique class counter to ensure CSS specificity over the global
    ``zoom.py`` width injection.  The CSS is injected via ``st.html()``
    which Streamlit extracts to the page ``<head>``.
    """
    global _block_css_counter

    has_override = (
        block_spacing.left is not None
        or block_spacing.right is not None
        or block_spacing.width is not None
        or block_spacing.zoom is not None
    )
    if not has_override:
        return

    _block_css_counter += 1
    rules = []
    if block_spacing.width is not None:
        rules.append(f"width: {block_spacing.width}% !important;")
        rules.append(f"max-width: {block_spacing.width}% !important;")
    if block_spacing.left is not None:
        rules.append(f"padding-left: {block_spacing.left} !important;")
    if block_spacing.right is not None:
        rules.append(f"padding-right: {block_spacing.right} !important;")
    if block_spacing.zoom is not None:
        rules.append(f"zoom: {block_spacing.zoom / 100} !important;")

    css = (
        f'<style>.stx-block-spacing-{_block_css_counter} '
        f'.block-container {{ {" ".join(rules)} }}</style>'
    )
    st.html(css)


def _playwright_browsers_dir(package_dir: str) -> str:
    """Where Playwright keeps its browsers (``PLAYWRIGHT_BROWSERS_PATH`` or
    the platform default), without starting its driver."""
    import sys
    env = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
    if env == "0":
        return os.path.join(package_dir, "driver", "package", ".local-browsers")
    if env:
        return env
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches/ms-playwright")
    if sys.platform.startswith("win"):
        return os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")
    cache = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(cache, "ms-playwright")


def _chromium_installed_on_disk() -> bool | None:
    """True/False from Playwright's files on disk; None if the layout is unknown.

    ``driver/package/browsers.json`` gives the Chromium revision this
    Playwright expects; ``playwright install`` marks a finished install with
    ``<browsers dir>/chromium-<revision>/INSTALLATION_COMPLETE``.
    """
    import importlib.util
    spec = importlib.util.find_spec("playwright")
    if spec is None or not spec.origin:
        return False
    package_dir = os.path.dirname(spec.origin)
    try:
        with open(os.path.join(package_dir, "driver", "package", "browsers.json"),
                  encoding="utf-8") as f:
            browsers = json.load(f)["browsers"]
        revision = next(b["revision"] for b in browsers if b["name"] == "chromium")
    except (OSError, ValueError, KeyError, StopIteration):
        return None
    marker = os.path.join(_playwright_browsers_dir(package_dir),
                          f"chromium-{revision}", "INSTALLATION_COMPLETE")
    return os.path.isfile(marker)


@functools.lru_cache(maxsize=1)
def _is_pdf_available() -> bool:
    """Return True if playwright is installed AND its Chromium is present.

    Read from Playwright's files on disk, once per process: the export panel
    asks on every rerun, and starting the Playwright driver for it cost
    0.25-0.7 s each time (#98). Installing Chromium while the app runs needs a
    restart of the app to show the PDF option. Falls back to asking the
    driver (still once) if Playwright's on-disk layout is not recognised.
    """
    found = _chromium_installed_on_disk()
    if found is not None:
        return found
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = p.chromium.executable_path
            if not path:
                return False
            return os.path.isfile(path)
    except Exception:
        return False


def _margin_mm(css_value: str) -> int:
    """Extract the integer millimetre value from a CSS margin string."""
    import re as _re
    m = _re.match(r"^([0-9]+)", css_value.strip())
    return int(m.group(1)) if m else 0


def _resolve_pdf_base_url() -> str:
    """Base URL of the running Streamlit server, for PDF media resolution.

    Chromium headless (``export_pdf``) runs as a sibling process of this
    server, so ``localhost`` + the runtime port/baseUrlPath is correct by
    construction and immune to reverse proxies (issue #44).  The
    browser-visible ``st.context.url`` is the fallback.  Returns ``""``
    when neither source is available (bare mode) — ``export_pdf`` then
    behaves exactly as without a base.
    """
    try:
        port = st.get_option("server.port")
        base_path = (st.get_option("server.baseUrlPath") or "").strip("/")
        if port:
            base = f"http://localhost:{port}/"
            if base_path:
                base += base_path + "/"
            return base
    except Exception:  # pragma: no cover — bare mode / config drift
        pass
    try:
        from urllib.parse import urlsplit
        u = urlsplit(str(st.context.url))
        if u.scheme and u.netloc:
            path = u.path or "/"
            if not path.endswith("/"):
                # Drop the last segment (a page path), keep the directory.
                path = path.rsplit("/", 1)[0] + "/"
            return f"{u.scheme}://{u.netloc}{path}"
    except Exception:  # pragma: no cover — bare mode / older Streamlit
        pass
    return ""


def _offer_export_downloads(html: str, base_name: str,
                            pdf_config: PdfConfig | None = None,
                            paginated: bool = False,
                            html_zoom: int = 0) -> None:
    """Render a 'Download as...' expander with export options and download buttons.

    Format checkboxes (HTML / PDF) live **outside** the form so they trigger
    a rerun, allowing the PDF layout section to appear/disappear dynamically.
    The form contains only the configuration options and the Generate button.
    """
    from .pdf_export import PdfLoadReport, PdfMode, export_pdf

    rules = get_print_state()                  # what the author lets a reader take (#107)
    if not (rules["app_html"] or rules["app_pdf"]):
        return
    pdf_available = _is_pdf_available() and rules["app_pdf"]
    state_key = f"_stx_export_{base_name}"
    defaults = pdf_config or PdfConfig()

    # Deterministic config fingerprint: when PdfConfig changes in book.py,
    # widget keys change, forcing Streamlit to create fresh widgets with
    # the new default values.  Old orphaned keys are harmless.
    _cfg_str = (f"{defaults.format}|{defaults.landscape}|{defaults.print_background}|"
                f"{defaults.page_numbers}|{defaults.scale}|{defaults.content_width}|{defaults.zoom}|"
                f"{defaults.margin_top}|{defaults.margin_bottom}|"
                f"{defaults.margin_left}|{defaults.margin_right}")
    _cfg_fp = hashlib.md5(_cfg_str.encode()).hexdigest()[:6]
    _pk = f"{base_name}_{_cfg_fp}"  # PDF widget key suffix

    # Full-book HTML available from paginated cache build
    full_book_html = st.session_state.get(_STX_FULL_EXPORT_HTML_KEY) if paginated else None

    _BREAK_PAGE = "Page break between sections"
    _BREAK_CONTINUOUS = "Continuous flow"

    with st.expander("Download as..."):

        # ── Format checkboxes — outside form for dynamic rerun ────
        want_html = False
        if rules["app_html"]:
            want_html = st.checkbox("HTML", value=True,
                                    key=f"_stx_want_html_{base_name}")
        want_pdf = False
        if pdf_available:
            want_pdf = st.checkbox("PDF", value=False,
                                   key=f"_stx_want_pdf_{base_name}")
        elif rules["app_pdf"]:
            st.caption("PDF requires `streamtex[pdf]`")

        # ── Form — configuration + Generate ──────────────────────
        with st.form(key=f"_stx_export_form_{_pk}"):

            # ── Content (applies to both formats) ────────────────
            st.markdown("**Content**")

            # Slide notes left to the reader (note5): one box, ticked by default
            from .slide_note import has_choice
            want_notes = True
            if has_choice():
                want_notes = st.checkbox("Slide notes (watermark…)", value=True,
                                         key=f"_stx_want_notes_{_pk}")

            # Scope (paginated view only)
            export_scope = "Full document"
            if paginated:
                export_scope = st.radio(
                    "Scope",
                    options=["Full document", "Current section"],
                    index=0,
                    key=f"_stx_export_scope_{_pk}",
                )
                if not full_book_html and export_scope == "Current section":
                    st.caption("Exporting current section")

            # Section breaks
            _view = st.session_state.get(_STX_VIEW_MODE_KEY, "Paginated")
            _break_default = 0 if _view == "Paginated" else 1
            section_breaks = st.radio(
                "Section breaks",
                options=[_BREAK_PAGE, _BREAK_CONTINUOUS],
                index=_break_default,
                key=f"_stx_export_breaks_{_pk}",
            )

            # ── HTML enrichment options ─────────────────────────
            enrich_nav = False
            enrich_title = ""
            html_zoom_pct = 0
            if want_html:
                html_zoom_pct = st.number_input(
                    "Zoom HTML (%)", min_value=0, max_value=400,
                    value=max(0, min(400, int(html_zoom or 0))), step=10,
                    key=f"_stx_export_html_zoom_{_pk}_{html_zoom}",
                    help="0 = the HTML file follows the view zoom (Settings › Zoom %). "
                         "A value fixes the zoom of the HTML file whatever the screen "
                         "shows; it replaces the view zoom (the PDF zoom multiplies it).",
                )
                st.markdown("**HTML navigation**")
                enrich_nav = st.checkbox(
                    "Enriched navigation (TOC sidebar, markers, search)",
                    value=True,
                    key=f"_stx_export_enrich_{_pk}",
                )
                if enrich_nav:
                    # Auto-detect title from cache TOC
                    _cache = st.session_state.get(_STX_CACHE_KEY, {})
                    _toc = _cache.get("toc", [])
                    _auto = ""
                    for _e in _toc:
                        if _e.get("level") == 1:
                            _auto = _e.get("_reg_label") or _e.get("title", "")
                            break
                    enrich_title = st.text_input(
                        "Document title",
                        value=_auto,
                        key=f"_stx_export_title_{_pk}",
                    )

            # ── PDF layout (only when PDF is checked) ────────────
            # Variables with safe defaults for the submit handler
            pdf_format = defaults.format
            pdf_landscape = defaults.landscape
            pdf_background = defaults.print_background
            pdf_page_numbers = defaults.page_numbers
            pdf_scale = defaults.scale
            pdf_zoom = defaults.zoom
            pdf_content_width = defaults.content_width
            m_top = _margin_mm(defaults.margin_top)
            m_bottom = _margin_mm(defaults.margin_bottom)
            m_left = _margin_mm(defaults.margin_left)
            m_right = _margin_mm(defaults.margin_right)

            if want_pdf:
                _cur_w = st.session_state.get(_PAGE_WIDTH_KEY, 100)
                _cur_z = st.session_state.get(_ZOOM_KEY, 100)
                st.markdown("**PDF layout**")
                st.caption(f"Current view: Zoom {_cur_z}% (carried into the PDF, times Zoom below) · "
                           f"Width {_cur_w}% (HTML only; the PDF uses Content width)")
                _FORMAT_OPTIONS = [
                    "16:9", "16:10", "4:3",
                    "A4", "A3", "Letter", "Legal", "Tabloid",
                    "Custom ratio",
                ]
                _fmt_default = defaults.format
                _fmt_idx = next(
                    (i for i, f in enumerate(_FORMAT_OPTIONS) if f.lower() == _fmt_default.lower()),
                    0,
                )
                # If defaults.format is a custom ratio not in the list, select "Custom ratio"
                if _fmt_idx == 0 and _fmt_default.lower() not in [f.lower() for f in _FORMAT_OPTIONS]:
                    _fmt_idx = len(_FORMAT_OPTIONS) - 1
                _pdf_format_choice = st.selectbox(
                    "Page size",
                    options=_FORMAT_OPTIONS,
                    index=_fmt_idx,
                    key=f"_stx_pdf_format_{_pk}",
                )
                _is_custom = _pdf_format_choice == "Custom ratio"
                _has_custom_ratio = ":" in defaults.format and defaults.format not in _FORMAT_OPTIONS
                _custom_default = defaults.format if _has_custom_ratio else "21:9"
                _custom_ratio = st.text_input(
                    "Ratio (W:H)", value=_custom_default,
                    disabled=not _is_custom,
                    key=f"_stx_pdf_custom_ratio_{_pk}",
                )
                pdf_format = _custom_ratio if _is_custom else _pdf_format_choice
                # Hide landscape checkbox for ratio-based formats (always landscape)
                if ":" in pdf_format and pdf_format != "Custom ratio":
                    pdf_landscape = True
                else:
                    pdf_landscape = st.checkbox("Landscape", value=defaults.landscape,
                                                key=f"_stx_pdf_land_{_pk}")
                pdf_background = st.checkbox("Backgrounds", value=defaults.print_background,
                                             key=f"_stx_pdf_bg_{_pk}")
                pdf_page_numbers = st.checkbox("Page numbers", value=defaults.page_numbers,
                                               key=f"_stx_pdf_pn_{_pk}")
                _scale_default = max(10, min(500, round(defaults.scale * 100)))
                _pdf_scale_pct = st.number_input(
                    "Scale (%)", min_value=10, max_value=500,
                    value=_scale_default, step=10,
                    key=f"_stx_pdf_scale_{_pk}",
                    help="Chrome's print scale: shrinks sizes in pt/px and lets the "
                         "text reflow; sizes in vw/vh stay proportional to the page. "
                         "To shrink everything, use Zoom.",
                )
                pdf_scale = _pdf_scale_pct / 100.0
                pdf_zoom = st.number_input(
                    "Zoom (%)", min_value=10, max_value=400,
                    value=max(10, min(400, int(defaults.zoom))), step=10,
                    key=f"_stx_pdf_zoom_{_pk}",
                    help="Shrinks or enlarges everything in the PDF, sizes in vw/vh "
                         "included; multiplies with the view zoom (view 80 % x 70 % = 56 %). "
                         "Scale only shrinks pt/px sizes.",
                )
                _cw_default = max(10, min(100, defaults.content_width))
                pdf_content_width = st.number_input(
                    "Content width (%)", min_value=10, max_value=100,
                    value=_cw_default, step=10,
                    key=f"_stx_pdf_cw_{_pk}",
                )
                st.markdown("**Margins (mm)**")
                m_top = st.number_input("Top", min_value=0, value=_margin_mm(defaults.margin_top),
                                        key=f"_stx_pdf_mt_{_pk}")
                m_bottom = st.number_input("Bottom", min_value=0, value=_margin_mm(defaults.margin_bottom),
                                           key=f"_stx_pdf_mb_{_pk}")
                m_left = st.number_input("Left", min_value=0, value=_margin_mm(defaults.margin_left),
                                         key=f"_stx_pdf_ml_{_pk}")
                m_right = st.number_input("Right", min_value=0, value=_margin_mm(defaults.margin_right),
                                          key=f"_stx_pdf_mr_{_pk}")

            submitted = st.form_submit_button("Generate")

        if submitted:
            results = {}
            # Resolve which HTML to use based on scope
            effective_html = html
            if paginated and export_scope == "Full document":
                if not full_book_html:
                    # Full-book HTML is missing (session was reloaded).
                    # Trigger on-demand rebuild, then rerun to pick up the result.
                    rebuild_fn = st.session_state.pop("_stx_export_rebuild_fn", None)
                    if rebuild_fn:
                        with st.spinner("Generating full document..."):
                            rebuild_fn()
                        st.rerun()
                if full_book_html:
                    # Built once per session with the view of that moment:
                    # carry the current view zoom and width (#110).
                    effective_html = apply_view_to_export_html(
                        full_book_html,
                        built_view=st.session_state.get(_STX_FULL_EXPORT_VIEW_KEY),
                        page_width=f"{st.session_state.get(_PAGE_WIDTH_KEY, 100)}%",
                        zoom=st.session_state.get(_ZOOM_KEY, 100) / 100,
                    )

            if want_html:
                # Enrich a separate copy — keep effective_html raw for PDF
                html_download = effective_html
                if html_zoom_pct:
                    # A fixed zoom for the HTML file only (#110); the PDF
                    # keeps the view zoom times its own Zoom.
                    html_download = apply_view_to_export_html(
                        html_download,
                        page_width=f"{st.session_state.get(_PAGE_WIDTH_KEY, 100)}%",
                        zoom=html_zoom_pct / 100,
                    )
                from .export import lazy_load_images
                html_download = lazy_load_images(            # the HTML file only (#115)
                    html_download, st.session_state.get(_STX_CACHE_KEY, {}).get("markers"))
                if enrich_nav:
                    try:
                        from .export_enrich import enrich_export_html
                        _cache = st.session_state.get(_STX_CACHE_KEY, {})
                        html_download = enrich_export_html(
                            html_download,
                            toc=_cache.get("toc"),
                            markers=_cache.get("markers"),
                            search_index=_cache.get("search_index"),
                            doc_version=_cache.get("doc_version", ""),
                            lib_version=_cache.get("lib_version", ""),
                            notice=rules["notice"],
                        )
                        # Apply custom title override
                        if enrich_title:
                            import re as _re
                            html_download = _re.sub(
                                r"<title>[^<]*</title>",
                                f"<title>{enrich_title}</title>",
                                html_download,
                                count=1,
                            )
                    except Exception:
                        # Title-enrichment is cosmetic: if the regex substitution
                        # raises (malformed HTML, encoding issue), keep the
                        # original html_download untouched and continue.
                        pass

                html_download = apply_html_print_rule(html_download, rules)   # #107
                from .slide_note import apply_slide_notes
                html_download = apply_slide_notes(html_download, download=True,   # note3, note5
                                                  chosen=want_notes)
                collector = get_asset_collector()
                # Served media (configure_image_path) must survive off the
                # server: materialise them into the collector / as data
                # URIs on the EXPORT copy only (issue #48).
                from .export import materialize_served_media
                html_download = materialize_served_media(html_download,
                                                         collector)
                if collector:
                    # External mode: create ZIP with HTML + data/ folder
                    results["zip"] = collector.to_zip(html_download, base_name)
                else:
                    results["html"] = html_download
            if want_pdf and pdf_available:
                _pdf_mode = (PdfMode.PAGINATED if section_breaks == _BREAK_PAGE
                             else PdfMode.CONTINUOUS)
                with st.spinner("Generating PDF..."):
                    _t0 = time.monotonic()
                    try:
                        cfg = PdfConfig(
                            mode=_pdf_mode,
                            format=pdf_format,
                            landscape=pdf_landscape,
                            margin_top=f"{m_top}mm",
                            margin_bottom=f"{m_bottom}mm",
                            margin_left=f"{m_left}mm",
                            margin_right=f"{m_right}mm",
                            print_background=pdf_background,
                            scale=pdf_scale,
                            zoom=pdf_zoom,
                            content_width=pdf_content_width,
                            page_numbers=pdf_page_numbers,
                            header_template=defaults.header_template,
                            footer_template=defaults.footer_template,
                            theme_bg=st.session_state.get(_STX_THEME_BG_KEY, "#fff"),
                            theme_text=st.session_state.get(_STX_THEME_TEXT_KEY, "#333"),
                            # Media served by this very server (issue #44):
                            # an explicit author base_url wins, else the
                            # running server's own address.
                            base_url=defaults.base_url or _resolve_pdf_base_url(),
                            load_timeout_ms=defaults.load_timeout_ms,
                        )
                        _toc = st.session_state.get(_STX_CACHE_KEY, {}).get("toc")
                        _report = PdfLoadReport()
                        from .slide_note import apply_slide_notes
                        _pdf_html = apply_slide_notes(effective_html, pdf=True, download=True,
                                                      chosen=want_notes)     # note5
                        results["pdf"] = export_pdf(_pdf_html, config=cfg, toc=_toc,
                                                    report=_report)
                        if _report.timed_out:  # shown with the download button
                            results["pdf_warning"] = _report.message(cfg.load_timeout_ms)
                        _view_z = st.session_state.get(_ZOOM_KEY, 100)
                        results["pdf_zoom_note"] = (
                            f"PDF zoom: view {_view_z:g}% × {pdf_zoom:g}% = {_view_z * pdf_zoom / 100:g}%")
                    except Exception as exc:
                        st.error(f"PDF generation failed after {time.monotonic() - _t0:.0f} s: {exc}")
            st.session_state[state_key] = results

        # Show download buttons from cached results
        results = st.session_state.get(state_key, {})
        if "zip" in results:
            st.download_button(
                label="Download HTML (ZIP)",
                data=results["zip"],
                file_name=f"{base_name}.zip",
                mime="application/zip",
                key=f"_stx_dl_zip_{base_name}",
            )
        elif "html" in results:
            st.download_button(
                label="Download HTML",
                data=results["html"],
                file_name=f"{base_name}.html",
                mime="text/html",
                key=f"_stx_dl_html_{base_name}",
            )
        if "pdf" in results:
            if results.get("pdf_zoom_note"):
                st.caption(results["pdf_zoom_note"])
            if results.get("pdf_warning"):
                st.warning(results["pdf_warning"])
            st.download_button(
                label="Download PDF",
                data=results["pdf"],
                file_name=f"{base_name}.pdf",
                mime="application/pdf",
                key=f"_stx_dl_pdf_{base_name}",
            )


def _run_auto_exports(
    exports: list[ExportConfig],
    html: str,
    base_name: str,
) -> None:
    """Execute all ``mode=ALWAYS`` exports — write files to disk.

    Skips configs whose ``mode`` is not ``ALWAYS``.  HTML exports are
    written directly; PDF exports go through ``export_pdf()``.

    A sidebar notification summarises what was written.
    """
    from .pdf_export import export_pdf

    written: list[str] = []
    for cfg in exports:
        if cfg.mode != ExportMode.ALWAYS:
            continue
        path = build_export_filename(cfg, base_name)
        try:
            if cfg.format == "pdf":
                pdf_cfg = cfg.pdf
                if pdf_cfg is None:
                    from .pdf_export import PdfConfig
                    pdf_cfg = PdfConfig()
                # Inject theme colours from session state
                pdf_cfg.theme_bg = st.session_state.get(_STX_THEME_BG_KEY, "#fff")
                pdf_cfg.theme_text = st.session_state.get(_STX_THEME_TEXT_KEY, "#333")
                if not pdf_cfg.base_url:
                    pdf_cfg.base_url = _resolve_pdf_base_url()  # issue #44
                _toc = st.session_state.get(_STX_CACHE_KEY, {}).get("toc")
                from .slide_note import apply_slide_notes
                export_pdf(apply_slide_notes(html, pdf=True), output_path=path, config=pdf_cfg, toc=_toc)
            else:
                from pathlib import Path as _P
                collector = get_asset_collector()
                # Materialise served media on the export copy (issue #48);
                # local variable — the raw `html` stays untouched for the
                # PDF branch (which resolves media via base_url instead).
                from .export import lazy_load_images, materialize_served_media
                _html_out = materialize_served_media(html, collector)
                _html_out = lazy_load_images(                 # #115
                    _html_out, st.session_state.get(_STX_CACHE_KEY, {}).get("markers"))
                _html_out = apply_html_print_rule(_html_out, get_print_state())   # #107
                from .slide_note import apply_slide_notes
                _html_out = apply_slide_notes(_html_out)                          # note3
                if collector:
                    # External mode: write HTML + data/ folder to disk
                    out_dir = str(_P(path).parent)
                    written_path = collector.write_to_disk(_html_out, out_dir, base_name)
                    path = written_path
                else:
                    _P(path).parent.mkdir(parents=True, exist_ok=True)
                    _P(path).write_text(_html_out, encoding="utf-8")
            written.append(path)
        except Exception as exc:
            logger.warning("Auto-export failed for %s: %s", path, exc)
            with st.sidebar:
                st.warning(f"Export failed: {path}\n{exc}")

    if written:
        with st.sidebar:
            label = ", ".join(f"`{w}`" for w in written)
            st.caption(f"Auto-exported: {label}")


def _resolve_sidebar_max_level(toc_config: TOCConfig, paginated: bool) -> int | None:
    """Return the effective max TOC level for the sidebar.

    If the user set ``sidebar_max_level`` explicitly, honour it.
    Otherwise fall back to a mode-dependent default:
    paginated → 1, continuous → 2.
    Returns ``None`` when *toc_config* is ``None`` (no TOC).
    """
    if toc_config is None:
        return None
    if toc_config.sidebar_max_level is not None:
        return toc_config.sidebar_max_level
    return 1 if paginated else 2


def _setup_bibliography(bib_sources, bib_config):
    """Load bibliography sources and set config (called at start of st_book)."""
    from .bib import get_bib_registry, load_bib, reset_bib_registry, set_bib_config

    reset_bib_registry()

    if bib_config is not None:
        set_bib_config(bib_config)

    if bib_sources:
        registry = get_bib_registry()
        for source_path in bib_sources:
            try:
                entries = load_bib(source_path)
                registry.register_many(entries)
                logger.debug(f"Loaded {len(entries)} bib entries from {source_path}")
            except Exception as e:
                logger.warning(f"Failed to load bibliography from {source_path}: {e}")


def _inject_bib_preview_if_enabled():
    """Inject bib hover scaffold if bibliography hover is enabled."""
    from .bib import get_bib_config
    from .bib_preview import inject_bib_preview_scaffold

    if get_bib_config().hover_enabled:
        inject_bib_preview_scaffold()


def _st_book_impl(module_list, toc_config: TOCConfig = None, marker_config: MarkerConfig = None, separator=None,
            export: bool = True, export_title: str = "StreamTeX Export",
            pdf_config: PdfConfig = None,
            exports: list[ExportConfig] | None = None,
            paginate: bool = False,
            paginate_by="entry",
            html_export_mode="continuous",
            view_modes: list[ViewMode] | None = None,
            banner_color: str = "rgba(211, 47, 47, 0.8)",
            banner: BannerConfig = None,
            bib_sources=None, bib_config=None,
            inspector=None,
            chrome_banner: bool = False,
            page_width: int = 90,
            zoom: int = 100,
            presentation_profiles: list[PresentationProfile] | None = None,
            doc_version: str | None = None,
            loading: bool = True,
            scale=None,
            block_args: tuple = (),
            block_kwargs: dict | None = None,
            lang: str | None = None,
            html_export_zoom: int = 0,
            notice=None,
            printable: bool | PrintConfig = True):
    """Generates a web page e-book from a list of block modules.

    :param separator: Optional module with a build() function, rendered between each block.
    :param export: If True, enables HTML export with a download button in the sidebar.
    :param export_title: Title used for the exported HTML document.
    :param pdf_config: Optional PdfConfig to customise PDF export (format, margins, scale, etc.).
    :param exports: Optional list of ExportConfig for auto-export to disk.
        Each config defines one output file (format, mode, output_dir, filename,
        timestamp, pdf).  Configs with ``mode=ExportMode.ALWAYS`` are written
        automatically after rendering.  Configs with ``mode=ExportMode.MANUAL``
        show in the sidebar panel.  Overrides ``export`` when provided.
    :param paginate: If True, renders one block at a time for faster widget interactions.
    :param paginate_by: The pages of the paginated view (#121): ``"entry"``
        (default) one page per entry; ``N`` or ``"depth:N"`` pages that follow
        the composition tree down to depth N (an entry has depth 0, what it
        includes depth 1…); ``"leaf"`` one page per leaf — an inclusion that
        includes no other block (an atom or a composite). Arrows, markers,
        TOC, exports and PDF are the same for every value; only the pages and
        ``?page=`` numbers change (``?marker=<key>`` is the durable link).
        ``st_include(..., page=True | False)`` overrides it locally.
    :param html_export_mode: What ``stx export html`` writes (#106):
        ``"continuous"`` (default) one file; ``"paginated"`` one file per page
        of the page map; ``"both"`` the two, with a button in the navigation
        bar that opens the same slide in the other mode.
    :param view_modes: Optional list of allowed ViewMode values.
        When a single mode is given, the View radio is hidden and
        the document is locked to that mode.  Defaults to both modes.
    :param banner_color: Background color for paginated navigation banners (CSS value).
    :param banner: Optional BannerConfig for full banner customisation (overrides banner_color).
    :param bib_sources: Optional list of paths to .bib, .json, .ris, or .csl-json files.
    :param bib_config: Optional BibConfig to configure bibliography formatting.
    :param inspector: Optional InspectorConfig to enable the block inspector panel.
    :param page_width: Page width as % of browser width (default 90).
    :param zoom: Default zoom level as % (default 100).
    :param loading: If True (default), show a full-screen overlay with progress during loading.
    :param html_export_zoom: Starting value of the "Zoom HTML (%)" field of the
        export panel (#110). ``0`` (default) = the exported HTML follows the
        view zoom (Settings › Zoom %); a value fixes the zoom of the HTML
        file whatever the screen shows.
    :param scale: Optional ``ScaleConfig`` to override the indexed responsive
        font scale for this document only. When provided, an inline ``<style>``
        block is emitted after the default CSS load, redefining
        ``--stx-scale-0..N`` for desktop / tablet / mobile breakpoints.
    :param block_args: Positional args forwarded verbatim to every
        ``block.build()`` call.
    :param block_kwargs: Keyword args forwarded verbatim to every
        ``block.build()`` call. Both are part of the pagination cache key
        (one cache per variant — e.g. ``{"lang": "fr"}`` gets its own
        TOC / markers / page titles); keep the values to plain data.
    :param lang: Hand a language to every block (``build(lang=…)``):
        ``"auto"`` = :func:`streamtex.i18n.current_lang` (``$STX_LANG`` >
        ``?lang=`` > default), or an explicit code. An explicit ``"lang"``
        in ``block_kwargs`` wins. ``None`` (default) forwards nothing.
    :param notice: A usage notice of this document (#107), ``"…"`` or
        ``{"en": …, "fr": …}``: one line under the version in the sidebar of
        the app and of the HTML export, and the only thing on the printed
        sheet when printing is off.
    :param printable: What a reader may print or download (#107). ``True``
        (default) everything; ``False`` no printing of the app, no PDF in the
        "Download as..." panel, no printing of the HTML export (the HTML
        download stays); a :class:`~streamtex.printing.PrintConfig` sets
        ``app_print``, ``app_pdf``, ``html_print`` and ``app_html`` one by one.
        Automatic exports (``exports=[...]``) are the author's and keep
        writing their PDF.
    """
    _pagewalk.set_paginate_by(paginate_by)      # ValueError on a wrong value (#121)
    if html_export_mode not in HTML_EXPORT_MODES:
        raise ValueError(f"html_export_mode must be one of {', '.join(HTML_EXPORT_MODES)} "
                         f"— got {html_export_mode!r}")
    global _html_export_mode
    _html_export_mode = html_export_mode       # read by stx export html (#106)
    if lang is not None:
        from .i18n import current_lang

        resolved = current_lang() if lang == "auto" else lang
        block_kwargs = {"lang": resolved, **(block_kwargs or {})}
    if doc_version == "auto":
        doc_version = _project_version()
    _block_args = tuple(block_args or ())
    _block_kwargs = dict(block_kwargs or {})
    # --- Usage notice and print rules (#107): read by the panel and every export ---
    st.session_state[PRINT_KEY] = print_state(printable, notice, _block_kwargs.get("lang"))
    # --- Resolve PdfConfig from exports list if not provided directly ---
    if pdf_config is None and exports:
        for _ecfg in exports:
            if _ecfg.format == "pdf" and _ecfg.pdf is not None:
                pdf_config = _ecfg.pdf
                break

    # --- Resolve export flags from exports list ---
    if exports is not None:
        has_always = any(c.mode == ExportMode.ALWAYS for c in exports)
        has_manual = any(c.mode == ExportMode.MANUAL for c in exports)
        has_never_only = all(c.mode == ExportMode.NEVER for c in exports)
        # Enable buffer if any config needs HTML generation
        export = has_always or has_manual
        if has_never_only:
            export = False
    # --- Resolve allowed view modes ---
    _allowed_modes: list[str] = (
        [m.value for m in view_modes]
        if view_modes
        else [ViewMode.PAGINATED.value, ViewMode.CONTINUOUS.value]
    )
    if not _allowed_modes:
        raise ValueError("view_modes must contain at least one ViewMode.")
    # --- Resolve banner configuration ---
    if banner is not None:
        banner_config = banner
    else:
        banner_config = BannerConfig(color=banner_color)
    # --- Store version info for export enrichment ---
    if doc_version:
        from . import __version__ as _lib_ver
        st.session_state["_stx_doc_version"] = doc_version
        st.session_state["_stx_lib_version"] = _lib_ver

    # --- Headless warmup: build + save cache, then return ---
    if _warmup_mode:
        # The references first: an HTML export without them shows every
        # citation as [key?] and an empty bibliography.
        _setup_bibliography(bib_sources, bib_config)
        _warmup_build_cache(module_list, toc_config, marker_config,
                            separator,
                            block_args=_block_args,
                            block_kwargs=_block_kwargs)
        return

    # --- Password gate (env-driven, no-op locally) ---
    _password_gate()

    # --- Loading overlay (after gate, before any slow work) ---
    _show_loading = loading and not _warmup_mode
    if _show_loading:
        inject_loading_overlay()
    # --- Marker runtime (env-gated; no-op unless STX_USE_MARKER_RUNTIME=1) ---
    # Injects the global stylesheet + MutationObserver. Idempotent within a session.
    inject_marker_runtime()
    # --- Chrome recommendation banner (JS-injected, no block flow impact) ---
    if chrome_banner:
        st_chrome_banner()
    # --- Cache theme colors (once, early, in guaranteed Streamlit context) ---
    if _STX_THEME_BG_KEY not in st.session_state:
        _bg = st.get_option("theme.backgroundColor")
        _txt = st.get_option("theme.textColor")
        if not _bg or not _txt:
            _base = st.get_option("theme.base")
            if _base == "dark":
                _bg = _bg or "#0e1117"
                _txt = _txt or "#fafafa"
            else:
                _bg = _bg or "#fff"
                _txt = _txt or "#333"
        st.session_state[_STX_THEME_BG_KEY] = _bg
        st.session_state[_STX_THEME_TEXT_KEY] = _txt
    # --- Bibliography setup ---
    _setup_bibliography(bib_sources, bib_config)
    # --- Presentation profiles ---
    default_profile = build_default_profile(page_width, zoom, paginate)
    user_profiles = presentation_profiles or []
    if any(p.name == "Default" for p in user_profiles):
        all_profiles = list(user_profiles)
    else:
        all_profiles = [default_profile] + list(user_profiles)
    _pnames = [p.name for p in all_profiles]
    if len(set(_pnames)) != len(_pnames):
        _dupes = {n for n in _pnames if _pnames.count(n) > 1}
        raise ValueError(f"Duplicate profile names: {_dupes}.")
    profile_names = [p.name for p in all_profiles]
    profile_by_name = {p.name: p for p in all_profiles}
    if _ACTIVE_PROFILE_KEY not in st.session_state:
        st.session_state[_ACTIVE_PROFILE_KEY] = profile_names[0]
        # Apply first profile's layout as initial values so zoom/width
        # match the profile without requiring an explicit click.
        _initial = all_profiles[0]
        if _PAGE_WIDTH_KEY not in st.session_state:
            page_width = _initial.layout.width
            st.session_state[_PAGE_WIDTH_KEY] = page_width
        if _ZOOM_KEY not in st.session_state:
            zoom = _initial.layout.zoom
            st.session_state[_ZOOM_KEY] = zoom
    active_name = st.session_state.get(_ACTIVE_PROFILE_KEY, profile_names[0])
    if active_name not in profile_by_name:
        active_name = profile_names[0]
        st.session_state[_ACTIVE_PROFILE_KEY] = active_name
    active_profile = profile_by_name[active_name]
    _profile_modified = is_profile_modified(active_profile)

    # --- Profile switch detection (BEFORE any widget) ---
    _pending_switch = st.session_state.pop("_stx_profile_pending", None)
    if _pending_switch and _pending_switch in profile_by_name:
        apply_profile(profile_by_name[_pending_switch])
        st.session_state["_stx_profile_select"] = _pending_switch
        st.rerun()

    # --- Settings expander (sidebar) ---
    if _STX_VIEW_MODE_KEY not in st.session_state:
        _default = "Paginated" if paginate else "Continuous"
        st.session_state[_STX_VIEW_MODE_KEY] = (
            _default if _default in _allowed_modes else _allowed_modes[0]
        )
    # Force-clamp if the current value is no longer allowed (profile switch, etc.)
    if st.session_state.get(_STX_VIEW_MODE_KEY) not in _allowed_modes:
        st.session_state[_STX_VIEW_MODE_KEY] = _allowed_modes[0]

    def _on_profile_change():
        st.session_state["_stx_profile_pending"] = st.session_state["_stx_profile_select"]

    with st.sidebar:
        if doc_version:
            from . import __version__ as _lib_version
            _ver = f"docs {doc_version} \u00b7 lib {_lib_version}"
            _is_pag = st.session_state.get(_STX_VIEW_MODE_KEY,
                "Paginated" if paginate else "Continuous") == "Paginated"
            _ver_href = (f"#stx-goto-{_first_page_of_last_entry(len(module_list))}"
                         if _is_pag else "#changelog")
            st.markdown(
                f'<a href="{_ver_href}" style="display:block;text-align:center;'
                f'font-size:0.8em;opacity:0.55;text-decoration:none;color:inherit;"'
                f'>{_ver}</a>',
                unsafe_allow_html=True,
            )
        _print_rules = st.session_state[PRINT_KEY]
        if _print_rules["notice"]:
            st.markdown(notice_html(_print_rules["notice"],
                                    "text-align:center;font-size:0.75em;opacity:0.55;"),
                        unsafe_allow_html=True)
        if not _print_rules["app_print"]:
            # the printed sheet carries the notice only (#107)
            st.markdown(f"<style>{print_block_css(_print_rules['notice'])}</style>",
                        unsafe_allow_html=True)
        _stx_settings = st.expander("Settings")
        with _stx_settings:
            if marker_config is not None:
                _stx_settings.toggle(
                    "Navigation bar",
                    value=marker_config.show_nav_ui,
                    key="_stx_show_nav_ui",
                )
            # ── Profile selector with inline reset ──
            def _format_profile(name):
                if name == active_name and _profile_modified:
                    return f"{name} *"
                return name

            _col_select, _col_reset = _stx_settings.columns([6, 1],
                                                              vertical_alignment="bottom")
            with _col_select:
                st.selectbox(
                    "\U0001F4F1 Profile",
                    options=profile_names,
                    format_func=_format_profile,
                    key="_stx_profile_select",
                    on_change=_on_profile_change,
                )
            with _col_reset:
                if st.button("\u21BB", key="_stx_profile_reset",
                             help="Reset to profile values",
                             use_container_width=True):
                    st.session_state["_stx_profile_pending"] = active_name
                    st.rerun()

            # ── Existing controls ──
            if len(_allowed_modes) > 1:
                _stx_settings.radio(
                    "**View**",
                    options=_allowed_modes,
                    horizontal=True,
                    key=_STX_VIEW_MODE_KEY,
                )
            add_zoom_options(default_page_width=page_width, default_zoom=zoom,
                             container=_stx_settings)
            add_wrap_all_option(container=_stx_settings)
            _stx_settings.divider()
            add_slide_break_options(container=_stx_settings)

        # Hidden profile buttons for JS→Streamlit switching (floating bar).
        # MutationObserver hides them via inline style whenever React renders them.
        # Buttons remain clickable (position:absolute, not display:none).
        _prof_ctr = st.container()
        with _prof_ctr:
            for _p in all_profiles:
                def _switch_profile(_name=_p.name):
                    st.session_state["_stx_profile_pending"] = _name
                st.button(f"stx_prof_{_p.name}", key=f"_stx_pbtn_{_p.name}",
                          on_click=_switch_profile)
        st.iframe("""<script>
        (function(){
            var HIDE = 'position:absolute;left:-9999px;height:0;overflow:hidden;pointer-events:auto;';
            function hideProfileButtons() {
                var btns = parent.document.querySelectorAll('[data-testid="stBaseButton-secondary"]');
                for (var i = 0; i < btns.length; i++) {
                    var txt = (btns[i].textContent || '').trim();
                    if (txt.indexOf('stx_prof_') === 0) {
                        var w = btns[i].closest('[data-testid="stButton"]');
                        if (w && w.style.cssText.indexOf('-9999px') < 0) {
                            w.style.cssText = HIDE;
                        }
                    }
                }
            }
            hideProfileButtons();
            var sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                var obs = new MutationObserver(hideProfileButtons);
                obs.observe(sidebar, { childList: true, subtree: true });
            }
        })();
        </script>""", height=1)

    # Slide notes (note3): their rules and the notes fixed on the screen, once per page
    from .slide_note import st_slide_notes_page
    st_slide_notes_page()

    if st.session_state[_STX_VIEW_MODE_KEY] == "Paginated":
        _paginated_book(module_list, toc_config, marker_config, separator,
                        export, export_title, banner_config,
                        pdf_config=pdf_config, exports=exports,
                        inspector=inspector,
                        page_width=page_width, zoom=zoom,
                        html_export_zoom=html_export_zoom,
                        profile_names=profile_names,
                        active_profile=active_name,
                        profile_modified=_profile_modified,
                        all_profiles=all_profiles,
                        loading=_show_loading,
                        block_args=_block_args,
                        block_kwargs=_block_kwargs)
        return

    start_time = time.time()
    logger.debug("Starting st_book function...")

    # Load default CSS styles
    load_css("default.css")

    # Inject per-document scale override if a ScaleConfig was provided.
    if scale is not None:
        from .styles.scale import emit_scale_css
        st.markdown(
            f"<style>\n{emit_scale_css(scale)}\n</style>",
            unsafe_allow_html=True,
        )

    # Ensure the hover card is ready before any content is rendered.
    inject_link_preview_scaffold()

    # Inject bibliography hover preview if enabled
    _inject_bib_preview_if_enabled()

    # Initialise the export buffer (reads effective width/zoom from session_state)
    effective_pw = f"{st.session_state.get(_PAGE_WIDTH_KEY, page_width)}%"
    effective_zoom = st.session_state.get(_ZOOM_KEY, zoom) / 100
    reset_export_buffer(ExportConfig(enabled=export, page_title=export_title,
                                     page_width=effective_pw, zoom=effective_zoom))

    # Inject inspector CSS once + reserve sidebar placeholder
    _inspector_placeholder = None
    if inspector and inspector.enabled:
        from .inspector import inject_inspector_css
        inject_inspector_css()
        with st.sidebar:
            _inspector_placeholder = st.empty()

    # Clear previous run's headers
    reset_toc_registry(toc_config)

    # Initialize marker navigation (opt-in)
    if marker_config is not None:
        reset_marker_registry(marker_config)

    # Extract ToC config and create ToC placeholders
    use_toc_sidebar = toc_config is not None
    use_toc_block = use_toc_sidebar and toc_config.toc_position is not None
    markers_sidebar = None
    if use_toc_sidebar:
        toc_sidebar, markers_sidebar, search_js_ph = build_ToC_sidebar_placeholder(
            has_markers=marker_config is not None,
            has_search=toc_config.search,
        )
        toc_block = None
        toc_content_style = None
    if use_toc_block:
        # Determine ToC insertion position
        toc_pos = toc_config.toc_position
        if toc_pos < 0 or toc_pos >= len(module_list):
            toc_pos = len(module_list)
        toc_title_style = toc_config.title_style
        toc_content_style = toc_config.content_style

    # Start search collector if enabled
    use_search = use_toc_sidebar and toc_config.search
    collector = start_collector() if use_search else None

    # Switch overlay from "Initializing…" to progress mode
    _total_modules = len(module_list)
    if _show_loading:
        update_loading_progress(0, _total_modules)

    # Store active profile for section spacing resolution in st_slide_break/st_write
    set_active_profile(active_profile)

    # Resolve block spacing (profile-aware)
    _block_sp = resolve_block_spacing(profile=active_profile)

    # Run the blocks (potentially populating the ToC registry)
    for i, module in enumerate(module_list):

        # Generate Toc at appropriate position
        if use_toc_block and i == toc_pos:
            toc_block = st_toc(toc_title_style)

        if collector is not None:
            collector.set_block(i)

        toc_before = len(toc_entries()) if use_toc_sidebar else 0
        markers_before = len(marker_entries()) if marker_config is not None else 0

        # Block spacing: inject block.top before build()
        if _block_sp.top is not None:
            st_space("v", _block_sp.top)
        mark_block_top_injected()

        # Block-level horizontal CSS override (Phase 2)
        _inject_block_horizontal_css(_block_sp)

        marker_slide_boundary()     # each entry opens a slide (#116 §4.6)
        try:
            st_include(module, *_block_args, _inspector_config=inspector, **_block_kwargs)
        finally:
            # Close any open section wrapper from Phase 3
            from .slide import _close_section_wrapper_if_open
            _close_section_wrapper_if_open()
            # Reset per-block spacing override
            reset_block_spacing()

        # Update loading overlay progress
        if _show_loading:
            _mod_name = getattr(module, '__name__', '').rsplit('.', 1)[-1]
            update_loading_progress(i + 1, _total_modules, _mod_name)

        # Tag new TOC entries with their block index
        if use_toc_sidebar:
            for entry in toc_entries()[toc_before:]:
                if "block_idx" not in entry:
                    entry["block_idx"] = i

        # Tag new marker entries with their block index (for search filtering)
        if marker_config is not None:
            for entry in marker_entries()[markers_before:]:
                if "block_idx" not in entry:
                    entry["block_idx"] = i

        # Separator between blocks (not after the last one)
        if separator and i < len(module_list) - 1:
            st_include(separator, *_block_args, **_block_kwargs)

        # Block spacing: inject block.bottom after build()
        if _block_sp.bottom is not None:
            st_space("v", _block_sp.bottom)

    # Remove loading overlay after all modules are rendered
    if _show_loading:
        remove_loading_overlay()

    # Stop collector and get search index
    block_index = stop_collector() if use_search else None

    # One number per marker, for every surface (#117)
    if marker_config is not None:
        annotate_marker_numbers(marker_entries())

    # Generate Toc at appropriate position
    if use_toc_block and toc_pos == len(module_list):
        toc_block = st_toc(toc_title_style)

    # Fill the ToC placeholder
    if use_toc_sidebar:
        effective_max_level = _resolve_sidebar_max_level(toc_config, paginated=False)
        populate_toc(toc_sidebar, toc_block, toc_content_style,
                     block_index=block_index, search_js_placeholder=search_js_ph,
                     max_level=effective_max_level, toc_config=toc_config)
        if markers_sidebar is not None:
            populate_markers_sidebar(markers_sidebar, block_index=block_index)

    # Inject marker navigation JS (only if markers were registered).
    # The bar names the sidebar entries of its slide in cyan, as in a
    # paginated book: the continuous tables carry data-stx-nav too.
    if marker_config is not None:
        inject_marker_navigation(
            profile_names=profile_names,
            active_profile=active_name,
            profile_modified=_profile_modified,
            nav_toc=_toc_nav_table(toc_entries(), marker_entries(),
                                   _resolve_sidebar_max_level(toc_config, paginated=False))
            if use_toc_sidebar else None,
        )

    # Presentation footer (auto-rendered when PresentationConfig is active)
    _pres_cfg = get_presentation_config()
    if _pres_cfg is not None and _pres_cfg.footer:
        _n = stop_count() if _pres_cfg.counter_mode == "slide" else 0
        # "slide": slide 1 over the stops (#117); the widget then keeps it
        # in sync. Without stops, or in "bloc" mode: the entries.
        st_presentation_footer(current_slide=1, total_slides=_n or len(module_list),
                               config=_pres_cfg)

    # Offer export downloads when export is active
    if is_export_active():
        full_html = generate_export_html()
        if full_html:
            base_name = export_title.replace(' ', '_').lower()
            # Auto-export (mode=ALWAYS) configs
            if exports:
                _run_auto_exports(exports, full_html, base_name)
            # Sidebar panel for manual configs (or export=True)
            _show_manual = exports is None or any(
                c.mode == ExportMode.MANUAL for c in exports
            )
            if _show_manual:
                with st.sidebar:
                    _offer_export_downloads(full_html, base_name, pdf_config=pdf_config,
                                            html_zoom=html_export_zoom)

    # --- Inspector panel (opt-in, rendered into reserved sidebar placeholder) ---
    if _inspector_placeholder is not None and st.session_state.get("_stx_inspector_open", False):
        from .inspector import FileCategoryRegistry, _find_project_root, discover_sources, render_inspector_panel
        _block_name = st.session_state.get("_stx_inspector_block", "")
        _target = next(
            (m for m in module_list
             if getattr(m, '__name__', '').rsplit('.', 1)[-1] == _block_name),
            None,
        )
        if _target:
            _cat_registry = FileCategoryRegistry()
            _sources = discover_sources(_target, _cat_registry)
            _proj_root = _find_project_root(getattr(_target, '__file__', '') or '')
            render_inspector_panel(
                _sources, inspector, _cat_registry, _inspector_placeholder,
                project_root=_proj_root,
            )

    end_time = time.time()
    duration = end_time - start_time
    logger.debug("st_book function completed in %.2f seconds.", duration)


@st.cache_resource
def _read_css(file_name: str) -> str:
    """Read a CSS file from the streamtex.static package (cached in memory)."""
    try:
        with resources.open_text('streamtex.static', file_name) as f:
            return f.read()
    except (FileNotFoundError, ModuleNotFoundError, TypeError) as e:
        logger.debug("[StreamTeX] CSS resource fallback for '%s': %s", file_name, e)
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, 'static')
        css_file_path = os.path.join(static_dir, file_name)
        with open(css_file_path, 'r') as f:
            return f.read()


def load_css(file_name: str):
    """Loads a CSS file and injects it into the StreamTeX app."""
    st.html(f'<style>{_read_css(file_name)}</style>')


# What the continuous sidebar shows while the blocks run: its tables are only
# known after the last block, and a long document takes a while (#137).
_TOC_WAITING = "Building the table of contents…"
_MARKERS_WAITING = "Building the markers…"


def _waiting(placeholder: Delta, text: str) -> Delta:
    """Fill a sidebar placeholder with a waiting line, until its table replaces it."""
    placeholder.markdown(
        f'<div class="stx-sidebar-waiting" style="font-size:13px;font-style:italic;opacity:.65;'
        f'padding:4px 0;">{text}</div>', unsafe_allow_html=True)
    return placeholder


def build_ToC_sidebar_placeholder(has_markers=False, has_search=False):
    with st.sidebar:
        # Search input above tabs (always visible regardless of active tab)
        if has_search:
            st.markdown(generate_search_input_html(), unsafe_allow_html=True)
            if st.button("Refresh search index", key="_stx_refresh_search_cont",
                         use_container_width=True, type="tertiary"):
                st.rerun()
            search_js_placeholder = st.empty()
        else:
            search_js_placeholder = None
        if has_markers:
            tab_markers, tab_toc = st.tabs(["Markers", "Contents"])
            toc_sidebar = _waiting(tab_toc.empty(), _TOC_WAITING)
            markers_sidebar = _waiting(tab_markers.empty(), _MARKERS_WAITING)
            return toc_sidebar, markers_sidebar, search_js_placeholder
        else:
            st.header("Table of Contents")
            toc_sidebar = _waiting(st.empty(), _TOC_WAITING)
            return toc_sidebar, None, search_js_placeholder


def _toc_dot_anchors(markers: list[dict]) -> set[str]:
    """TOC anchors that carry the "●" dot: those linked to a stop (#116).

    The same rule in continuous and paginated mode.
    """
    anchors = set()
    for m in markers:
        if is_stop(m):
            anchors.add(m["anchor"])
            if m.get("toc_anchor"):
                anchors.add(m["toc_anchor"])
    return anchors


def _toc_target_marker(entry: dict, markers: list[dict]) -> int | None:
    """The marker a TOC heading of another page lands on (#127).

    The heading's own marker (``marker=True`` or ``"attach"``); else the last
    stop registered before the heading on its page, i.e. the slide holding
    it. None when the heading comes before every stop of its page, or for a
    cache written before ``_markers_before`` existed: the link then opens the
    page on its first marker.
    """
    page = entry.get("page_idx", 0)
    anchor = entry.get("key_anchor")
    for m in markers:
        if anchor and m.get("toc_anchor") == anchor and m.get("page_idx", 0) == page:
            return m["index"]
    before = entry.get("_markers_before")
    if before is None:
        return None
    target = None
    for m in markers:
        if m["index"] >= before:
            break
        if is_stop(m) and m.get("page_idx", 0) == page:
            target = m["index"]
    return target


def _goto_href(page_idx: int, marker_idx: int | None) -> str:
    """Sidebar link to another page: ``#stx-goto-<page>[-<marker>]`` (#127)."""
    return f"#stx-goto-{page_idx}" if marker_idx is None else f"#stx-goto-{page_idx}-{marker_idx}"


def _toc_nav_table(toc: list[dict], markers: list[dict], max_level: int | None) -> dict[int, int]:
    """The Contents entry in cyan on each slide of a paginated book (#130).

    Maps every stop's marker index to the position, in *toc*, of the heading
    in force on that slide: the first listed heading of the slide, else the
    last one before it.  A heading belongs to the slide its sidebar link
    lands on (``_toc_target_marker``), the page's first slide when it comes
    before every stop.  Slides before any heading are absent.  The floating
    bar looks its current slide up in this table (``navToc``).
    """
    stops = [m["index"] for m in markers if is_stop(m)]
    page_first: dict[int, int] = {}
    for m in markers:
        if is_stop(m):
            page_first.setdefault(m.get("page_idx", 0), m["index"])
    slides: list[tuple[int, int]] = []        # (slide's stop index, toc position)
    for pos, entry in enumerate(toc):
        if max_level is not None and entry["level"] > max_level:
            continue
        target = _toc_target_marker(entry, markers)
        first = page_first.get(entry.get("page_idx", 0))
        if first is None:
            continue
        if target is None or target < first:
            target = first
        slide = max(k for k in stops if k <= target)
        slides.append((slide, pos))
    table: dict[int, int] = {}
    for stop in stops:
        held = [slide for slide, _ in slides if slide <= stop]
        if held:
            slide = max(held)
            table[stop] = min(pos for k, pos in slides if k == slide)
    return table


def populate_toc(toc_sidebar: Delta, toc_block: Delta = None, toc_content_style: Style = None,
                 block_index: dict[int, str] = None, search_js_placeholder=None,
                 max_level: int | None = None, toc_config: TOCConfig | None = None):
    toc_entry_list = toc_entries()
    marker_anchors = _toc_dot_anchors(marker_entries())
    indent_char = "&nbsp;"

    with toc_sidebar.container():
        if block_index is not None:
            # Search-enabled: single st.markdown block (entries with data-stx-block)
            toc_parts = []
            for pos, entry in enumerate(toc_entry_list):
                if max_level is not None and entry['level'] > max_level:
                    continue
                indent = indent_char * (entry['level'] - 1) * 4
                dot = (
                    '<span style="opacity:.5;font-size:6px;vertical-align:middle;'
                    'margin-right:4px;">&#9679;</span>'
                    if entry['key_anchor'] in marker_anchors else ''
                )
                block_attr = f' data-stx-block="{entry.get("block_idx", 0)}"'
                toc_parts.append(
                    f'<div data-stx-nav="toc{pos}"{block_attr} style="overflow:hidden;text-overflow:ellipsis;'
                    f'white-space:nowrap;padding:1px 0;font-size:14px;">'
                    f'{indent}{dot}<a href="#{entry["key_anchor"]}">'
                    f'{entry["title"]}</a></div>'
                )
            toc_parts.append('<div style="height:40px;"></div>')
            st.markdown("\n".join(toc_parts), unsafe_allow_html=True)
        else:
            for pos, entry in enumerate(toc_entry_list):
                if max_level is not None and entry['level'] > max_level:
                    continue
                indent = indent_char * (entry['level'] - 1) * 4
                dot = (
                    '<span style="opacity:.5;font-size:6px;vertical-align:middle;'
                    'margin-right:4px;">&#9679;</span>'
                    if entry['key_anchor'] in marker_anchors else ''
                )
                st.html(
                    f'<span data-stx-nav="toc{pos}" style="overflow:hidden;text-overflow:ellipsis;'
                    f'text-wrap:nowrap;word-wrap:normal;">'
                    f'{indent}{dot}<a href="#{entry["key_anchor"]}">'
                    f'{entry["title"]}</a></span>'
                )

    # Inject search JS into the dedicated placeholder (above tabs)
    if search_js_placeholder is not None and block_index is not None:
        with search_js_placeholder.container():
            st.iframe(generate_search_script(block_index), height=1)

    if toc_block is not None:
        with toc_block.container():
            main_num = toc_config is not None and toc_config.effective_numbering in (
                NumberingMode.BOTH, NumberingMode.MAIN_ONLY
            )
            for entry in toc_entry_list:
                indent = indent_char * (entry['level'] - 1) * 2
                label = entry.get("_reg_label", entry["title"])
                if main_num:
                    label = entry.get("section_number", "") + label
                st_write(toc_content_style, f"{indent}{label}",
                                link=f"#{entry['key_anchor']}", hover=False, no_link_decor=True)
                st_br()


def populate_markers_sidebar(markers_placeholder: Delta, block_index: dict[int, str] = None):
    entries = [e for e in annotate_marker_numbers(marker_entries()) if is_listed(e)]
    if not entries:
        markers_placeholder.empty()                     # no waiting line left behind
        return
    with markers_placeholder.container():
        if block_index is not None:
            # Search-enabled: single st.markdown block with data-stx-block attributes
            parts = []
            for entry in entries:
                block_attr = f' data-stx-block="{entry.get("block_idx", 0)}"'
                parts.append(
                    f'<div data-stx-nav="mk{entry["index"]}"{block_attr} style="overflow:hidden;'
                    f'text-overflow:ellipsis;white-space:nowrap;padding:1px 0;font-size:14px;">'
                    f'<a href="#{entry["anchor"]}">{marker_row_text(entry)}</a></div>'
                )
            parts.append('<div style="height:40px;"></div>')
            st.markdown("\n".join(parts), unsafe_allow_html=True)
        else:
            for entry in entries:
                st.html(
                    f'<span data-stx-nav="mk{entry["index"]}" style="overflow:hidden;'
                    f'text-overflow:ellipsis;text-wrap:nowrap;word-wrap:normal;">'
                    f'<a href="#{entry["anchor"]}">{marker_row_text(entry)}</a></span>'
                )


def st_toc(toc_title_style):
    st_write(toc_title_style, "Table of Contents", tag=Tags.div, toc_lvl='1')
    st_space("v", 4)
    toc_block = st.empty()
    st_space("v", "70px")
    return toc_block


class IncludeCycleError(RuntimeError):
    """A block includes itself, directly or through other blocks (#119).

    ``chain``: the display names of the cycle, first == last
    (``("lists.a", "lists.b", "lists.a")``); ``stack``: every inclusion in
    progress when it was detected, outermost first.
    """

    def __init__(self, chain: tuple[str, ...], stack: tuple[str, ...]):
        self.chain = chain
        self.stack = stack
        super().__init__(
            f"Include cycle: {' → '.join(chain)}. A block cannot include itself, directly "
            "or through other blocks: remove one of these st_include calls.")


#: The inclusions in progress, outermost first: ``(key, display name)``. The
#: key is the block's real file path, so a block reloaded into a new object
#: or imported under two names is still the same block. A ``ContextVar``:
#: each Streamlit script run has its own.
_INCLUDE_STACK: ContextVar[tuple[tuple[object, str], ...]] = ContextVar(
    "stx_include_stack", default=())


# ---------------------------------------------------------------------------
# Fresh code for included blocks (#120)
# ---------------------------------------------------------------------------

_INCLUDE_RELOAD = True
#: real path -> (weakref to the module, mtime of its code, generation, {project import: its generation then})
_INCLUDED: dict[str, tuple] = {}
_INCLUDED_LOCK = threading.RLock()
_GENERATION = itertools.count(1)          # bumped each time a module gets new code
_IMPORTS: dict[str, tuple[float, tuple[str, ...]]] = {}   # real path -> (mtime, module names it imports)
_NOT_PROJECT = ("streamtex", "streamlit")


def set_include_reload(enabled: bool) -> None:
    """Re-execute a block reached through ``st_include`` when its file changed (default on).

    The project modules the block imports are followed too: when one changed,
    it is executed again, then every module and block that imports it.
    The environment variable ``STX_INCLUDE_RELOAD=0`` turns it off and wins
    over this setting. Off, the block's file is still watched by the page cache.
    """
    global _INCLUDE_RELOAD
    _INCLUDE_RELOAD = bool(enabled)


def _include_reload_enabled() -> bool:
    env = os.environ.get("STX_INCLUDE_RELOAD")
    if env is not None and env.strip() != "":
        return env.strip() not in ("0", "false", "False", "no")
    return _INCLUDE_RELOAD


@functools.lru_cache(maxsize=1)
def _installed_roots() -> tuple[str, ...]:
    paths = sysconfig.get_paths()
    roots = {os.path.realpath(paths[k]) for k in ("stdlib", "platstdlib", "purelib", "platlib") if paths.get(k)}
    return tuple(r.rstrip(os.sep) + os.sep for r in roots)


def _project_file(mod) -> str | None:
    """The real path of a module written by the project, else ``None``.

    Not the project's: the standard library, installed packages
    (``site-packages``), StreamTeX and Streamlit, and modules without a
    ``.py`` source.
    """
    if not isinstance(mod, types.ModuleType):
        return None
    if (getattr(mod, "__name__", None) or "").partition(".")[0] in _NOT_PROJECT:
        return None
    path = getattr(mod, "__file__", None)
    if not path or not path.endswith(".py"):
        return None
    key = os.path.realpath(path)
    parts = key.split(os.sep)
    if key.startswith(_installed_roots()) or "site-packages" in parts or "dist-packages" in parts:
        return None
    return key


def _imported_names(mod, key: str, mtime: float) -> tuple[str, ...]:
    """The module names a file imports (``import`` / ``from … import``), read once per mtime."""
    hit = _IMPORTS.get(key)
    if hit is not None and hit[0] == mtime:
        return hit[1]
    try:
        with open(key, "rb") as f:
            tree = ast.parse(f.read(), key)
    except (OSError, SyntaxError, ValueError):
        return ()                               # running the file reports the error
    package = getattr(mod, "__package__", None) or ""
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            try:
                base = importlib.util.resolve_name("." * node.level + (node.module or ""), package)
            except (ImportError, ValueError):
                continue
            names.append(base)
            names += [f"{base}.{a.name}" for a in node.names if a.name != "*"]   # submodules
    out = tuple(dict.fromkeys(names))
    _IMPORTS[key] = (mtime, out)
    return out


def _exec_in_place(mod, key: str) -> None:
    spec = importlib.util.spec_from_file_location(mod.__name__, key)
    spec.loader.exec_module(mod)                # same object: every holder sees it


def _refresh_module(mod, key: str, seen: set[str]) -> int | None:
    """Bring *mod* up to date with its file and its project imports; its generation.

    The project modules it imports are brought up to date first. First sight
    of the file: recorded (generation 0). Another object for a known file
    (Streamlit evicted and re-imported it, a registry re-executed it):
    recorded under a new generation, so its importers run again. Same
    object: executed again **in place** when its file changed or when one of
    its project imports got new code since it last ran. A failure is raised
    and the old record kept, so the next run retries.
    """
    from .watch import watch_file
    try:
        mtime = os.path.getmtime(key)
    except OSError:
        return None
    deps: dict[str, int] = {}
    for name in _imported_names(mod, key, mtime):
        dkey = _project_file(sys.modules.get(name))
        if dkey is None or dkey == key:
            continue
        if dkey in seen:                        # already done in this walk, or an import cycle
            rec = _INCLUDED.get(dkey)
            if rec is not None:
                deps[dkey] = rec[2]
            continue
        seen.add(dkey)
        gen = _refresh_module(sys.modules[name], dkey, seen)
        if gen is not None:
            deps[dkey] = gen
    rec = _INCLUDED.get(key)
    if rec is None or rec[0]() is not mod:
        gen = 0 if rec is None else next(_GENERATION)
        _INCLUDED[key] = (weakref.ref(mod), mtime, gen, deps)
        watch_file(key, mtime)
        return gen
    stale = rec[1] != mtime or any(rec[3].get(k, g) != g for k, g in deps.items())
    if not stale:
        _INCLUDED[key] = (rec[0], rec[1], rec[2], {**rec[3], **deps})
        watch_file(key, rec[1])
        return rec[2]
    _exec_in_place(mod, key)
    gen = next(_GENERATION)
    _INCLUDED[key] = (weakref.ref(mod), mtime, gen, deps)
    watch_file(key, mtime)
    return gen


def _refresh_included(block) -> None:
    """Watch an included block's file and give it fresh code (#120).

    The block and the project modules it imports, at any depth (``shared/``,
    a pack outside ``site-packages``), are watched; a changed one is
    executed again in place, then every module and block importing it, so
    every holder (a list block's ``ITEMS``, the entries given to
    ``st_book``) sees the new code. See :func:`_refresh_module`.
    """
    path = getattr(block, "__file__", None)
    if not path or not os.path.isfile(path):
        return
    key = os.path.realpath(path)
    if not _include_reload_enabled():
        from .watch import watch_file
        watch_file(key)
        return
    with _INCLUDED_LOCK:
        _refresh_module(block, key, {key})


def _include_frame(block) -> tuple[object, str]:
    path = getattr(block, "__file__", None)
    key = os.path.realpath(path) if path else ("id", id(block))
    return key, getattr(block, "__name__", None) or repr(block)


def _check_include_cycle(stack, frame) -> None:
    """Raise :class:`IncludeCycleError` if *frame* is already in progress."""
    keys = [k for k, _ in stack]
    if frame[0] in keys:
        i = keys.index(frame[0])
        names = tuple(n for _, n in stack)
        raise IncludeCycleError(names[i:] + (frame[1],), names)


def st_include(block_file_module, *args, markers=True, break_before=False, page=None,
               _inspector_config=None, **kwargs):
    """Render another block's ``build()`` in place, like ``\\input``.

    ``break_before`` (#118): ``True`` draws the standard break (the module's
    break settings, no marker) before the block; a ``SlideBreakConfig`` draws
    that break, used as given (its ``marker`` included); ``False`` (default)
    draws nothing. The break belongs to the host: this inclusion's
    ``markers`` does not apply to it.

    ``markers`` changes the roles of every marker the included ``build()``
    places — its own ``st_marker`` calls, its breaks' markers, its headings'
    markers, at any depth of nested inclusions (#113):

    =================  ===============================================
    ``True``           unchanged (default)
    ``False``          no stop, not listed (each marker keeps its
                       anchor and its deep link)
    ``"hidden"``       stops kept, none listed
    ``{"stop": …, "listed": …, "toc": False}``  each key forces that role;
                       ``"toc": False`` also drops the TOC entries
    =================  ===============================================

    Nested inclusions inherit the override; on a conflict the outer one
    wins. The layout never changes: rules, spacers, spacing and content are
    rendered identically. ``markers`` and ``break_before`` are not passed to
    ``build()``.

    The block's file is watched by the page cache, and a block whose file
    changed is executed again in place, so reloading the page is enough —
    for blocks reached through ``st_include``, in any directory, and for the
    project modules they import (#120;
    ``set_include_reload(False)`` or ``STX_INCLUDE_RELOAD=0`` to turn it off).

    ``page`` (#121) matters only with ``st_book(paginate_by=…)`` other than
    ``"entry"``: ``True`` = this inclusion starts a page with its whole
    subtree; ``False`` = it and its subtree stay on the enclosing page;
    ``None`` (default) = decided by ``paginate_by``.

    A block cannot include itself, directly or through other blocks: the
    re-entry raises :class:`IncludeCycleError` naming the chain, before
    anything of it is drawn (#119). Including the same block several times
    in a row is fine. An error in ``build()`` shows one red message, at the
    innermost inclusion, and propagates.
    """
    from .marker import include_role_override, normalize_markers_arg
    from .slide import SlideBreakConfig

    normalize_markers_arg(markers)          # ValueError before anything renders
    if page not in (None, True, False):
        raise TypeError(f"st_include(page={page!r}): expected None, True or False")
    if not (isinstance(break_before, (bool, SlideBreakConfig))):
        raise TypeError(f"st_include(break_before={break_before!r}): expected True, False "
                        "or a SlideBreakConfig")
    if not block_file_module:
        st.markdown(":red-background[Block module is None — not found]")
        return

    # Fresh code and a watched file for every included block (#120)
    try:
        _refresh_included(block_file_module)
    except Exception as e:
        name = getattr(block_file_module, '__name__', str(block_file_module))
        st.markdown(f":red-background[Error in block '{name}': {e}]")
        try:
            e._stx_reported = True
        except AttributeError:
            pass
        raise

    mod_path = getattr(block_file_module, '__file__', None) or getattr(block_file_module, '__name__', '?')
    if not hasattr(block_file_module, 'build'):
        st.markdown(f":red-background[The file {mod_path} does not contain a build() function.]")
        return

    module_name = getattr(block_file_module, '__name__', str(block_file_module))

    # Pages following the tree (#121): another page's page-starting
    # inclusion is not executed at all
    walk = _pagewalk.current()
    path = None
    if walk is not None:
        path = walk.enter(block_file_module, page)
        if walk.skip(path):
            return

    # No cycle (#119): checked before anything of this inclusion is drawn
    frame = _include_frame(block_file_module)
    stack = _INCLUDE_STACK.get()
    _check_include_cycle(stack, frame)
    token = _INCLUDE_STACK.set(stack + (frame,))
    begun = False
    try:
        # The break before the block, in the host's context (#118)
        if break_before is True:
            from .slide import _standard_break
            _standard_break()
        elif isinstance(break_before, SlideBreakConfig):
            from .slide import st_slide_break
            st_slide_break(config=break_before)

        # Inspector edit button (opt-in)
        # Uses st.html() directly (not _render()), so never appears in exported HTML.
        if _inspector_config and _inspector_config.enabled:
            from .inspector import render_edit_button
            short_name = module_name.rsplit('.', 1)[-1]
            render_edit_button(short_name, _inspector_config)

        if walk is not None:
            walk.begin(path)
            begun = True
        with include_role_override(markers):
            block_file_module.build(*args, **kwargs)
    except Exception as e:
        # One red message per error: the innermost inclusion shows it (#119)
        if not getattr(e, "_stx_reported", False):
            if isinstance(e, IncludeCycleError):
                st.markdown(f":red-background[{e}]")
            else:
                st.markdown(f":red-background[Error in block '{module_name}': {e}]")
            try:
                e._stx_reported = True
                e._stx_block = module_name      # the block named by the export (#134)
            except AttributeError:
                pass
        raise
    finally:
        if begun:
            walk.end(path)
        _INCLUDE_STACK.reset(token)


_BREAK = "break"


def st_sequence(items, *args, separator=_BREAK, markers=True, **kwargs) -> None:
    """Include several blocks in order, a break between two, none at the ends (#118).

    The body of a *list block*::

        ITEMS = [bck_intro, bck_detail, bck_list_examples]

        def build(*args, **kwargs):
            st_sequence(ITEMS, *args, **kwargs)

    :param items: blocks (objects with ``build()``), included in this order.
    :param separator: what goes between two items: ``"break"`` (default) the
        standard break — the module's break settings, no marker (each item
        brings its own); a ``SlideBreakConfig`` — that break; ``None`` —
        nothing; a block — its ``build()``, as ``st_book(separator=…)``.
        Never before the first item, never after the last.
    :param markers: passed to every item's ``st_include`` (#113); the breaks
        have no marker.
    :param args, kwargs: passed to every item's ``build()`` (and to a
        separator block's), at any depth of nested lists.
    """
    from .slide import SlideBreakConfig

    if separator == _BREAK:
        brk = True
    elif separator is None:
        brk = False
    elif isinstance(separator, SlideBreakConfig):
        brk = separator
    elif hasattr(separator, "build"):
        brk = False
    else:
        raise TypeError(f"st_sequence(separator={separator!r}): expected 'break', None, "
                        "a SlideBreakConfig or a block")
    for i, item in enumerate(items):
        if i and brk is False and separator is not None:
            st_include(separator, *args, **kwargs)
        st_include(item, *args, markers=markers, break_before=brk if i else False, **kwargs)


# ---------------------------------------------------------------------------
# Paginated mode
# ---------------------------------------------------------------------------

_STX_CACHE_KEY = "_stx_page_cache"
_STX_PAGE_KEY = "_stx_current_page"
_STX_INITIAL_MARKER_KEY = "_stx_initial_marker"


def _initial_page_from_url(cache, total) -> tuple[int, int | None]:
    """Resolve the first page of the session from the URL (deep link).

    Reads ``st.query_params`` defensively -- absent outside a real script
    run (tests, headless) -- and delegates to ``deeplink.resolve_initial_page``.
    """
    try:
        params = dict(st.query_params)
    except Exception:  # noqa: BLE001 -- no script context / mocked st
        return 0, None
    if not params:
        return 0, None
    from .deeplink import resolve_initial_page
    return resolve_initial_page(params, (cache or {}).get("markers", []), total)
_STX_VIEW_MODE_KEY = "_stx_view_mode"
_STX_THEME_BG_KEY = "_stx_theme_bg"
_STX_THEME_TEXT_KEY = "_stx_theme_text"


def _block_kwargs_fingerprint(block_args: tuple = (),
                              block_kwargs: dict | None = None) -> str:
    """Return a short, deterministic fingerprint of the args forwarded to
    every ``block.build()`` — ``""`` when nothing is forwarded.

    The values are serialised with ``json.dumps(sort_keys=True, default=repr)``
    so plain data (str / int / bool / lists / dicts) gives a stable key across
    processes. An object whose ``repr`` embeds a memory address would change
    on every run and defeat the cache: keep forwarded kwargs to plain data.
    """
    if not block_args and not block_kwargs:
        return ""
    payload = json.dumps({"args": list(block_args or ()),
                          "kwargs": dict(block_kwargs or {})},
                         sort_keys=True, ensure_ascii=False, default=repr)
    return hashlib.md5(payload.encode()).hexdigest()[:8]


def _watched_current(cache: dict) -> bool:
    from .watch import snapshot_is_current
    return snapshot_is_current(cache.get("watched"))


def _watched_snapshot() -> dict:
    from .watch import watched_snapshot
    return watched_snapshot()


def _find_book_file() -> str | None:
    """The module's ``book.py``: the innermost ``__main__`` script on the call stack (#120).

    Streamlit runs the script as ``__main__`` with its ``__file__``; the
    ``stx`` CLIs execute ``book.py`` the same way. Library and tool files
    (anything under ``sys.prefix``, ``site-packages``) are skipped, so a test
    runner's ``__main__`` is never taken for a book. ``None`` if there is none.
    """
    import sys
    f = sys._getframe(1)
    prefix = os.path.realpath(sys.prefix)
    while f is not None:
        g = f.f_globals
        path = g.get("__file__")
        if g.get("__name__") == "__main__" and isinstance(path, str) and path.endswith(".py"):
            real = os.path.realpath(path)
            if "site-packages" not in real and not real.startswith(prefix + os.sep):
                return os.path.abspath(path)
        f = f.f_back
    return None


def _anchor_dir(module_list, book_file: str | None) -> str | None:
    """The directory the page cache belongs to: the book's, else the entries' parent."""
    if book_file:
        return os.path.dirname(os.path.abspath(book_file))
    for m in module_list:
        fpath = getattr(m, '__file__', None)
        if fpath:
            return os.path.dirname(os.path.dirname(os.path.abspath(fpath)))
    return None


@functools.lru_cache(maxsize=1)
def _editable_library_stamp() -> str:
    """Newest mtime of the library's ``.py`` files when it runs from a checkout.

    An editable install (``uv sync`` in the repo, ``stx dev link``) imports the
    library from its source tree and keeps its version number while its code
    changes, so the version alone would let the page cache serve titles built
    by older code. A regular install lives under ``site-packages`` and returns
    ``""``: the cache key is unchanged. Computed once per server process.
    """
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    parts = pkg_dir.split(os.sep)
    if "site-packages" in parts or "dist-packages" in parts:
        return ""
    newest = 0.0
    for root, dirs, files in os.walk(pkg_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                with contextlib.suppress(OSError):
                    newest = max(newest, os.path.getmtime(os.path.join(root, f)))
    return f"{newest}"


def _compute_cache_hash(module_list, block_args: tuple = (),
                        block_kwargs: dict | None = None, book_file: str | None = None):
    """Return a hash that changes when the module list or file contents change.

    The hash incorporates:
    - Module names (detects add/remove/reorder)
    - File modification times of the entries (detects content edits)
    - the module's own files: its ``book.py``, every ``custom/**/*.py`` and
      ``blocks/helpers.py`` next to it (*book_file*, #120; without it, next to
      the entries' parent directory as before), and the helper modules next
      to the entries (detects config changes, #53)

    Blocks reached through ``st_include`` and data files read through
    ``stx.load_*`` / ``watch_file`` are NOT part of the hash (they are known
    only once the blocks have run): the cache stores their mtimes as its
    ``"watched"`` snapshot and is discarded as soon as one changed.
    - streamtex library version (detects library upgrades), plus the newest
      mtime of its sources when it is installed editable (development)
    - A fingerprint of ``block_args`` / ``block_kwargs`` when non-empty, so a
      document built with ``block_kwargs={"lang": "fr"}`` never reuses the
      TOC / markers / page titles cached for ``"en"``
    """
    parts: list[str] = []

    # 1. Module names + mtimes
    for m in module_list:
        name = getattr(m, '__name__', str(m))
        fpath = getattr(m, '__file__', None)
        mtime = str(os.path.getmtime(fpath)) if fpath and os.path.isfile(fpath) else "0"
        parts.append(f"{name}:{mtime}")

    # 2. Ancillary files that affect TOC/markers/search output.
    #    Resolve relative to the first module's directory (= the project's blocks/).
    first_file = None
    for m in module_list:
        first_file = getattr(m, '__file__', None)
        if first_file:
            break
    if first_file:
        project_dir = _anchor_dir(module_list, book_file)
        ancillary = [
            os.path.abspath(book_file) if book_file else os.path.join(project_dir, "book.py"),
            os.path.join(project_dir, "custom", "styles.py"),
            os.path.join(project_dir, "blocks", "helpers.py"),
        ]
        for fp in ancillary:
            if os.path.isfile(fp):
                parts.append(f"{fp}:{os.path.getmtime(fp)}")
        # #53 — every custom/**/*.py (config, visuals, slide helpers…), not
        # only styles.py, and the helper modules living next to the blocks
        # in every block directory (shared-blocks/ folders included).
        seen = set(ancillary)
        extra: list[str] = []
        custom_dir = os.path.join(project_dir, "custom")
        if os.path.isdir(custom_dir):
            for root, dirs, files in os.walk(custom_dir):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                extra += [os.path.join(root, f) for f in files if f.endswith(".py")]
        block_dirs = {os.path.dirname(os.path.abspath(getattr(m, "__file__", "") or ""))
                      for m in module_list if getattr(m, "__file__", None)}
        module_files = {os.path.abspath(getattr(m, "__file__", "") or "") for m in module_list}
        for d in sorted(block_dirs):
            try:
                names = os.listdir(d)
            except OSError:
                continue
            extra += [os.path.join(d, f) for f in names
                      if f.endswith(".py") and os.path.join(d, f) not in module_files]
        for fp in sorted(set(extra) - seen):
            if os.path.isfile(fp):
                parts.append(f"{fp}:{os.path.getmtime(fp)}")

    # 3. Pages following the tree (#121): another page map
    _mode = _pagewalk.paginate_by()
    if _mode != _pagewalk.ENTRY:
        parts.append(f"pages:{_mode}")

    # 3b. Library version (invalidates on upgrade); an editable install keeps
    # its version across commits, so its source mtimes count too.
    try:
        from . import __version__
        parts.append(f"stx:{__version__}")
    except ImportError:
        pass
    stamp = _editable_library_stamp()
    if stamp:
        parts.append(f"stxsrc:{stamp}")

    # 4. Forwarded block args/kwargs (empty → no part, hash unchanged)
    fp = _block_kwargs_fingerprint(block_args, block_kwargs)
    if fp:
        parts.append(f"kw:{fp}")

    return hashlib.md5("|".join(parts).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Persistent file cache (survives session restarts / server reruns)
# ---------------------------------------------------------------------------

_STX_FILE_CACHE_DIR = ".stx_cache"
_STX_FILE_CACHE_NAME = "page_cache.json"


def _resolve_cache_path(module_list, block_args: tuple = (),
                        block_kwargs: dict | None = None,
                        book_file: str | None = None) -> str | None:
    """Return the path to the persistent cache file for this module.

    The cache lives next to the module's ``book.py`` (*book_file*, #120):
    ``<book dir>/.stx_cache/page_cache.json`` — for the standard layout the
    same place as before (the parent of ``blocks/``). When
    ``block_args`` / ``block_kwargs`` are forwarded to the blocks, the file
    name carries their fingerprint — ``page_cache-<fp8>.json`` — so that one
    cache per variant (one per language, typically) coexists on disk instead
    of being overwritten at every switch.
    Returns None if the project directory cannot be determined.
    """
    for m in module_list:
        fpath = getattr(m, '__file__', None)
        if fpath:
            project_dir = _anchor_dir(module_list, book_file)
            fp = _block_kwargs_fingerprint(block_args, block_kwargs)
            stem, ext = os.path.splitext(_STX_FILE_CACHE_NAME)
            name = f"{stem}-{fp}{ext}" if fp else _STX_FILE_CACHE_NAME
            return os.path.join(project_dir, _STX_FILE_CACHE_DIR, name)
    return None


def _load_file_cache(cache_path: str, expected_hash: str) -> dict | None:
    """Load the persistent cache from disk if it exists and the hash matches."""
    try:
        if not os.path.isfile(cache_path):
            return None
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("hash") != expected_hash:
            logger.debug("File cache hash mismatch — will rebuild.")
            return None
        from .watch import snapshot_is_current
        if not snapshot_is_current(data.get("watched")):
            logger.debug("A data file read by the blocks changed — will rebuild.")
            return None
        # search_index keys are ints in memory but strings in JSON; convert back
        si = data.get("search_index")
        if isinstance(si, dict):
            data["search_index"] = {int(k): v for k, v in si.items()}
        # marker entries of an older library: give them their roles (#116)
        # and their numbers (#117)
        annotate_marker_numbers(normalize_marker_entries(data.get("markers") or []))
        logger.debug("Loaded page cache from %s", cache_path)
        return data
    except Exception:
        logger.debug("Failed to load file cache — will rebuild.", exc_info=True)
        return None


def _save_file_cache(cache_path: str, cache: dict) -> None:
    """Persist the page cache to disk (best-effort, never raises)."""
    try:
        cache_dir = os.path.dirname(cache_path)
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, separators=(",", ":"))
        logger.debug("Saved page cache to %s", cache_path)
    except Exception:
        logger.debug("Failed to save file cache.", exc_info=True)


def _first_page_of_last_entry(n_entries: int) -> int:
    """The page index where the last entry starts (#121; the entry index without pages)."""
    pages = (st.session_state.get(_STX_CACHE_KEY) or {}).get("pages") or []
    for i, p in enumerate(pages):
        if p.get("entry") == n_entries - 1:
            return i
    return n_entries - 1


def _page_named(cache, titles: list[str], pages: list[dict], tree_mode: bool) -> list[bool]:
    """Which pages are "named" — the others are footers for the banners and the loop-back.

    One page per entry: a page is named when it has a title (0.7.45 rule).
    Pages following the tree (#121): an entry is named when one of its pages
    has a title, and every page of a named entry is named; a page of it still
    without a title takes the title of the nearest earlier page of the same
    entry (a continuation page), so it is never taken for a footer.
    """
    named = [not t.startswith("Section ") for t in titles]
    if not tree_mode:
        return named
    entry_of = [p.get("entry", i) for i, p in enumerate(pages)]
    entry_named = {}
    for i, e in enumerate(entry_of):
        entry_named[e] = entry_named.get(e, False) or named[i]
    for i, e in enumerate(entry_of):
        if not named[i] and entry_named.get(e):
            j = i - 1
            while j >= 0 and entry_of[j] == e and not named[j]:
                j -= 1
            if j >= 0 and entry_of[j] == e:
                titles[i] = titles[j]
    return [entry_named.get(e, False) for e in entry_of]


_STX_PAGE_ANCHOR_KEY = "_stx_page_anchor"


def _rederive_current_page(cache) -> None:
    """Keep the presenter on the same slide when the page map changes (#121).

    The first stop of the current page is remembered with the cache hash;
    after a rebuild (a list block edited, ``paginate_by`` changed) the page
    holding that stop becomes the current page.
    """
    remembered = st.session_state.get(_STX_PAGE_ANCHOR_KEY)
    markers = cache.get("markers", [])
    if remembered and remembered[0] != cache.get("hash") and _STX_PAGE_KEY in st.session_state:
        for e in markers:
            if e.get("anchor") == remembered[1]:
                st.session_state[_STX_PAGE_KEY] = e.get("page_idx", 0)
                break
    page = st.session_state.get(_STX_PAGE_KEY, 0)
    first = next((e for e in markers if is_stop(e) and e.get("page_idx", 0) == page), None)
    if first is not None:
        st.session_state[_STX_PAGE_ANCHOR_KEY] = (cache.get("hash"), first["anchor"])


def _render_page(module, page: dict, pages: list[dict], block_args, block_kwargs, inspector) -> None:
    """Render one page: its whole entry, or one part of it through the gate (#121)."""
    start = page.get("start") or []
    if not start:
        st_include(module, *block_args, _inspector_config=inspector, **block_kwargs)
        return
    entry_idx = page.get("entry")
    starts = [p["start"] for p in pages if p.get("entry") == entry_idx]
    gate = _pagewalk.Gate(start, starts)
    from . import marker as _marker_mod
    reg = _marker_mod._registry
    n_markers = len(reg._entries) if reg is not None else 0
    toc_reg = _toc_mod.toc
    toc_state = (len(toc_reg.toc_list), list(toc_reg.numbers), toc_reg.current_level) if toc_reg else None
    token = _pagewalk.activate(gate)
    try:
        st_include(module, *block_args, _inspector_config=inspector, **block_kwargs)
    finally:
        _pagewalk.deactivate(token)
    if gate.met:
        return
    # The live render did not meet the page the cache expects (a block whose
    # inclusions depend on widget state): show the whole entry instead.
    logger.warning("Page %s of entry %s not met in the live render: showing the whole entry.",
                   start, getattr(module, "__name__", module))
    if reg is not None:
        del reg._entries[n_markers:]
    if toc_reg is not None and toc_state is not None:
        del toc_reg.toc_list[toc_state[0]:]
        toc_reg.numbers, toc_reg.current_level = toc_state[1], toc_state[2]
    st_include(module, *block_args, _inspector_config=inspector, **block_kwargs)


def _stops_on_page(markers: list[dict], page: int) -> int:
    """How many slides (navigation stops) *page* holds."""
    return sum(1 for m in markers if is_stop(m) and m.get("page_idx", 0) == page)


def _footer_first_slide(markers: list[dict], page: int, initial_marker: int | None) -> int:
    """The slide number the footer shows on its first paint (#117).

    The deep-linked marker's number; else the first stop of *page*; else the
    last stop before the page; else 1. *markers* carry ``number``.
    """
    if initial_marker is not None:
        for e in markers:
            if e.get("index") == initial_marker and e.get("number"):
                return e["number"]
    before = None
    for e in markers:
        if not is_stop(e) or not e.get("number"):
            continue
        pg = e.get("page_idx", 0)
        if pg == page:
            return e["number"]
        if pg < page:
            before = e["number"]
    return before or 1


def _get_page_titles(cache, total):
    """Extract page title for each page.

    When markers are available (#116): (1) the first listed marker of the
    page, with its slide number (#117); else (2) the label of the listed
    marker whose row covers the page's first stop (a row begun on an earlier
    page); else the page stays unnamed. Falls back to TOC section titles when
    the module has no marker at all.
    """
    titles = [f"Section {i + 1}" for i in range(total)]

    # Prefer marker-based titles (matches sidebar Markers tab & floating bar)
    markers = cache.get("markers", [])
    if markers:
        named = set()
        for entry in markers:
            if not is_listed(entry):
                continue
            num = entry.get("number")
            idx = entry.get("page_idx", 0)
            if idx < total and idx not in named:
                titles[idx] = f"{num} {entry['label']}" if num else entry["label"]
                named.add(idx)
        # (2) pages whose stops all continue a row begun earlier
        first_stop = {}
        for entry in markers:
            if is_stop(entry):
                first_stop.setdefault(entry.get("page_idx", 0), entry)
        for idx, stop in first_stop.items():
            if idx >= total or idx in named:
                continue
            row = None
            for entry in markers:
                if entry["index"] > stop["index"]:
                    break
                if is_listed(entry):
                    row = entry
            if row is not None:
                titles[idx] = row["label"]
        return titles

    # Fallback: TOC titles (includes section number from register_entry)
    for entry in cache.get("toc", []):
        idx = entry.get("page_idx", 0)
        if idx < total and titles[idx].startswith("Section "):
            titles[idx] = entry["title"]
    return titles


def _preseed_toc_registry(cached_toc, current_page):
    """Replay TOC registrations for pages before *current_page*.

    This ensures that section numbering and anchors are identical to the
    full-render pass, so cached sidebar links match the live anchors.
    """
    registry = _toc_mod.toc
    if registry is None:
        return
    for entry in cached_toc:
        if entry.get("page_idx", 0) >= current_page:
            break
        # Replay the original registration (advances numbering state)
        registry.register_entry(entry["_reg_label"], entry["_reg_level"])


def _snapshot_widget_keys(keys):
    """Snapshot a widget-key collection, independent of Streamlit version.

    Streamlit <1.58 stores ``widget_user_keys_this_run`` / ``widget_ids_this_run``
    as a plain ``set`` (``.copy()`` works); >=1.58 uses a ``ThreadSafeSet`` that
    has no ``.copy()`` but exposes ``.snapshot()``. Returns a detached copy of
    the current contents in both cases.
    """
    snap = getattr(keys, "snapshot", None)
    return snap() if callable(snap) else set(keys)


def _restore_widget_keys(target, saved):
    """Restore a widget-key collection in place, preserving its container type.

    Mutates ``target`` rather than reassigning it, so a plain ``set`` is never
    swapped into a slot that Streamlit >=1.58 expects to be a ``ThreadSafeSet``.
    Re-populates via ``.check_and_add`` (ThreadSafeSet) or ``.update`` (set).
    """
    target.clear()
    check_and_add = getattr(target, "check_and_add", None)
    if callable(check_and_add):
        for key in saved:
            check_and_add(key)
    else:
        target.update(saved)


def _widget_key_holder(ctx):
    """Locate the object carrying the per-run widget key sets.

    Streamlit <1.60 stores ``widget_user_keys_this_run`` / ``widget_ids_this_run``
    directly on ``ScriptRunContext``; 1.60 moved them to the ``SharedRunState``
    exposed as ``ctx.shared``. Returns the carrying object, or ``None`` when
    neither location exists (future Streamlit — isolation is then skipped
    rather than crashing the whole cache build).
    """
    if hasattr(ctx, "widget_user_keys_this_run"):
        return ctx
    shared = getattr(ctx, "shared", None)
    if shared is not None and hasattr(shared, "widget_user_keys_this_run"):
        return shared
    return None


@contextlib.contextmanager
def _isolate_widget_keys():
    """Isolate widget key registration during cache build.

    Saves the current key-tracking sets, lets the cache build register
    keys freely, then restores the original sets.  This way the real
    render pass sees no keys from the cache build and avoids
    ``StreamlitDuplicateElementKey`` errors for blocks that use
    hardcoded widget keys.
    """
    ctx = get_script_run_ctx()
    holder = _widget_key_holder(ctx) if ctx is not None else None
    if holder is None:
        yield
        return
    saved_user_keys = _snapshot_widget_keys(holder.widget_user_keys_this_run)
    saved_ids = _snapshot_widget_keys(holder.widget_ids_this_run)
    try:
        yield
    finally:
        _restore_widget_keys(holder.widget_user_keys_this_run, saved_user_keys)
        _restore_widget_keys(holder.widget_ids_this_run, saved_ids)


_STX_FULL_EXPORT_HTML_KEY = "_stx_full_export_html"
_STX_FULL_EXPORT_VIEW_KEY = "_stx_full_export_view"  # (page_width, zoom) it was built with


# Streamlit primitives whose DOM emission is suppressed during the
# cache-build loop.  See ``_suppress_cache_build_dom`` below — the
# attributes listed here are the ones streamtex blocks invoke that
# would otherwise stream thousands of deltas per cold cache build.
#
# Excluded on purpose:
#   * ``container`` — the hidden cache-build wrapper itself relies on
#     ``with hidden.container():`` to nest deltas; the per-block
#     ``with st.container():`` calls inside streamtex primitives need
#     to keep their context-manager protocol.
#   * ``iframe`` — ``update_loading_progress()`` re-emits a progress
#     iframe after every block.  Keeping ``st.iframe`` live is the only
#     way the loading overlay percentage actually updates during the
#     cache build.
#   * ``columns``, ``tabs``, ``empty``, ``expander`` — rarely used in
#     streamtex primitives; preserving them keeps user ``build()``
#     functions that mix in raw Streamlit widgets behaving like before.
_CACHE_BUILD_DOM_PATCH_ATTRS = (
    "html", "markdown", "write", "text", "code", "caption",
    "header", "subheader", "title", "divider",
)


@contextlib.contextmanager
def _suppress_cache_build_dom():
    """Monkey-patch streamlit DOM-emitting primitives to no-ops.

    During the Tier-3 ``_build_page_cache`` rebuild, streamtex renders
    every block inside a hidden ``st.empty().container()`` that is
    immediately wiped by ``hidden.empty()`` once the cache is captured.
    The browser, however, still receives every intermediate delta over
    the WebSocket and pays for the React reconciliation, the
    MutationObserver bookkeeping, and (on big decks) the CSS parse of
    hundreds of per-instance attribute-selector ``<style>`` blocks
    before the wipe can take effect.  On Chrome with the FC-260507 deck
    (~40 styled blocks) this is what produced the multi-tens-of-seconds
    "Loading… 73 % module 30/41" freeze that motivated this branch.

    The cache build itself does **not** need any of that DOM: TOC
    entries, marker entries, the search index and the export buffer are
    all populated by the Python-side state machinery *before* the
    streamlit primitive ever emits.  By suppressing the emits for the
    span of the cache-build loop, we cut the WebSocket payload to a
    couple of progress-iframe + skeleton-container deltas per block and
    keep the browser idle until the visible page renders.

    Restored unconditionally on exit so that the post-cache page render
    (which IS visible) goes through the unpatched streamlit primitives.
    """
    saved = {}
    noop = lambda *a, **kw: None  # noqa: E731 — concise sentinel
    for attr in _CACHE_BUILD_DOM_PATCH_ATTRS:
        if hasattr(st, attr):
            saved[attr] = getattr(st, attr)
            setattr(st, attr, noop)
    try:
        yield
    finally:
        for attr, val in saved.items():
            setattr(st, attr, val)


def _assign_tree_pages(walk, entry_idx: int, pages: list[dict], collector,
                       entry_name: str = "", entry_pos=None) -> None:
    """Close the dry walk of one entry: its pages and the page of what it registered (#121)."""
    starts, local = walk.assign()
    base = len(pages)
    if starts:
        for p in starts:
            node = walk.nodes.get(tuple(p), {})
            parent = walk.nodes.get(tuple(p)[:-1], {}) if len(p) > 1 else {"name": entry_name}
            pages.append({"entry": entry_idx, "start": list(p), "block": node.get("name", entry_name),
                          "parent": parent.get("name", entry_name)})
    else:
        pages.append({"entry": entry_idx, "start": [], "block": entry_name, "parent": ""})
    if _export_page_sentinels:
        # where each page starts in the export (#106): the entry's start, then
        # the end of the previous page-starting inclusion; a start inside an
        # open container cannot be cut and stays with the previous page
        positions = [entry_pos] + [walk.exit_pos.get(tuple(p)) for p in starts[:-1]]
        for j in range(len(positions) - 1, -1, -1):
            if positions[j] is not None:
                export_insert_root(positions[j], PAGE_SENTINEL.format(n=base + j))
    markers = marker_entries()
    tocs = toc_entries() if _toc_mod.toc is not None else []
    stops: set[int] = set()
    for (kind, idx), loc in local.items():
        if kind == "m" and idx < len(markers):
            markers[idx]["page_idx"] = base + loc
            if is_stop(markers[idx]):
                stops.add(base + loc)
        elif kind == "t" and idx < len(tocs):
            tocs[idx]["page_idx"] = base + loc
        elif kind == "s" and collector is not None:
            frags = collector._blocks.pop(idx, None)
            if frags:
                collector._blocks.setdefault(base + loc, []).extend(frags)
    for j in range(base, len(pages)):
        if j not in stops and markers:
            p = pages[j]
            logger.warning("Arrows will not stop on page %d (entry %d, path %s): it holds no stop marker.",
                           j + 1, entry_idx, p["start"])


def _build_page_cache(module_list, toc_config, marker_config, separator,
                      cache_hash,
                      export_config: ExportConfig | None = None,
                      progress_callback=None,
                      hidden_container=None,
                      block_args: tuple = (),
                      block_kwargs: dict | None = None):
    """Execute all blocks inside st.empty() to collect TOC/markers, then cache.

    When *export_config* is provided the export buffer is active during the
    full render so the complete HTML is captured and stored in session_state
    under ``_STX_FULL_EXPORT_HTML_KEY``.

    *hidden_container* is an optional pre-created ``st.empty()`` in the main
    area.  When provided it is used instead of creating a new one — this
    prevents blocks from rendering inside the sidebar when the rebuild is
    triggered from the export panel.
    """
    # Normalise block_kwargs so all downstream code can spread it freely.
    block_kwargs = block_kwargs or {}
    reset_toc_registry(toc_config)
    if marker_config is not None:
        reset_marker_registry(marker_config)

    # Activate export buffer during cache build to capture full-book HTML
    if export_config is not None:
        reset_export_buffer(export_config)
    else:
        reset_export_buffer(ExportConfig(enabled=False))

    # Signal interactive-only widgets (e.g. image editor) to skip rendering
    set_cache_building(True)
    try:
        use_search = toc_config is not None and toc_config.search
        collector = start_collector() if use_search else None

        # Resolve block spacing for cache build (no profile in cache build)
        _block_sp = resolve_block_spacing()

        hidden = hidden_container if hidden_container is not None else st.empty()
        # _suppress_cache_build_dom: see its docstring.  When export_config
        # is provided we still want the streamtex export buffer to be
        # populated, but that buffer is appended-to by ``st_html`` (the
        # streamtex wrapper) *before* the patched ``streamlit.html``
        # call returns, so the buffer is preserved regardless.
        _mode = _pagewalk.paginate_by()
        pages: list[dict] = []
        _limited = _warmup_mode and _warmup_up_to_slide is not None and marker_config is not None
        _kept = len(module_list)
        with hidden.container(), _isolate_widget_keys(), _suppress_cache_build_dom():
            for i, module in enumerate(module_list):
                toc_before = len(toc_entries()) if toc_config else 0
                markers_before = len(marker_entries()) if marker_config else 0
                base = len(pages)          # the entry's first page (#121)

                if collector is not None:
                    collector.set_block(base)
                _entry_pos = export_root_position() if _export_page_sentinels else None
                walk = (_pagewalk.DryWalk(_mode, collector, export_root_position if _export_page_sentinels else None)
                        if _mode != _pagewalk.ENTRY else None)
                walk_token = _pagewalk.activate(walk) if walk is not None else None

                # Block spacing: inject block.top + set flag
                if _block_sp.top is not None:
                    st_space("v", _block_sp.top)
                mark_block_top_injected()
                marker_slide_boundary()     # each entry opens a slide (#116)

                try:
                    if _warmup_mode:
                        try:
                            st_include(module, *block_args, **block_kwargs)
                        except IncludeCycleError:
                            raise           # never skipped: the export would miss it (#119)
                        except Exception as e:
                            name = getattr(e, "_stx_block", None) or getattr(module, '__name__', str(module))
                            logger.warning("Warmup: block %s raised — skipping.", name)
                            _warmup_errors.append((name, f"{type(e).__name__}: {e}"))
                    else:
                        st_include(module, *block_args, **block_kwargs)
                finally:
                    if walk_token is not None:
                        _pagewalk.deactivate(walk_token)

                # Close any open section wrapper + reset per-block override
                from .slide import _close_section_wrapper_if_open
                _close_section_wrapper_if_open()
                reset_block_spacing()

                # The entry's pages, and the page of everything it registered
                _ename = getattr(module, "__name__", str(module))
                if walk is not None:
                    _assign_tree_pages(walk, i, pages, collector, _ename, _entry_pos)
                    if collector is not None:
                        collector.set_block(len(pages) - 1)
                else:
                    pages.append({"entry": i, "start": [], "block": _ename, "parent": ""})
                    if _export_page_sentinels and _entry_pos is not None:
                        export_insert_root(_entry_pos, PAGE_SENTINEL.format(n=base))

                # Tag new TOC entries with their page index
                if toc_config:
                    for entry in toc_entries()[toc_before:]:
                        if "page_idx" not in entry:
                            entry["page_idx"] = base
                # Tag new marker entries with their page index
                if marker_config:
                    for entry in marker_entries()[markers_before:]:
                        if "page_idx" not in entry:
                            entry["page_idx"] = base

                if progress_callback is not None:
                    _mod_name = getattr(module, '__name__', '').rsplit('.', 1)[-1]
                    progress_callback(i + 1, len(module_list), _mod_name)

                if _limited and sum(1 for m in marker_entries() if is_stop(m)) >= _warmup_up_to_slide:
                    _kept = i + 1          # the entry holding the slide, whole (#146)
                    break

                if separator and i < len(module_list) - 1:
                    st_include(separator, *block_args, **block_kwargs)

                # Block spacing: inject block.bottom after build()
                if _block_sp.bottom is not None:
                    st_space("v", _block_sp.bottom)

                # Insert slide break between blocks for PDF page-break support.
                # Without this, the exported HTML has no .stx-slide-break-spacer
                # elements, so @media print page-break rules have nothing to target.
                # marker=False: export slide breaks only need the CSS spacer for
                # page-break-after, not a navigation marker (which would pollute
                # the marker registry with phantom entries).
                if export_config is not None and i < len(module_list) - 1:
                    # the module's own break settings, as every other break (#118)
                    from .slide import _standard_break
                    _standard_break()

        hidden.empty()
    finally:
        set_cache_building(False)

    # Store the full-book HTML before resetting the buffer
    if export_config is not None:
        full_html = generate_export_html()
        if full_html:
            st.session_state[_STX_FULL_EXPORT_HTML_KEY] = full_html
            st.session_state[_STX_FULL_EXPORT_VIEW_KEY] = (export_config.page_width, export_config.zoom)
        reset_export_buffer(ExportConfig(enabled=False))

    search_index = stop_collector() if use_search else None

    if marker_config:
        annotate_marker_numbers(marker_entries())     # #117
    if _warmup_mode and _warmup_up_to_slide is not None:
        global _warmup_limit_result
        _stops = sum(1 for m in marker_entries() if is_stop(m)) if marker_config else 0
        _warmup_limit_result = {"up_to_slide": _warmup_up_to_slide, "last_slide": _stops,
                                "entries": _kept, "stops": _stops}

    # Store navigation data for CLI export enrichment (sidebar, markers, search)
    if export_config is not None:
        st.session_state["_stx_export_nav"] = {
            "toc": copy.deepcopy(toc_entries()) if toc_config else [],
            "markers": copy.deepcopy(marker_entries()) if marker_config else [],
            "search_index": search_index,
        }

    # Persist cited bibliography keys so st_bibliography(only_cited=True) works
    # in paginated mode (cite() calls only run during cache build, not per-page).
    from .bib import get_bib_registry as _get_bib_registry
    _bib_cited = list(_get_bib_registry()._cited)

    st.session_state[_STX_CACHE_KEY] = {
        "hash": cache_hash,
        "toc": copy.deepcopy(toc_entries()) if toc_config else [],
        "markers": copy.deepcopy(marker_entries()) if marker_config else [],
        "total": len(pages),                     # pages (#121)
        "entries": _kept,                        # all of them, unless --up-to-slide (#146)
        "paginate_by": _mode,
        "pages": pages,
        "search_index": search_index,
        "cited_keys": _bib_cited,
        "doc_version": st.session_state.get("_stx_doc_version", ""),
        "lib_version": st.session_state.get("_stx_lib_version", ""),
        # Data files the blocks read through stx.load_*/watch_file during
        # this build (#53): checked again when the persisted cache is loaded.
        "watched": _watched_snapshot(),
    }


def _warmup_build_cache(module_list, toc_config, marker_config, separator,
                        block_args: tuple = (),
                        block_kwargs: dict | None = None):
    """Build and persist the page cache without Streamlit UI (headless).

    Called by ``st_book()`` when ``_warmup_mode`` is True.
    Skips all sidebar / banner / page rendering — only builds the cache
    (TOC, markers, search index) and writes it to disk.

    When ``_warmup_export_config`` is set, the export buffer is activated
    so the full-book HTML is captured in session_state alongside the cache.
    """
    book_file = _find_book_file()                      # the cache belongs to it (#120)
    cache_hash = _compute_cache_hash(module_list, block_args, block_kwargs, book_file)
    cache_path = _resolve_cache_path(module_list, block_args, block_kwargs, book_file)
    # Use the export config if set by CLI ``stx export html``, otherwise disable
    export_cfg = _warmup_export_config
    if export_cfg is not None:
        _build_page_cache(module_list, toc_config, marker_config,
                          separator, cache_hash,
                          export_config=export_cfg,
                          block_args=block_args,
                          block_kwargs=block_kwargs)
    else:
        reset_export_buffer(ExportConfig(enabled=False))
        _build_page_cache(module_list, toc_config, marker_config,
                          separator, cache_hash,
                          block_args=block_args,
                          block_kwargs=block_kwargs)
    cache = st.session_state.get(_STX_CACHE_KEY)
    if _warmup_up_to_slide is not None:
        # a cut document: never the cache the live book would load (#146)
        logger.info("Warmup: --up-to-slide, the page cache is not saved.")
    elif cache and cache_path:
        _save_file_cache(cache_path, cache)
        logger.info("Warmup: saved page cache to %s", cache_path)
    elif not cache_path:
        logger.warning("Warmup: could not determine cache path.")


_STX_REFRESH_SEARCH_KEY = "_stx_refresh_search"


def _build_paginated_sidebar(cache, current_page, total, toc_config, marker_config):
    """Populate the sidebar from cached data (st.markdown for direct DOM access).

    The search JS iframe is normally injected here.  When a "Refresh search
    index" is pending (``_STX_REFRESH_SEARCH_KEY`` in session state), injection
    is deferred to ``_paginated_book`` so the index can be updated first.
    """
    show_search = toc_config is not None and toc_config.search

    with st.sidebar:
        # Search input above tabs (always visible regardless of active tab)
        if show_search:
            st.markdown(generate_search_input_html(), unsafe_allow_html=True)
            if st.button("Refresh search index", key="_stx_refresh_search_pag",
                         use_container_width=True, type="tertiary"):
                st.session_state[_STX_REFRESH_SEARCH_KEY] = True
                st.rerun()

        has_markers = (marker_config is not None
                       and any(is_listed(e) for e in cache.get("markers", [])))

        if has_markers:
            tab_markers, tab_toc = st.tabs(["Markers", "Contents"])
        else:
            tab_toc = st.container()
            tab_markers = None

        # --- TOC ---
        cached_toc = cache.get("toc", [])
        cache_markers = cache.get("markers", [])
        marker_anchors = _toc_dot_anchors(cache_markers)
        indent_char = "&nbsp;"
        effective_max_level = _resolve_sidebar_max_level(toc_config, paginated=True)

        toc_parts = []

        # The cyan entry of each tab is chosen by the floating bar, slide by
        # slide (#130): every entry carries data-stx-nav, and the bar writes
        # one style rule naming the entry of its current slide.
        for pos, entry in enumerate(cached_toc):
            if effective_max_level is not None and entry["level"] > effective_max_level:
                continue
            indent = indent_char * (entry["level"] - 1) * 4
            dot = (
                '<span style="opacity:.5;font-size:6px;vertical-align:middle;'
                'margin-right:4px;">&#9679;</span>'
                if entry.get("key_anchor") in marker_anchors else ""
            )
            page_idx = entry.get("page_idx", 0)
            title_esc = entry["title"]
            if page_idx == current_page:
                link = f'<a href="#{entry["key_anchor"]}">{title_esc}</a>'
            else:
                href = _goto_href(page_idx, _toc_target_marker(entry, cache_markers))
                # the heading, for a long slide whose start would leave it below the screen (#131)
                link = (f'<a href="{href}" class="stx-page-link" '
                        f'data-stx-heading="{entry["key_anchor"]}">{title_esc}</a>')
            block_attr = f' data-stx-block="{page_idx}"' if show_search else ''
            toc_parts.append(
                f'<div data-stx-nav="toc{pos}"{block_attr} style="overflow:hidden;'
                f'text-overflow:ellipsis;white-space:nowrap;padding:1px 0;font-size:14px;">'
                f'{indent}{dot}{link}</div>'
            )

        # Bottom spacer so Download button doesn't overlap last entry
        toc_parts.append('<div style="height:40px;"></div>')

        with tab_toc:
            if toc_parts:
                st.markdown("\n".join(toc_parts), unsafe_allow_html=True)

        # --- Markers ---
        if tab_markers is not None:
            marker_parts = []
            for entry in cache.get("markers", []):
                if not is_listed(entry):
                    continue
                row = marker_row_text(entry)     # same text as the popup (#117)
                page_idx = entry.get("page_idx", 0)
                if page_idx == current_page:
                    link = f'<a href="#{entry["anchor"]}">{row}</a>'
                else:
                    link = (
                        f'<a href="{_goto_href(page_idx, entry["index"])}" class="stx-page-link">'
                        f'{row}</a>'
                    )
                block_attr = f' data-stx-block="{page_idx}"' if show_search else ''
                marker_parts.append(
                    f'<div data-stx-nav="mk{entry["index"]}"{block_attr} style="overflow:hidden;'
                    f'text-overflow:ellipsis;white-space:nowrap;font-size:14px;">{link}</div>'
                )
            marker_parts.append('<div style="height:40px;"></div>')
            with tab_markers:
                if marker_parts:
                    st.markdown("\n".join(marker_parts), unsafe_allow_html=True)

        # Search JS — inject now unless a refresh is pending (in that case
        # _paginated_book injects it after the page renders with updated data).
        if show_search and not st.session_state.get(_STX_REFRESH_SEARCH_KEY):
            search_index = cache.get("search_index")
            if search_index:
                st.iframe(generate_search_script(search_index), height=1)


def _inject_paginated_nav_js(current_page, total, marker_config,
                             page_marker_info=None, last_named_page=None,
                             initial_marker=None, has_bar=True):
    """Inject JS for cross-page navigation via hidden buttons.

    Navigation mechanisms:
    - Banner: IntersectionObserver on sentinel auto-triggers next page on wheel
    - Marker callbacks: cross-page marker navigation from marker.py widget
    - Sidebar links: click .stx-page-link (rendered via st.markdown) to change page
    - Hidden buttons: JS finds stx_nav_* buttons and clicks them programmatically
    """
    js_body = """
<script>
(function() {
    var hostDoc = parent.document;
    var hostWin = hostDoc.defaultView || parent;
    var currentPage = __CURRENT_PAGE__;
    var totalPages = __TOTAL_PAGES__;
    var lastNamedPage = __LAST_NAMED_PAGE__;
    var pageFirstMarker = __PAGE_FIRST_MARKER__;
    var pageLastMarker  = __PAGE_LAST_MARKER__;
    var initialMarker = __INITIAL_MARKER__;

    /* A page without the floating bar has no slide to name: clear the
       sidebar highlight rule the bar of the previous page wrote (#130). */
    if (!__HAS_BAR__) {
        var hlRule = hostDoc.getElementById('stx-sidebar-active-style');
        if (hlRule) hlRule.textContent = '';
    }

    /* --- Deep link (?marker=): the server resolved the page; make the
       marker widget start (and scroll) on the requested marker instead of
       the first marker of the page. Consumed by marker.py's init.       */
    if (initialMarker !== null) {
        hostWin._stxMarkerStartIdx = initialMarker;
    }

    if (hostWin._stxPaginatedCleanup) {
        try { hostWin._stxPaginatedCleanup(); } catch(e) {}
    }

    /* --- Find and hide navigation buttons --- */
    var navButtons = {};
    function findNavButtons() {
        var allBtns = hostDoc.querySelectorAll(
            '[data-testid="stBaseButton-secondary"]');
        for (var i = 0; i < allBtns.length; i++) {
            var txt = (allBtns[i].textContent || '').trim();
            if (txt.indexOf('stx_nav_') === 0) {
                var page = parseInt(txt.substring(8), 10);
                if (!isNaN(page)) {
                    navButtons[page] = allBtns[i];
                    var wrapper = allBtns[i].closest('[data-testid="stButton"]');
                    if (wrapper) wrapper.style.cssText =
                        'position:absolute;left:-9999px;height:0;overflow:hidden;';
                }
            }
        }
    }
    findNavButtons();
    setTimeout(findNavButtons, 300);
    setTimeout(findNavButtons, 1000);

    /* --- Navigate to a specific page by clicking the hidden button --- */
    var navigating = false;
    function navigateToPage(targetPage) {
        if (targetPage < 0 || targetPage >= totalPages) return;
        if (navigating) {
            /* A rerun is already in flight.  Instead of silently dropping
               this request (the old `if (navigating) return;` — issue 6.2,
               the double-click / double-PageDown "stuck" bug), COALESCE it:
               remember the latest requested page and apply it once the
               rerun lands (see the pending-nav block in init below).      */
            if (targetPage !== currentPage) {
                hostWin._stxPendingPage = targetPage;
                hostWin._stxPendingMarker = null;
            }
            return;
        }
        if (targetPage === currentPage) return;
        findNavButtons();
        var btn = navButtons[targetPage];
        if (!btn) return;           /* nothing in flight: no flag left set */
        navigating = true;          /* block further signals */
        hostWin._stxScrollReset = true;
        btn.click();
    }

    /* -- Find the real scroll container --
       Use .stMain directly — it is Streamlit's designated scroll
       container (<section> with overflow:auto).                     */
    var scrollEl = (function() {
        var main = hostDoc.querySelector('.stMain')
                || hostDoc.querySelector('[data-testid="stMain"]');
        if (main) return main;
        /* Fallback: walk up from content */
        var start = hostDoc.querySelector('[data-testid="stVerticalBlock"]')
                 || hostDoc.body;
        var el = start;
        while (el && el !== hostDoc.documentElement) {
            var ov = hostWin.getComputedStyle(el).overflowY;
            if (ov === 'auto' || ov === 'scroll' || ov === 'overlay')
                return el;
            el = el.parentElement;
        }
        return hostDoc.scrollingElement || hostDoc.documentElement;
    })();

    /* -- Scroll reset after page navigation --
       Dual mechanism: explicit _stxScrollReset flag (set by navigateToPage)
       + page-change detection (_stxPrevPage) which covers banner button
       clicks that go through on_click Python callbacks directly.         */
    var needsReset = false;
    if (hostWin._stxScrollReset) {
        hostWin._stxScrollReset = false;
        needsReset = true;
    }
    var prevPage = hostWin._stxPrevPage;
    hostWin._stxPrevPage = currentPage;
    if (prevPage !== undefined && prevPage !== currentPage) {
        needsReset = true;
    }
    if (needsReset) {
        function doScrollReset() {
            scrollEl.scrollTop = 0;
            var mains = hostDoc.querySelectorAll('.stMain, [data-testid="stMain"]');
            for (var m = 0; m < mains.length; m++) mains[m].scrollTop = 0;
            try { hostWin.scrollTo({top: 0, behavior: 'instant'}); }
            catch(e) { hostWin.scrollTo(0, 0); }
        }
        doScrollReset();
        [0, 50, 100, 200, 400].forEach(function(ms) {
            setTimeout(doScrollReset, ms);
        });
    }

    /* =================================================================
     * BANNER — banner clicks + auto-trigger zones
     *
     * Bottom: IntersectionObserver on sentinel + wheel/touch deltaY > 0
     * Top:    isAtTop() + wheel/touch deltaY < 0  (800ms startup delay)
     * Banners: click on red banners → navigateToPage
     * ================================================================= */
    var sentinel = null;
    var prevBanner = null;
    var nextBanner = null;
    var bannerNextActive = false;
    var bannerNextTimer = null;
    var bannerPrevTimer = null;
    var bannerObs = null;
    var bannerPrevReady = false;

    function isAtTop() { return scrollEl.scrollTop < 15; }

    /* Delay top auto-trigger to avoid residual momentum after scroll reset */
    var bannerReadyTimer = setTimeout(function() {
        bannerPrevReady = true;
    }, 800);

    /* --- Trackpad inertia cooldown ---
       When the user scrolls to a boundary (bottom sentinel visible or
       top of page), trackpad inertia keeps firing wheel events.  Without
       protection these residual events can trigger an unwanted page
       change.  The cooldown absorbs inertia events and only re-arms
       navigation after TWO conditions are met:
         1. At least COOLDOWN_MIN_MS since the boundary was reached
         2. No wheel event for COOLDOWN_GAP_MS (= inertia has stopped)
       This adapts naturally: mouse wheels (no inertia) clear quickly,
       long trackpad gestures wait until inertia actually ends.          */
    var COOLDOWN_MIN_MS = 400;
    var COOLDOWN_GAP_MS = 150;
    var nextCooldown = false;       /* bottom boundary cooldown active */
    var nextCooldownSince = 0;      /* timestamp when bottom cooldown started */
    var nextCooldownEnd = null;     /* timer: gap detection for bottom */
    var prevCooldown = false;       /* top boundary cooldown active */
    var prevCooldownSince = 0;
    var prevCooldownEnd = null;
    var prevCooldownDone = false;   /* true once cooldown completed (reset on leave) */

    /* --- Deferred element lookup (DOM may not be ready on cold start) --- */
    function prevClick() {
        if (navigating || currentPage <= 0) return;
        var pp = currentPage - 1;
        hostWin._stxMarkerStartIdx =
            pageFirstMarker[pp] !== undefined ? pageFirstMarker[pp] : null;
        navigateToPage(pp);
    }
    function nextClick() {
        if (navigating) return;
        var np;
        if (currentPage >= lastNamedPage) {
            /* Loop back to first page */
            np = 0;
        } else if (currentPage >= totalPages - 1) {
            return;
        } else {
            np = currentPage + 1;
        }
        hostWin._stxMarkerStartIdx =
            pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : null;
        navigateToPage(np);
    }

    function findElements() {
        /* Sentinel — attach IntersectionObserver on first find */
        if (!sentinel && currentPage < totalPages - 1) {
            sentinel = hostDoc.getElementById('stx-banner-sentinel');
            if (sentinel && !bannerObs) {
                bannerObs = new hostWin.IntersectionObserver(function(entries) {
                    var wasActive = bannerNextActive;
                    bannerNextActive = entries[0].isIntersecting;
                    if (!bannerNextActive) {
                        clearTimeout(bannerNextTimer); bannerNextTimer = null;
                        /* Reset cooldown when user scrolls away from boundary */
                        nextCooldown = false;
                        clearTimeout(nextCooldownEnd); nextCooldownEnd = null;
                    } else if (!wasActive) {
                        /* Sentinel just became visible — start cooldown */
                        nextCooldown = true;
                        nextCooldownSince = Date.now();
                        clearTimeout(nextCooldownEnd); nextCooldownEnd = null;
                    }
                }, { threshold: 0.1 });
                bannerObs.observe(sentinel);
            }
        }
        /* Banners — attach click handlers on first find */
        if (!prevBanner) {
            prevBanner = hostDoc.getElementById('stx-banner-prev');
            if (prevBanner) prevBanner.addEventListener('click', prevClick);
        }
        if (!nextBanner) {
            nextBanner = hostDoc.getElementById('stx-banner-next');
            if (nextBanner) nextBanner.addEventListener('click', nextClick);
        }
    }
    findElements();
    setTimeout(findElements, 300);
    setTimeout(findElements, 1000);

    function bannerWheel(e) {
        if (navigating) return;

        /* Bottom: scroll down while sentinel visible → next page */
        if (e.deltaY > 0 && bannerNextActive) {
            clearTimeout(bannerPrevTimer); bannerPrevTimer = null;

            /* Cooldown: absorb trackpad inertia events */
            if (nextCooldown) {
                if (Date.now() - nextCooldownSince < COOLDOWN_MIN_MS) return;
                /* Min time elapsed — wait for inertia gap to end cooldown */
                clearTimeout(nextCooldownEnd);
                nextCooldownEnd = setTimeout(function() {
                    nextCooldown = false;
                }, COOLDOWN_GAP_MS);
                return;
            }

            if (!bannerNextTimer) {
                bannerNextTimer = setTimeout(function() {
                    if (!bannerNextActive || navigating) return;
                    var np = currentPage >= lastNamedPage ? 0 : currentPage + 1;
                    hostWin._stxMarkerStartIdx =
                        pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : null;
                    navigateToPage(np);
                }, 400);
            }
            return;
        }

        /* Top: scroll up while at top of page → prev page */
        if (e.deltaY < 0 && bannerPrevReady
                && currentPage > 0 && isAtTop()) {
            clearTimeout(bannerNextTimer); bannerNextTimer = null;

            /* Cooldown: absorb trackpad inertia events.
               prevCooldownDone stays true once cooldown has elapsed,
               so navigation proceeds until user scrolls away and back. */
            if (!prevCooldown && !prevCooldownDone) {
                prevCooldown = true;
                prevCooldownSince = Date.now();
            }
            if (prevCooldown) {
                if (Date.now() - prevCooldownSince < COOLDOWN_MIN_MS) return;
                clearTimeout(prevCooldownEnd);
                prevCooldownEnd = setTimeout(function() {
                    prevCooldown = false;
                    prevCooldownDone = true;
                }, COOLDOWN_GAP_MS);
                return;
            }

            if (!bannerPrevTimer) {
                bannerPrevTimer = setTimeout(function() {
                    if (navigating || !isAtTop()) return;
                    var pp = currentPage - 1;
                    hostWin._stxMarkerStartIdx =
                        pageFirstMarker[pp] !== undefined ? pageFirstMarker[pp] : null;
                    navigateToPage(pp);
                }, 400);
            }
            return;
        }

        /* Not at a boundary: cancel timers */
        clearTimeout(bannerNextTimer); bannerNextTimer = null;
        clearTimeout(bannerPrevTimer); bannerPrevTimer = null;
        /* Reset top cooldown when user scrolls away from top */
        if (!isAtTop()) {
            prevCooldown = false;
            prevCooldownDone = false;
            clearTimeout(prevCooldownEnd); prevCooldownEnd = null;
        }
    }

    /* Wheel listener — handles both top and bottom auto-trigger */
    hostDoc.addEventListener('wheel', bannerWheel, { passive: true });

    /* Touch listener — iOS/mobile fallback (wheel events don't fire
       for touch scrolling on Safari/iOS).  We track touch start/end
       positions and synthesise the same logic as bannerWheel.        */
    var touchStartY = null;
    hostDoc.addEventListener('touchstart', function(e) {
        if (e.touches.length === 1) touchStartY = e.touches[0].clientY;
    }, { passive: true });
    hostDoc.addEventListener('touchend', function(e) {
        if (touchStartY === null || navigating) return;
        var endY = e.changedTouches[0].clientY;
        var deltaY = touchStartY - endY;   /* positive = swipe up (scroll down) */
        touchStartY = null;
        var threshold = 40;                 /* px – ignore tiny taps */
        if (Math.abs(deltaY) < threshold) return;
        bannerWheel({ deltaY: deltaY });
    }, { passive: true });

    /* --- Cross-page marker callbacks (used by marker.py widget) --- */
    hostWin._stxMarkerGoToPage = function(page) {
        navigateToPage(page);
    };

    hostWin._stxMarkerBoundary = function(direction) {
        if (direction === 'next') {
            var np;
            if (currentPage >= lastNamedPage) {
                np = 0;  /* Loop back to first page */
            } else if (currentPage < totalPages - 1) {
                np = currentPage + 1;
            } else {
                return;
            }
            hostWin._stxMarkerStartIdx =
                pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : null;
            navigateToPage(np);
        } else if (direction === 'prev') {
            var pp;
            if (currentPage > 0) {
                pp = currentPage - 1;
            } else {
                pp = lastNamedPage;  /* Loop back to last page */
            }
            hostWin._stxMarkerStartIdx =
                pageLastMarker[pp] !== undefined ? pageLastMarker[pp] : null;
            navigateToPage(pp);
        }
    };

    /* --- Ensure marker start index matches current page ---
       Covers cases where no explicit navigation handler set it
       (e.g. sidebar link click, initial page load, browser refresh).
       Runs synchronously BEFORE marker.py's 500ms init reads it. */
    if (hostWin._stxMarkerStartIdx == null) {
        var fm = pageFirstMarker[currentPage];
        if (fm !== undefined) hostWin._stxMarkerStartIdx = fm;
    }

    /* --- Apply a coalesced pending navigation (issue 6.2) ---
       If a second navigation arrived while the previous rerun was in
       flight, navigateToPage stored the latest requested page here rather
       than dropping it.  Now that we have landed, apply it so a rapid
       double-press advances correctly (and the widget lands on the right
       marker) instead of getting stuck one page short.                  */
    if (hostWin._stxPendingPage != null) {
        var pend = hostWin._stxPendingPage;
        var pendMarker = hostWin._stxPendingMarker;
        hostWin._stxPendingPage = null;
        hostWin._stxPendingMarker = null;
        if (pend !== currentPage && pend >= 0 && pend < totalPages) {
            hostWin._stxMarkerStartIdx = pendMarker != null ? pendMarker
                : (pageFirstMarker[pend] !== undefined ? pageFirstMarker[pend] : null);
            navigateToPage(pend);
        }
    }

    /* --- Sidebar link interception (st.markdown = direct DOM) --- */
    function linkClick(e) {
        var a = e.target.closest('a[href^="#stx-goto-"]');
        if (!a) return;
        e.preventDefault();
        e.stopPropagation();
        var href = a.getAttribute('href') || '';
        var match = href.match(/^#stx-goto-(\\d+)(?:-(\\d+))?/);
        if (!match) return;
        var p = parseInt(match[1], 10);
        if (isNaN(p) || p === currentPage) return;
        /* The floating marker widget initialises on the link's marker
           (#stx-goto-<page>-<marker>, #127), else on the page's first. */
        var target = match[2] !== undefined ? parseInt(match[2], 10)
            : (pageFirstMarker[p] !== undefined ? pageFirstMarker[p] : null);
        hostWin._stxMarkerStartIdx = target;
        /* a Contents heading: the bar shows it if its slide start would leave it below the screen (#131) */
        hostWin._stxLandingHeading = a.getAttribute('data-stx-heading') || null;
        navigateToPage(p);
        /* a rerun in flight queued the page: queue its marker with it */
        if (hostWin._stxPendingPage === p) hostWin._stxPendingMarker = target;
    }
    hostDoc.addEventListener('click', linkClick, true);

    /* --- Cleanup --- */
    hostWin._stxPaginatedCleanup = function() {
        if (bannerObs) bannerObs.disconnect();
        hostDoc.removeEventListener('wheel', bannerWheel);
        clearTimeout(bannerNextTimer);
        clearTimeout(bannerPrevTimer);
        clearTimeout(bannerReadyTimer);
        clearTimeout(nextCooldownEnd);
        clearTimeout(prevCooldownEnd);
        if (prevBanner) prevBanner.removeEventListener('click', prevClick);
        if (nextBanner) nextBanner.removeEventListener('click', nextClick);
        hostDoc.removeEventListener('click', linkClick, true);
        hostWin._stxMarkerBoundary = null;
        hostWin._stxMarkerGoToPage = null;
    };
})();
</script>
"""
    pmi_first = json.dumps(page_marker_info["first"]) if page_marker_info else "{}"
    pmi_last = json.dumps(page_marker_info["last"]) if page_marker_info else "{}"
    _lnp = last_named_page if last_named_page is not None else total - 1
    js_body = (js_body
               .replace("__CURRENT_PAGE__", str(current_page))
               .replace("__TOTAL_PAGES__", str(total))
               .replace("__LAST_NAMED_PAGE__", str(_lnp))
               .replace("__PAGE_FIRST_MARKER__", pmi_first)
               .replace("__PAGE_LAST_MARKER__", pmi_last)
               .replace("__INITIAL_MARKER__",
                        str(int(initial_marker)) if initial_marker is not None else "null")
               .replace("__HAS_BAR__", "true" if has_bar else "false"))
    st.iframe(js_body, height=1)


def _paginated_book(module_list, toc_config, marker_config, separator,
                    export, export_title, banner_config: BannerConfig,
                    pdf_config=None, exports=None, inspector=None,
                    page_width=100, zoom=100,
                    profile_names=None, active_profile=None,
                    profile_modified=False, all_profiles=None,
                    loading=False,
                    block_args: tuple = (),
                    block_kwargs: dict | None = None,
                    html_export_zoom: int = 0):
    """Paginated rendering — only renders one block per rerun."""
    start_time = time.time()
    logger.debug("Starting st_book (paginated)...")
    # Normalise block_kwargs so all downstream code can spread it freely.
    block_kwargs = block_kwargs or {}

    total = len(module_list)
    if total == 0:
        # Defensive: ensure the loading overlay (injected by st_book before
        # delegating to us) doesn't get stuck on screen when the book has
        # no blocks to render.
        if loading:
            remove_loading_overlay()
        return

    # --- Common setup ---
    # (Settings expander already rendered by st_book before branching here)
    load_css("default.css")
    inject_link_preview_scaffold()
    _inject_bib_preview_if_enabled()

    # Inject inspector CSS once + reserve sidebar placeholder
    _inspector_placeholder = None
    if inspector and inspector.enabled:
        from .inspector import inject_inspector_css
        inject_inspector_css()
        with st.sidebar:
            _inspector_placeholder = st.empty()

    # --- Effective layout values (needed by both cache build and current-page export) ---
    effective_pw = f"{st.session_state.get(_PAGE_WIDTH_KEY, page_width)}%"
    effective_zoom = st.session_state.get(_ZOOM_KEY, zoom) / 100

    # --- Cache management (3-tier: session → file → full rebuild) ---
    book_file = _find_book_file()                      # the cache belongs to it (#120)
    cache_hash = _compute_cache_hash(module_list, block_args, block_kwargs, book_file)
    cache_path = _resolve_cache_path(module_list, block_args, block_kwargs, book_file)

    # Tier 1: session_state (instant — survives intra-session reruns)
    cache = st.session_state.get(_STX_CACHE_KEY)
    has_valid_cache = (
        cache is not None
        and cache.get("hash") == cache_hash
        and _watched_current(cache)
        and cache.get("entries", cache.get("total")) == total
        and cache.get("paginate_by", _pagewalk.ENTRY) == _pagewalk.paginate_by()
    )
    # Invalidate cache if search was enabled but cache lacks search_index
    if has_valid_cache and toc_config and toc_config.search:
        if cache.get("search_index") is None:
            has_valid_cache = False

    # Tier 2: persistent file cache (fast — survives restarts/reloads)
    if not has_valid_cache and cache_path:
        file_cache = _load_file_cache(cache_path, cache_hash)
        if file_cache is not None:
            # Extra validation: search_index must be present if search is on
            if toc_config and toc_config.search and file_cache.get("search_index") is None:
                file_cache = None
            if file_cache is not None:
                st.session_state[_STX_CACHE_KEY] = file_cache
                cache = file_cache
                has_valid_cache = True
                logger.info("Restored page cache from disk (skipped full render).")

    # Tier 3: full rebuild (slow — renders all blocks in hidden container)
    if not has_valid_cache:
        # Pass export_config so the cache build also captures the full-book HTML
        _cache_export_cfg = None
        if export:
            _cache_export_cfg = ExportConfig(
                enabled=True, page_title=export_title,
                page_width=effective_pw, zoom=effective_zoom,
            )
        # Progress callback for loading overlay
        _progress_cb = update_loading_progress if loading else None
        try:
            _build_page_cache(module_list, toc_config, marker_config,
                              separator, cache_hash,
                              export_config=_cache_export_cfg,
                              progress_callback=_progress_cb,
                              block_args=block_args,
                              block_kwargs=block_kwargs)
        except IncludeCycleError as e:
            # the DOM is suppressed during the build: show it now (#119)
            st.error(str(e))
            raise
        cache = st.session_state[_STX_CACHE_KEY]
        # Persist to disk for future sessions
        if cache_path:
            _save_file_cache(cache_path, cache)

    # When cache was restored from session/disk, full-book HTML may be missing.
    # We do NOT rebuild here — _build_page_cache() renders all blocks in a
    # hidden st.empty() container, creating temporary iframes that interfere
    # with the marker navigation bar and cause it to freeze.
    # Instead, store a rebuild callback in session_state so the export panel
    # can trigger it on-demand when the user clicks "Generate".
    if export and _STX_FULL_EXPORT_HTML_KEY not in st.session_state:
        # Pre-create a hidden placeholder in the MAIN area so that when the
        # export panel (in the sidebar) triggers a rebuild, blocks render here
        # instead of polluting the sidebar.
        _main_placeholder = st.empty()
        def _rebuild_full_export():
            _ecfg = ExportConfig(
                enabled=True, page_title=export_title,
                page_width=effective_pw, zoom=effective_zoom,
            )
            _build_page_cache(module_list, toc_config, marker_config,
                              separator, cache_hash,
                              export_config=_ecfg,
                              hidden_container=_main_placeholder,
                              block_args=block_args,
                              block_kwargs=block_kwargs)
        st.session_state["_stx_export_rebuild_fn"] = _rebuild_full_export

    # Remove loading overlay (after cache is ready, before page render)
    if loading:
        remove_loading_overlay()

    # Pages (#121): one per entry, or following the composition tree
    n_entries = total
    pages = cache.get("pages") or [{"entry": i, "start": []} for i in range(n_entries)]
    total = len(pages)
    _tree_mode = _pagewalk.paginate_by() != _pagewalk.ENTRY
    if _tree_mode:
        _rederive_current_page(cache)

    # --- Current page ---
    # First run of the session: honour a deep link (?marker= / ?page=, see
    # deeplink.py). Any other run keeps the page chosen by the navigation.
    if _STX_PAGE_KEY not in st.session_state:
        _init_page, _init_marker = _initial_page_from_url(cache, total)
        st.session_state[_STX_PAGE_KEY] = _init_page
        if _init_marker is not None:
            st.session_state[_STX_INITIAL_MARKER_KEY] = _init_marker
    current_page = max(0, min(st.session_state[_STX_PAGE_KEY], total - 1))
    st.session_state[_STX_PAGE_KEY] = current_page

    # --- Sidebar (from cache) ---
    _build_paginated_sidebar(cache, current_page, total, toc_config, marker_config)

    # --- Search index refresh (current page only) ---
    _refresh_search = st.session_state.pop(_STX_REFRESH_SEARCH_KEY, False)
    if _refresh_search:
        _refresh_collector = start_collector()
        _refresh_collector.set_block(current_page)
    reset_export_buffer(ExportConfig(enabled=export, page_title=export_title,
                                     page_width=effective_pw, zoom=effective_zoom))
    reset_toc_registry(toc_config)
    if marker_config is not None:
        reset_marker_registry(marker_config)

    # Pre-seed TOC so numbering/anchors match cache
    if toc_config and cache.get("toc"):
        _preseed_toc_registry(cache["toc"], current_page)

    # Pre-seed markers for pages BEFORE current (for global navigation)
    if marker_config and cache.get("markers"):
        from . import marker as _marker_mod
        registry = _marker_mod._registry
        if registry is not None:
            for entry in cache["markers"]:
                if entry.get("page_idx", 0) >= current_page:
                    break
                registry._entries.append(dict(entry, page=entry.get("page_idx", 0)))

    # Pre-seed bibliography cited keys from cache so only_cited=True works
    if cache.get("cited_keys"):
        from .bib import get_bib_registry as _get_bib_reg
        _bib_reg = _get_bib_reg()
        for _key in cache["cited_keys"]:
            if _key not in _bib_reg._cited:
                _bib_reg._cited.append(_key)

    # --- Banner — page titles for navigation labels ---
    page_titles = _get_page_titles(cache, total)
    page_named = _page_named(cache, page_titles, pages, _tree_mode)

    # Banner — top (previous section, clickable via JS)
    # Skip banner for unnamed pages (e.g., footer blocks without markers/TOC)
    if current_page > 0 and banner_config.mode != BannerMode.HIDDEN:
        _prev = page_titles[current_page - 1]
        if page_named[current_page - 1]:
            _render_banner("stx-banner-prev", _prev, "◂", banner_config)
            css = banner_config._resolve()
            if css and css["show_dividers"]:
                st.divider()

    # --- Render current block (with block spacing) ---
    _pg_active_prof = None
    if all_profiles and active_profile:
        _pg_active_prof = next((p for p in all_profiles if p.name == active_profile), None)
    set_active_profile(_pg_active_prof)
    _pg_block_sp = resolve_block_spacing(profile=_pg_active_prof)
    _page = pages[current_page]
    _entry_idx = _page.get("entry", current_page)
    # block.top belongs to the entry: before its first page only (#121)
    _first_of_entry = current_page == 0 or pages[current_page - 1].get("entry") != _entry_idx
    if _first_of_entry:
        if _pg_block_sp.top is not None:
            st_space("v", _pg_block_sp.top)
        mark_block_top_injected()
    _inject_block_horizontal_css(_pg_block_sp)

    marker_slide_boundary()     # each entry opens a slide (#116)
    try:
        _render_page(module_list[_entry_idx], _page, pages, block_args, block_kwargs, inspector)
    finally:
        from .slide import _close_section_wrapper_if_open
        _close_section_wrapper_if_open()
        reset_block_spacing()

    # --- Finalize search index refresh ---
    if _refresh_search:
        new_texts = stop_collector()
        search_index = cache.get("search_index")
        if search_index is not None and new_texts:
            search_index.update(new_texts)
            st.session_state[_STX_CACHE_KEY] = cache
        # Re-inject search JS with updated index (deferred from sidebar)
        if cache.get("search_index"):
            with st.sidebar:
                st.iframe(
                    generate_search_script(cache["search_index"]), height=1)

    # Banner — bottom (next section or loop-back to first)
    if current_page < total - 1:
        _next = page_titles[current_page + 1]
        _next_is_named = page_named[current_page + 1]
        if banner_config.mode != BannerMode.HIDDEN:
            css = banner_config._resolve()
            if _next_is_named:
                # Normal next-page banner
                if css and css["show_dividers"]:
                    st.divider()
                _render_banner("stx-banner-next", _next, "▸", banner_config)
            else:
                # Next page is unnamed (footer) → loop back to first page
                _first = page_titles[0]
                if page_named[0] and css:
                    if css["show_dividers"]:
                        st.divider()
                    _render_loop_banner(_first, banner_config)
        # Buffer zone before auto-trigger sentinel (padding disabled —
        # trackpad inertia cooldown in JS handles accidental navigation)
        st.markdown(
            '<div class="stx-banner-buffer"></div>'
            "<style>"
            ".stx-banner-buffer{padding-top:0px}"
            "</style>",
            unsafe_allow_html=True,
        )
    elif banner_config.mode != BannerMode.HIDDEN:
        # Last page (including footer) → loop back to first page
        _first = page_titles[0]
        css = banner_config._resolve()
        if page_named[0] and css:
            if css["show_dividers"]:
                st.divider()
            _render_loop_banner(_first, banner_config)
    # Sentinel always rendered (even in HIDDEN mode) for auto-scroll JS
    if current_page < total - 1:
        st.markdown(
            '<div id="stx-banner-sentinel" style="height:1px;"></div>',
            unsafe_allow_html=True,
        )

    # Post-seed markers for pages AFTER current (for global navigation)
    if marker_config and cache.get("markers"):
        from . import marker as _marker_mod
        registry = _marker_mod._registry
        if registry is not None:
            for entry in cache["markers"]:
                if entry.get("page_idx", 0) <= current_page:
                    continue
                registry._entries.append(dict(entry, page=entry.get("page_idx", 0)))
    if marker_config is not None:
        # one number per marker, the live entries of this page included (#117)
        annotate_marker_numbers(marker_entries())

    # --- Presentation footer (auto-rendered when PresentationConfig is active) ---
    _pres_cfg = get_presentation_config()
    if _pres_cfg is not None and _stops_on_page(cache.get("markers", []), current_page) > 1:
        presentation_page_scrolls(_pres_cfg)         # several slides on this page (#153)
    if _pres_cfg is not None and _pres_cfg.footer:
        _n = stop_count() if _pres_cfg.counter_mode == "slide" else 0
        if _n:
            # first paint = the slide the widget will start on (#117)
            _first = _footer_first_slide(cache.get("markers", []), current_page,
                                         st.session_state.get(_STX_INITIAL_MARKER_KEY))
            st_presentation_footer(current_slide=_first, total_slides=_n, config=_pres_cfg)
        else:
            st_presentation_footer(
                current_slide=current_page + 1,
                total_slides=total,
                config=_pres_cfg,
            )

    # --- Export downloads (BEFORE marker navigation) ---
    # The export panel creates sidebar widgets (expander, form, checkboxes).
    # These MUST be rendered before inject_marker_navigation() because
    # adding sidebar widgets AFTER the marker iframe causes Streamlit to
    # rebuild the sidebar DOM, which destroys the marker iframe and freezes
    # the floating navigation bar.
    if is_export_active():
        section_html = generate_export_html()
        if section_html:
            base_name = export_title.replace(' ', '_').lower()
            # Auto-export uses full-book HTML when available
            _full_html = st.session_state.get(_STX_FULL_EXPORT_HTML_KEY) or section_html
            if exports:
                _run_auto_exports(exports, _full_html, base_name)
            _show_manual = exports is None or any(
                c.mode == ExportMode.MANUAL for c in exports
            )
            if _show_manual:
                with st.sidebar:
                    _offer_export_downloads(section_html, base_name,
                                            pdf_config=pdf_config, paginated=True,
                                            html_zoom=html_export_zoom)

    # --- Marker navigation widget (ALL markers, cross-page aware) ---
    # Skip the widget if the current page has no markers (e.g. footer)
    _page_has_markers = any(
        e.get("page_idx", 0) == current_page for e in cache.get("markers", [])
    ) or (_tree_mode and any(is_stop(e) for e in cache.get("markers", [])))   # #121 (w1)
    if marker_config is not None and _page_has_markers:
        inject_marker_navigation(
            profile_names=profile_names,
            active_profile=active_profile,
            profile_modified=profile_modified,
            nav_toc=_toc_nav_table(cache.get("toc", []), cache.get("markers", []),
                                   _resolve_sidebar_max_level(toc_config, paginated=True)),
        )

    # --- Hidden navigation buttons (one per page, clickable by JS) ---
    for i in range(total):
        def _goto_page(page=i):
            st.session_state[_STX_PAGE_KEY] = page
        st.button(f"stx_nav_{i}", key=f"_stx_goto_{i}", on_click=_goto_page)

    # --- Compute page↔marker mapping for synchronized navigation ---
    page_marker_info = None
    if marker_config and cache.get("markers"):
        page_first = {}
        page_last = {}
        for entry in cache["markers"]:
            if not is_stop(entry):
                continue
            pg = entry.get("page_idx", 0)
            if pg not in page_first:
                page_first[pg] = entry["index"]
            page_last[pg] = entry["index"]
        page_marker_info = {"first": page_first, "last": page_last}

    # --- Compute last named page (for loop-back on overscroll) ---
    _last_named = total - 1
    for i in range(total - 1, -1, -1):
        if page_named[i]:
            _last_named = i
            break

    # --- Paginated navigation JS (finds & hides buttons, overscroll, callbacks) ---
    # A deep-linked marker is consumed once: the widget scrolls to it on this
    # run, later runs fall back to the first marker of the page.
    _initial_marker = st.session_state.pop(_STX_INITIAL_MARKER_KEY, None)
    _inject_paginated_nav_js(current_page, total, marker_config, page_marker_info,
                             last_named_page=_last_named,
                             initial_marker=_initial_marker,
                             has_bar=marker_config is not None and _page_has_markers)

    # --- Inspector panel (opt-in, rendered into reserved sidebar placeholder) ---
    if _inspector_placeholder is not None and st.session_state.get("_stx_inspector_open", False):
        from .inspector import FileCategoryRegistry, _find_project_root, discover_sources, render_inspector_panel
        _block_name = st.session_state.get("_stx_inspector_block", "")
        _target = next(
            (m for m in module_list
             if getattr(m, '__name__', '').rsplit('.', 1)[-1] == _block_name),
            None,
        )
        if _target:
            _cat_registry = FileCategoryRegistry()
            _sources = discover_sources(_target, _cat_registry)
            _proj_root = _find_project_root(getattr(_target, '__file__', '') or '')
            render_inspector_panel(
                _sources, inspector, _cat_registry, _inspector_placeholder,
                project_root=_proj_root,
            )

    end_time = time.time()
    logger.debug("st_book (paginated) completed in %.2fs [page %d/%d]",
                 end_time - start_time, current_page + 1, total)


# ---------------------------------------------------------------------------
# Book defaults declared once per project (#90)
# ---------------------------------------------------------------------------

#: The book settings ``[book.defaults]`` of ``stx.toml`` may provide. Book
#: configuration only — nothing that reaches the content of a block.
BOOK_DEFAULT_KEYS = frozenset({
    "paginate", "paginate_by", "html_export_mode", "page_width", "zoom", "export", "export_title", "loading",
    "chrome_banner", "banner_color", "doc_version", "lang", "html_export_zoom",
})


def _main_script_dir() -> str:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx(suppress_warning=True)
        path = getattr(ctx, "main_script_path", None) if ctx else None
        if path:
            return os.path.dirname(os.path.abspath(path))
    except Exception:  # noqa: BLE001 — bare mode / Streamlit drift
        pass
    return os.getcwd()


def _find_upwards(start: str, name: str) -> str | None:
    cur = os.path.abspath(start)
    while True:
        cand = os.path.join(cur, name)
        if os.path.isfile(cand):
            return cand
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def _book_defaults(start: str | None = None) -> dict:
    """``[book.defaults]`` of the nearest ``stx.toml`` above the book (live re-read)."""
    path = _find_upwards(start or _main_script_dir(), "stx.toml")
    if not path:
        return {}
    from .watch import load_toml

    try:
        section = load_toml(path).get("book", {}).get("defaults", {})
    except Exception:  # noqa: BLE001 — a broken stx.toml must not break the book
        logger.warning("stx.toml [book.defaults] unreadable: %s", path, exc_info=True)
        return {}
    unknown = set(section) - BOOK_DEFAULT_KEYS
    if unknown:
        logger.warning("stx.toml [book.defaults]: ignored key(s) %s (allowed: %s)",
                       sorted(unknown), ", ".join(sorted(BOOK_DEFAULT_KEYS)))
    return {k: v for k, v in section.items() if k in BOOK_DEFAULT_KEYS}


def _project_version(start: str | None = None) -> str | None:
    """``[project].version`` of the nearest ``pyproject.toml`` above the book."""
    path = _find_upwards(start or _main_script_dir(), "pyproject.toml")
    if not path:
        return None
    from .watch import load_toml

    try:
        return load_toml(path).get("project", {}).get("version")
    except Exception:  # noqa: BLE001
        return None


import functools as _functools  # noqa: E402
import inspect as _inspect  # noqa: E402

_IMPL_PARAMS = list(_inspect.signature(_st_book_impl).parameters)


_DEFAULTS_DOC = """Generates a web page e-book from a list of block modules.

    Every parameter of the book can be given here; the ones NOT given are
    taken from ``[book.defaults]`` of the project's ``stx.toml`` when it
    declares them (``paginate``, ``page_width``, ``zoom``, ``export``,
    ``export_title``, ``loading``, ``chrome_banner``, ``banner_color``,
    ``doc_version``, ``lang``), then from the defaults below.
    ``doc_version="auto"`` reads ``[project].version`` of ``pyproject.toml``.
    """


@_functools.wraps(_st_book_impl)
def st_book(module_list, *args, **kwargs):
    positional = set(_IMPL_PARAMS[1:1 + len(args)])
    for key, value in _book_defaults().items():
        if key not in kwargs and key not in positional:
            kwargs[key] = value
    return _st_book_impl(module_list, *args, **kwargs)


# functools.wraps copied the implementation's docstring over the wrapper's:
# keep both, so help(st_book) documents [book.defaults] and doc_version="auto".
st_book.__doc__ = _DEFAULTS_DOC + "\n" + (_st_book_impl.__doc__ or "")
