import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    gap = ns("gap: 24px;", "instr_gap")
    rule_active = s.medium + s.project.colors.structure + s.bold
    rule_inactive = s.medium + s.project.colors.gray_baseline
    caption = s.big + s.center_txt + s.italic

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Instruction Engineering",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(cols="1fr auto 1fr", grid_style=bs.gap):
        with st_block(s.project.containers.beamer_block):
            st_write(s.project.titles.block_title, "9 Rule Categories")
            st_space(size=1)
            st_write(bs.rule_active, "behavioral")
            st_write(bs.rule_active, "cognitive")
            st_write(bs.rule_active, "gateway_types")
            st_write(bs.rule_active, "split_join_pair")
            st_write(bs.rule_active, "token_routing")
            st_write(bs.rule_inactive, "event_placement")
            st_write(bs.rule_inactive, "task_sequencing")
            st_write(bs.rule_inactive, "error_handling")
            st_write(bs.rule_inactive, "termination")
        with st_block(s.center_txt):
            st_space(size=5)
            st_write(s.big + s.project.colors.structure, "filter by type")
            st_write(s.big + s.project.colors.structure, "-->")
        with st_block(s.project.containers.beamer_block):
            st_write(s.project.titles.block_title, "Gateway Agent")
            st_space(size=1)
            st_write(bs.rule_active, "gateway_types")
            st_write(bs.rule_active, "split_join_pairing")
            st_write(bs.rule_active, "token_routing")
            st_space(size=1)
            st_write(bs.body, "+ behavioral, cognitive")
            st_write(bs.body, "+ BPMN 2.0.2 exemplars")
    st_space(size=2)
    st_write(
        bs.caption,
        "Selective exposure prevents prompt dilution: each agent sees only pertinent rules.",
    )
    st_space(size=2)
