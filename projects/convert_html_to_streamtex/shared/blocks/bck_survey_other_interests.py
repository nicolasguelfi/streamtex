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
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "AIAI"),
        (s.project.colors.forest_green, "AI"),
        (s.project.colors.burnt_orange, " Survey "),
        tag=t.h4,
    )
    st_image(uri="illustration_aiai-image-test_img1.png")
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.gold + s.bold, "Game - Further Interests")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.link_blue + s.bold, "Click HERE & RightClick & Open in Private Window!", link="https://docs.google.com/forms/d/e/1FAIpQLSesdNfuhfJBR7I1NQSh55rg75sKSjlJtWMx2ZskJ0qUgdZayw/viewform")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
