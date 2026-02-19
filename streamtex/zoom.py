import streamlit as st
import streamlit.components.v1 as components

_ZOOM_STATE_KEY = "streamtex_zoom"


def add_zoom_options():
    """Adds a generic 'View Options' menu to the sidebar using a popover."""

    # 1. Initialize State
    if _ZOOM_STATE_KEY not in st.session_state:
        st.session_state[_ZOOM_STATE_KEY] = "Fit"

    # 2. Define Options
    zoom_levels = ["Fit", 50, 75, 90, 100, 110, 125, 150, 175, 200]

    # 3. Create the Menu (Popover)
    with st.sidebar:
        option = st.selectbox(
            "**Zoom Level**",
            options=zoom_levels,
            format_func=lambda x: x if x == "Fit" else f"{x}%",
            index=zoom_levels.index(st.session_state[_ZOOM_STATE_KEY])
                      if st.session_state[_ZOOM_STATE_KEY] in zoom_levels else 0,
            key="streamtex_zoom_list"
        )

        # Update state if changed
        if option != st.session_state[_ZOOM_STATE_KEY]:
            st.session_state[_ZOOM_STATE_KEY] = option
            st.rerun()  # Force rerun to apply CSS immediately

    # 4. Apply the styles
    inject_zoom_logic(st.session_state[_ZOOM_STATE_KEY])


def inject_zoom_logic(zoom_setting):
    """
    Applies page layout and calculates negative margins to remove whitespace.

    Since Streamlit 1.41+, st.html() renders <script> inside a sandboxed iframe
    while <style> tags are extracted to the host page (since 1.43+).
    Therefore:
      - CSS uses :has() for sidebar detection (no JS needed).
      - JS uses parent.document to access the main page DOM from the iframe.
    """

    # Constants
    # 17 inches * 72 pt/inch = 1224 pt
    PAGE_WIDTH = "1224pt"
    # 0.5 inches * 72 pt/inch = 36 pt
    PAGE_PADDING = "36pt"

    # 1. Determine Scale Strategy
    if zoom_setting == "Fit":
        # Calculate scale based on viewport
        scale_val = "var(--streamtex-fit-scale, 1)"

        # JS logic for Fit mode (uses doc/win/page from parent scope)
        fit_logic_js = """
                // Calculate fit scale accounting for sidebar offset
                const pageWidthPx = page.scrollWidth;
                const computedMargin = parseFloat(
                    win.getComputedStyle(page).marginLeft) || 0;
                const availableWidth = win.innerWidth - computedMargin - 40;
                const fitScale = Math.min(1, availableWidth / pageWidthPx);
                doc.documentElement.style.setProperty(
                    '--streamtex-fit-scale', fitScale);
        """
    else:
        # Fixed mode
        scale_val = zoom_setting / 100.0
        fit_logic_js = ""  # No calculation needed

    # 2. CSS with :has() for sidebar-aware layout
    # <style> tags are extracted from st.html() to the host page (Streamlit 1.43+)
    css = f"""
    <style>
        :root {{
            --streamtex-scale: {scale_val};
            --streamtex-sidebar-offset: 0px;
        }}

        /* Pure-CSS sidebar detection (works even if JS fails) */
        .stApp:has([data-testid="stSidebar"][aria-expanded="true"]) {{
            --streamtex-sidebar-offset: 17.5rem;
        }}

        .stMain .block-container {{
            /* Dimensions */
            width: {PAGE_WIDTH} !important;
            min-width: {PAGE_WIDTH} !important;
            max-width: {PAGE_WIDTH} !important;

            /* Padding */
            padding-left: {PAGE_PADDING} !important;
            padding-right: {PAGE_PADDING} !important;

            /* Scaling */
            transform: scale(var(--streamtex-scale));
            transform-origin: top left;
            margin-left: var(--streamtex-sidebar-offset, 0px);
        }}
    </style>
    """

    # 3. JS via components.html() — st.html() strips <script> in Streamlit 1.54+
    # Uses parent.document to access the main page from the iframe.
    js_logic = f"""
    <script>
        (function() {{
            var doc = parent.document;
            var win = doc.defaultView || parent;

            // Cleanup previous run
            if (win._stxZoomCleanup) {{
                try {{ win._stxZoomCleanup(); }} catch(e) {{}}
            }}

            function updateLayout() {{
                try {{
                    var page = doc.querySelector('.block-container');
                    if (!page) return;

                    // Refine sidebar offset with exact pixel width
                    var sidebar = doc.querySelector(
                        '[data-testid="stSidebar"]');
                    var app = doc.querySelector('.stApp');
                    if (app) {{
                        if (sidebar && sidebar.offsetWidth > 50) {{
                            app.style.setProperty(
                                '--streamtex-sidebar-offset',
                                sidebar.offsetWidth + 'px');
                        }} else {{
                            app.style.setProperty(
                                '--streamtex-sidebar-offset', '0px');
                        }}
                    }}

                    // Fit scale logic
                    {fit_logic_js}

                    // Ghost space fix: collapse gap between layout and visual size
                    var rootStyle = win.getComputedStyle(doc.documentElement);
                    var scale =
                        parseFloat(rootStyle.getPropertyValue('--streamtex-scale'))
                        || parseFloat(rootStyle.getPropertyValue(
                               '--streamtex-fit-scale'))
                        || 1;
                    // Vertical ghost space
                    var origHeight = page.offsetHeight;
                    var visualHeight = origHeight * scale;
                    var ghostSpace = origHeight - visualHeight;
                    if (ghostSpace > 50) {{
                        page.style.marginBottom = '-' + (ghostSpace - 50) + 'px';
                    }}
                    // Horizontal ghost space (prevents horizontal scrollbar)
                    var origWidth = page.offsetWidth;
                    var hGhostSpace = Math.round(origWidth * (1 - scale));
                    if (hGhostSpace > 5) {{
                        page.style.marginRight = '-' + hGhostSpace + 'px';
                    }} else {{
                        page.style.marginRight = '';
                    }}
                }} catch(e) {{}}
            }}

            // Window resize
            win.addEventListener('resize', updateLayout);

            // DOM mutations (sidebar open/close, content changes)
            var obs = new MutationObserver(updateLayout);
            obs.observe(doc.body,
                {{ childList: true, subtree: true, attributes: true }});

            // ResizeObserver on sidebar for drag-resize
            var resObs = null;
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar && typeof ResizeObserver !== 'undefined') {{
                resObs = new ResizeObserver(updateLayout);
                resObs.observe(sidebar);
            }}

            // Cleanup for next Streamlit rerun
            win._stxZoomCleanup = function() {{
                win.removeEventListener('resize', updateLayout);
                obs.disconnect();
                if (resObs) resObs.disconnect();
            }};

            setTimeout(updateLayout, 200);
        }})();
    </script>
    """

    st.html(css)
    # components.html() creates a real iframe where scripts execute
    components.html(js_logic, height=0)
