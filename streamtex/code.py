import textwrap
from typing import Optional

from .export import _render
from .styles import StxStyles, Style
from .utils import generate_key

_WRAP_ALL_KEY = "_stx_wrap_all"

try:
    import streamlit as st
    _cache_code = st.cache_data(show_spinner=False)
except Exception:
    def _cache_code(f):  # no-op outside Streamlit (tests, CLI)
        return f


@_cache_code
def _highlight_code(code: str, language: str, line_numbers: bool,
                    font_size: str, line_start: int = 1) -> str:
    """Return Pygments-highlighted HTML for the given code.

    The result is cached by Streamlit based on (code, language,
    line_numbers, font_size, line_start) so that re-renders skip Pygments
    entirely.

    :param line_start: First line number displayed (Pygments ``linenostart``).
    """
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import TextLexer, get_lexer_by_name

        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except Exception:
            lexer = TextLexer(stripall=True)

        fmt_options = dict(
            noclasses=True,
            style="monokai",
        )
        if line_numbers:
            fmt_options["linenos"] = "table"
            fmt_options["linenostart"] = line_start

        formatter = HtmlFormatter(**fmt_options)
        return highlight(code, lexer, formatter)

    except ImportError:
        # Fallback: plain <pre> with optional line numbers
        lines = code.split("\n")
        if line_numbers:
            numbered = []
            for i, line in enumerate(lines, line_start):
                num = f"{i:>4} "
                numbered.append(f"{num}{line}")
            body = "\n".join(numbered)
        else:
            body = code
        return (
            f'<pre style="font-family: monospace; background-color: #272822; '
            f'color: #F8F8F2; padding: 12pt; border-radius: 6px; '
            f'overflow-x: auto; margin: 0; font-size: {font_size};'
            f' white-space: pre;">{body}</pre>'
        )


_CODE_SIZE_DEFAULT = "var(--stx-code-size, 18pt)"


def st_code(
    style: Style = StxStyles.none,
    code: str = "",
    language: str = "python",
    line_numbers: bool = True,
    font_size: str = _CODE_SIZE_DEFAULT,
    line_number_color: str = "#6A9BC5",
    wrap: Optional[bool] = None,
    file: str | None = None,
    encoding: str = "utf-8",
    line_start: int | None = None,
    start_line: int | None = None,
    end_line: int | None = None,
):
    """Renders syntax-highlighted code via st.html() using Pygments.

    :param style: A Style object for the outer container div.
    :param code: The source code string to display.
    :param language: The programming language for syntax highlighting.
    :param line_numbers: Whether to show line numbers.
    :param font_size: CSS font size for the code text.
        Defaults to the responsive CSS variable ``--stx-code-size``
        (desktop 18pt, tablet 14pt, mobile 11pt).
    :param line_number_color: CSS color for line numbers (default "#6A9BC5").
    :param wrap: Initial wrap state for this code block.  ``None`` (default)
        reads from the global sidebar toggle set by ``add_wrap_all_option()``
        (falls back to ``True``).  Pass ``True`` or ``False`` explicitly to
        override the global setting for a specific block.
    :param file: Path to a source file.  Resolved via ``resolve_static()`` so
        that relative paths search configured static source directories.
        Mutually exclusive with *code*.
    :param encoding: File encoding (only used when *file* is provided).
    :param line_start: First line number displayed (Pygments ``linenostart``).
        When ``None`` and ``start_line`` is set, defaults to ``start_line``
        (absolute numbering).  Set to ``1`` for relative numbering.
    :param start_line: 1-based first line to extract from content.
    :param end_line: 1-based last line to extract from content (inclusive).
    """
    from .utils import resolve_content

    code = resolve_content(code, file=file, encoding=encoding)
    if not file:
        code = textwrap.dedent(code).strip()

    # Line extraction
    if start_line or end_line:
        lines = code.splitlines()
        s = (start_line or 1) - 1
        e = end_line or len(lines)
        code = "\n".join(lines[s:e])

    # line_start default: absolute numbering when start_line is given
    if line_start is None:
        line_start = start_line if start_line else 1

    # Resolve wrap: explicit > global session state > True
    if wrap is None:
        try:
            wrap = st.session_state.get(_WRAP_ALL_KEY, True)
        except Exception:
            wrap = True

    highlighted = _highlight_code(code, language, line_numbers, font_size,
                                   line_start)

    uid = generate_key("stx-wrap")

    line_no_css = ""
    if line_numbers and line_number_color:
        line_no_css = (
            f"<style>"
            f".linenodiv pre span {{ color: {line_number_color} !important; }}"
            f".linenodiv pre {{ color: {line_number_color}; }}"
            f"</style>"
        )

    checked_attr = " checked" if wrap else ""

    lineno_nowrap_css = (
        f"#stx-wrap-{uid}:checked ~ .stx-code-{uid} .linenodiv pre {{"
        f" white-space: pre !important;"
        f" word-break: normal !important;"
        f" overflow-wrap: normal !important;"
        f" min-width: 2.5em;"
        f"}}"
    ) if line_numbers else ""

    toggle_css = (
        f"<style>"
        f"#stx-wrap-{uid} {{ display: none; }}"
        f"#stx-wrap-{uid}:checked ~ .stx-code-{uid} pre {{"
        f" white-space: pre-wrap !important;"
        f" word-break: break-word !important;"
        f" overflow-wrap: break-word !important;"
        f"}}"
        f"{lineno_nowrap_css}"
        f".stx-wlbl-{uid} {{"
        f" position: absolute; top: 4px; right: 8px;"
        f" cursor: pointer; z-index: 10;"
        f" padding: 2px 8px; border-radius: 3px;"
        f" background: rgba(255,255,255,0.1);"
        f" color: #888; font-size: 11px;"
        f" font-family: sans-serif; user-select: none;"
        f"}}"
        f".stx-wlbl-{uid}:hover {{ background: rgba(255,255,255,0.2); color: #ccc; }}"
        f"#stx-wrap-{uid}:checked ~ .stx-code-{uid} .stx-wlbl-{uid} {{"
        f" color: #6A9BC5; background: rgba(106,155,197,0.15);"
        f"}}"
        f"</style>"
    )

    container_style = (
        f"{style}; text-align: left; width: 0; min-width: 100%; overflow-x: auto; "
        f"color: #F8F8F2; font-size: {font_size};"
    )

    final_html = (
        f'{line_no_css}'
        f'{toggle_css}'
        f'<input type="checkbox" id="stx-wrap-{uid}"{checked_attr} />'
        f'<div class="stx-code-{uid}" style="position: relative;">'
        f'<label for="stx-wrap-{uid}" class="stx-wlbl-{uid}">wrap</label>'
        f'<div style="{container_style}">{highlighted}</div>'
        f'</div>'
    )
    _render(final_html)


def add_wrap_all_option(default: bool = True, container=None):
    """Adds a **Wrap All** toggle to the sidebar.

    When toggled, all code blocks rendered by ``st_code()`` will use
    the new wrap state on the next Streamlit re-render.  Individual
    per-block "wrap" buttons still work for fine-grained control within
    a single render cycle.

    :param default: Initial state of the toggle (default ``True``).
    :param container: Streamlit container to render into (default: sidebar).
    """
    if _WRAP_ALL_KEY not in st.session_state:
        st.session_state[_WRAP_ALL_KEY] = default

    ctx = container if container is not None else st.sidebar
    ctx.toggle("Wrap All", key=_WRAP_ALL_KEY)
