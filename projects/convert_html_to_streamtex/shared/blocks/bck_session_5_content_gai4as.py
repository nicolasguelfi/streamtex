import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #731b47 -> s.project.colors.dark_purple
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 5 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Ethics & Society ", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Project Session 3 ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "Ethical Constraints", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
