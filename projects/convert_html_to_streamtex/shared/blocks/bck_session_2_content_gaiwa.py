import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #2f5a1b -> s.project.colors.forest_green
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 2 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Content ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "AI & Deep Learning - Part 1&2  (60') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Break (15') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Ethics & Society "),
        (s.project.colors.burnt_orange, "& "),
        (s.project.colors.gold, "AI"),
        (s.project.colors.burnt_orange, " "),
        (s.project.colors.bright_red, "(60')"),
        tag=t.h4,
    )
    st_space(size=1)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Generative "),
        (s.project.colors.gold, "AI"),
        (s.project.colors.burnt_orange, " Practice - Session 1 (75')"),
        tag=t.h4,
    )
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
