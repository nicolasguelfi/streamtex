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
      #2f5a1b -> s.project.colors.forest_green
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Game - Your Profile ", tag=t.h2, toc_lvl="+1")
    st_image(uri="illustration_aiai-image-test_img1.png")
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.gold + s.bold, "Game - Your Profile")
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Click HERE & RightClick & ", "https://docs.google.com/forms/d/e/1FAIpQLScl5M6-u2lykUAxh_DRZAxuIvUewTSOUTNmpMBOpzvJ-AbvvA/viewform"), (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, "Open!", "https://docs.google.com/forms/d/e/1FAIpQLScl5M6-u2lykUAxh_DRZAxuIvUewTSOUTNmpMBOpzvJ-AbvvA/viewform"))
    st_write(s.project.pres.paragraphs.p_xl + s.italic, "(Check the 'end of game link' to see the results) ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
