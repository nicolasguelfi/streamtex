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
      #351b75 -> s.project.colors.dark_purple
      #990000 -> s.project.colors.bright_red
      #a61b00 -> s.project.colors.salmon
      #b45f06 -> s.project.colors.burnt_orange
      #cc4125 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Scientific & technical Basic Notions ", tag=t.h2, toc_lvl="+1")
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "!! recap on practice for "),
        (s.project.colors.link_blue + s.bold, "_MNIST_keras.ipynb"),
        (s.project.colors.bright_red + s.bold, " until "),
        (s.project.colors.salmon + s.bold, "Using a CNN - Convolutional Neural Network "),
        (s.project.colors.bright_red + s.bold, "!!"),
    )
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " calculus")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " probabilities_and_statistics ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " code_various_tensors")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " metrics ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " loss_functions")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " optimizers ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " activation_functions")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " embeddings ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.salmon + s.bold, "....."),
        (s.project.colors.salmon + s.bold, "better"),
        (s.project.colors.salmon + s.bold, " to consult for next week project🙂 "),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "/notebooks/notions"),
        (s.project.colors.salmon + s.bold, "..... "),
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
