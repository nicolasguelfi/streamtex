from contextlib import contextmanager

import streamlit as st

from .export import export_pop_wrapper, export_push_wrapper, is_export_active
from .utils import generate_key

_PAGE_WIDTH_KEY = "_stx_page_width"
_ZOOM_KEY = "_stx_zoom"

_SENTINEL = object()


def add_zoom_options(default_page_width: int = 100, default_zoom: int = 100,
                     container=_SENTINEL):
    """Adds Width% and Zoom% controls to the sidebar.

    - **Width %**: page width as percentage of browser window (10-400%).
    - **Zoom %**: CSS zoom applied to the page content (10-400%).

    :param default_page_width: Initial page width percentage (default 100).
    :param default_zoom: Initial zoom percentage (default 100).
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


def set_zoom(factor: int) -> None:
    """Set the CSS zoom for all subsequent content in the current scope.

    Unlike :func:`st_zoom` (context manager), this is an imperative call
    with no automatic cleanup.  The zoom remains active until:

    - :func:`reset_zoom` is called,
    - the next ``st_slide_break()`` clears it, or
    - ``st_book`` cleans up after ``build()`` returns.

    Args:
        factor: Zoom percentage.  ``100`` = normal, ``50`` = half,
            ``200`` = double.

    Example::

        set_zoom(75)
        st_write(s.body, "Dense content at 75%")
        st_write(s.body, "Still 75%")
        reset_zoom()
        st_write(s.body, "Back to inherited zoom")
    """
    from .spacing import set_section_zoom

    set_section_zoom(factor)


def reset_zoom() -> None:
    """Restore the zoom to the value inherited from the spacing hierarchy.

    Resolves the current effective section zoom from the 5-level override
    hierarchy (built-in → global → profile → block) and re-applies it,
    effectively undoing any prior :func:`set_zoom` call.

    Safe to call even if :func:`set_zoom` was never called.
    """
    from .spacing import resolve_section_spacing, set_section_zoom

    inherited = resolve_section_spacing()
    set_section_zoom(inherited.zoom)


@contextmanager
def st_zoom(factor: int = 100):
    """Apply a CSS zoom factor to all enclosed content.

    Uses a scoped CSS rule via ``:has()`` selector (same pattern as
    ``st_block``) so the zoom applies only to the Streamlit container
    created by this context manager.

    Args:
        factor: Zoom percentage.  ``100`` = normal, ``50`` = half size,
            ``200`` = double size.  Composes multiplicatively with the
            global page zoom and any section-level zoom.

    Example::

        with st_zoom(75):
            st_write(s.body, "Dense content rendered at 75%")
            st_image(s.img, "diagram.png")
    """
    zoom_id = generate_key("zoom")
    zoom_value = factor / 100

    css_and_marker = (
        f'<style>'
        f'div:has(> .element-container > .stHtml > span.{zoom_id})'
        f'{{ zoom: {zoom_value}; }}'
        f' .element-container:has(.stHtml > span.{zoom_id})'
        f'{{ width: auto; }}'
        f'</style>'
        f'<span class="{zoom_id}" style="display:none;"></span>'
    )

    if is_export_active():
        export_push_wrapper(
            f'<div class="stx-zoom" style="zoom: {zoom_value};">'
        )

    with st.container():
        st.html(css_and_marker)
        yield

    if is_export_active():
        export_pop_wrapper("</div>")
