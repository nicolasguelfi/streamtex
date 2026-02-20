import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    main_title = s.project.titles.main_title + s.center_txt
    subtitle = s.project.colors.structure_light + s.big + s.center_txt
    authors = s.large + s.center_txt
    affiliation = s.big + s.center_txt + s.italic
    date = s.big + s.center_txt + s.project.colors.gray_baseline
    underline = ns("text-decoration: underline;", "underline")

bs = BlockStyles


def build():
    st_space(size=5)
    with st_block(s.center_txt):
        st_image(uri="uni.png", width="120px")
    st_space(size=3)
    with st_block(s.center_txt):
        st_write(
            bs.main_title,
            "A Semantically-Grounded Agentic Framework for Assisting BPMN Model Instance Execution",
        )
    st_space(size=2)
    with st_block(s.center_txt):
        st_write(bs.subtitle, "MODELSWARD 2026")
    st_space(size=2)
    with st_block(s.center_txt):
        st_write(
            bs.authors,
            (bs.underline, "Tiago Sousa"),
            ", Nicolas Guelfi and Benoit Ries",
        )
    st_space(size=1)
    with st_block(s.center_txt):
        st_write(bs.affiliation, "University of Luxembourg")
    st_space(size=1)
    with st_block(s.center_txt):
        st_write(bs.date, "11 February 2026")
    st_space(size=5)
