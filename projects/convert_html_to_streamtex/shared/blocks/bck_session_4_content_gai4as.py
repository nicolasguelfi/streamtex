import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 4 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Overview ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up the computers ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Project - Overview ", tag=t.h5)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Project Session "),
        "1",
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Break (15')", tag=t.h4)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Project Session "),
        (s.project.colors.bright_red, "2"),
        tag=t.h4,
    )
    st_space(size=1)
    st_space(size=1)
