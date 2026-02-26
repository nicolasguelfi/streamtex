from .export import _render
from .styles import StxStyles, Style

try:
    import streamlit as st
    _cache_code = st.cache_data(show_spinner=False)
except Exception:
    def _cache_code(f):  # no-op outside Streamlit (tests, CLI)
        return f


@_cache_code
def _highlight_code(code: str, language: str, line_numbers: bool,
                    font_size: str) -> str:
    """Return Pygments-highlighted HTML for the given code.

    The result is cached by Streamlit based on (code, language,
    line_numbers, font_size) so that re-renders skip Pygments entirely.
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

        formatter = HtmlFormatter(**fmt_options)
        return highlight(code, lexer, formatter)

    except ImportError:
        # Fallback: plain <pre> with optional line numbers
        lines = code.split("\n")
        if line_numbers:
            numbered = []
            for i, line in enumerate(lines, 1):
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
    wrap: bool = False,
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
    :param wrap: When True, long lines wrap instead of scrolling horizontally.
        Useful for JSON, logs, or prose-like code.  Keep False (default) for
        code where horizontal alignment matters (tables, diffs).
    """
    highlighted = _highlight_code(code, language, line_numbers, font_size)

    line_no_css = ""
    if line_numbers and line_number_color:
        line_no_css = (
            f"<style>"
            f".linenodiv pre span {{ color: {line_number_color} !important; }}"
            f".linenodiv pre {{ color: {line_number_color}; }}"
            f"</style>"
        )

    wrap_css = (
        "white-space: pre-wrap; word-break: break-word; overflow-wrap: break-word;"
        if wrap
        else ""
    )

    container_style = (
        f"{style}; text-align: left; overflow-x: auto; "
        f"color: #F8F8F2; font-size: {font_size}; {wrap_css}"
    )
    final_html = f'{line_no_css}<div style="{container_style}">{highlighted}</div>'
    _render(final_html)
