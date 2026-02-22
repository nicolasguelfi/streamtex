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
      #783e04 -> s.project.colors.burnt_orange
      #990000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Tiago Sousa", tag=t.h3)
    st_space(size=1)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "Expertise Domains: ")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, "Software Engineering  ")
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "Artificial Intelligence ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " Sustainability ")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" More information: ")
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_space(size=1)
