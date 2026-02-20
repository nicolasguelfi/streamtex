import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    main_title = s.project.titles.main_title + s.center_txt
    authors = s.large + s.center_txt
    affiliation = s.big + s.center_txt + s.italic
    questions = s.project.colors.structure + s.bold + s.Huge + s.center_txt
    underline = ns("text-decoration: underline;", "q_underline")

bs = BlockStyles


def build():
    st_space(size=5)
    with st_block(s.center_txt):
        st_write(
            bs.main_title,
            "A Semantically-Grounded Agentic Framework for Assisting BPMN Model Instance Execution",
        )
    st_space(size=2)
    with st_block(s.center_txt):
        st_write(
            bs.authors,
            (bs.underline, "Tiago Sousa"),
            ", Nicolas Guelfi, Benoit Ries",
        )
    st_space(size=1)
    with st_block(s.center_txt):
        st_write(bs.affiliation, "University of Luxembourg")
    st_space(size=4)
    with st_block(s.center_txt):
        st_write(bs.questions, "Questions?")
    st_space(size=5)
