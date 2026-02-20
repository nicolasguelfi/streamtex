"""TikZ diagram rendering — LaTeX pipeline + HTML export as SVG.

Pipeline: TikZ source → ``.tex`` file → ``pdflatex`` → ``dvisvgm`` → SVG.
Live rendering displays the SVG via ``st.html()`` inside a styled container.
Export injects the SVG into the HTML buffer.

LaTeX (``pdflatex`` and ``dvisvgm``) is an **optional** system dependency.
When absent, a warning is shown and the raw TikZ source is displayed as a
``<pre>`` block (graceful fallback).
"""

import os
import subprocess
import tempfile
from html import escape

import streamlit as st

from .export import _render, export_append, is_export_active


@st.cache_data(show_spinner=False)
def _compile_tikz(code: str, preamble: str) -> str:
    """Compile TikZ *code* to SVG via pdflatex + dvisvgm.

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

        # Step 1: pdflatex → PDF
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
            capture_output=True,
            check=True,
            timeout=30,
        )

        pdf_path = os.path.join(tmpdir, "diagram.pdf")
        svg_path = os.path.join(tmpdir, "diagram.svg")

        # Step 2: pdf2svg or dvisvgm → SVG
        subprocess.run(
            ["dvisvgm", "--pdf", "--no-fonts", "--exact-bbox", "-o", svg_path, pdf_path],
            capture_output=True,
            check=True,
            timeout=30,
        )

        with open(svg_path, encoding="utf-8") as f:
            return f.read()


def st_tikz(code: str, *, preamble: str = "", dpi: int = 300) -> None:
    """Render a TikZ diagram.

    Parameters
    ----------
    code : str
        The TikZ source code (everything between ``\\begin{document}`` and
        ``\\end{document}`` is handled automatically).
    preamble : str
        Extra LaTeX preamble lines (e.g. ``\\usepackage{pgfplots}``).
    dpi : int
        Resolution hint (currently unused, reserved for future rasterisation).
    """
    svg: str | None = None

    try:
        svg = _compile_tikz(code, preamble)
    except FileNotFoundError:
        st.warning(
            "LaTeX not found — install `pdflatex` and `dvisvgm` "
            "for TikZ rendering."
        )
        st.code(code, language="latex")
    except Exception as exc:
        st.error(f"TikZ compilation failed: {exc}")
        st.code(code, language="latex")

    # --- Live + export rendering ---
    if svg is not None:
        _render(f'<div class="stx-tikz">{svg}</div>')
    elif is_export_active():
        export_append(f'<pre class="stx-tikz">{escape(code)}</pre>')
