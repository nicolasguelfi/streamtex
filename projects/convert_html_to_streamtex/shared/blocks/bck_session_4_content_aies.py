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
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 4 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Content ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "AI & Society (90')", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break (15')", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Interactive Mini-Workshop  ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "on "),
        (s.project.colors.purple, "AI & Society (& Ethics)"),
        (s.project.colors.burnt_orange, " (90')"),
        tag=t.h4,
    )
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.navy_blue, "DLH Training Survey ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Wrap-up discussion", tag=t.h4)
    st_space(size=4)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.navy_blue + s.bold, "---Training Closure--- ")
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "!! The End !! ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
