import streamlit as st
import streamlit.components.v1 as components

_PAGE_WIDTH_KEY = "_stx_page_width"
_ZOOM_KEY = "_stx_zoom"
_ZOOM_FIT_KEY = "_stx_zoom_fit"
_ZOOM_PREV_KEY = "_stx_zoom_prev"

_SENTINEL = object()


def add_zoom_options(default_page_width: int = 100, default_zoom: int | str = 100,
                     container=_SENTINEL):
    """Adds Width% and Zoom% controls to the sidebar.

    - **Width %**: page width as percentage of browser window (10-400%).
    - **Zoom %**: CSS zoom applied to the page content (10-400%), or
      ``"fit"`` for auto-fit to viewport height.

    :param default_page_width: Initial page width percentage (default 100).
    :param default_zoom: Initial zoom percentage (default 100), or ``"fit"``.
    :param container: Streamlit container to render into.  When omitted,
        widgets are placed in ``st.sidebar``.  Pass any container (or
        ``st`` itself when already inside a context manager) to render
        there instead.
    """
    # Initialize session state with defaults (don't overwrite existing values)
    if _PAGE_WIDTH_KEY not in st.session_state:
        st.session_state[_PAGE_WIDTH_KEY] = default_page_width
    if _ZOOM_KEY not in st.session_state:
        st.session_state[_ZOOM_KEY] = default_zoom

    ctx = st.sidebar if container is _SENTINEL else container
    ctx.number_input(
        "Width %",
        min_value=10,
        max_value=400,
        step=10,
        key=_PAGE_WIDTH_KEY,
    )

    # --- Zoom: toggle between numeric and "fit" ---
    zoom_val = st.session_state[_ZOOM_KEY]
    _is_fit = zoom_val == "fit"

    # Initialize the fit toggle state from the current zoom value
    if _ZOOM_FIT_KEY not in st.session_state:
        st.session_state[_ZOOM_FIT_KEY] = _is_fit

    def _on_fit_toggle():
        if st.session_state[_ZOOM_FIT_KEY]:
            # Save current numeric zoom before switching to fit
            cur = st.session_state.get(_ZOOM_KEY, 100)
            if cur != "fit":
                st.session_state[_ZOOM_PREV_KEY] = cur
            st.session_state[_ZOOM_KEY] = "fit"
        else:
            # Restore previous numeric zoom
            st.session_state[_ZOOM_KEY] = st.session_state.get(_ZOOM_PREV_KEY, 100)

    ctx.toggle("Fit to page", key=_ZOOM_FIT_KEY, on_change=_on_fit_toggle)

    if st.session_state[_ZOOM_KEY] == "fit":
        # Show greyed-out zoom input (no key binding — value is cosmetic)
        _prev = st.session_state.get(_ZOOM_PREV_KEY, 100)
        ctx.number_input(
            "Zoom %",
            value=_prev,
            min_value=10,
            max_value=400,
            step=10,
            disabled=True,
        )
    else:
        ctx.number_input(
            "Zoom %",
            min_value=10,
            max_value=400,
            step=10,
            key=_ZOOM_KEY,
        )

    inject_zoom_logic(
        st.session_state[_PAGE_WIDTH_KEY],
        st.session_state[_ZOOM_KEY],
    )


def inject_zoom_logic(page_width_pct: int = 100, zoom_pct: int | str = 100):
    """Injects pure CSS for page width and zoom.

    Uses CSS ``zoom`` property (Baseline 2024 — all modern browsers since
    Firefox 126, May 2024).

    - Width < 100%: symmetric margins (page centered).
    - Width = 100%: full width.
    - Width > 100%: horizontal scrollbar.
    - Zoom is independent, applied inside the page container.
    - ``zoom_pct = "fit"``: auto-fit content height to viewport via JS.

    CSS is injected via ``st.html()`` (extracted to host page since
    Streamlit 1.43+).

    :param page_width_pct: Page width as percentage (default 100).
    :param zoom_pct: Zoom level as percentage (default 100), or ``"fit"``.
    """
    from .constants import PAGE_PADDING

    if zoom_pct == "fit":
        _inject_zoom_fit(page_width_pct, PAGE_PADDING)
    else:
        _inject_zoom_fixed(page_width_pct, zoom_pct, PAGE_PADDING)


def _inject_zoom_fixed(page_width_pct: int, zoom_pct: int, page_padding: str):
    """Inject pure CSS for fixed zoom.

    Also cleans up any active fit-zoom JS observer from a previous run
    and resets inline ``zoom`` style that fit-zoom may have set on the
    container element.
    """
    zoom_value = zoom_pct / 100

    css = f"""
    <style>
        .stMainBlockContainer {{
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}

        .stMain .block-container {{
            /* Document dimensions */
            width: {page_width_pct}% !important;
            max-width: {page_width_pct}% !important;

            /* Internal padding */
            padding-left: {page_padding} !important;
            padding-right: {page_padding} !important;

            /* Natural centering */
            margin-left: auto !important;
            margin-right: auto !important;

            /* CSS zoom */
            zoom: {zoom_value};
        }}
    </style>
    """

    st.html(css)

    # Cleanup any active fit-zoom JS observer and reset inline zoom style.
    # The fit JS sets container.style.zoom directly (inline), which overrides
    # the CSS rule above.  We must clear both the observer and the inline style.
    components.html("""<script>
    (function(){
        var hw = parent.document.defaultView || parent;
        if (hw._stxZoomFitCleanup) {
            hw._stxZoomFitCleanup();
            hw._stxZoomFitCleanup = null;
        }
        var c = parent.document.querySelector('.stMain .block-container');
        if (c) c.style.zoom = '';
    })();
    </script>""", height=0)


def _inject_zoom_fit(page_width_pct: int, page_padding: str):
    """Inject CSS + JS for auto-fit zoom.

    The JS measures the content height of the block container and
    calculates the zoom factor so the content fits within the viewport.
    Re-calculates on window resize via ResizeObserver.
    """
    # CSS for width (same as fixed, but zoom is set by JS)
    # JS for auto-fit zoom calculation
    js = f"""
    <style>
        .stMainBlockContainer {{
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}
        .stMain .block-container {{
            width: {page_width_pct}% !important;
            max-width: {page_width_pct}% !important;
            padding-left: {page_padding} !important;
            padding-right: {page_padding} !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
    </style>
    <script>
    (function() {{
        var hostDoc = parent.document;
        var hostWin = hostDoc.defaultView || parent;

        /* Clean up previous fit observer */
        if (hostWin._stxZoomFitCleanup) {{
            try {{ hostWin._stxZoomFitCleanup(); }} catch(e) {{}}
        }}

        function fitZoom() {{
            var container = hostDoc.querySelector('.stMain .block-container');
            if (!container) return;
            /* Reset zoom to 1 to measure natural content height */
            container.style.zoom = '1';
            /* Wait one frame for layout recalculation */
            requestAnimationFrame(function() {{
                var contentH = container.scrollHeight;
                /* Viewport height minus Streamlit header (~64px) and some padding */
                var viewportH = hostWin.innerHeight || hostDoc.documentElement.clientHeight;
                var headerEl = hostDoc.querySelector('header[data-testid="stHeader"]');
                var headerH = headerEl ? headerEl.offsetHeight : 0;
                var available = viewportH - headerH;
                if (contentH > 0 && available > 0) {{
                    var fit = available / contentH;
                    container.style.zoom = String(fit);
                }}
            }});
        }}

        /* Initial fit after content renders */
        setTimeout(fitZoom, 600);

        /* Re-fit on viewport resize */
        var resizeTimer = null;
        function onResize() {{
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(fitZoom, 200);
        }}
        hostWin.addEventListener('resize', onResize);

        /* Re-fit when content changes (block navigation in paginated mode) */
        var obs = null;
        var container = hostDoc.querySelector('.stMain .block-container');
        if (container) {{
            obs = new MutationObserver(function() {{
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(fitZoom, 300);
            }});
            obs.observe(container, {{ childList: true, subtree: true }});
        }}

        /* Cleanup function for next injection */
        hostWin._stxZoomFitCleanup = function() {{
            hostWin.removeEventListener('resize', onResize);
            clearTimeout(resizeTimer);
            if (obs) obs.disconnect();
        }};
    }})();
    </script>
    """

    # components.html() creates a real iframe where scripts execute
    # (st.html() strips <script> tags in Streamlit 1.54+)
    components.html(js, height=0)
