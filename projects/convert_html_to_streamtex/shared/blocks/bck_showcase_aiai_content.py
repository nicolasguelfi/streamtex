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
    """
    pass

bs = BlockStyles

def build():
    st_space(size=2)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Showcase ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Text Generation ")
        with lst.item():
            st_write(" Image Recognition ")
        with lst.item():
            st_write(" Image Generation ")
        with lst.item():
            st_write(" video generation ")
        with lst.item():
            st_write(" Music Generation ")
        with lst.item():
            st_write(" GenAI on your computer ")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, "Debriefing ")
    st_space(size=3)
    st_space(size=1)
