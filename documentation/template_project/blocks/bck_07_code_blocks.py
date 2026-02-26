import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_tip
import textwrap


class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    st_write(bs.heading, "Code Blocks", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Basic code ---
    st_write(bs.sub, "Syntax-Highlighted Code", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        stx.st_code(code=\"\"\"
        def greet(name):
            return f"Hello, {name}!"
        \"\"\", language="python", line_numbers=True)
    """))
    st_space("v", 1)

    stx.st_code(code=textwrap.dedent("""\
        def greet(name):
            return f"Hello, {name}!"
    """), language="python", line_numbers=True)
    st_space("v", 2)

    # --- Styled code box ---
    st_write(bs.sub, "Styled Code Box", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        stx.st_code(s.project.containers.code_box,
                   code="SELECT * FROM users WHERE active = true;",
                   language="sql", line_numbers=False)
    """))
    st_space("v", 1)

    stx.st_code(s.project.containers.code_box,
               code="SELECT * FROM users WHERE active = true;",
               language="sql", line_numbers=False)
    st_space("v", 2)

    # --- Line wrapping ---
    st_write(bs.sub, "Line Wrapping (wrap parameter)", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large,
             "Use ", (s.bold, "wrap=True"),
             " for content where horizontal alignment doesn't matter "
             "(JSON, logs, long strings). Lines wrap instead of scrolling.")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # Default: wrap=False — horizontal scroll for long lines
        stx.st_code(code="long line...", language="python")

        # wrap=True — lines wrap on narrow screens
        stx.st_code(code='{"key": "value", "nested": {...}}',
                   language="json", wrap=True)
    """))
    st_space("v", 1)

    stx.st_code(s.project.containers.code_box,
                code='{"project": "StreamTeX", "version": "0.2.0", "description": "A Python library on top of Streamlit for styled content rendering with responsive design"}',
                language="json", wrap=True)
    st_space("v", 2)

    # --- Responsive font size ---
    st_write(bs.sub, "Responsive Font Size", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large,
             "Code blocks use the CSS variable ", (s.bold, "--stx-code-size"),
             " which adapts to screen size automatically:")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # Responsive sizing (automatic, no code needed):
        #   Desktop  → 18pt
        #   Tablet   → 14pt  (≤1024px)
        #   Mobile   → 11pt  (≤480px)

        # Override with explicit font_size if needed:
        stx.st_code(code="print('small')", font_size="12pt")
    """))
    st_space("v", 2)

    # --- Helper pattern ---
    st_write(bs.sub, "Reusable show_code() Helper", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # In blocks/helpers.py:
        def show_code(code_string, language="python",
                     line_numbers=True, wrap=False):
            stx.st_code(s.project.containers.code_box, code=code_string,
                       language=language, line_numbers=line_numbers, wrap=wrap)

        # In any block:
        from blocks.helpers import show_code
        show_code("print('Hello')")
        show_code('{"key": "value"}', language="json", wrap=True)
    """))
    st_space("v", 2)

    show_tip(
        "stx.st_code() uses Pygments for syntax highlighting. "
        "Font size adapts automatically to screen size via --stx-code-size. "
        "Use wrap=True for JSON/logs, wrap=False (default) for aligned code."
    )
