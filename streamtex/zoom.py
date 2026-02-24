import streamlit as st

_PAGE_WIDTH_KEY = "_stx_page_width"
_ZOOM_KEY = "_stx_zoom"


def add_zoom_options(default_page_width: int = 100, default_zoom: int = 100):
    """Adds Width% and Zoom% controls to the sidebar.

    Two independent ``st.number_input`` widgets side by side:
    - **Width %**: page width as percentage of browser window (10-400%).
    - **Zoom %**: CSS zoom applied to the page content (10-400%).

    :param default_page_width: Initial page width percentage (default 100).
    :param default_zoom: Initial zoom percentage (default 100).
    """
    # Initialize session state with defaults (don't overwrite existing values)
    if _PAGE_WIDTH_KEY not in st.session_state:
        st.session_state[_PAGE_WIDTH_KEY] = default_page_width
    if _ZOOM_KEY not in st.session_state:
        st.session_state[_ZOOM_KEY] = default_zoom

    with st.sidebar:
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "Width %",
                min_value=10,
                max_value=400,
                step=10,
                key=_PAGE_WIDTH_KEY,
            )
        with col2:
            st.number_input(
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


def inject_zoom_logic(page_width_pct: int = 100, zoom_pct: int = 100):
    """Injects pure CSS for page width and zoom.

    Uses CSS ``zoom`` property (Baseline 2024 — all modern browsers since
    Firefox 126, May 2024).

    - Width < 100%: symmetric margins (page centered).
    - Width = 100%: full width.
    - Width > 100%: horizontal scrollbar.
    - Zoom is independent, applied inside the page container.

    CSS is injected via ``st.html()`` (extracted to host page since
    Streamlit 1.43+).

    :param page_width_pct: Page width as percentage (default 100).
    :param zoom_pct: Zoom level as percentage (default 100).
    """
    from .constants import PAGE_PADDING

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
            padding-left: {PAGE_PADDING} !important;
            padding-right: {PAGE_PADDING} !important;

            /* Natural centering */
            margin-left: auto !important;
            margin-right: auto !important;

            /* CSS zoom */
            zoom: {zoom_value};
        }}
    </style>
    """

    st.html(css)
