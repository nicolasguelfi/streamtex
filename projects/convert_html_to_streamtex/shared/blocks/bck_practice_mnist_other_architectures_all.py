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
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Practice - Other Architectures ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Goal(s) ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Inspect how ",
                (s.project.colors.bright_red + s.bold, "GAN/LSTM/Transformers"),
                "can be applied to MNIST ",
            )
        with lst.item():
            st_write(" Check the performance Digits Recognition/Generation ")
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Process ", tag=t.h4)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Open the notebooks",
                (s.project.colors.gold + s.bold, "_MNIST_"),
                (s.project.colors.bright_red + s.bold, "GAN"),
                (s.project.colors.gold + s.bold, ".ipynb_MNIST_"),
                (s.project.colors.bright_red + s.bold, "LSTM"),
                (s.project.colors.gold + s.bold, ".ipynb_MNIST_"),
                (s.project.colors.bright_red + s.bold, "VISTRANSF"),
                (s.project.colors.gold + s.bold, ".ipynb "),
            )
    st_space(size=3)
    st_space(size=1)
