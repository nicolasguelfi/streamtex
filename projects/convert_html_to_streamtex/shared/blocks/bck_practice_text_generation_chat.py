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
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.link_blue, "First Practice of "),
        (s.project.colors.burnt_orange, "Generative AI"),
        tag=t.h3,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Objectives ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Choose your ",
                (s.project.colors.gold + s.bold, "own best domain of expertise "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Start a chat to ",
                (s.project.colors.gold + s.bold, "test its capacity"),
                " to answer questions from your domain ",
            )
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "Targets:")
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=1)
