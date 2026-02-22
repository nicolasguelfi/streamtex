import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #1155cc -> s.project.colors.link_blue
      #b45f06 -> s.project.colors.burnt_orange
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 1 ", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Introduction  ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "& Training Group Discovery (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Deep Learning & Generative AI (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Designing a ChatBot (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up the computers (30') ", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2", tag=t.h3)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Design Your ChatBot (60') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "ChatBot Demos (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Q&A and Survey (15') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "TRAINING END ", tag=t.h4)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
