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
    cell = ns("border: 1px solid gray;") + s.container.paddings.little_padding + s.center_txt
bs = BlockStyles


def build():
    st_write(bs.heading, "Grids", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Equal columns ---
    st_write(bs.sub, "Equal Columns (integer)", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        with st_grid(cols=3, cell_styles=bs.cell) as g:
            with g.cell(): st_write("A1")
            with g.cell(): st_write("B1")
            with g.cell(): st_write("C1")
            with g.cell(): st_write("A2")
            with g.cell(): st_write("B2")
            with g.cell(): st_write("C2")
    """))
    st_space("v", 1)

    with st_grid(cols=3, cell_styles=bs.cell) as g:
        with g.cell(): st_write("A1")
        with g.cell(): st_write("B1")
        with g.cell(): st_write("C1")
        with g.cell(): st_write("A2")
        with g.cell(): st_write("B2")
        with g.cell(): st_write("C2")
    st_space("v", 2)

    # --- CSS grid template ---
    st_write(bs.sub, "Unequal Columns (CSS template)", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        with st_grid(cols="auto 1fr", cell_styles=bs.cell) as g:
            with g.cell(): st_write("Label")
            with g.cell(): st_write("This column takes remaining space")
    """))
    st_space("v", 1)

    with st_grid(cols="auto 1fr", cell_styles=bs.cell) as g:
        with g.cell(): st_write("Label")
        with g.cell(): st_write("This column takes remaining space")
        with g.cell(): st_write("Row 2")
        with g.cell(): st_write("Also fills the rest of the row")
    st_space("v", 2)

    # --- StyleGrid ---
    st_write(bs.sub, "StyleGrid — Per-Cell Styling", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        styled_cells = (
            sg.create("A1:B2", s.large)
            * sg.create("A1:B1", s.bold + s.text.colors.white
                                 + s.container.bg_colors.red_bg)
        )
        with st_grid(cols=2, cell_styles=styled_cells) as g:
            with g.cell(): st_write("A1 — bold white on red")
            with g.cell(): st_write("B1 — bold white on red")
            with g.cell(): st_write("A2 — large")
            with g.cell(): st_write("B2 — large")
    """))
    st_space("v", 1)

    styled_cells = (
        sg.create("A1:B2", s.large)
        * sg.create("A1:B1", s.bold + s.text.colors.white
                             + s.container.bg_colors.red_bg)
    )
    with st_grid(cols=2, cell_styles=styled_cells) as g:
        with g.cell(): st_write("A1 — bold white on red")
        with g.cell(): st_write("B1 — bold white on red")
        with g.cell(): st_write("A2 — large")
        with g.cell(): st_write("B2 — large")
    st_space("v", 2)

    show_tip(
        "sg.create(range, style) targets cells by Excel-like ranges. "
        "Multiply (*) to replace styles, add (+) to combine them."
    )
