import streamlit as st
import streamlit.components.v1 as components

_ZOOM_STATE_KEY = "streamtex_zoom"


def add_zoom_options(page_width: str | None = None):
    """Adds a generic 'View Options' menu to the sidebar using a popover.

    :param page_width: Custom page width (CSS value). Defaults to PAGE_WIDTH constant.
    """

    # 1. Initialize State
    if _ZOOM_STATE_KEY not in st.session_state:
        st.session_state[_ZOOM_STATE_KEY] = "Fit"

    # 2. Define Options
    zoom_levels = ["Fit", "Fill", 50, 75, 90, 100, 110, 125, 150, 175, 200]

    # 3. Create the Menu (Popover)
    with st.sidebar:
        option = st.selectbox(
            "**Zoom Level**",
            options=zoom_levels,
            format_func=lambda x: x if isinstance(x, str) else f"{x}%",
            index=zoom_levels.index(st.session_state[_ZOOM_STATE_KEY])
                      if st.session_state[_ZOOM_STATE_KEY] in zoom_levels else 0,
            key="streamtex_zoom_list"
        )

        # Update state if changed
        if option != st.session_state[_ZOOM_STATE_KEY]:
            st.session_state[_ZOOM_STATE_KEY] = option
            st.rerun()  # Force rerun to apply CSS immediately

    # 4. Apply the styles
    inject_zoom_logic(st.session_state[_ZOOM_STATE_KEY], page_width=page_width)


def inject_zoom_logic(zoom_setting, page_width: str | None = None):
    """
    Applies page layout with CSS zoom for proper scaling.

    Uses CSS ``zoom`` property (Baseline 2024 — all modern browsers since
    Firefox 126, May 2024) instead of ``transform: scale()``.

    CSS zoom modifies the actual box model so:
    - No ghost-space compensation needed (layout matches visual size)
    - No sidebar offset tracking needed (Streamlit sizes .stMain itself)
    - Scroll and measurement APIs stay in a single coordinate system

    CSS is injected via st.html() (extracted to host page since Streamlit 1.43+).
    JS is injected via components.html() (runs in an iframe, accesses host via
    parent.document).

    :param page_width: Custom page width (CSS value). Defaults to PAGE_WIDTH constant.
    """

    # Constants — centralized in streamtex.constants
    from .constants import PAGE_WIDTH as _DEFAULT_WIDTH, PAGE_PADDING

    pw = page_width if page_width is not None else _DEFAULT_WIDTH

    # --- CSS ---------------------------------------------------------------
    css = f"""
    <style>
        .stMainBlockContainer {{
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}

        .stMain .block-container {{
            /* Document dimensions */
            width: {pw} !important;
            max-width: {pw} !important;

            /* Internal padding */
            padding-left: {PAGE_PADDING} !important;
            padding-right: {PAGE_PADDING} !important;

            /* Natural centering (works for zoom < 1 and zoom > 1) */
            margin-left: auto !important;
            margin-right: auto !important;

            /* CSS zoom — replaces transform: scale() */
            zoom: var(--streamtex-zoom, 1);
        }}
    </style>
    """

    st.html(css)

    # --- JS: cleanup previous run + set zoom value -------------------------
    if zoom_setting == "Fit":
        zoom_js = """
            var stMain = doc.querySelector('.stMain')
                      || doc.querySelector('[data-testid="stMain"]');
            var page = doc.querySelector('.block-container');
            if (stMain && page) {
                function updateFitZoom() {
                    try {
                        var available = stMain.clientWidth;
                        /* offsetWidth returns the UN-zoomed width (CSS zoom spec) */
                        var pageWidth = page.offsetWidth;
                        if (pageWidth <= 0) return;
                        var fitZoom = Math.min(1, available / pageWidth);
                        doc.documentElement.style.setProperty(
                            '--streamtex-zoom', fitZoom);
                    } catch(e) {}
                }
                /* ResizeObserver on stMain fires when:
                   - browser window resizes
                   - sidebar opens / closes (Streamlit resizes stMain) */
                var ro = new ResizeObserver(updateFitZoom);
                ro.observe(stMain);
                updateFitZoom();
                win._stxZoomCleanup = function() { ro.disconnect(); };
            }"""
    elif zoom_setting == "Fill":
        zoom_js = """
            var stMain = doc.querySelector('.stMain')
                      || doc.querySelector('[data-testid="stMain"]');
            var page = doc.querySelector('.block-container');
            if (stMain && page) {
                function updateFillZoom() {
                    try {
                        var available = stMain.clientWidth;
                        /* offsetWidth returns the UN-zoomed width (CSS zoom spec) */
                        var pageWidth = page.offsetWidth;
                        if (pageWidth <= 0) return;
                        var fillZoom = Math.min(2, available / pageWidth);
                        doc.documentElement.style.setProperty(
                            '--streamtex-zoom', fillZoom);
                    } catch(e) {}
                }
                /* ResizeObserver on stMain fires when:
                   - browser window resizes
                   - sidebar opens / closes (Streamlit resizes stMain) */
                var ro = new ResizeObserver(updateFillZoom);
                ro.observe(stMain);
                updateFillZoom();
                win._stxZoomCleanup = function() { ro.disconnect(); };
            }"""
    else:
        zoom_js = (
            "doc.documentElement.style.setProperty("
            "'--streamtex-zoom', __ZOOM_VAL__);"
            .replace("__ZOOM_VAL__", str(zoom_setting / 100.0))
        )

    js_logic = f"""
    <script>
        (function() {{
            var doc = parent.document;
            var win = doc.defaultView || parent;

            /* Cleanup previous run (disconnect old ResizeObserver etc.) */
            if (win._stxZoomCleanup) {{
                try {{ win._stxZoomCleanup(); }} catch(e) {{}}
            }}
            win._stxZoomCleanup = null;

            {zoom_js}
        }})();
    </script>
    """

    # components.html() creates a real iframe where scripts execute
    components.html(js_logic, height=0)
