"""LaTeX rendering — math formulas via Streamlit native, documents via LaTeX.js.

``st_latex()`` wraps Streamlit's built-in ``st.latex()`` for math formulas.

``st_latex_doc()`` renders full LaTeX documents or fragments using the
`LaTeX.js <https://latex.js.org/>`_ programmatic API loaded from CDN inside
a ``components.html()`` iframe.  Fragments (no ``\\documentclass``) are
automatically wrapped in a minimal ``\\documentclass{article}`` document
because LaTeX.js requires a full document structure to parse commands
like ``\\section``, ``\\begin{tabular}``, etc.

Zero system dependency — JavaScript runs client-side (same pattern as Mermaid).
"""

import json
from contextlib import nullcontext
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from .container import st_block
from .export import export_append, is_export_active
from .latex_utils import is_full_document
from .styles import Style

# ---------------------------------------------------------------------------
# LaTeX.js CDN and HTML template
# ---------------------------------------------------------------------------

_LATEX_JS_CDN = "https://cdn.jsdelivr.net/npm/latex.js@0.12.6/dist/"

# Uses the programmatic API (parse + HtmlGenerator) instead of the
# <latex-js> web component.  This gives proper error handling and avoids
# silent failures.  The LaTeX source is passed as a JSON-escaped JS string
# literal (__CODE__), which correctly preserves all backslashes and special
# characters without needing html.escape().
_LATEX_DOC_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; background: __BG__; overflow: auto; }
  #output { padding: 16px; min-height: 100%; }
  .stx-err { color: #c00; font-family: monospace; font-size: 13px;
             padding: 16px; white-space: pre-wrap; }
</style>
</head>
<body>
<div id="output"></div>
<script type="module">
var out = document.getElementById('output');
try {
  var m = await import('__CDN__latex.mjs');
  var gen = new m.HtmlGenerator({ hyphenate: __HYPHENATE__ });
  m.parse(__CODE__, { generator: gen });
  document.head.appendChild(gen.stylesAndScripts('__CDN__'));
  out.appendChild(gen.domFragment());
} catch (e) {
  out.innerHTML = '<div class="stx-err">LaTeX.js error: ' + e + '<\\/div>';
}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# st_latex — Math formulas (Streamlit native)
# ---------------------------------------------------------------------------


def st_latex(
    content: str = "",
    *,
    style: Style | None = None,
    file: str | None = None,
    encoding: str = "utf-8",
) -> None:
    """Render a LaTeX math formula via Streamlit's native ``st.latex()``.

    Parameters
    ----------
    content : str
        LaTeX math expression (e.g. ``r"E = mc^2"``).
    style : Style | None
        Optional StreamTeX style to wrap the formula in a styled container.
    file : str | None
        Path to a ``.tex`` file.  Resolved via ``resolve_static()``.
        Mutually exclusive with *content*.
    encoding : str
        File encoding (only used when *file* is provided).
    """
    from .utils import resolve_content

    text = resolve_content(content, file=file, encoding=encoding)
    if not text:
        return

    with st_block(style) if style is not None else nullcontext():
        st.latex(text)

    if is_export_active():
        export_append(
            f'<div class="stx-latex"><code>{escape(text)}</code></div>'
        )


# ---------------------------------------------------------------------------
# st_latex_doc — Full documents / fragments via LaTeX.js
# ---------------------------------------------------------------------------


def st_latex_doc(
    code: str = "",
    *,
    style: Style | None = None,
    light_bg: bool = True,
    height: int = 600,
    hyphenate: bool = True,
    file: str | None = None,
    encoding: str = "utf-8",
    **kw,
) -> None:
    """Render a LaTeX document or fragment via the LaTeX.js web component.

    Parameters
    ----------
    code : str
        LaTeX source code.  If this is a fragment (no ``\\documentclass``),
        it is automatically wrapped in a minimal ``article`` document
        because LaTeX.js requires a full document to parse structured
        commands (``\\section``, ``\\begin{tabular}``, etc.).
    style : Style | None
        Optional StreamTeX style to wrap the iframe in a styled container.
    light_bg : bool
        When True (default), render on a white background.
    height : int
        Height in pixels for the iframe.  Defaults to 600.
    hyphenate : bool
        Enable LaTeX.js hyphenation.  Defaults to True.
    file : str | None
        Path to a ``.tex`` file.  Resolved via ``resolve_static()``.
        Mutually exclusive with *code*.
    encoding : str
        File encoding (only used when *file* is provided).
    **kw
        Reserved for future use.
    """
    from .utils import resolve_content

    code = resolve_content(code, file=file, encoding=encoding)
    if not code:
        return

    # LaTeX.js requires a full document (\documentclass + \begin{document})
    # to parse structured commands (\section, \begin{tabular}, etc.).
    # Wrap fragments in a minimal article document automatically.
    if not is_full_document(code):
        code = (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            f"{code}\n"
            "\\end{document}"
        )

    bg = "#fff" if light_bg else "transparent"
    hyph = "true" if hyphenate else "false"
    # json.dumps produces a quoted JS string literal with proper escaping
    # of backslashes, quotes, newlines.  Replace </ to prevent premature
    # </script> closure (standard XSS prevention in inline scripts).
    js_code = json.dumps(code).replace("</", "<\\/")

    html = (
        _LATEX_DOC_TEMPLATE
        .replace("__CDN__", _LATEX_JS_CDN)
        .replace("__BG__", bg)
        .replace("__HYPHENATE__", hyph)
        .replace("__CODE__", js_code)
    )

    with st_block(style) if style is not None else nullcontext():
        components.html(html, height=height, scrolling=True)

    # --- Export rendering ---
    if is_export_active():
        export_append(
            f'<div class="stx-latex-doc">'
            f"<latex-js baseURL=\"{_LATEX_JS_CDN}\" "
            f"hyphenate=\"{hyph}\">"
            f"{escape(code)}"
            f"</latex-js></div>"
        )
