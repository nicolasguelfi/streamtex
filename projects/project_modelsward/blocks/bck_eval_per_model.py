import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    gap = ns("gap: 24px;", "eval_model_gap")
    stat = s.project.titles.emphasis_structure
    note = s.big + s.center_txt

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Per-Model Impact: Decomposition vs. Feedback",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(cols=2, grid_style=bs.gap):
        with st_block(s.project.containers.beamer_block):
            st_write(s.project.titles.block_title, "Weaker Models: Decomposition")
            st_space(size=1)
            st_write(
                bs.body,
                "GLM-4.6: 15% -> 97.5% ",
                (bs.stat, "(+82.5 pp)"),
            )
            st_space(size=1)
            st_write(
                bs.body,
                "Flash Lite: 0% -> 82.5% ",
                (bs.stat, "(+82.5 pp)"),
            )
            st_space(size=1)
            st_write(
                s.big + s.italic,
                "Architecture compensates for limited base capabilities.",
            )
        with st_block(s.project.containers.beamer_block):
            st_write(s.project.titles.block_title, "Stronger Models: CoT Feedback")
            st_space(size=1)
            st_write(
                bs.body,
                "GPT-5: 97.5% -> 92.5%, but self-correction: 15% -> ",
                (bs.stat, "67.5%"),
            )
            st_space(size=1)
            st_write(bs.body, "Nano: 57.5% (still +7.5 pp)")
            st_space(size=1)
            st_write(
                s.big + s.italic,
                "CoT feedback improves error recovery, not initial generation.",
            )
    st_space(size=2)
    st_write(
        bs.note,
        "Best overall: Gemini 2.5 Pro & GLM-4.6 at 97.5%  |  Weakest: GPT-5 Nano at 57.5%",
    )
    st_space(size=2)
