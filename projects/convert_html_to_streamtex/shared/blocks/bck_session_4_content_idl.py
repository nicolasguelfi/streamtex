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
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 4 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Session content ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Session introduction (15') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up computers (15') ", tag=t.h4)
    st_write(s.project.pres.titles.h4, "DEEP LEARNING PART 3 Pytorch (75') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Break (15') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4, "DEEP LEARNING PART 3 Pytorch (75') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Session(s) Survey(s) (15') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
