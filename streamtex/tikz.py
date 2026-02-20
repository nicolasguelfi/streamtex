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


def _extract_svg_height(svg: str) -> int:
    """Extract the height in pixels from a processed SVG string.

    Returns a pixel value suitable for ``_render(height=...)``, with a
    small padding to avoid clipping.  Falls back to 400 if parsing fails.
    """
    m = re.search(r"<svg[^>]*\bheight=['\"](\d[\d.]*)", svg)
    if m:
        return int(float(m.group(1))) + 20  # padding for iframe border
    return 400


def st_tikz(code: str, *, style: Style | None = None, preamble: str = "") -> None:
    """Render a TikZ diagram.

    Parameters
    ----------
    code : str
        The TikZ source code (everything between ``\\begin{document}`` and
        ``\\end{document}`` is handled automatically).
    style : Style | None
        Optional StreamTeX style to wrap the diagram in a styled container.
    preamble : str
        Extra LaTeX preamble lines (e.g. ``\\usepackage{pgfplots}``).
    """
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
            html = f'<div class="stx-tikz" style="background:#fff;padding:8px;display:inline-block">{svg}</div>'
            _render(html, height=_extract_svg_height(svg))
        elif is_export_active():
            export_append(f'<pre class="stx-tikz">{escape(code)}</pre>')
