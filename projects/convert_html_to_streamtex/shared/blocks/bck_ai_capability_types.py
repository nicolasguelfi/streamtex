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
      #783e04 -> s.project.colors.burnt_orange
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange + s.bold, "Artificial Narrow Intelligence "),
                (s.project.colors.burnt_orange + s.bold, "(ANI) "),
            )
        with lst.item():
            pass
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange + s.bold, "Artificial General Intelligence "),
                (s.project.colors.burnt_orange + s.bold, "(AGI) "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "solve any problem by thinking, understanding, and acting in a way that is ",
                (s.project.colors.forest_green + s.bold, "indistinguishable"),
                " from a human. ",
            )
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange + s.bold, "Artificial Super Intelligence "),
                (s.project.colors.burnt_orange + s.bold, "(ASI) "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "self-aware and ",
                (s.project.colors.forest_green + s.bold, "surpasses"),
                " the limits of human intelligence. ",
            )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://insights.daffodilsw.com/blog/how-does-ai-work-top-10-key-apps-that-use-ai")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
