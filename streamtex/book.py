import streamlit as st
from streamlit.delta_generator import DeltaGenerator as Delta
import streamlit.components.v1 as components
import copy
import hashlib
import json
import time
import os
import importlib.resources as resources

from .styles import Style
from .write import st_write
from .space import st_space, st_br
from . import toc as _toc_mod
from .toc import reset_toc_registry, toc_entries, TOCConfig
from .marker import reset_marker_registry, inject_marker_navigation, MarkerConfig, marker_entries
from .enums import Tags
from .utils import inject_link_preview_scaffold
from .zoom import add_zoom_options
from .export import ExportConfig, reset_export_buffer, generate_export_html, is_export_active
from .search import start_collector, stop_collector, generate_search_input_html, generate_search_script

import logging
logger = logging.getLogger(__name__)


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
    from .bib import reset_bib_registry, set_bib_config, get_bib_registry, load_bib

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
            paginate: bool = False,
            monties_color: str = "rgba(211, 47, 47, 0.8)",
            bib_sources=None, bib_config=None,
            *args, **kwargs):
    """Generates a web page e-book from a list of block modules.

    :param separator: Optional module with a build() function, rendered between each block.
    :param export: If True, enables HTML export with a download button in the sidebar.
    :param export_title: Title used for the exported HTML document.
    :param paginate: If True, renders one block at a time for faster widget interactions.
    :param monties_color: Background color for paginated navigation banners (CSS value).
    :param bib_sources: Optional list of paths to .bib, .json, .ris, or .csl-json files.
    :param bib_config: Optional BibConfig to configure bibliography formatting.
    """
    # --- Bibliography setup ---
    _setup_bibliography(bib_sources, bib_config)
    # --- View mode toggle (sidebar) ---
    if _STX_VIEW_MODE_KEY not in st.session_state:
        st.session_state[_STX_VIEW_MODE_KEY] = "Paginated" if paginate else "Continuous"

    with st.sidebar:
        st.radio(
            "**View**",
            options=["Paginated", "Continuous"],
            horizontal=True,
            key=_STX_VIEW_MODE_KEY,
        )

    if st.session_state[_STX_VIEW_MODE_KEY] == "Paginated":
        _paginated_book(module_list, toc_config, marker_config, separator,
                        export, export_title, monties_color, *args, **kwargs)
        return

    start_time = time.time()
    logger.debug("Starting st_book function...")

    # Initialise the export buffer (no-op if export=False)
    reset_export_buffer(ExportConfig(enabled=export, page_title=export_title))

    # Load default CSS styles
    load_css("default.css")

    # Ensure the hover card is ready before any content is rendered.
    inject_link_preview_scaffold()

    # Inject bibliography hover preview if enabled
    _inject_bib_preview_if_enabled()

    # Add zoom options to sidebar
    add_zoom_options()

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

        st_include(module, *args, **kwargs)

        # Tag new TOC entries with their block index
        if use_toc_sidebar:
            for entry in toc_entries()[toc_before:]:
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
                     max_level=effective_max_level)
        if markers_sidebar is not None:
            populate_markers_sidebar(markers_sidebar)

    # Inject marker navigation JS (only if markers were registered)
    if marker_config is not None:
        inject_marker_navigation()

    # Offer HTML download when export is active
    if is_export_active():
        full_html = generate_export_html()
        if full_html:
            file_name = f"{export_title.replace(' ', '_').lower()}.html"
            with st.sidebar:
                st.download_button(
                    label="\U0001F4E5 Download HTML",
                    data=full_html,
                    file_name=file_name,
                    mime="text/html",
                )

    end_time = time.time()
    duration = end_time - start_time
    logger.debug("st_book function completed in %.2f seconds.", duration)


def load_css(file_name: str):
    """Loads a CSS file and injects it into the StreamTeX app."""
    try:
        with resources.open_text('streamtex.static', file_name) as f:
            st.html(f'<style>{f.read()}</style>')
    except (FileNotFoundError, ModuleNotFoundError, TypeError) as e:
        logger.debug("[StreamTeX] CSS resource fallback for '%s': %s", file_name, e)
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, 'static')
        css_file_path = os.path.join(static_dir, file_name)
        # Read the CSS file
        with open(css_file_path, 'r') as f:
            st.html(f'<style>{f.read()}</style>')


def build_ToC_sidebar_placeholder(has_markers=False, has_search=False):
    with st.sidebar:
        # Search input above tabs (always visible regardless of active tab)
        if has_search:
            st.markdown(generate_search_input_html(), unsafe_allow_html=True)
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
                 max_level: int | None = None):
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
            for entry in toc_entry_list:
                indent = indent_char * (entry['level'] - 1) * 2
                st_write(toc_content_style, f"{indent}{entry['title']}",
                                link=f"#{entry['key_anchor']}", hover=False, no_link_decor=True)
                st_br()


def populate_markers_sidebar(markers_placeholder: Delta):
    entries = marker_entries()
    if not entries:
        return
    with markers_placeholder.container():
        for entry in entries:
            idx = entry['index'] + 1
            st.html(
                f'<span style="overflow:hidden;text-overflow:ellipsis;text-wrap:nowrap;word-wrap:normal;">'
                f'<a href="#{entry["anchor"]}">{idx}. {entry["label"]}</a></span>'
            )


def st_toc(toc_title_style):
    st_write(toc_title_style, "Table of Contents", tag=Tags.div, toc_lvl='1')
    st_space("v", 4)
    toc_block = st.empty()
    st_space("v", "70px")
    return toc_block


def st_include(block_file_module, *args, **kwargs):
    if not block_file_module:
        st.markdown(f":red-background[File {block_file_module.__path__} not found]")
        return

    if not hasattr(block_file_module, 'build'):
        st.markdown(f":red-background[The file {block_file_module.__path__} does not contain a build() function.]")
        return

    module_name = getattr(block_file_module, '__name__', str(block_file_module))
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


def _build_paginated_sidebar(cache, current_page, total, toc_config, marker_config):
    """Populate the sidebar from cached data (st.markdown for direct DOM access)."""
    search_index = cache.get("search_index")
    show_search = toc_config is not None and toc_config.search

    with st.sidebar:
        # Search input above tabs (always visible regardless of active tab)
        if show_search:
            st.markdown(generate_search_input_html(), unsafe_allow_html=True)

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
                link = f'<a href="#{entry["key_anchor"]}">{title_esc}</a>'
            else:
                link = (
                    f'<a href="#stx-goto-{page_idx}" class="stx-page-link" '
                    f'style="opacity:.6;">{title_esc}</a>'
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
                    link = f'<a href="#{entry["anchor"]}">{idx}. {entry["label"]}</a>'
                else:
                    link = (
                        f'<a href="#stx-goto-{page_idx}" class="stx-page-link" '
                        f'style="opacity:.6;">{idx}. {entry["label"]}</a>'
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

        # Search JS (above tabs level, invisible iframe)
        if search_index:
            components.html(generate_search_script(search_index), height=0)


def _inject_paginated_nav_js(current_page, total, marker_config,
                             page_marker_info=None):
    """Inject JS for cross-page navigation via hidden buttons.

    Navigation mechanisms:
    - Monties: IntersectionObserver on sentinel auto-triggers next page on wheel
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
       + page-change detection (_stxPrevPage) which covers Monties button
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
     * MONTIES — banner clicks + auto-trigger zones
     *
     * Bottom: IntersectionObserver on sentinel + wheel deltaY > 0
     * Top:    isAtTop() + wheel deltaY < 0  (800ms startup delay)
     * Banners: click on red banners → navigateToPage
     * ================================================================= */
    var sentinel = null;
    var prevBanner = null;
    var nextBanner = null;
    var montiesNextActive = false;
    var montiesNextTimer = null;
    var montiesPrevTimer = null;
    var montiesObs = null;
    var montiesPrevReady = false;

    function isAtTop() { return scrollEl.scrollTop < 15; }

    /* Delay top auto-trigger to avoid residual momentum after scroll reset */
    var montiesReadyTimer = setTimeout(function() {
        montiesPrevReady = true;
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
            sentinel = hostDoc.getElementById('stx-monties-sentinel');
            if (sentinel && !montiesObs) {
                montiesObs = new hostWin.IntersectionObserver(function(entries) {
                    montiesNextActive = entries[0].isIntersecting;
                    if (!montiesNextActive) {
                        clearTimeout(montiesNextTimer); montiesNextTimer = null;
                    }
                }, { threshold: 0.1 });
                montiesObs.observe(sentinel);
            }
        }
        /* Banners — attach click handlers on first find */
        if (!prevBanner) {
            prevBanner = hostDoc.getElementById('stx-monties-prev');
            if (prevBanner) prevBanner.addEventListener('click', prevClick);
        }
        if (!nextBanner) {
            nextBanner = hostDoc.getElementById('stx-monties-next');
            if (nextBanner) nextBanner.addEventListener('click', nextClick);
        }
    }
    findElements();
    setTimeout(findElements, 300);
    setTimeout(findElements, 1000);

    function montiesWheel(e) {
        if (navigating) return;

        /* Bottom: scroll down while sentinel visible → next page */
        if (e.deltaY > 0 && montiesNextActive) {
            clearTimeout(montiesPrevTimer); montiesPrevTimer = null;
            if (!montiesNextTimer) {
                montiesNextTimer = setTimeout(function() {
                    if (!montiesNextActive || navigating) return;
                    var np = currentPage + 1;
                    hostWin._stxMarkerStartIdx =
                        pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : 0;
                    navigateToPage(np);
                }, 400);
            }
            return;
        }

        /* Top: scroll up while at top of page → prev page */
        if (e.deltaY < 0 && montiesPrevReady
                && currentPage > 0 && isAtTop()) {
            clearTimeout(montiesNextTimer); montiesNextTimer = null;
            if (!montiesPrevTimer) {
                montiesPrevTimer = setTimeout(function() {
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
        clearTimeout(montiesNextTimer); montiesNextTimer = null;
        clearTimeout(montiesPrevTimer); montiesPrevTimer = null;
    }

    /* Wheel listener — handles both top and bottom auto-trigger */
    hostDoc.addEventListener('wheel', montiesWheel, { passive: true });

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
        if (montiesObs) montiesObs.disconnect();
        hostDoc.removeEventListener('wheel', montiesWheel);
        clearTimeout(montiesNextTimer);
        clearTimeout(montiesPrevTimer);
        clearTimeout(montiesReadyTimer);
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
                    export, export_title, monties_color, *args, **kwargs):
    """Paginated rendering — only renders one block per rerun."""
    start_time = time.time()
    logger.debug("Starting st_book (paginated)...")

    total = len(module_list)
    if total == 0:
        return

    # --- Common setup ---
    load_css("default.css")
    inject_link_preview_scaffold()
    _inject_bib_preview_if_enabled()
    add_zoom_options()

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

    # --- Prepare registries for current page ---
    reset_export_buffer(ExportConfig(enabled=export, page_title=export_title))
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

    # --- Monties — page titles for navigation labels ---
    page_titles = _get_page_titles(cache, total)

    # Monties — top banner (previous section, clickable via JS)
    if current_page > 0:
        _prev = page_titles[current_page - 1]
        st.markdown(
            f'<div id="stx-monties-prev" style="background:{monties_color};color:white;'
            f'font-weight:bold;font-size:1.3rem;padding:18px 24px;text-align:center;'
            f'cursor:pointer;border-radius:8px;user-select:none;">'
            f'◂&ensp;{_prev}</div>',
            unsafe_allow_html=True,
        )
        st.divider()

    # --- Render current block ---
    st_include(module_list[current_page], *args, **kwargs)

    # Monties — bottom banner (next section, clickable via JS)
    if current_page < total - 1:
        _next = page_titles[current_page + 1]
        st.divider()
        st.markdown(
            f'<div id="stx-monties-next" style="background:{monties_color};color:white;'
            f'font-weight:bold;font-size:1.3rem;padding:18px 24px;text-align:center;'
            f'cursor:pointer;border-radius:8px;user-select:none;">'
            f'{_next}&ensp;▸</div>',
            unsafe_allow_html=True,
        )
        # Buffer zone before auto-trigger sentinel (800px)
        st_space("v", "800px")
        # Sentinel watched by IntersectionObserver in paginated nav JS
        st.markdown(
            '<div id="stx-monties-sentinel" style="height:1px;"></div>',
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

    # --- Export download button ---
    if is_export_active():
        full_html = generate_export_html()
        if full_html:
            file_name = f"{export_title.replace(' ', '_').lower()}.html"
            with st.sidebar:
                st.download_button(
                    label="\U0001F4E5 Download HTML",
                    data=full_html,
                    file_name=file_name,
                    mime="text/html",
                )

    end_time = time.time()
    logger.debug("st_book (paginated) completed in %.2fs [page %d/%d]",
                 end_time - start_time, current_page + 1, total)
