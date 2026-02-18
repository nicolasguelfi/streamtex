import streamlit as st
from .styles import Style, StreamTeX_Styles
from .export import _render


def st_code(
    style: Style = StreamTeX_Styles.none,
    code: str = "",
    language: str = "python",
    line_numbers: bool = True,
    font_size: str = "20pt",
    line_number_color: str = "#6A9BC5",
):
    """Renders syntax-highlighted code via st.html() using Pygments.

    :param style: A Style object for the outer container div.
    :param code: The source code string to display.
    :param language: The programming language for syntax highlighting.
    :param line_numbers: Whether to show line numbers.
    :param font_size: CSS font size for the code text (default "20pt").
    :param line_number_color: CSS color for line numbers (default "#6A9BC5").
    """
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, TextLexer
        from pygments.formatters import HtmlFormatter

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
        highlighted = highlight(code, lexer, formatter)

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
        highlighted = (
            f'<pre style="font-family: monospace; background-color: #272822; '
            f'color: #F8F8F2; padding: 12pt; border-radius: 6px; '
            f'overflow-x: auto; margin: 0; font-size: {font_size};">{body}</pre>'
        )

    line_no_css = ""
    if line_numbers and line_number_color:
        line_no_css = (
            f"<style>"
            f".linenodiv pre span {{ color: {line_number_color} !important; }}"
            f".linenodiv pre {{ color: {line_number_color}; }}"
            f"</style>"
        )

    container_style = (
        f"{style}; text-align: left; overflow-x: auto; "
        f"color: #F8F8F2; font-size: {font_size};"
    )
    final_html = f'{line_no_css}<div style="{container_style}">{highlighted}</div>'
    _render(final_html)
