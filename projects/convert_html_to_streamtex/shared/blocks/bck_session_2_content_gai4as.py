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
      #37761c -> s.project.colors.olive_green
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up the computers (30') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Quasible Training Tool (60')", tag=t.h4)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.olive_green, "Break (15')", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Practice - Session 1 (60') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Wrap-up (15') ", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Session END", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
