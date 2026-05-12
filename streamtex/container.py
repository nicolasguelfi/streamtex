from contextlib import contextmanager

import streamlit as st

from .export import export_pop_wrapper, export_push_wrapper, is_export_active
from .styles import StxStyles, Style
from .utils import generate_key


def _build_block_payload(block_id: str, style: Style, section_css: str) -> str:
    """Return the `<style>+<span>` payload that scopes ``st_block`` to its container.

    Emits a sentinel ``<span class="stx-marker" data-stx-kind="block" …>``
    that the global :mod:`streamtex.marker_runtime` MutationObserver
    translates into a ``.stx-block`` class on the parent
    ``[data-testid="stVerticalBlock"]``.  When the user supplies a
    non-empty style, an extra per-instance ``<style>`` keyed by the
    attribute selector ``[data-stx-block-uid="…"]`` carries it
    (preserves the cascade semantics of the historical ``:has()`` rule).
    """
    combined = f"{style!s}{section_css}".strip()
    if combined:
        inline_css = (
            f'<style>'
            f'[data-stx-block-uid="{block_id}"]'
            f'{{{style!s}{section_css}}}'
            f'</style>'
        )
    else:
        inline_css = ''
    return (
        f'{inline_css}'
        f'<span class="stx-marker {block_id}" '
        f'data-stx-kind="block" data-stx-uid="{block_id}" '
        f'style="display:none;"></span>'
    )


def _build_span_payload(block_id: str, style: Style, section_css: str) -> str:
    """Return the `<style>+<span>` payload that scopes ``st_span`` to its container.

    Mirrors :func:`_build_block_payload` but with ``data-stx-kind="span"``.
    The flex-row container styles (display:flex, flex-direction:row,
    white-space:pre) live in the global stylesheet under ``.stx-span``;
    only the user-supplied ``style`` is per-instance.
    """
    combined = f"{style!s}{section_css}".strip()
    if combined:
        inline_css = (
            f'<style>'
            f'[data-stx-span-uid="{block_id}"]'
            f'{{{style!s}{section_css}}}'
            f'</style>'
        )
    else:
        inline_css = ''
    return (
        f'{inline_css}'
        f'<span class="stx-marker {block_id}" '
        f'data-stx-kind="span" data-stx-uid="{block_id}" '
        f'style="display:none;"></span>'
    )


@contextmanager
def st_block(style: Style = StxStyles.none, _export_wrapper: bool = True):
    """A Context Manager that wraps content within a styled container."""

    # 1. Generate a unique ID to scope the CSS to this specific block
    block_id = generate_key("block")

    # 2. Section-level horizontal spacing (adds padding to this container)
    from .spacing import get_section_horizontal
    _sh = get_section_horizontal()
    _section_css = ""
    if _sh is not None:
        if _sh.left:
            _section_css += f" margin-left: {_sh.left};"
        if _sh.right:
            _section_css += f" margin-right: {_sh.right};"

    # 3. Build CSS + marker span (fused into a single st.html call)
    css_and_marker = _build_block_payload(block_id, style, _section_css)

    # 4. Export wrapper (no-op when export is inactive)
    # Prepend flex-direction:column to mirror Streamlit's stVerticalBlock
    # (same pattern as st_span which prepends flex-direction:row).
    # User styles that override display or flex-direction win because
    # later declarations in the same style attribute take precedence.
    _base = 'display:flex;flex-direction:column;gap:0.1rem;'
    _export_style = f'{_base}{style}{_section_css}' if _section_css else f'{_base}{style}'
    if is_export_active() and _export_wrapper:
        export_push_wrapper(f'<div class="stx-block" style="{_export_style}">')

    # 4. Create a native Streamlit container
    with st.container():
        # Inject CSS + marker in one call (halves WebSocket messages)
        st.html(css_and_marker)
        yield

    if is_export_active() and _export_wrapper:
        export_pop_wrapper("</div>")


@contextmanager
def st_span(style: Style = StxStyles.none):
    """
    A Context Manager that wraps content within a styled container.
    Its contents are inserted in the same line.
    """

    # 1. Generate a unique ID to scope the CSS to this specific block
    block_id = generate_key("span")

    # 2. Section-level horizontal spacing
    from .spacing import get_section_horizontal
    _sh = get_section_horizontal()
    _section_css = ""
    if _sh is not None:
        if _sh.left:
            _section_css += f" margin-left: {_sh.left};"
        if _sh.right:
            _section_css += f" margin-right: {_sh.right};"

    # 3. Build CSS + marker span (fused into a single st.html call)
    css_and_marker = _build_span_payload(block_id, style, _section_css)

    # 4. Export wrapper (no-op when export is inactive)
    _export_style = f'display:flex;flex-direction:row;white-space:pre;{style}{_section_css}'
    if is_export_active():
        export_push_wrapper(f'<div style="{_export_style}">')

    # 4. Create a native Streamlit container
    with st.container():
        # Inject CSS + marker in one call (halves WebSocket messages)
        st.html(css_and_marker)
        yield

    if is_export_active():
        export_pop_wrapper("</div>")
