import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """TOC demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Table of Contents Configuration",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # TOCConfig fields
        st_write(bs.sub, "TOCConfig fields", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Configure the Table of Contents
            with TOCConfig in book.py.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            toc = TOCConfig(
                numerate_titles=False,
                toc_position=0,
                title_style=s.project.titles.course_title + s.center_txt,
                content_style=s.large + s.text.colors.reset
            )
        """))
        st_space("v", 1)

        with st_grid(cols=2, cell_styles=bs.cell) as g:
            # header
            with g.cell(): st_write(s.bold + s.large, "Field")
            with g.cell(): st_write(s.bold + s.large, "Description")
            # row 1
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "numerate_titles")
            with g.cell():
                st_write(s.large,
                         "True = numbered (1.1, 1.2...),")
                st_br()
                st_write(s.large, "False = plain text")
            # row 2
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "toc_position")
            with g.cell():
                st_write(s.large,
                         "Index in block list where TOC renders.")
                st_br()
                st_write(s.large,
                         "-1 = end, 0 = start, None = no inline TOC")
            # row 3
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "title_style")
            with g.cell():
                st_write(s.large, "Style for the TOC heading")
            # row 4
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "content_style")
            with g.cell():
                st_write(s.large, "Style for TOC entry links")
        st_space("v", 2)

        # Absolute vs relative levels
        st_write(bs.sub, "toc_lvl: absolute vs relative", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Register text in the TOC
            with absolute or relative level numbers.
        """))
        st_space("v", 1)

        with st_grid(cols="1fr 1fr 1fr", cell_styles=bs.cell) as g:
            # header
            with g.cell(): st_write(s.bold + s.large, "Syntax")
            with g.cell(): st_write(s.bold + s.large, "Type")
            with g.cell(): st_write(s.bold + s.large, "Meaning")
            # row 1
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         'toc_lvl="1"')
            with g.cell(): st_write(s.large, "Absolute")
            with g.cell(): st_write(s.large, "Top-level section")
            # row 2
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         'toc_lvl="2"')
            with g.cell(): st_write(s.large, "Absolute")
            with g.cell(): st_write(s.large, "Second-level section")
            # row 3
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         'toc_lvl="+1"')
            with g.cell(): st_write(s.large, "Relative")
            with g.cell(): st_write(s.large, "One level deeper")
            # row 4
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         'toc_lvl="-1"')
            with g.cell(): st_write(s.large, "Relative")
            with g.cell(): st_write(s.large, "One level shallower")
        st_space("v", 2)

        # label parameter
        st_write(bs.sub, "The label parameter", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Provide a custom short string for the sidebar TOC entry.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.huge, "Very Long Title...",
                     toc_lvl="2", label="Short Title")
        """))
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Use absolute levels for major sections.
            Use relative levels (+1, -1) for subsections within a block.
        """))
