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
      #666666 -> s.project.colors.gray
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
    """
    pass

bs = BlockStyles

def build():
    st_space(size=2)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green + s.bold, "Install "),
        (s.project.colors.burnt_orange + s.bold, "Google Chrome"),
        (s.project.colors.gray + s.bold + s.italic, "(for screen sharing) "),
    )
    st_space(size=4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.pres.paragraphs.p_xl, " open the ", (s.bold, "COURSEPACK"))
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Go to:",
                (s.project.colors.gold + s.bold, "Useful Information / Google Meet "),
            )
        with lst.item():
            st_write(" Follow the process ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
