from contextlib import contextmanager

import streamlit as st

from .export import export_pop_wrapper, export_push_wrapper, is_export_active
from .styles import StxStyles, Style
from .utils import generate_key


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
    css_and_marker = (
        f'<style>'
        f'div:has(> .element-container > .stHtml > span.{block_id})'
        f'{{ {str(style)}{_section_css} }}'
        f' .element-container:has(.stHtml > span.{block_id})'
        f'{{ width: auto; }}'
        f'</style>'
        f'<span class="{block_id}" style="display:none;"></span>'
    )

    # 4. Export wrapper (no-op when export is inactive)
    _export_style = f'{style}{_section_css}' if _section_css else str(style)
    if is_export_active() and _export_wrapper:
        export_push_wrapper(f'<div style="{_export_style}">')

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
    css_and_marker = (
        f'<style>'
        f'div:has(> .element-container > .stHtml > span.{block_id}) > *'
        f'{{ width: auto; }}'
        f' div:has(> .element-container > .stHtml > span.{block_id})'
        f'{{ display: flex; flex-direction: row; white-space: pre; {str(style)}{_section_css} }}'
        f' .element-container:has(.stHtml > span.{block_id})'
        f'{{ width: auto; }}'
        f'</style>'
        f'<span class="{block_id}" style="display:none;"></span>'
    )

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



