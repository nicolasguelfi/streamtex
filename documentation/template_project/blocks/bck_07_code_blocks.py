import streamlit as st
from streamtex import *
import streamtex as sx
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
        sx.st_code(code=\"\"\"
        def greet(name):
            return f"Hello, {name}!"
        \"\"\", language="python", line_numbers=True)
    """))
    st_space("v", 1)

    sx.st_code(code=textwrap.dedent("""\
        def greet(name):
            return f"Hello, {name}!"
    """), language="python", line_numbers=True)
    st_space("v", 2)

    # --- Styled code box ---
    st_write(bs.sub, "Styled Code Box", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        sx.st_code(s.project.containers.code_box,
                   code="SELECT * FROM users WHERE active = true;",
                   language="sql", line_numbers=False)
    """))
    st_space("v", 1)

    sx.st_code(s.project.containers.code_box,
               code="SELECT * FROM users WHERE active = true;",
               language="sql", line_numbers=False)
    st_space("v", 2)

    # --- Helper pattern ---
    st_write(bs.sub, "Reusable show_code() Helper", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # In blocks/helpers.py:
        def show_code(code_string, language="python", line_numbers=True):
            sx.st_code(s.project.containers.code_box, code=code_string,
                       language=language, line_numbers=line_numbers)

        # In any block:
        from blocks.helpers import show_code
        show_code("print('Hello')")
    """))
    st_space("v", 2)

    show_tip(
        "sx.st_code() uses Pygments for syntax highlighting. "
        "Wrap it in a styled container for consistent presentation. "
        "The helpers.show_code() pattern keeps blocks DRY."
    )
