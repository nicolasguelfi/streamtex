"""PlantUML diagram rendering — server-side SVG via HTTP + HTML export.

Live rendering fetches SVG from a PlantUML server (public by default,
configurable) and displays it inside a ``components.html()`` iframe with
interactive pan (click + drag) and zoom (mouse wheel) controls — same UX
as the Mermaid renderer.

Export rendering uses the same HTTP fetch and injects the SVG into the
HTML export buffer, with a graceful ``<pre>`` fallback on failure.

No external Python dependency is needed — encoding uses stdlib only
(``zlib`` + custom base64 alphabet).
"""

import urllib.request
import zlib
from contextlib import nullcontext
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from .container import st_block
from .export import export_append, is_export_active
from .styles import Style

# ---------------------------------------------------------------------------
# PlantUML text encoding (UTF-8 → zlib deflate → custom base64)
#
# The PlantUML server expects a custom base64 alphabet:
#   0-9 → '0'-'9', 10-35 → 'A'-'Z', 36-61 → 'a'-'z', 62 → '-', 63 → '_'
# ---------------------------------------------------------------------------

_PLANTUML_ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
)


def _encode3(b1: int, b2: int, b3: int) -> str:
    """Encode 3 bytes into 4 PlantUML base64 characters."""
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return (
        _PLANTUML_ALPHABET[c1]
        + _PLANTUML_ALPHABET[c2]
        + _PLANTUML_ALPHABET[c3]
        + _PLANTUML_ALPHABET[c4]
    )


def _encode(code: str) -> str:
    """Encode PlantUML source text for use in a server URL."""
    data = zlib.compress(code.encode("utf-8"))[2:-4]  # raw deflate
    result = []
    for i in range(0, len(data), 3):
        if i + 2 < len(data):
            result.append(_encode3(data[i], data[i + 1], data[i + 2]))
        elif i + 1 < len(data):
            result.append(_encode3(data[i], data[i + 1], 0))
        else:
            result.append(_encode3(data[i], 0, 0))
    return "".join(result)


# ---------------------------------------------------------------------------
# SVG fetch from PlantUML server (cached)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _fetch_svg(code: str, server: str) -> str:
    """Fetch SVG from a PlantUML server. Raises on network failure."""
    encoded = _encode(code)
    url = f"{server.rstrip('/')}/svg/{encoded}"
    req = urllib.request.Request(url, headers={
        "Accept": "image/svg+xml",
        "User-Agent": "StreamTeX/0.2",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


# ---------------------------------------------------------------------------
# HTML template for live rendering (pan + zoom, same UX as Mermaid)
# ---------------------------------------------------------------------------

_PLANTUML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
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
<div id="viewport">__SVG__</div>
<div id="controls">
  <button onclick="zoomIn()" title="Zoom in">+</button>
  <button onclick="resetView()" title="Reset">Reset</button>
  <button onclick="zoomOut()" title="Zoom out">&minus;</button>
</div>
<script>
  var _s = 1, _tx = 0, _ty = 0;
  var _svg = document.querySelector('#viewport svg');

  function _apply() {
    if (!_svg) return;
    _svg.style.transform = 'translate(' + _tx + 'px,' + _ty + 'px) scale(' + _s + ')';
  }
  function zoomIn()    { _s *= 1.2; _apply(); }
  function zoomOut()   { _s /= 1.2; _apply(); }
  function resetView() { _s = 1; _tx = 0; _ty = 0; _apply(); }

  if (_svg) {
    _svg.style.transformOrigin = '0 0';
    var vp = document.getElementById('viewport');
    var drag = false, sx = 0, sy = 0;

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
  }
</script>
</body>
</html>
"""


def st_plantuml(
    code: str,
    *,
    style: Style | None = None,
    light_bg: bool = True,
    height: int = 500,
    server: str = "https://www.plantuml.com/plantuml",
    **kw,
) -> None:
    """Render a PlantUML diagram.

    Parameters
    ----------
    code : str
        The PlantUML diagram source code (including @startuml/@enduml).
    style : Style | None
        Optional StreamTeX style to wrap the diagram in a styled container.
    light_bg : bool
        When True (default), render the diagram on a white background.
        Set to False to use a transparent background.
    height : int
        Height in pixels for the diagram iframe.  Defaults to 500.
    server : str
        PlantUML server URL.  Defaults to the public server.
    """
    bg = "#fff" if light_bg else "transparent"

    with st_block(style) if style is not None else nullcontext():
        try:
            svg = _fetch_svg(code, server)
            html = (
                _PLANTUML_TEMPLATE
                .replace("__BG__", bg)
                .replace("__SVG__", svg)
            )
            components.html(html, height=height, scrolling=True)
        except Exception:
            st.warning(
                "PlantUML server unreachable — showing raw source. "
                "Check your network or configure a local server."
            )
            st.code(code, language="text")

    # --- Export rendering ---
    if is_export_active():
        try:
            svg = _fetch_svg(code, server)
            export_append(f'<div class="stx-plantuml">{svg}</div>')
        except Exception:
            export_append(f'<pre class="stx-plantuml">{escape(code)}</pre>')
