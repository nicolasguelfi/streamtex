import copy
import hashlib
import importlib.resources as resources
import json
import logging
import os
import time

import streamlit as st
import streamlit.components.v1 as components
from streamlit.delta_generator import DeltaGenerator as Delta

from . import toc as _toc_mod
from .auth import _password_gate
from .banner import BannerConfig, BannerMode, _render_banner
from .code import add_wrap_all_option
from .enums import Tags
from .export import ExportConfig, generate_export_html, is_export_active, reset_export_buffer
from .marker import MarkerConfig, inject_marker_navigation, marker_entries, reset_marker_registry
from .pdf_export import PdfConfig
from .search import generate_search_input_html, generate_search_script, start_collector, stop_collector
from .slide import add_slide_break_options
from .space import st_br, st_space
from .styles import Style
from .toc import NumberingMode, TOCConfig, reset_toc_registry, toc_entries
from .utils import inject_link_preview_scaffold
from .write import st_write
from .zoom import _PAGE_WIDTH_KEY, _ZOOM_KEY, add_zoom_options

logger = logging.getLogger(__name__)


def _is_pdf_available() -> bool:
    """Return True if playwright is installed (PDF export possible)."""
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def _offer_export_downloads(html: str, base_name: str,
                            pdf_config: PdfConfig | None = None) -> None:
    """Render a 'Download as...' expander with format selection and download buttons.

    Uses st.form so that toggling options does NOT trigger a full page rerun.
    Files are generated on submit and cached in session_state.
    """
    from .pdf_export import PdfMode, export_pdf

    pdf_available = _is_pdf_available()
    state_key = f"_stx_export_{base_name}"
    defaults = pdf_config or PdfConfig()

    with st.expander("Download as..."):
        with st.form(key=f"_stx_export_form_{base_name}"):
            want_html = st.checkbox("HTML", value=True)
            want_pdf = False
            if pdf_available:
                want_pdf = st.checkbox("PDF", value=False)

                # --- PDF options (single column for narrow sidebar) ---
                _cur_w = st.session_state.get(_PAGE_WIDTH_KEY, 100)
                _cur_z = st.session_state.get(_ZOOM_KEY, 100)
                st.caption(f"Current view: Width {_cur_w}% · Zoom {_cur_z}%")
                st.markdown("**PDF options**")
                pdf_format = st.selectbox(
                    "Page format",
                    options=["A4", "A3", "Letter", "Legal", "Tabloid"],
                    index=["A4", "A3", "Letter", "Legal", "Tabloid"].index(defaults.format)
                    if defaults.format in ["A4", "A3", "Letter", "Legal", "Tabloid"] else 0,
                    key=f"_stx_pdf_format_{base_name}",
                )
                # Default to the current view mode (Paginated/Continuous radio)
                _view = st.session_state.get(_STX_VIEW_MODE_KEY, "Paginated")
                _mode_default = 0 if _view == "Paginated" else 1
                pdf_mode = st.selectbox(
                    "Slide breaks",
                    options=["Paginated", "Continuous"],
                    index=_mode_default,
                    key=f"_stx_pdf_mode_{base_name}",
                )
                pdf_landscape = st.checkbox("Landscape", value=defaults.landscape,
                                            key=f"_stx_pdf_land_{base_name}")
                pdf_background = st.checkbox("Print background", value=defaults.print_background,
                                             key=f"_stx_pdf_bg_{base_name}")
                pdf_page_numbers = st.checkbox("Page numbers", value=defaults.page_numbers,
                                               key=f"_stx_pdf_pn_{base_name}")
                # Default PDF scale to current Zoom % (if user hasn't set a custom scale)
                _zoom_pct = st.session_state.get(_ZOOM_KEY, 100)
                _scale_default = round(_zoom_pct / 100, 1)
                _scale_default = max(0.5, min(2.0, _scale_default))
                pdf_scale = st.slider("Scale", min_value=0.5, max_value=2.0,
                                      value=_scale_default, step=0.1,
                                      key=f"_stx_pdf_scale_{base_name}")
                st.markdown("**Margins**")
                m_top = st.text_input("Top", value=defaults.margin_top,
                                      key=f"_stx_pdf_mt_{base_name}")
                m_bottom = st.text_input("Bottom", value=defaults.margin_bottom,
                                         key=f"_stx_pdf_mb_{base_name}")
                m_left = st.text_input("Left", value=defaults.margin_left,
                                       key=f"_stx_pdf_ml_{base_name}")
                m_right = st.text_input("Right", value=defaults.margin_right,
                                        key=f"_stx_pdf_mr_{base_name}")
            else:
                st.caption("PDF requires `streamtex[pdf]`")

            submitted = st.form_submit_button("Generate")

        if submitted:
            results = {}
            if want_html:
                results["html"] = html
            if want_pdf and pdf_available:
                with st.spinner("Generating PDF..."):
                    cfg = PdfConfig(
                        mode=PdfMode.PAGINATED if pdf_mode == "Paginated" else PdfMode.CONTINUOUS,
                        format=pdf_format,
                        landscape=pdf_landscape,
                        margin_top=m_top,
                        margin_bottom=m_bottom,
                        margin_left=m_left,
                        margin_right=m_right,
                        print_background=pdf_background,
                        scale=pdf_scale,
                        page_numbers=pdf_page_numbers,
                        header_template=defaults.header_template,
                        footer_template=defaults.footer_template,
                        theme_bg=st.session_state.get(_STX_THEME_BG_KEY, "#fff"),
                        theme_text=st.session_state.get(_STX_THEME_TEXT_KEY, "#333"),
                    )
                    results["pdf"] = export_pdf(html, config=cfg)
            st.session_state[state_key] = results

        # Show download buttons from cached results
        results = st.session_state.get(state_key, {})
        if "html" in results:
            st.download_button(
                label="Download HTML",
                data=results["html"],
                file_name=f"{base_name}.html",
                mime="text/html",
                key=f"_stx_dl_html_{base_name}",
            )
        if "pdf" in results:
            st.download_button(
                label="Download PDF",
                data=results["pdf"],
                file_name=f"{base_name}.pdf",
                mime="application/pdf",
                key=f"_stx_dl_pdf_{base_name}",
            )


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


def st_book(module_list, toc_config: TOCConfig = None, marker_config: MarkerConfig = None, separator=None,
            export: bool = True, export_title: str = "StreamTeX Export",
            pdf_config: PdfConfig = None,
            paginate: bool = False,
            banner_color: str = "rgba(211, 47, 47, 0.8)",
            banner: BannerConfig = None,
            bib_sources=None, bib_config=None,
            inspector=None,
            page_width: int = 90,
            zoom: int = 100,
            *args, monties_color: str = None, **kwargs):
    """Generates a web page e-book from a list of block modules.

    :param separator: Optional module with a build() function, rendered between each block.
    :param export: If True, enables HTML export with a download button in the sidebar.
    :param export_title: Title used for the exported HTML document.
    :param pdf_config: Optional PdfConfig to customise PDF export (format, margins, scale, etc.).
    :param paginate: If True, renders one block at a time for faster widget interactions.
    :param banner_color: Background color for paginated navigation banners (CSS value).
    :param banner: Optional BannerConfig for full banner customisation (overrides banner_color).
    :param bib_sources: Optional list of paths to .bib, .json, .ris, or .csl-json files.
    :param bib_config: Optional BibConfig to configure bibliography formatting.
    :param inspector: Optional InspectorConfig to enable the block inspector panel.
    :param page_width: Page width as % of browser width (default 90).
    :param zoom: Default zoom level as % (default 100).
    """
    # --- Resolve banner configuration (3 levels) ---
    if banner is not None:
        banner_config = banner
    elif monties_color is not None:
        import warnings
        warnings.warn(
            "monties_color is deprecated, use banner= instead",
            DeprecationWarning,
            stacklevel=2,
        )
        banner_config = BannerConfig(color=monties_color)
    else:
        banner_config = BannerConfig(color=banner_color)
    # --- Password gate (env-driven, no-op locally) ---
    _password_gate()
    # --- Cache theme colors (once, early, in guaranteed Streamlit context) ---
    if _STX_THEME_BG_KEY not in st.session_state:
        st.session_state[_STX_THEME_BG_KEY] = st.get_option("theme.backgroundColor") or "#fff"
        st.session_state[_STX_THEME_TEXT_KEY] = st.get_option("theme.textColor") or "#333"
    # --- Bibliography setup ---
    _setup_bibliography(bib_sources, bib_config)
    # --- Settings expander (sidebar) ---
    if _STX_VIEW_MODE_KEY not in st.session_state:
        st.session_state[_STX_VIEW_MODE_KEY] = "Paginated" if paginate else "Continuous"

    with st.sidebar:
        _stx_settings = st.expander("Settings")
        with _stx_settings:
            _stx_settings.radio(
                "**View**",
                options=["Paginated", "Continuous"],
                horizontal=True,
                key=_STX_VIEW_MODE_KEY,
            )
            add_zoom_options(default_page_width=page_width, default_zoom=zoom,
                             container=_stx_settings)
            add_wrap_all_option(container=_stx_settings)
            _stx_settings.divider()
            add_slide_break_options(container=_stx_settings)

    if st.session_state[_STX_VIEW_MODE_KEY] == "Paginated":
        _paginated_book(module_list, toc_config, marker_config, separator,
                        export, export_title, banner_config, *args,
                        pdf_config=pdf_config, inspector=inspector,
                        page_width=page_width, zoom=zoom, **kwargs)
        return

    start_time = time.time()
    logger.debug("Starting st_book function...")

    # Load default CSS styles
    load_css("default.css")

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

    # Run the blocks (potentially populating the ToC registry)
    for i, module in enumerate(module_list):

        # Generate Toc at appropriate position
        if use_toc_block and i == toc_pos:
            toc_block = st_toc(toc_title_style)

        if collector is not None:
            collector.set_block(i)

        toc_before = len(toc_entries()) if use_toc_sidebar else 0
        markers_before = len(marker_entries()) if marker_config is not None else 0

        st_include(module, *args, _inspector_config=inspector, **kwargs)

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
            st_include(separator, *args, **kwargs)

        st_space("v", "70px")

    # Stop collector and get search index
    block_index = stop_collector() if use_search else None

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

    # Inject marker navigation JS (only if markers were registered)
    if marker_config is not None:
        inject_marker_navigation()

    # Offer export downloads when export is active
    if is_export_active():
        full_html = generate_export_html()
        if full_html:
            base_name = export_title.replace(' ', '_').lower()
            with st.sidebar:
                _offer_export_downloads(full_html, base_name, pdf_config=pdf_config)

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
            toc_sidebar = tab_toc.empty()
            markers_sidebar = tab_markers.empty()
            return toc_sidebar, markers_sidebar, search_js_placeholder
        else:
            st.header("Table of Contents")
            toc_sidebar = st.empty()
            return toc_sidebar, None, search_js_placeholder


def populate_toc(toc_sidebar: Delta, toc_block: Delta = None, toc_content_style: Style = None,
                 block_index: dict[int, str] = None, search_js_placeholder=None,
                 max_level: int | None = None, toc_config: TOCConfig | None = None):
    toc_entry_list = toc_entries()
    marker_anchors = {m['anchor'] for m in marker_entries()}
    indent_char = "&nbsp;"

    with toc_sidebar.container():
        if block_index is not None:
            # Search-enabled: single st.markdown block (entries with data-stx-block)
            toc_parts = []
            for entry in toc_entry_list:
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
                    f'<div{block_attr} style="overflow:hidden;text-overflow:ellipsis;'
                    f'white-space:nowrap;padding:1px 0;font-size:14px;">'
                    f'{indent}{dot}<a href="#{entry["key_anchor"]}">'
                    f'{entry["title"]}</a></div>'
                )
            toc_parts.append('<div style="height:40px;"></div>')
            st.markdown("\n".join(toc_parts), unsafe_allow_html=True)
        else:
            for entry in toc_entry_list:
                if max_level is not None and entry['level'] > max_level:
                    continue
                indent = indent_char * (entry['level'] - 1) * 4
                dot = (
                    '<span style="opacity:.5;font-size:6px;vertical-align:middle;'
                    'margin-right:4px;">&#9679;</span>'
                    if entry['key_anchor'] in marker_anchors else ''
                )
                st.html(
                    f'<span style="overflow:hidden;text-overflow:ellipsis;'
                    f'text-wrap:nowrap;word-wrap:normal;">'
                    f'{indent}{dot}<a href="#{entry["key_anchor"]}">'
                    f'{entry["title"]}</a></span>'
                )

    # Inject search JS into the dedicated placeholder (above tabs)
    if search_js_placeholder is not None and block_index is not None:
        with search_js_placeholder.container():
            components.html(generate_search_script(block_index), height=0)

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
    entries = [e for e in marker_entries() if not e.get("hidden")]
    if not entries:
        return
    with markers_placeholder.container():
        if block_index is not None:
            # Search-enabled: single st.markdown block with data-stx-block attributes
            parts = []
            for i, entry in enumerate(entries):
                block_attr = f' data-stx-block="{entry.get("block_idx", 0)}"'
                parts.append(
                    f'<div{block_attr} style="overflow:hidden;text-overflow:ellipsis;'
                    f'white-space:nowrap;padding:1px 0;font-size:14px;">'
                    f'<a href="#{entry["anchor"]}">{i + 1}. {entry["label"]}</a></div>'
                )
            parts.append('<div style="height:40px;"></div>')
            st.markdown("\n".join(parts), unsafe_allow_html=True)
        else:
            for i, entry in enumerate(entries):
                st.html(
                    f'<span style="overflow:hidden;text-overflow:ellipsis;text-wrap:nowrap;word-wrap:normal;">'
                    f'<a href="#{entry["anchor"]}">{i + 1}. {entry["label"]}</a></span>'
                )


def st_toc(toc_title_style):
    st_write(toc_title_style, "Table of Contents", tag=Tags.div, toc_lvl='1')
    st_space("v", 4)
    toc_block = st.empty()
    st_space("v", "70px")
    return toc_block


def st_include(block_file_module, *args, _inspector_config=None, **kwargs):
    if not block_file_module:
        st.markdown(":red-background[Block module is None — not found]")
        return

    mod_path = getattr(block_file_module, '__file__', None) or getattr(block_file_module, '__name__', '?')
    if not hasattr(block_file_module, 'build'):
        st.markdown(f":red-background[The file {mod_path} does not contain a build() function.]")
        return

    module_name = getattr(block_file_module, '__name__', str(block_file_module))

    # Inspector edit button (opt-in)
    # Uses st.html() directly (not _render()), so never appears in exported HTML.
    if _inspector_config and _inspector_config.enabled:
        from .inspector import render_edit_button
        short_name = module_name.rsplit('.', 1)[-1]
        render_edit_button(short_name, _inspector_config)

    try:
        block_file_module.build(*args, **kwargs)
    except Exception as e:
        st.markdown(f":red-background[Error in block '{module_name}': {e}]")
        raise


# ---------------------------------------------------------------------------
# Paginated mode
# ---------------------------------------------------------------------------

_STX_CACHE_KEY = "_stx_page_cache"
_STX_PAGE_KEY = "_stx_current_page"
_STX_VIEW_MODE_KEY = "_stx_view_mode"
_STX_THEME_BG_KEY = "_stx_theme_bg"
_STX_THEME_TEXT_KEY = "_stx_theme_text"


def _compute_cache_hash(module_list):
    """Return a hash that changes when the module list changes."""
    names = "|".join(getattr(m, '__name__', str(m)) for m in module_list)
    return hashlib.md5(names.encode()).hexdigest()


def _get_page_titles(cache, total):
    """Extract the first TOC title for each page (fallback to 'Section N')."""
    titles = [f"Section {i + 1}" for i in range(total)]
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


def _build_page_cache(module_list, toc_config, marker_config, separator,
                      cache_hash, *args, **kwargs):
    """Execute all blocks inside st.empty() to collect TOC/markers, then cache."""
    reset_toc_registry(toc_config)
    if marker_config is not None:
        reset_marker_registry(marker_config)

    use_search = toc_config is not None and toc_config.search
    collector = start_collector() if use_search else None

    hidden = st.empty()
    with hidden.container():
        for i, module in enumerate(module_list):
            toc_before = len(toc_entries()) if toc_config else 0
            markers_before = len(marker_entries()) if marker_config else 0

            if collector is not None:
                collector.set_block(i)

            st_include(module, *args, **kwargs)

            # Tag new TOC entries with their page index
            if toc_config:
                for entry in toc_entries()[toc_before:]:
                    if "page_idx" not in entry:
                        entry["page_idx"] = i
            # Tag new marker entries with their page index
            if marker_config:
                for entry in marker_entries()[markers_before:]:
                    if "page_idx" not in entry:
                        entry["page_idx"] = i

            if separator and i < len(module_list) - 1:
                st_include(separator, *args, **kwargs)

    hidden.empty()

    search_index = stop_collector() if use_search else None

    st.session_state[_STX_CACHE_KEY] = {
        "hash": cache_hash,
        "toc": copy.deepcopy(toc_entries()) if toc_config else [],
        "markers": copy.deepcopy(marker_entries()) if marker_config else [],
        "total": len(module_list),
        "search_index": search_index,
    }


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

        has_markers = marker_config is not None and cache.get("markers")

        if has_markers:
            tab_markers, tab_toc = st.tabs(["Markers", "Contents"])
        else:
            tab_toc = st.container()
            tab_markers = None

        # --- TOC ---
        cached_toc = cache.get("toc", [])
        marker_anchors = {m["anchor"] for m in cache.get("markers", [])}
        indent_char = "&nbsp;"
        effective_max_level = _resolve_sidebar_max_level(toc_config, paginated=True)

        toc_parts = []

        for entry in cached_toc:
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
                link = (
                    f'<a href="#{entry["key_anchor"]}" '
                    f'style="color:var(--stx-link-active-color);">{title_esc}</a>'
                )
            else:
                link = (
                    f'<a href="#stx-goto-{page_idx}" class="stx-page-link">'
                    f'{title_esc}</a>'
                )
            block_attr = f' data-stx-block="{page_idx}"' if show_search else ''
            toc_parts.append(
                f'<div{block_attr} style="overflow:hidden;text-overflow:ellipsis;'
                f'white-space:nowrap;padding:1px 0;font-size:14px;">'
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
                idx = entry["index"] + 1
                page_idx = entry.get("page_idx", 0)
                if page_idx == current_page:
                    link = (
                        f'<a href="#{entry["anchor"]}" '
                        f'style="color:var(--stx-link-active-color);">{idx}. {entry["label"]}</a>'
                    )
                else:
                    link = (
                        f'<a href="#stx-goto-{page_idx}" class="stx-page-link">'
                        f'{idx}. {entry["label"]}</a>'
                    )
                block_attr = f' data-stx-block="{page_idx}"' if show_search else ''
                marker_parts.append(
                    f'<div{block_attr} style="overflow:hidden;text-overflow:ellipsis;'
                    f'white-space:nowrap;font-size:14px;">{link}</div>'
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
                components.html(generate_search_script(search_index), height=0)


def _inject_paginated_nav_js(current_page, total, marker_config,
                             page_marker_info=None):
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
    var pageFirstMarker = __PAGE_FIRST_MARKER__;
    var pageLastMarker  = __PAGE_LAST_MARKER__;

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
        if (navigating) return;
        if (targetPage < 0 || targetPage >= totalPages
            || targetPage === currentPage) return;
        navigating = true;          /* block further signals */
        hostWin._stxScrollReset = true;
        findNavButtons();
        var btn = navButtons[targetPage];
        if (btn) btn.click();
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

    /* --- Deferred element lookup (DOM may not be ready on cold start) --- */
    function prevClick() {
        if (navigating || currentPage <= 0) return;
        var pp = currentPage - 1;
        hostWin._stxMarkerStartIdx =
            pageFirstMarker[pp] !== undefined ? pageFirstMarker[pp] : 0;
        navigateToPage(pp);
    }
    function nextClick() {
        if (navigating || currentPage >= totalPages - 1) return;
        var np = currentPage + 1;
        hostWin._stxMarkerStartIdx =
            pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : 0;
        navigateToPage(np);
    }

    function findElements() {
        /* Sentinel — attach IntersectionObserver on first find */
        if (!sentinel && currentPage < totalPages - 1) {
            sentinel = hostDoc.getElementById('stx-banner-sentinel');
            if (sentinel && !bannerObs) {
                bannerObs = new hostWin.IntersectionObserver(function(entries) {
                    bannerNextActive = entries[0].isIntersecting;
                    if (!bannerNextActive) {
                        clearTimeout(bannerNextTimer); bannerNextTimer = null;
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
            if (!bannerNextTimer) {
                bannerNextTimer = setTimeout(function() {
                    if (!bannerNextActive || navigating) return;
                    var np = currentPage + 1;
                    hostWin._stxMarkerStartIdx =
                        pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : 0;
                    navigateToPage(np);
                }, 400);
            }
            return;
        }

        /* Top: scroll up while at top of page → prev page */
        if (e.deltaY < 0 && bannerPrevReady
                && currentPage > 0 && isAtTop()) {
            clearTimeout(bannerNextTimer); bannerNextTimer = null;
            if (!bannerPrevTimer) {
                bannerPrevTimer = setTimeout(function() {
                    if (navigating || !isAtTop()) return;
                    var pp = currentPage - 1;
                    hostWin._stxMarkerStartIdx =
                        pageFirstMarker[pp] !== undefined ? pageFirstMarker[pp] : 0;
                    navigateToPage(pp);
                }, 400);
            }
            return;
        }

        /* Not at a boundary: cancel timers */
        clearTimeout(bannerNextTimer); bannerNextTimer = null;
        clearTimeout(bannerPrevTimer); bannerPrevTimer = null;
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
        if (direction === 'next' && currentPage < totalPages - 1) {
            var np = currentPage + 1;
            hostWin._stxMarkerStartIdx =
                pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : 0;
            navigateToPage(np);
        } else if (direction === 'prev' && currentPage > 0) {
            var pp = currentPage - 1;
            hostWin._stxMarkerStartIdx =
                pageLastMarker[pp] !== undefined ? pageLastMarker[pp] : -1;
            navigateToPage(pp);
        }
    };

    /* --- Ensure marker start index matches current page ---
       Covers cases where no explicit navigation handler set it
       (e.g. sidebar link click, initial page load, browser refresh).
       Runs synchronously BEFORE marker.py's 500ms init reads it. */
    if (!hostWin._stxMarkerStartIdx) {
        var fm = pageFirstMarker[currentPage];
        if (fm !== undefined) hostWin._stxMarkerStartIdx = fm;
    }

    /* --- Sidebar link interception (st.markdown = direct DOM) --- */
    function linkClick(e) {
        var a = e.target.closest('a[href^="#stx-goto-"]');
        if (!a) return;
        e.preventDefault();
        e.stopPropagation();
        var href = a.getAttribute('href') || '';
        var match = href.match(/^#stx-goto-(\\d+)/);
        if (!match) return;
        var p = parseInt(match[1], 10);
        if (isNaN(p) || p === currentPage) return;
        /* Set marker start index for the target page so the
           floating marker widget initialises on the right marker */
        hostWin._stxMarkerStartIdx =
            pageFirstMarker[p] !== undefined ? pageFirstMarker[p] : 0;
        navigateToPage(p);
    }
    hostDoc.addEventListener('click', linkClick, true);

    /* --- Cleanup --- */
    hostWin._stxPaginatedCleanup = function() {
        if (bannerObs) bannerObs.disconnect();
        hostDoc.removeEventListener('wheel', bannerWheel);
        clearTimeout(bannerNextTimer);
        clearTimeout(bannerPrevTimer);
        clearTimeout(bannerReadyTimer);
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
    js_body = (js_body
               .replace("__CURRENT_PAGE__", str(current_page))
               .replace("__TOTAL_PAGES__", str(total))
               .replace("__PAGE_FIRST_MARKER__", pmi_first)
               .replace("__PAGE_LAST_MARKER__", pmi_last))
    components.html(js_body, height=0)


def _paginated_book(module_list, toc_config, marker_config, separator,
                    export, export_title, banner_config: BannerConfig, *args,
                    pdf_config=None, inspector=None, page_width=100, zoom=100,
                    **kwargs):
    """Paginated rendering — only renders one block per rerun."""
    start_time = time.time()
    logger.debug("Starting st_book (paginated)...")

    total = len(module_list)
    if total == 0:
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

    # --- Cache management ---
    cache_hash = _compute_cache_hash(module_list)
    cache = st.session_state.get(_STX_CACHE_KEY)
    has_valid_cache = (
        cache is not None
        and cache.get("hash") == cache_hash
        and cache.get("total") == total
    )
    # Invalidate cache if search was enabled but cache lacks search_index
    if has_valid_cache and toc_config and toc_config.search:
        if cache.get("search_index") is None:
            has_valid_cache = False

    if not has_valid_cache:
        reset_export_buffer(ExportConfig(enabled=False))
        _build_page_cache(module_list, toc_config, marker_config,
                          separator, cache_hash, *args, **kwargs)
        cache = st.session_state[_STX_CACHE_KEY]

    # --- Current page ---
    if _STX_PAGE_KEY not in st.session_state:
        st.session_state[_STX_PAGE_KEY] = 0
    current_page = max(0, min(st.session_state[_STX_PAGE_KEY], total - 1))
    st.session_state[_STX_PAGE_KEY] = current_page

    # --- Sidebar (from cache) ---
    _build_paginated_sidebar(cache, current_page, total, toc_config, marker_config)

    # --- Search index refresh (current page only) ---
    _refresh_search = st.session_state.pop(_STX_REFRESH_SEARCH_KEY, False)
    if _refresh_search:
        _refresh_collector = start_collector()
        _refresh_collector.set_block(current_page)

    # --- Prepare registries for current page ---
    effective_pw = f"{st.session_state.get(_PAGE_WIDTH_KEY, page_width)}%"
    effective_zoom = st.session_state.get(_ZOOM_KEY, zoom) / 100
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
                registry._entries.append({
                    "index": entry["index"],
                    "label": entry["label"],
                    "anchor": entry["anchor"],
                    "page": entry.get("page_idx", 0),
                })

    # --- Banner — page titles for navigation labels ---
    page_titles = _get_page_titles(cache, total)

    # Banner — top (previous section, clickable via JS)
    if current_page > 0 and banner_config.mode != BannerMode.HIDDEN:
        _prev = page_titles[current_page - 1]
        _render_banner("stx-banner-prev", _prev, "◂", banner_config)
        css = banner_config._resolve()
        if css and css["show_dividers"]:
            st.divider()

    # --- Render current block ---
    st_include(module_list[current_page], *args, _inspector_config=inspector, **kwargs)

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
                components.html(
                    generate_search_script(cache["search_index"]), height=0)

    # Banner — bottom (next section, clickable via JS)
    if current_page < total - 1:
        _next = page_titles[current_page + 1]
        if banner_config.mode != BannerMode.HIDDEN:
            css = banner_config._resolve()
            if css and css["show_dividers"]:
                st.divider()
            _render_banner("stx-banner-next", _next, "▸", banner_config)
        # Buffer zone before auto-trigger sentinel
        # Shorter on narrow viewports (mobile) so users don't scroll forever
        st.markdown(
            '<div class="stx-banner-buffer"></div>'
            "<style>"
            ".stx-banner-buffer{padding-top:800px}"
            "@media(max-width:800px){.stx-banner-buffer{padding-top:400px}}"
            "</style>",
            unsafe_allow_html=True,
        )
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
                registry._entries.append({
                    "index": entry["index"],
                    "label": entry["label"],
                    "anchor": entry["anchor"],
                    "page": entry.get("page_idx", 0),
                })

    # --- Marker navigation widget (ALL markers, cross-page aware) ---
    if marker_config is not None:
        inject_marker_navigation()

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
            pg = entry.get("page_idx", 0)
            if pg not in page_first:
                page_first[pg] = entry["index"]
            page_last[pg] = entry["index"]
        page_marker_info = {"first": page_first, "last": page_last}

    # --- Paginated navigation JS (finds & hides buttons, overscroll, callbacks) ---
    _inject_paginated_nav_js(current_page, total, marker_config, page_marker_info)

    # --- Export downloads ---
    if is_export_active():
        full_html = generate_export_html()
        if full_html:
            base_name = export_title.replace(' ', '_').lower()
            with st.sidebar:
                _offer_export_downloads(full_html, base_name, pdf_config=pdf_config)

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
