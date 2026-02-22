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
      #274e13 -> s.project.colors.forest_green
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #9900ff -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.forest_green, "4"),
        (s.project.colors.dark_purple, "LC"),
        (s.project.colors.link_blue, " "),
        (s.project.colors.purple, "Projects "),
        tag=t.h1,
        toc_lvl="1",
    )
    st_space(size=2)
    st_space(size=3)
    st_space(size=1)
