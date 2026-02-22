import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #660000 -> s.project.colors.deep_red
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=5, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.deep_red + s.bold, "Input layer ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.deep_red + s.bold, "connection ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.deep_red + s.bold, "Hiddenlayer 1 ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.deep_red + s.bold, "connection ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.deep_red + s.bold, "outputlayer ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "1 ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "dense ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "3 ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "dense ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "1 ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "weights qty = (1 x 3) + (3 x 1) = 6 ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "if biases it would give: ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "[(1 x 3) + ",
        (s.project.colors.bright_red + s.bold, "3"),
        " ] + [ (3 x 1) + ",
        (s.project.colors.bright_red + s.bold, "1"),
        "]= 6 + ",
        (s.project.colors.bright_red + s.bold, "4 "),
    )
    st_write(s.project.pres.paragraphs.p_xl, "= 10 ")
    st_space(size=3)
    st_space(size=1)
