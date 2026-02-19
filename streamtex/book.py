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


def st_book(module_list, toc_config: TOCConfig = None, marker_config: MarkerConfig = None, separator=None,
            export: bool = True, export_title: str = "StreamTeX Export",
            paginate: bool = False,
            *args, **kwargs):
    """Generates a web page e-book from a list of block modules.

    :param separator: Optional module with a build() function, rendered between each block.
    :param export: If True, enables HTML export with a download button in the sidebar.
    :param export_title: Title used for the exported HTML document.
    :param paginate: If True, renders one block at a time for faster widget interactions.
    """
    if paginate:
        _paginated_book(module_list, toc_config, marker_config, separator,
                        export, export_title, *args, **kwargs)
        return

    start_time = time.time()
    print("Starting st_book function...")

    # Initialise the export buffer (no-op if export=False)
    reset_export_buffer(ExportConfig(enabled=export, page_title=export_title))

    # Load default CSS styles
    load_css("default.css")

    # Ensure the hover card is ready before any content is rendered.
    inject_link_preview_scaffold()

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
        toc_sidebar, markers_sidebar = build_ToC_sidebar_placeholder(
            has_markers=marker_config is not None
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

    # Run the blocks (potentially populating the ToC registry)
    for i, module in enumerate(module_list):

        # Generate Toc at appropriate position
        if use_toc_block and i == toc_pos:
            toc_block = st_toc(toc_title_style)

        st_include(module, *args, **kwargs)

        # Separator between blocks (not after the last one)
        if separator and i < len(module_list) - 1:
            st_include(separator, *args, **kwargs)

        st_space("v", "70px")

    # Generate Toc at appropriate position
    if use_toc_block and toc_pos == len(module_list):
        toc_block = st_toc(toc_title_style)

    # Fill the ToC placeholder
    if use_toc_sidebar:
        populate_toc(toc_sidebar, toc_block, toc_content_style)
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
    print(f"st_book function completed in {duration:.2f} seconds.")


def load_css(file_name: str):
    """Loads a CSS file and injects it into the StreamTeX app."""
    try:
        with resources.open_text('streamtex.static', file_name) as f:
            st.html(f'<style>{f.read()}</style>')
    except (FileNotFoundError, ModuleNotFoundError, TypeError) as e:
        print(f"[StreamTeX] CSS resource fallback for '{file_name}': {e}")
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, 'static')
        css_file_path = os.path.join(static_dir, file_name)
        # Read the CSS file
        with open(css_file_path, 'r') as f:
            st.html(f'<style>{f.read()}</style>')


def build_ToC_sidebar_placeholder(has_markers=False):
    with st.sidebar:
        if has_markers:
            tab_markers, tab_toc = st.tabs(["Markers", "Contents"])
            toc_sidebar = tab_toc.empty()
            markers_sidebar = tab_markers.empty()
            return toc_sidebar, markers_sidebar
        else:
            st.header("Table of Contents")
            toc_sidebar = st.empty()
            return toc_sidebar, None


def populate_toc(toc_sidebar: Delta, toc_block: Delta = None, toc_content_style: Style = None):
    toc_entry_list = toc_entries()
    marker_anchors = {m['anchor'] for m in marker_entries()}
    indent_char = "&nbsp;"

    with toc_sidebar.container():
        for entry in toc_entry_list:
            # Indentation based on level
            indent = indent_char * (entry['level'] - 1) * 4

            # Marker indicator dot for TOC entries that are also navigation markers
            dot = ('<span style="opacity:.5;font-size:6px;vertical-align:middle;'
                   'margin-right:4px;">&#9679;</span>'
                   if entry['key_anchor'] in marker_anchors else '')

            # Native Streamlit Link to ID
            st.html(
                f"<span style=\"overflow: hidden; text-overflow: ellipsis; text-wrap: nowrap; word-wrap: normal;\">"
                f"{indent}{dot}<a href=\"#{entry['key_anchor']}\">{entry['title']}</a></span>"
            )
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

    hidden = st.empty()
    with hidden.container():
        for i, module in enumerate(module_list):
            toc_before = len(toc_entries()) if toc_config else 0
            markers_before = len(marker_entries()) if marker_config else 0

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

    st.session_state[_STX_CACHE_KEY] = {
        "hash": cache_hash,
        "toc": copy.deepcopy(toc_entries()) if toc_config else [],
        "markers": copy.deepcopy(marker_entries()) if marker_config else [],
        "total": len(module_list),
    }


def _build_paginated_sidebar(cache, current_page, total, toc_config, marker_config):
    """Populate the sidebar from cached data (st.markdown for direct DOM access)."""
    with st.sidebar:
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

        toc_parts = []
        for entry in cached_toc:
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
            toc_parts.append(
                f'<div style="overflow:hidden;text-overflow:ellipsis;'
                f'white-space:nowrap;padding:1px 0;font-size:14px;">'
                f'{indent}{dot}{link}</div>'
            )

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
                marker_parts.append(
                    f'<div style="overflow:hidden;text-overflow:ellipsis;'
                    f'white-space:nowrap;font-size:14px;">{link}</div>'
                )
            with tab_markers:
                if marker_parts:
                    st.markdown("\n".join(marker_parts), unsafe_allow_html=True)


def _inject_paginated_nav_js(current_page, total, marker_config,
                             page_marker_info=None):
    """Inject JS for cross-page navigation via hidden buttons.

    Navigation mechanisms:
    - Overscroll: scrolling past bottom/top triggers prev/next page
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
        reenablePE();               /* restore iframe interactions */
        findNavButtons();
        var btn = navButtons[targetPage];
        if (btn) btn.click();
    }

    /* =================================================================
     * OVERSCROLL DETECTION  (scroll → pause → re-scroll → navigate)
     *
     * Three independent event sources feed one shared state machine:
     *  1. wheel events on hostDoc          (cursor over non-iframe areas)
     *  2. wheel events on iframe docs      (cursor over st.html content)
     *  3. scroll events on the container   (elastic bounce on macOS)
     *
     * State machine:
     *  idle     → boundary signal         → phase1
     *  phase1   → signals keep coming     → stay  (restart gap timer)
     *  phase1   → GAP_MS silence          → waiting
     *  waiting  → boundary signal         → TRIGGER → cooldown
     *  waiting  → WAIT_MS expires         → idle
     *  cooldown → ignore COOLDOWN_MS      → idle
     * ================================================================= */

    /* -- Find the real scroll container --
       Use .stMain directly — it is Streamlit's designated scroll
       container (<section> with overflow:auto).  Walking up from
       content risks landing on an intermediate wrapper that has
       overflow:auto but doesn't actually scroll (e.g. when the
       sidebar is collapsed and the content is shorter).             */
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
       Multiple delayed attempts override browser / Streamlit scroll
       restoration which can fire asynchronously after our initial reset.
       We target scrollEl, .stMain, and the window to cover all cases. */
    if (hostWin._stxScrollReset) {
        hostWin._stxScrollReset = false;
        function doScrollReset() {
            scrollEl.scrollTop = 0;
            /* Also target well-known Streamlit containers directly */
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

    var overState = 'idle';
    var overDir = null;
    var gapTimer = null;
    var waitTimer = null;
    var GAP_MS = 500;
    var WAIT_MS = 3000;
    var COOLDOWN_MS = 2000;

    function isAtBot() {
        return scrollEl.scrollHeight - scrollEl.scrollTop
               - scrollEl.clientHeight < 15;
    }
    function isAtTop() { return scrollEl.scrollTop < 15; }

    /* -- Pointer-events management for overscroll at boundaries --
       Wheel events inside iframes do NOT propagate to the parent doc.
       When the scroll container reaches a boundary we temporarily disable
       pointer-events on all iframes so that subsequent wheel events fall
       through to the parent document and reach our wheelHandler.
       The marker widget buttons live in the parent DOM (not in iframes)
       so they remain clickable at all times.                           -- */
    var peDisabled = false;
    var peTimer = null;
    var PE_TIMEOUT_MS = 5000;

    function setIframePE(enabled) {
        var iframes = hostDoc.querySelectorAll('iframe');
        for (var k = 0; k < iframes.length; k++)
            iframes[k].style.pointerEvents = enabled ? '' : 'none';
        peDisabled = !enabled;
    }
    function reenablePE() {
        clearTimeout(peTimer);
        if (peDisabled) setIframePE(true);
    }
    function checkBoundaryPE() {
        if (navigating) return;
        /* Content fits without scrolling — no overscroll needed */
        if (scrollEl.scrollHeight <= scrollEl.clientHeight + 30) return;
        var atBot = isAtBot() && currentPage < totalPages - 1;
        var atTop = isAtTop() && currentPage > 0;
        if (atBot || atTop) {
            if (!peDisabled) {
                setIframePE(false);
                peTimer = setTimeout(reenablePE, PE_TIMEOUT_MS);
            }
        } else {
            reenablePE();
        }
    }
    scrollEl.addEventListener('scroll', checkBoundaryPE);

    /* Periodic boundary check — catches cases where the scroll event
       misses the exact boundary moment (e.g. momentum scroll ending
       exactly at bottom, or content height changing after load).
       Does NOT re-enable PE — only the scroll listener does that
       when the user scrolls away from the boundary.                  */
    var peCheckInterval = setInterval(function() {
        if (navigating) return;
        if (scrollEl.scrollHeight <= scrollEl.clientHeight + 30) return;
        var atBot = isAtBot() && currentPage < totalPages - 1;
        var atTop = isAtTop() && currentPage > 0;
        if (atBot || atTop) {
            if (!peDisabled) {
                setIframePE(false);
                clearTimeout(peTimer);
                peTimer = setTimeout(reenablePE, PE_TIMEOUT_MS);
            }
        }
    }, 300);

    function resetOver() {
        overState = 'idle'; overDir = null;
        clearTimeout(gapTimer); clearTimeout(waitTimer);
    }

    /* -- Shared state machine entry point -- */
    function boundarySignal(dir) {
        if (overDir && dir !== overDir) { resetOver(); return; }
        overDir = dir;
        if (overState === 'cooldown') return;

        if (overState === 'idle' || overState === 'phase1') {
            overState = 'phase1';
            clearTimeout(gapTimer);
            gapTimer = setTimeout(function() {
                overState = 'waiting';
                waitTimer = setTimeout(resetOver, WAIT_MS);
            }, GAP_MS);
        } else if (overState === 'waiting') {
            overState = 'cooldown'; overDir = null;
            clearTimeout(gapTimer); clearTimeout(waitTimer);
            setTimeout(function() { overState = 'idle'; }, COOLDOWN_MS);
            if (dir === 'down') {
                var np = currentPage + 1;
                hostWin._stxMarkerStartIdx =
                    pageFirstMarker[np] !== undefined ? pageFirstMarker[np] : 0;
                navigateToPage(np);
            } else {
                var pp = currentPage - 1;
                hostWin._stxMarkerStartIdx =
                    pageFirstMarker[pp] !== undefined ? pageFirstMarker[pp] : 0;
                navigateToPage(pp);
            }
        }
    }

    /* -- Source 1 & 2: wheel events (parent doc + iframes) -- */
    function wheelHandler(e) {
        var dir = null;
        if (e.deltaY > 0 && isAtBot() && currentPage < totalPages - 1)
            dir = 'down';
        else if (e.deltaY < 0 && isAtTop() && currentPage > 0)
            dir = 'up';
        if (!dir) {
            if ((overDir === 'down' && !isAtBot())
             || (overDir === 'up'   && !isAtTop())) resetOver();
            return;
        }
        /* Keep PE disabled while boundary wheel events keep coming */
        if (peDisabled) {
            clearTimeout(peTimer);
            peTimer = setTimeout(reenablePE, PE_TIMEOUT_MS);
        }
        boundarySignal(dir);
    }

    /* Listen on the parent document itself (captures wheel on
       non-iframe elements: Streamlit wrappers, gaps, buttons…) */
    hostDoc.addEventListener('wheel', wheelHandler, { passive: true });

    /* Also attach to each iframe's contentDocument */
    var attachedWF = new WeakSet();
    function attachWheelIframe(iframe) {
        if (attachedWF.has(iframe)) return;
        attachedWF.add(iframe);
        function tryA() {
            try { var d = iframe.contentDocument;
                  if (d) d.addEventListener('wheel', wheelHandler,
                                            { passive: true });
            } catch(x) {}
        }
        tryA(); iframe.addEventListener('load', tryA);
    }
    function scanWF() {
        hostDoc.querySelectorAll('iframe').forEach(attachWheelIframe);
    }
    scanWF();
    var wheelObs = new MutationObserver(scanWF);
    wheelObs.observe(hostDoc.body, { childList: true, subtree: true });
    var wheelScan = setInterval(scanWF, 2000);

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
        navigateToPage(p);
    }
    hostDoc.addEventListener('click', linkClick, true);

    /* --- Cleanup --- */
    hostWin._stxPaginatedCleanup = function() {
        hostDoc.removeEventListener('wheel', wheelHandler);
        wheelObs.disconnect(); clearInterval(wheelScan);
        hostDoc.removeEventListener('click', linkClick, true);
        clearTimeout(gapTimer); clearTimeout(waitTimer);
        reenablePE();
        clearInterval(peCheckInterval);
        scrollEl.removeEventListener('scroll', checkBoundaryPE);
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
                    export, export_title, *args, **kwargs):
    """Paginated rendering — only renders one block per rerun."""
    start_time = time.time()
    print("Starting st_book (paginated)...")

    total = len(module_list)
    if total == 0:
        return

    # --- Common setup ---
    load_css("default.css")
    inject_link_preview_scaffold()
    add_zoom_options()

    # --- Cache management ---
    cache_hash = _compute_cache_hash(module_list)
    cache = st.session_state.get(_STX_CACHE_KEY)
    has_valid_cache = (
        cache is not None
        and cache.get("hash") == cache_hash
        and cache.get("total") == total
    )

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

    # --- Render current block ---
    st_include(module_list[current_page], *args, **kwargs)

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
    print(f"st_book (paginated) completed in {end_time - start_time:.2f}s "
          f"[page {current_page + 1}/{total}]")
