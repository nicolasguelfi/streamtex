import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #063763 -> s.project.colors.navy_blue
      #1155cc -> s.project.colors.link_blue
      #274e13 -> s.project.colors.forest_green
      #731b47 -> s.project.colors.dark_purple
      #b45f06 -> s.project.colors.burnt_orange
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 1 ", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Introduction  ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "& Training Group Discovery (30') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Showcasing Generative AI (45') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Resources (30') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break (15') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Deep Learning & Generative AI (60') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Generative AI Practice (30')", tag=t.h4)
    st_space(size=1)
    st_space(size=4)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Lunch (60') ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2", tag=t.h3)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Designing a ChatBot (30') ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.navy_blue, "Design Your ChatBot - Part 1 (60')"),
        (s.project.colors.bright_red, "Break (15')"),
        (s.project.colors.navy_blue, "Design Your ChatBot - Part 2 (60')"),
        tag=t.h4,
    )
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "ChatBot Demos (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Q&A and Survey (15') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "TRAINING END ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
