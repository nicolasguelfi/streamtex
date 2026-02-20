import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    header = s.bold + s.big + s.project.colors.structure
    cell = s.big
    cell_bold = s.bold + s.big
    gap = ns("gap: 24px;", "eval_eff_gap")
    stat = s.project.titles.emphasis_structure + s.big
    note = s.big + s.center_txt

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Validation Efficiency",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(cols="55% 45%", grid_style=bs.gap):
        with st_block():
            with st_grid(
                cols=3,
                grid_style=s.project.containers.gap_12,
                cell_styles=(
                    sg.create("A1:C1", s.project.containers.table_header)
                    + sg.create("A2:C4", s.project.containers.table_cell)
                ),
            ) as g:
                with g.cell():
                    st_write(bs.header, "Metric")
                with g.cell():
                    st_write(bs.header, "Proposed")
                with g.cell():
                    st_write(bs.header, "Baseline")
                with g.cell():
                    st_write(bs.cell, "Avg repair attempts")
                with g.cell():
                    st_write(bs.cell_bold, "0.66")
                with g.cell():
                    st_write(bs.cell, "1.99")
                with g.cell():
                    st_write(bs.cell, "Avg validation attempts")
                with g.cell():
                    st_write(bs.cell_bold, "1.54")
                with g.cell():
                    st_write(bs.cell, "2.54")
                with g.cell():
                    st_write(bs.cell, "Self-correction rate")
                with g.cell():
                    st_write(bs.cell_bold, "29.2%")
                with g.cell():
                    st_write(bs.cell, "3.9%")
        with st_block():
            st_space(size=2)
            st_write(bs.stat, "67% fewer repairs")
            st_space(size=1)
            st_write(bs.stat, "39% fewer validations")
            st_space(size=1)
            st_write(bs.stat, "+25.3 pp self-correction")
    st_space(size=2)
    st_write(
        bs.note,
        "Execution time: +35% (86s vs. 64s), modest overhead for +38 pp gain",
    )
    st_space(size=2)
