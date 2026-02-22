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
      #37761c -> s.project.colors.olive_green
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Practice - MNIST_Keras 4  ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Goal(s) ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.olive_green + s.bold, "Experiment CNN")
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
                (s.project.colors.forest_green + s.bold + s.italic, "(located in git/aiai/notebooks/)"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " restart the kernel",
                (s.italic, "(menu Kernel / Restart Kernel ...)"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "set the mode",
                (s.project.colors.burnt_orange + s.bold, "mode = "),
                (s.project.colors.burnt_orange + s.bold, "2"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " set the number of epochs",
                (s.project.colors.burnt_orange + s.bold, "epochs = "),
                (s.project.colors.burnt_orange + s.bold, "100"),
                (s.project.colors.bright_red + s.bold, " CLICK INSIDE THE CELL BELOW THIS ONE:"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " run all above cells",
                (s.italic, "(menu Run / Run All Above Selected Cell)"),
            )
        with lst.item():
            st_write(" Run (shift+enter) and check the notebook cells and output one by one ")
        with lst.item():
            st_write(" See if you can relate the cell contents with the deep learning concepts learned ")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, "REDO with ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange + s.bold, "epochs = "),
                (s.project.colors.burnt_orange + s.bold, "5"),
            )
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, " STOP AT THE END")
    st_write(s.project.pres.paragraphs.p_xl, "🙂 ")
    st_space(size=1)
