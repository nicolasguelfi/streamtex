"""Mermaid diagram rendering — live via components.html + HTML export as SVG.

Live rendering uses the Mermaid JS library loaded via CDN inside a
``components.html()`` iframe.  This gives full control over the iframe
background and theme, ensuring diagrams are readable in any OS/browser
dark-mode configuration.

The rendered diagram supports interactive pan (click + drag) and zoom
(mouse wheel), with +/- and Reset controls.

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

# ---------------------------------------------------------------------------
# HTML template rendered inside components.html().
#
# Mermaid JS is loaded client-side from CDN — no Python dependency needed
# for live rendering.  Placeholders use __UPPER__ markers to avoid clashes
# with JavaScript braces.
# ---------------------------------------------------------------------------
_MERMAID_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; background: __BG__; overflow: hidden; }
  #viewport {
    width: 100%; height: calc(100% - 32px);
    overflow: hidden; cursor: grab;
    display: flex; justify-content: center; align-items: start;
  }
  #viewport.dragging { cursor: grabbing; }
  #viewport svg { transform-origin: 0 0; }
  #controls {
    height: 32px; display: flex; gap: 4px;
    justify-content: center; align-items: center;
    background: rgba(128,128,128,0.12);
  }
  #controls button {
    border: 1px solid #aaa; background: #f0f0f0; color: #333;
    padding: 2px 10px; cursor: pointer; font-size: 13px;
    border-radius: 3px; line-height: 1.4;
  }
  #controls button:hover { background: #ddd; }
</style>
</head>
<body>
<div id="viewport">
  <pre class="mermaid">__CODE__</pre>
</div>
<div id="controls">
  <button onclick="zoomIn()" title="Zoom in">+</button>
  <button onclick="resetView()" title="Reset">Reset</button>
  <button onclick="zoomOut()" title="Zoom out">&minus;</button>
</div>
<script>
  /* ---- Global state ---- */
  var _s = 1, _tx = 0, _ty = 0, _svg = null;

  function _apply() {
    if (!_svg) return;
    _svg.style.transform = 'translate(' + _tx + 'px,' + _ty + 'px) scale(' + _s + ')';
  }
  function zoomIn()    { _s *= 1.2; _apply(); }
  function zoomOut()   { _s /= 1.2; _apply(); }
  function resetView() { _s = 1; _tx = 0; _ty = 0; _apply(); }

  /* ---- Render Mermaid then attach pan-zoom ---- */
  mermaid.initialize({ startOnLoad: false, theme: '__THEME__' });
  mermaid.run().then(function() {
    _svg = document.querySelector('#viewport svg');
    if (!_svg) return;
    _svg.style.transformOrigin = '0 0';

    var vp = document.getElementById('viewport');
    var drag = false, sx = 0, sy = 0;

    /* Wheel zoom centred on cursor */
    vp.addEventListener('wheel', function(e) {
      e.preventDefault();
      var r = vp.getBoundingClientRect();
      var mx = e.clientX - r.left;
      var my = e.clientY - r.top;
      var f = e.deltaY < 0 ? 1.1 : 0.9;
      var ns = _s * f;
      _tx = mx - (mx - _tx) * ns / _s;
      _ty = my - (my - _ty) * ns / _s;
      _s = ns;
      _apply();
    }, { passive: false });

    /* Mouse drag pan */
    vp.addEventListener('mousedown', function(e) {
      drag = true;
      sx = e.clientX - _tx;
      sy = e.clientY - _ty;
      vp.classList.add('dragging');
      e.preventDefault();
    });
    document.addEventListener('mousemove', function(e) {
      if (!drag) return;
      _tx = e.clientX - sx;
      _ty = e.clientY - sy;
      _apply();
    });
    document.addEventListener('mouseup', function() {
      drag = false;
      vp.classList.remove('dragging');
    });
  });
</script>
</body>
</html>
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
    html = (
        _MERMAID_TEMPLATE
        .replace("__BG__", bg)
        .replace("__THEME__", theme)
        .replace("__CODE__", escape(code))
    )

    with st_block(style) if style is not None else nullcontext():
        components.html(html, height=height, scrolling=True)

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
