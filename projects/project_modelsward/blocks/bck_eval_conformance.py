import streamlit as st
import pandas as pd
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    gap = ns("gap: 24px;", "eval_conf_gap")
    stat_value = s.project.titles.emphasis_structure + s.Large
    stat_label = s.big
    italic_note = s.big + s.italic

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Agentic Architecture Nearly Doubles Semantic Conformance",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_grid(cols="55% 45%", grid_style=bs.gap):
        with st_block():
            data = pd.DataFrame(
                {
                    "Metric": ["Pass Rate", "1st Attempt", "1st Repair"],
                    "Proposed": [84.2, 25.0, 56.8],
                    "Baseline": [46.4, 5.8, 8.0],
                }
            )
            stx.st_bar_chart(
                data,
                x="Metric",
                y=["Proposed", "Baseline"],
                color=["#2c5282", "#A0AEC0"],
            )
        with st_block():
            st_space(size=2)
            st_write(bs.stat_value, "+37.8 pp")
            st_write(bs.stat_label, "pass rate")
            st_space(size=2)
            st_write(bs.stat_value, "331%")
            st_write(bs.stat_label, "first-attempt improvement")
            st_space(size=2)
            st_write(bs.stat_value, "7x")
            st_write(bs.stat_label, "first-repair success")
            st_space(size=2)
            st_write(
                bs.italic_note,
                "Improves both initial generation and error recovery.",
            )
    st_space(size=2)
