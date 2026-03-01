import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Grid cell styles demo."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    base_cell = (s.container.borders.solid_border
                 + s.container.paddings.small_padding
                 + s.center_txt
                 + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Grid Cell Styles",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Single style for all cells
        st_write(bs.sub, "cell_styles as a single Style", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pass a single Style to cell_styles
            to apply it uniformly to all cells.
        """))
        st_space("v", 1)

        show_code("""\
with st_grid(cols=2,
             cell_styles=bs.base_cell
                         + s.container.bg_colors.alice_blue_bg) as g:
    with g.cell(): st_write(s.large, "Same style")
    with g.cell(): st_write(s.large, "Same style")""")
        st_space("v", 1)

        with st_grid(cols=2,
                     cell_styles=bs.base_cell
                                 + s.container.bg_colors.alice_blue_bg) as g:
            with g.cell(): st_write(s.large, "Same style")
            with g.cell(): st_write(s.large, "Same style")
            with g.cell(): st_write(s.large, "Same style")
            with g.cell(): st_write(s.large, "Same style")
        st_space("v", 2)

        # StyleGrid.create() with Excel notation
        st_write(bs.sub,
                 "StyleGrid.create() with Excel notation",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Target specific cells with Excel-like notation
            for per-cell styling.
        """))
        st_space("v", 1)

        show_code(file="examples/grid/cell_stylegrid_create.py")
        st_space("v", 1)

        header_style = (s.bold + s.large
                        + s.container.bg_colors.steel_blue_bg
                        + s.text.colors.white)
        highlight = s.container.bg_colors.light_yellow_bg

        with st_grid(
            cols=3,
            cell_styles=sg.create("A1:C1", header_style + bs.base_cell)
                        + sg.create("A2:C3", s.large + bs.base_cell)
                        + sg.create("B2", highlight + bs.base_cell)
        ) as g:
            # row 1 (header)
            with g.cell(): st_write("Name")
            with g.cell(): st_write("Role")
            with g.cell(): st_write("Status")
            # row 2
            with g.cell(): st_write("Alice")
            with g.cell(): st_write("Developer (highlighted)")
            with g.cell(): st_write("Active")
            # row 3
            with g.cell(): st_write("Bob")
            with g.cell(): st_write("Designer")
            with g.cell(): st_write("Active")
        st_space("v", 2)

        # Operators on StyleGrid
        st_write(bs.sub, "StyleGrid operators: +, -, *", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Combine, subtract, or replace cell styles with operators.
        """))
        st_space("v", 1)

        show_code("""\
sg1 + sg2  # combine (CSS merge)
sg1 - sg2  # remove properties
sg1 * sg2  # replace (sg2 wins where non-empty)""")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Use sg.create() for complex grids.

            Combine multiple sg.create() calls with +
            to build the full cell style map.
        """))
