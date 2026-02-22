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
      #2f5a1b -> s.project.colors.forest_green
      #783e04 -> s.project.colors.burnt_orange
      #9900ff -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.purple + s.bold, "Who? ")
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Trainer(s)", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Nicolas Guelfi", tag=t.h3)
    st_space(size=3)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.burnt_orange + s.bold, " Activities "), "Education / Training ", " Research / Development")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.forest_green + s.bold, "Software Engineering "), " Requirements engineering ", " Critical systems ")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.burnt_orange + s.bold, "Contexts "), " University of Luxembourg", " Right-On-Skill sarl")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.forest_green + s.bold, "Artificial Intelligence "), " Generative AI ", " Deep Learning ", " Expert systems ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" More information: ")
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
