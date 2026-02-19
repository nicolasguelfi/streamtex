"""Shared helper functions for block files. No build() — ignored by st_include."""

import streamtex as sx
from streamtex import st_write, st_block, st_space
from custom.styles import Styles as s


def show_code(code_string, language="python", line_numbers=True):
    """Centered styled box with syntax-highlighted code."""
    sx.st_code(s.project.containers.code_box, code=code_string,
               language=language, line_numbers=line_numbers)


def show_tip(text):
    """Styled callout box for tips and explanations."""
    with st_block(s.project.containers.callout):
        st_write(s.project.titles.section_subtitle, "Tip")
        st_space("v", 1)
        for line in text.strip().splitlines():
            line = line.strip()
            if line:
                st_write(s.large, line)
