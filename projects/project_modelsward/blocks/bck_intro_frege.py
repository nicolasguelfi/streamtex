import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    block_title = s.project.titles.block_title
    block_body = s.medium
    gap = ns("gap: 24px;", "frege_gap")
    center_italic = s.big + s.center_txt + s.italic
    semantic_gap = s.project.titles.emphasis_structure + s.big + s.center_txt

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Why: Frege's Sense/Reference Distinction",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(cols=2, grid_style=bs.gap):
        with st_block(s.project.containers.beamer_block):
            st_write(bs.block_title, "Sense (Sinn)")
            st_space(size=1)
            st_write(bs.body, "What BPMN ", (s.italic, "looks like"))
            st_write(bs.block_body, "The mode of presentation of meaning")
            st_space(size=1)
            with st_list(list_type=lt.unordered, li_style=bs.block_body) as l:
                with l.item():
                    st_write("Distributional patterns")
                with l.item():
                    st_write("Syntactic co-occurrences (SYR_BPMN)")
                with l.item():
                    st_write(
                        bs.block_body,
                        "LLMs ",
                        (s.bold, "capture"),
                        " this",
                    )
        with st_block(s.project.containers.beamer_block):
            st_write(bs.block_title, "Reference (Bedeutung)")
            st_space(size=1)
            st_write(bs.body, "What BPMN ", (s.italic, "means at runtime"))
            st_write(bs.block_body, "The actual object or state of affairs")
            st_space(size=1)
            with st_list(list_type=lt.unordered, li_style=bs.block_body) as l:
                with l.item():
                    st_write("Token flow, synchronization (SER_BPMN)")
                with l.item():
                    st_write("Reachability, denotational semantics")
                with l.item():
                    st_write(
                        bs.block_body,
                        "LLMs ",
                        (s.bold, "lack"),
                        " this",
                    )
    st_space(size=2)
    st_write(
        bs.semantic_gap,
        "<-- semantic gap [Frege, 1892; Bender & Koller, 2020] -->",
    )
    st_space(size=1)
    st_write(
        bs.center_italic,
        "Statistical pattern matching cannot ensure semantic correctness.",
    )
    st_space(size=2)
