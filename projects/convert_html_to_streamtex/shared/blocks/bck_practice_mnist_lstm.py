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
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Practice - MNIST_LSTM ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Goal(s) ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Inspect how LSTM can be applied to MNIST ")
        with lst.item():
            st_write(" Check the performance of LSTM for Digits Recognition ")
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Process ", tag=t.h4)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Open the notebook",
                (s.project.colors.gold + s.bold, "_MNIST_"),
                (s.project.colors.bright_red + s.bold, "LSTM"),
                (s.project.colors.gold + s.bold, ".ipynb"),
                (s.project.colors.forest_green + s.bold + s.italic, "(located in git/aiai/notebooks/)"),
            )
        with lst.item():
            st_write(" Execute the notebook cells one by one ")
        with lst.item():
            st_write(" Read the notes ")
        with lst.item():
            st_write(" Check the cells outputs ")
    st_write(s.project.pres.paragraphs.p_xl, "🙂 ")
    st_space(size=4)
    st_space(size=1)
