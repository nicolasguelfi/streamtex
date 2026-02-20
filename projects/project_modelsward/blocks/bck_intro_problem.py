import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    emphasis = s.project.titles.emphasis_red
    italic_note = s.big + s.italic

bs = BlockStyles


def build():
    st_write(
        s.project.titles.section_title,
        "Introduction",
        toc_lvl="1",
    )
    st_space(size=2)
    st_write(
        s.project.titles.slide_title,
        "The Problem: Syntactically Valid, Semantically Broken",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_list(list_type=lt.unordered, li_style=bs.body) as l:
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Misconfigured gateways"),
                ": parallel splits without corresponding joins",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Improper event sequencing"),
                ": event-based gateways followed by tasks, not catching events",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Malformed control flows"),
                ": deadlocks or unreachable activities",
            )
    st_space(size=2)
    with st_block(s.project.containers.beamer_block_red):
        st_write(
            bs.italic_note,
            "LLM-generated BPMN looks correct but fails at runtime.",
            " [Drakopoulos et al., 2025]",
        )
    st_space(size=1)
    st_write(bs.body, "Consider the most common violation:")
    st_space(size=2)
