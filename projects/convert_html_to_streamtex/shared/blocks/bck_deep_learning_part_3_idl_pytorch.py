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
      #351b75 -> s.project.colors.dark_purple
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #a61b00 -> s.project.colors.salmon
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "DEEP LEARNING PART 3"),
        (s.project.colors.forest_green, "PyTorch "),
        tag=t.h2,
        toc_lvl="+1",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " code_packages-torch ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " code_packages_various ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, "code_various_dataloader ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " code_cl_ANN ")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " PRACTICE PyTorch 1 ")
        with lst.item():
            st_write(s.project.colors.dark_purple + s.bold, "code_cl_MNISTModule ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " code_monitoring ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " code_cl_CNN_B ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " code_cl_RESNET_A ")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " PRACTICE PyTorch 2")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.salmon + s.bold, "....."),
        (s.project.colors.salmon + s.bold, "better"),
        (s.project.colors.salmon + s.bold, " to consult for next week project🙂"),
        (s.project.colors.dark_purple + s.bold, "/notebooks/notions"),
        (s.project.colors.salmon + s.bold, "..... "),
    )
    st_space(size=4)
    st_space(size=3)
    st_space(size=1)
