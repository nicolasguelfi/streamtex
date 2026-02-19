import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Grid basics styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.center_txt
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Grid Basics", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Integer cols
        st_write(bs.sub, "st_grid with integer columns", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pass an integer to cols for equal-width columns.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_grid(cols=3, cell_styles=bs.cell) as g:
                with g.cell(): st_write(s.large, "Cell A1")
                with g.cell(): st_write(s.large, "Cell B1")
                with g.cell(): st_write(s.large, "Cell C1")
        """))
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=bs.cell) as g:
            with g.cell(): st_write(s.large, "Cell A1")
            with g.cell(): st_write(s.large, "Cell B1")
            with g.cell(): st_write(s.large, "Cell C1")
            with g.cell(): st_write(s.large, "Cell A2")
            with g.cell(): st_write(s.large, "Cell B2")
            with g.cell(): st_write(s.large, "Cell C2")
        st_space("v", 2)

        # String cols
        st_write(bs.sub, "st_grid with string columns", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pass a CSS grid-template-columns string for custom widths.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_grid(cols="1fr 2fr", cell_styles=bs.cell) as g:
                with g.cell(): st_write(s.large, "Narrow (1fr)")
                with g.cell(): st_write(s.large, "Wide (2fr)")
        """))
        st_space("v", 1)

        with st_grid(cols="1fr 2fr", cell_styles=bs.cell) as g:
            with g.cell(): st_write(s.large, "Narrow (1fr)")
            with g.cell(): st_write(s.large, "Wide (2fr)")
            with g.cell(): st_write(s.large, "Sidebar")
            with g.cell(): st_write(s.large, "Main content area takes more space")
        st_space("v", 2)

        # grid_style
        st_write(bs.sub, "grid_style parameter", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            grid_style applies CSS to the entire grid container.
        """))
        st_space("v", 1)

        table_style = ns("table-layout: fixed; width: 100%; border-collapse: collapse;")
        show_code(textwrap.dedent("""\
            table_style = ns("table-layout: fixed; width: 100%;")
            with st_grid(cols=2, grid_style=table_style,
                         cell_styles=bs.cell) as g:
                with g.cell(): st_write(s.bold + s.large, "Header A")
                with g.cell(): st_write(s.bold + s.large, "Header B")
        """))
        st_space("v", 1)

        with st_grid(cols=2, grid_style=table_style, cell_styles=bs.cell) as g:
            with g.cell(): st_write(s.bold + s.large, "Header A")
            with g.cell(): st_write(s.bold + s.large, "Header B")
            with g.cell(): st_write(s.large, "Data A1")
            with g.cell(): st_write(s.large, "Data B1")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Defaults: cols=2, grid_style=none, cell_styles=none.
            Cells auto-wrap to new rows when cols limit is reached.
            Use # row N comments for readability in complex grids.
        """))
