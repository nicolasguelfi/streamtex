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
    st_write(bs.heading, "Text & Styles", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Simple text ---
    st_write(bs.sub, "Simple Text", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        st_write(s.large, "Plain text in large size")
        st_write(s.bold + s.Large, "Bold text in Large size")
        st_write(s.italic + s.project.colors.accent, "Italic accent text")
    """))
    st_space("v", 1)

    st_write(s.large, "Plain text in large size")
    st_write(s.bold + s.Large, "Bold text in Large size")
    st_write(s.italic + s.project.colors.accent, "Italic accent text")
    st_space("v", 2)

    # --- Inline mixed styles ---
    st_write(bs.sub, "Inline Mixed Styles", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        st_write(s.large,
            "Normal ", (s.bold, "bold"), " and ",
            (s.italic + s.project.colors.primary, "italic blue"), " inline.")
    """))
    st_space("v", 1)

    st_write(s.large,
             "Normal ", (s.bold, "bold"), " and ",
             (s.italic + s.project.colors.primary, "italic blue"), " inline.")
    st_space("v", 2)

    # --- Links ---
    st_write(bs.sub, "Links", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        st_write(s.large, "Visit ",
            (s.project.colors.primary + s.large, "StreamTeX docs",
             "https://github.com/"), " for more.")
    """))
    st_space("v", 1)

    st_write(s.large, "Visit ",
             (s.project.colors.primary + s.large, "StreamTeX docs",
              "https://github.com/"), " for more.")
    st_space("v", 2)

    # --- Tags and TOC ---
    st_write(bs.sub, "HTML Tags & TOC Registration", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        st_write(s.huge + s.bold, "H1 Title", tag=t.h1, toc_lvl="1")
        st_write(s.Large + s.bold, "H2 Subtitle", tag=t.h2, toc_lvl="+1")
    """))
    st_space("v", 1)

    show_tip("Use toc_lvl=\"1\" for top-level entries and toc_lvl=\"+1\" for sub-levels.")
