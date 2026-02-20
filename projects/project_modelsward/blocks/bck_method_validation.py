import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    header = s.bold + s.big + s.project.colors.structure
    cell = s.big
    cell_bold = s.bold + s.big
    note = s.big + s.center_txt
    syr = s.project.colors.structure + s.bold + s.big
    ser = s.project.colors.green_pass + s.bold + s.big

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Six-Level Semantic Validation Hierarchy",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(
        cols=2,
        grid_style=s.project.containers.gap_12,
        cell_styles=(
            sg.create("A1:B1", s.project.containers.table_header)
            + sg.create("A2:B7", s.project.containers.table_cell)
        ),
    ) as g:
        with g.cell():
            st_write(bs.header, "Level")
        with g.cell():
            st_write(bs.header, "What it checks")
        with g.cell():
            st_write(bs.cell_bold, "1. Syntactic")
        with g.cell():
            st_write(bs.cell, "One start, >= 1 end, full connectivity, no event-to-event flows")
        with g.cell():
            st_write(bs.cell_bold, "2. Static Semantics")
        with g.cell():
            st_write(bs.cell, "Type constraints, unique IDs, integrity")
        with g.cell():
            st_write(bs.cell_bold, "3. Event Rules")
        with g.cell():
            st_write(bs.cell, "Start: no in; End: no out; Intermediate: both")
        with g.cell():
            st_write(bs.cell_bold, "4. Structural")
        with g.cell():
            st_write(bs.cell, "Task sequence limits, no consecutive service tasks, error handling")
        with g.cell():
            st_write(bs.cell_bold, "5. Topological")
        with g.cell():
            st_write(bs.cell, "Split/join symmetry, loops, exclusivity")
        with g.cell():
            st_write(bs.cell_bold, "6. Reachability")
        with g.cell():
            st_write(
                bs.cell,
                "Forward from start, backward from end; dead ends, unreachable islands",
            )
    st_space(size=2)
    st_write(
        bs.note,
        (bs.syr, "Levels 1-2 = SYR_BPMN (syntax)"),
        "  |  ",
        (bs.ser, "Levels 3-6 = SER_BPMN (semantics)"),
        "  |  ",
        (s.bold + s.big, "Fail-fast"),
    )
    st_space(size=2)
