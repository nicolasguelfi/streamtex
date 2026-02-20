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
    note = s.big + s.italic

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Agent Specialization: Roles and Responsibilities",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(
        cols=2,
        grid_style=s.project.containers.gap_12,
        cell_styles=(
            sg.create("A1:A1", s.project.containers.table_header)
            + sg.create("B1:B1", s.project.containers.table_header)
            + sg.create("A2:B5", s.project.containers.table_cell)
        ),
    ) as g:
        with g.cell():
            st_write(bs.header, "Agent")
        with g.cell():
            st_write(bs.header, "Role")
        with g.cell():
            st_write(bs.cell_bold, "Scenario Parser")
        with g.cell():
            st_write(bs.cell, "NL -> structured plan (entities, flows, types)")
        with g.cell():
            st_write(bs.cell_bold, "5 Generators")
        with g.cell():
            st_write(bs.cell, "StartEvent, Task, Gateway, IntermediateEvent, EndEvent")
        with g.cell():
            st_write(bs.cell_bold, "Collector / Validator")
        with g.cell():
            st_write(
                bs.cell,
                "Assembles elements; executes in simulator against validation hierarchy",
            )
        with g.cell():
            st_write(bs.cell_bold, "Repair Agent")
        with g.cell():
            st_write(
                bs.cell,
                "Analyzes failures via two-stage error mapping -> targeted regeneration",
            )
    st_space(size=2)
    st_write(
        bs.note,
        "Each generator operates on an isolated subtask, narrowing the generation space from all BPMN models to type-consistent configurations.",
    )
    st_space(size=2)
