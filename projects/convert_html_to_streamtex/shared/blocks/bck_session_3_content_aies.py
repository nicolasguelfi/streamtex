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
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 3 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Content ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Session introduction (15') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Prompt Engineering Practice (90') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break (15')", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Interactive Mini-Workshop  ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "on "),
        (s.project.colors.purple, "AI & Ethics"),
        (s.project.colors.burnt_orange, " (90')"),
        tag=t.h4,
    )
    st_space(size=4)
    st_space(size=3)
    st_space(size=1)
