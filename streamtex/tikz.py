"""TikZ diagram rendering — LaTeX pipeline + HTML export as SVG.

Pipeline: TikZ source → ``.tex`` file → ``latex`` (DVI) → ``dvisvgm`` → SVG.
Live rendering displays the SVG via ``_render()`` inside a styled container.
Export injects the SVG into the HTML buffer.

LaTeX (``latex`` and ``dvisvgm``) is an **optional** system dependency.
When absent, a warning is shown and the raw TikZ source is displayed as a
``<pre>`` block (graceful fallback).
"""

import glob
import os
import re
import subprocess
import tempfile
from contextlib import nullcontext
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from .container import st_block
from .export import _render, export_append, is_export_active
from .styles import Style


def _find_libgs() -> str | None:
    """Auto-detect the Ghostscript shared library path.

    dvisvgm needs libgs to process PostScript specials (used by TikZ).
    Returns the path if found, or None.
    """
    # Already set by user
    if os.environ.get("LIBGS"):
        return os.environ["LIBGS"]

    # Common locations per platform
    candidates = [
        # macOS Homebrew (Apple Silicon / Intel)
        "/opt/homebrew/lib/libgs.dylib",
        "/usr/local/lib/libgs.dylib",
        # Linux
        "/usr/lib/libgs.so",
        "/usr/lib/x86_64-linux-gnu/libgs.so",
        "/usr/lib/aarch64-linux-gnu/libgs.so",
    ]
    # Also try versioned Linux libs
    candidates.extend(glob.glob("/usr/lib/libgs.so.*"))
    candidates.extend(glob.glob("/usr/lib/*/libgs.so.*"))

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


@st.cache_data(show_spinner=False)
def _compile_tikz(code: str, preamble: str) -> str:
    """Compile TikZ *code* to SVG via latex + dvisvgm.

    Returns the SVG string on success, or raises ``RuntimeError`` /
    ``FileNotFoundError`` on failure.
    """
    tex_content = (
        "\\documentclass[tikz,border=2pt]{standalone}\n"
        f"{preamble}\n"
        "\\begin{document}\n"
        f"{code}\n"
        "\\end{document}\n"
    )

    with tempfile.TemporaryDirectory(prefix="stx_tikz_") as tmpdir:
        tex_path = os.path.join(tmpdir, "diagram.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)

        # Step 1: latex → DVI
        subprocess.run(
            ["latex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
            capture_output=True,
            check=True,
            timeout=30,
        )

        dvi_path = os.path.join(tmpdir, "diagram.dvi")
        svg_path = os.path.join(tmpdir, "diagram.svg")

        # Step 2: dvisvgm → SVG (needs libgs for TikZ PostScript specials)
        env = os.environ.copy()
        libgs = _find_libgs()
        if libgs:
            env["LIBGS"] = libgs

        subprocess.run(
            ["dvisvgm", "--no-fonts", "--exact-bbox", "-o", svg_path, dvi_path],
            capture_output=True,
            check=True,
            timeout=30,
            env=env,
        )

        with open(svg_path, encoding="utf-8") as f:
            return _make_svg_responsive(f.read())


_PT_RE = re.compile(r"([\d.]+)pt")
_SCALE = 2.0  # scale factor applied to pt → px conversion (1pt ≈ 1.333px)


def _pt_to_px(match: re.Match) -> str:
    """Convert a ``NNpt`` value to pixels, scaled for comfortable display."""
    return f"{float(match.group(1)) * 1.333 * _SCALE:.2f}"


def _make_svg_responsive(svg: str) -> str:
    """Convert fixed ``pt`` dimensions to ``px`` on the SVG root element.

    dvisvgm outputs ``width`` and ``height`` in ``pt`` units.  Streamlit's
    ``st.html()`` Shadow DOM cannot auto-size from ``pt``, so we convert
    to explicit pixel values.  A scale factor is applied for readability.
    """
    def _replace_dim(attr: str, svg_str: str) -> str:
        pat = re.compile(rf"(<svg\b[^>]*?\b{attr}=)(['\"])([^'\"]*?)\2")
        m = pat.search(svg_str)
        if not m:
            return svg_str
        raw = m.group(3)  # e.g. "108.183349pt"
        px = _PT_RE.sub(_pt_to_px, raw)
        return pat.sub(rf"\g<1>\g<2>{px}\g<2>", svg_str, count=1)

    svg = _replace_dim("width", svg)
    svg = _replace_dim("height", svg)
    return svg


_TIKZ_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; background: __BG__; overflow: hidden; }
  #viewport {
    width: 100%; height: calc(100% - 32px);
    overflow: hidden; cursor: grab;
    display: flex; justify-content: start; align-items: start;
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
  var _s = 1, _tx = 0, _ty = 0, _fitS = 1, _fitTx = 0, _fitTy = 0;
  var _svg = document.querySelector('#viewport svg');

  function _apply() {
    if (!_svg) return;
    _svg.style.transform = 'translate(' + _tx + 'px,' + _ty + 'px) scale(' + _s + ')';
  }
  function zoomIn()    { _s *= 1.2; _apply(); }
  function zoomOut()   { _s /= 1.2; _apply(); }
  function resetView() { _s = _fitS; _tx = _fitTx; _ty = _fitTy; _apply(); }

  function _autoFit() {
    if (!_svg) return;
    var vp = document.getElementById('viewport');
    var vw = vp.clientWidth, vh = vp.clientHeight;
    var sw = _svg.getAttribute('width'), sh = _svg.getAttribute('height');
    if (!sw || !sh) {
      var bb = _svg.getBBox();
      sw = bb.width; sh = bb.height;
    } else {
      sw = parseFloat(sw); sh = parseFloat(sh);
    }
    if (!sw || !sh) return;
    var scaleX = vw / sw, scaleY = vh / sh;
    _fitS = Math.min(scaleX, scaleY);
    _fitTx = (vw - sw * _fitS) / 2;
    _fitTy = (vh - sh * _fitS) / 2;
    _s = _fitS; _tx = _fitTx; _ty = _fitTy;
    _apply();
  }

  if (_svg) {
    _svg.style.transformOrigin = '0 0';
    _autoFit();

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


def _extract_svg_height(svg: str) -> int:
    """Extract the height in pixels from a processed SVG string.

    Returns a pixel value suitable for ``_render(height=...)``, with a
    small padding to avoid clipping.  Falls back to 400 if parsing fails.
    """
    m = re.search(r"<svg[^>]*\bheight=['\"](\d[\d.]*)", svg)
    if m:
        return int(float(m.group(1))) + 20  # padding for iframe border
    return 400


def st_tikz(
    code: str = "",
    *,
    style: Style | None = None,
    light_bg: bool = True,
    height: int | None = None,
    preamble: str = "",
    file: str | None = None,
    encoding: str = "utf-8",
) -> None:
    """Render a TikZ diagram.

    Parameters
    ----------
    code : str
        The TikZ source code (everything between ``\\begin{document}`` and
        ``\\end{document}`` is handled automatically).
    style : Style | None
        Optional StreamTeX style to wrap the diagram in a styled container.
    light_bg : bool
        When True (default), render the SVG on a white background so it
        stays readable on dark-mode pages.  Set to False to let the
        diagram follow the page theme.
    height : int | None
        Height in pixels for the display area.  When None (default), the
        height is auto-calculated from the compiled SVG.
    preamble : str
        Extra LaTeX preamble lines (e.g. ``\\usepackage{pgfplots}``).
    file : str | None
        Path to a ``.tex`` file.  Resolved via ``resolve_static()`` so that
        relative paths search configured static source directories.
        Mutually exclusive with *code*.
    encoding : str
        File encoding (only used when *file* is provided).
    """
    from .utils import resolve_content

    code = resolve_content(code, file=file, encoding=encoding)
    with st_block(style) if style is not None else nullcontext():
        svg: str | None = None

        try:
            svg = _compile_tikz(code, preamble)
        except FileNotFoundError:
            st.warning(
                "LaTeX not found — install `latex` and `dvisvgm` "
                "for TikZ rendering."
            )
            st.code(code, language="latex")
        except Exception as exc:
            st.error(f"TikZ compilation failed: {exc}")
            st.code(code, language="latex")

        # --- Live + export rendering ---
        if svg is not None:
            if height is not None:
                # Explicit height: use pan/zoom JS template (same UX as Mermaid/PlantUML)
                bg = "#fff" if light_bg else "transparent"
                html = (
                    _TIKZ_TEMPLATE
                    .replace("__BG__", bg)
                    .replace("__SVG__", svg)
                )
                components.html(html, height=height, scrolling=True)
            else:
                if light_bg:
                    css = "background:#fff;padding:8px;text-align:center"
                else:
                    css = "padding:8px;text-align:center"
                h = _extract_svg_height(svg)
                html = f'<div class="stx-tikz" style="{css}">{svg}</div>'
                _render(html, height=h, light_bg=light_bg)
        elif is_export_active():
            export_append(f'<pre class="stx-tikz">{escape(code)}</pre>')
