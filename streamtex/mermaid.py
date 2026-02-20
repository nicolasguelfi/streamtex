"""Mermaid diagram rendering — live via components.html + HTML export as SVG.

Live rendering uses the Mermaid JS library loaded via CDN inside a
``components.html()`` iframe.  This gives full control over the iframe
background and theme, ensuring diagrams are readable in any OS/browser
dark-mode configuration.

Export rendering uses ``mermaid-py`` to generate SVG via the mermaid.ink
service, with a graceful ``<pre>`` fallback on failure.

When *light_bg* is True (the default), the diagram is rendered on a white
background with the Mermaid "default" (light) theme.
"""

from contextlib import nullcontext
from html import escape

import streamlit.components.v1 as components

from .container import st_block
from .export import export_append, is_export_active
from .styles import Style

# HTML template rendered inside components.html().
# Mermaid JS is loaded client-side from CDN — no Python dependency needed
# for live rendering.  Double braces are literal braces in .format().
_MERMAID_HTML = """\
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
  body {{ background: {bg}; margin: 0; padding: 8px; }}
</style>
<pre class="mermaid">{code}</pre>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: '{theme}' }});
</script>
"""


def st_mermaid(
    code: str,
    *,
    style: Style | None = None,
    light_bg: bool = True,
    height: int = 500,
    **kw,
) -> None:
    """Render a Mermaid diagram.

    Parameters
    ----------
    code : str
        The Mermaid diagram source code.
    style : Style | None
        Optional StreamTeX style to wrap the diagram in a styled container.
    light_bg : bool
        When True (default), render the diagram on a white background with
        the Mermaid "default" light theme.  Set to False to use the "dark"
        theme with a transparent background.
    height : int
        Height in pixels for the diagram iframe.  Defaults to 500.
    **kw
        Reserved for future use.
    """
    bg = "#fff" if light_bg else "transparent"
    theme = "default" if light_bg else "dark"
    html = _MERMAID_HTML.format(bg=bg, theme=theme, code=escape(code))

    with st_block(style) if style is not None else nullcontext():
        components.html(html, height=height)

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
