"""StreamTeX — Markdown rendering with Streamlit's native engine."""

import streamlit as st

from .container import st_block
from .export import export_append, is_export_active
from .search import record_if_active
from .styles import StxStyles, Style
from .utils import resolve_content


def st_markdown(
    content: str = "",
    *,
    style: Style = StxStyles.none,
    file: str | None = None,
    encoding: str = "utf-8",
) -> None:
    """Render interpreted Markdown content with optional StreamTeX styling.

    Uses Streamlit's native ``st.markdown()`` engine which supports:
    - Standard Markdown (headings, bold, italic, lists, links, tables)
    - LaTeX math (inline ``$...$`` and display ``$$...$$``)
    - Code blocks with syntax highlighting

    Parameters
    ----------
    content : str
        Markdown source string.  Mutually exclusive with *file*.
    style : Style
        Optional StreamTeX style wrapping the rendered content.
    file : str | None
        Path to a ``.md`` file.  Resolved via ``resolve_static()`` so that
        relative paths search configured static source directories.
    encoding : str
        File encoding (only used when *file* is provided).
    """
    text = resolve_content(content, file=file, encoding=encoding)
    if not text:
        return

    if style is not StxStyles.none:
        with st_block(style):
            st.markdown(text, unsafe_allow_html=True)
    else:
        st.markdown(text, unsafe_allow_html=True)
    record_if_active(text)

    if is_export_active():
        try:
            import markdown as md_lib

            html = md_lib.markdown(text, extensions=["tables", "fenced_code"])
        except ImportError:
            html = f"<div>{text}</div>"
        export_append(html)
