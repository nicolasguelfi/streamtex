import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0c343d -> s.project.colors.teal
      #1155cc -> s.project.colors.link_blue
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #ffa500 -> s.project.colors.orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Practice - MNIST_Keras 1 ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Goal(s) ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" First \"look\" at some technologies used for Deep Learning Development ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green, " Python,  Tensorflow,  Jupyterlab,  Cloud Computing ("),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "GCP", "https://console.cloud.google.com"),
        (s.project.colors.forest_green, "),  GPU (Graphic Processing Units)"),
        ".... ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Process ", tag=t.h4)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Open the notebook",
                (s.project.colors.gold + s.bold, "_MNIST_keras.ipynb"),
                (s.project.colors.forest_green + s.bold + s.italic, "(located in git/aiai/notebooks/)"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.orange + s.bold, "Scroll down until you see "),
                (s.project.colors.teal + s.bold, "---> AIAI ACTION <--- "),
                (s.project.colors.orange + s.bold, "and proceed to the process described."),
            )
        with lst.item():
            st_write(" Check the cells outputs ")
        with lst.item():
            st_write(" Play the practice related Quizzes ")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.bright_red + s.bold, "STOP AT CELL ABOVE THIS ONE:"),
                "🙂 ",
            )
    st_space(size=3)
    st_space(size=1)
