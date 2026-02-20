import streamlit as st
import pandas as pd
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    note = s.big + s.center_txt
    syr = s.project.colors.structure + s.bold + s.big
    ser = s.project.colors.green_pass + s.bold + s.big

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Conformance by Validation Level",
        toc_lvl="2",
    )
    st_space(size=2)
    data = pd.DataFrame(
        {
            "Level": [
                "Syntax",
                "Static Sem.",
                "Event",
                "Structural",
                "Topological",
                "Integration",
            ],
            "Proposed": [95.2, 88.9, 88.9, 87.5, 75.7, 72.1],
            "Baseline": [53.2, 50.0, 49.1, 48.6, 44.8, 40.5],
        }
    )
    stx.st_bar_chart(
        data,
        x="Level",
        y=["Proposed", "Baseline"],
        color=["#2c5282", "#A0AEC0"],
    )
    st_space(size=1)
    st_write(
        bs.note,
        (bs.syr, "SYR_BPMN (Levels 1-2)"),
        "  |  ",
        (bs.ser, "SER_BPMN (Levels 3-6)"),
    )
    st_space(size=1)
    st_write(
        bs.note,
        "+30.9 to +42.0 pp across all levels  |  Declining gradient: local (95%) -> global (72%)",
    )
    st_space(size=2)
