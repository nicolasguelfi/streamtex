import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    emphasis = s.bold + s.big

bs = BlockStyles


def build():
    st_write(
        s.project.titles.section_title,
        "Related Work",
        toc_lvl="1",
    )
    st_space(size=2)
    st_write(
        s.project.titles.slide_title,
        "Related Work",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_list(list_type=lt.unordered, li_style=bs.body) as l:
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Prompt engineering"),
                ": improves completeness, but fragile and model-dependent; no formal validation",
                " [Busch et al., 2023; Wei et al., 2023; Hassan et al., 2024]",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Constrained decoding"),
                ": guarantees SYR_BPMN (syntax) but cannot verify SER_BPMN (semantics)",
                " [Shin et al., 2021; Geng et al., 2023]",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Multi-agent frameworks"),
                ": role-based specialization, but NL coordination lacks type constraints",
                " [Qian et al., 2024; Wu et al., 2023; Chen et al., 2023]",
            )
    st_space(size=2)
    with st_block(s.project.containers.beamer_block_red):
        st_write(s.project.titles.block_title, "Gap")
        st_space(size=1)
        st_write(
            bs.body,
            "All three approaches enforce ",
            (s.italic, "sense"),
            " (distributional patterns). None enforce ",
            (s.italic, "reference"),
            " (execution semantics).",
        )
    st_space(size=2)
