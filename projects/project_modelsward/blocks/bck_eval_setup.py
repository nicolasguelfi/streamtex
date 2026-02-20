import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    emphasis = s.bold + s.big
    gap = ns("gap: 24px;", "eval_setup_gap")

bs = BlockStyles


def build():
    st_write(
        s.project.titles.section_title,
        "Evaluation & Results",
        toc_lvl="1",
    )
    st_space(size=2)
    st_write(
        s.project.titles.slide_title,
        "Experimental Setup",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(cols=2, grid_style=bs.gap):
        with st_block(s.project.containers.beamer_block):
            st_write(s.project.titles.block_title, "Test Suite")
            st_space(size=1)
            with st_list(list_type=lt.unordered, li_style=bs.body) as l:
                with l.item():
                    st_write("40 scenarios across 6 difficulty levels")
                with l.item():
                    st_write("Aligned to validation hierarchy levels")
                with l.item():
                    st_write(
                        bs.body,
                        "Total: N = 360 (40 x 9 models)",
                    )
            st_space(size=1)
            st_write(
                bs.body,
                (bs.emphasis, "Baseline:"),
                " Monolithic single-prompt + post-hoc validation",
            )
            st_space(size=1)
            st_write(
                bs.body,
                (bs.emphasis, "Proposed:"),
                " Full multi-agent architecture with iterative repair",
            )
        with st_block(s.project.containers.beamer_block):
            st_write(s.project.titles.block_title, "9 LLMs Evaluated")
            st_space(size=1)
            with st_list(list_type=lt.unordered, li_style=bs.body) as l:
                with l.item():
                    st_write("GPT-5, GPT-5 Mini, GPT-5 Nano [OpenAI, 2025]")
                with l.item():
                    st_write(
                        "Gemini 2.5 Pro, Flash, Flash Lite [Comanici et al., 2025]",
                    )
                with l.item():
                    st_write("Grok-4 Fast")
                with l.item():
                    st_write("Qwen3 Coder 30B [Yang et al., 2025]")
                with l.item():
                    st_write("GLM-4.6 [Team, 2025]")
    st_space(size=2)
