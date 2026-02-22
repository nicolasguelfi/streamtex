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
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=2)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green, "G"),
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.dark_purple, "4"),
        (s.project.colors.navy_blue, "AS"),
        (s.project.colors.forest_green, "Showcase"),
    )
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Copilot ")
        with lst.item():
            st_write("Copilot in CRM")
        with lst.item():
            pass
    st_space(size=4)
