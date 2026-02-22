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
      #2f5a1b -> s.project.colors.forest_green
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 4 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Session Introduction ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session Content ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Session introduction (15') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "ETHICS (60') ", tag=t.h4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Ethics and AI ", tag=t.h5)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Survey ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "SOCIETY (60') ", tag=t.h4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "AI & Job Market ", tag=t.h5)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Survey ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Break (15') ", tag=t.h4)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Interactive "),
        (s.project.colors.burnt_orange, "Mini-Workshop"),
        (s.project.colors.burnt_orange, " on AI, Ethics, & Society "),
        (s.project.colors.burnt_orange, "(30') "),
        tag=t.h4,
    )
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Session Survey (10') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "Training Survey (10') ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "AIAIAI Survey and Discussion (10') ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.navy_blue + s.bold, "---Training Closure--- ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
