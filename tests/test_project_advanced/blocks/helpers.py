"""Shared helper functions for block files. No build() — ignored by st_include."""

from streamtex import st_write, st_block, st_space, st_br
import streamtex as sx
from custom.styles import Styles as s


def show_code(code_string, language="python", line_numbers=True):
    """Centered styled box with syntax-highlighted code — uses native st_code()."""
    sx.st_code(s.project.containers.code_box, code=code_string,
               language=language, line_numbers=line_numbers)


def show_code_inline(code_string, language="python", line_numbers=True):
    """Code display without box wrapper — for use inside callout containers."""
    sx.st_code(code=code_string, language=language, line_numbers=line_numbers)


def show_explanation(text):
    """Styled explanation box before an example.

    Pass a multi-line string (use textwrap.dedent). Each non-empty line
    is rendered on its own line for readability.
    """
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    with st_block(s.project.containers.explanation_box):
        st_write(s.project.titles.explanation_label, "Purpose")
        st_space("v", 1)
        for i, line in enumerate(lines):
            st_write(s.large, line)
            if i < len(lines) - 1:
                st_br()


def show_details(text):
    """'Details:' section with summary + expanded text.

    Pass a multi-line string (use textwrap.dedent). The first line becomes
    the bold summary; subsequent lines are detail text.
    """
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    with st_block(s.project.containers.details_box):
        st_write(s.project.titles.details_label, "Details:")
        st_space("v", 1)
        if lines:
            st_write(s.large + s.bold, lines[0])
            if len(lines) > 1:
                st_space("v", 1)
                for i, line in enumerate(lines[1:]):
                    st_write(s.large, line)
                    if i < len(lines) - 2:
                        st_br()
