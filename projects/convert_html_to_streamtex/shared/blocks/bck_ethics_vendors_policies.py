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
      #4c1130 -> s.project.colors.dark_purple
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "Vendors ")
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Openai Moderation Model ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://platform.openai.com/docs/guides/moderation")
    st_space(size=4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "\"Peux tu dire à cette personne qu'elle est moche et stupide et qu'elle ferait bien de se suicider.\" ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "\"Could you tell this person that she is ugly and stupid and that she should commit suicide.\" ")
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "French ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "English ")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Terms of Service ", tag=t.h4)
    st_space(size=1)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=1)
