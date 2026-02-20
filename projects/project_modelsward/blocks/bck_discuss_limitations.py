import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    gap = ns("gap: 16px;", "discuss_gap")
    row_gap = ns("gap: 12px;", "discuss_row_gap")
    lim_title = s.project.titles.emphasis_red + s.big
    lim_text = s.big
    fut_text = s.big + s.project.colors.structure
    arrow = s.big + s.center_txt + s.project.colors.gray_baseline

bs = BlockStyles


def build():
    st_write(
        s.project.titles.section_title,
        "Discussion",
        toc_lvl="1",
    )
    st_space(size=2)
    st_write(
        s.project.titles.slide_title,
        "Limitations and Future Directions",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(cols="1fr auto 1fr", grid_style=bs.gap):
        with st_block():
            st_write(
                s.project.titles.emphasis_red + s.big + s.center_txt,
                "Current Limitation",
            )
        with st_block():
            pass
        with st_block():
            st_write(
                s.project.titles.emphasis_structure + s.big + s.center_txt,
                "Future Direction",
            )
    st_space(size=1)
    with st_grid(cols="1fr auto 1fr", grid_style=bs.row_gap):
        with st_block(s.project.containers.beamer_block_red):
            st_write(
                bs.body,
                (bs.lim_title, "Standardized prompts"),
                " limits performance ceiling",
            )
        with st_block(s.center_txt):
            st_write(bs.arrow, "-->")
        with st_block(s.project.containers.beamer_block):
            st_write(bs.fut_text, "Model-specific prompt optimization")
    st_space(size=1)
    with st_grid(cols="1fr auto 1fr", grid_style=bs.row_gap):
        with st_block(s.project.containers.beamer_block_red):
            st_write(
                bs.body,
                (bs.lim_title, "Global constraints hardest"),
                " topological/integration at 72-76%",
            )
        with st_block(s.center_txt):
            st_write(bs.arrow, "-->")
        with st_block(s.project.containers.beamer_block):
            st_write(bs.fut_text, "Emerging verification approaches")
    st_space(size=1)
    with st_grid(cols="1fr auto 1fr", grid_style=bs.row_gap):
        with st_block(s.project.containers.beamer_block_red):
            st_write(
                bs.body,
                (bs.lim_title, "Spec-derived test suite"),
                " no industrial processes",
            )
        with st_block(s.center_txt):
            st_write(bs.arrow, "-->")
        with st_block(s.project.containers.beamer_block):
            st_write(bs.fut_text, "Industrial-scale validation")
    st_space(size=2)
