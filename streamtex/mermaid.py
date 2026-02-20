"""Mermaid diagram rendering — live component + HTML export as SVG.

Live rendering uses the ``streamlit-mermaid`` community component.
Export rendering uses ``mermaid-py`` to generate SVG via the mermaid.ink
service, with a graceful ``<pre>`` fallback on failure.
"""

from contextlib import nullcontext
from html import escape

import streamlit as st

from .container import st_block
from .export import export_append, is_export_active
from .styles import Style


def st_mermaid(code: str, *, style: Style | None = None, **kw) -> None:
    """Render a Mermaid diagram.

    Parameters
    ----------
    code : str
        The Mermaid diagram source code.
    style : Style | None
        Optional StreamTeX style to wrap the diagram in a styled container.
    **kw
        Extra keyword arguments forwarded to ``streamlit_mermaid.st_mermaid``.
    """
    with st_block(style) if style is not None else nullcontext():
        # --- Live rendering via streamlit-mermaid component ---
        try:
            from streamlit_mermaid import st_mermaid as _component_mermaid
            _component_mermaid(code, **kw)
        except ImportError:
            st.warning("Install `streamlit-mermaid` for live Mermaid rendering.")
            st.code(code, language="mermaid")

        # --- Export rendering ---
        if is_export_active():
            try:
                import mermaid as mermaid_py
                from mermaid.graph import Graph

                graph = Graph("stx-mermaid", code)
                svg = mermaid_py.Mermaid(graph).svg_response.text
                export_append(f'<div class="stx-mermaid">{svg}</div>')
            except Exception:
                export_append(f'<pre class="stx-mermaid">{escape(code)}</pre>')
