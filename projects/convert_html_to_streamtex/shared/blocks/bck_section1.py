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
      #660000 -> s.project.colors.deep_red
      #7f6000 -> s.project.colors.gold
      #be9000 -> s.project.colors.gold
    Dropped colors:
      #00ff00
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=2)
    st_space(size=1)
    st_space(size=5)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "AI AI ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.bold, "A"),
        (s.project.colors.gold + s.bold, "rtificial"),
        (s.project.colors.gold + s.bold, " "),
        (s.bold, "I"),
        (s.project.colors.gold + s.bold, "ntelligence"),
        (s.project.colors.gold + s.bold, " - "),
        (s.bold, "A"),
        (s.project.colors.gold + s.bold, "pplied"),
        (s.project.colors.gold + s.bold, " "),
        (s.bold, "I"),
        (s.project.colors.gold + s.bold, "ntroduction"),
        (s.project.colors.gold, ":"),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.gold + s.italic, "Concepts, Applications and Challenges")
    st_space(size=3)
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
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.forest_green, "prompt"), "  +  snow  +  ", (s.project.colors.deep_red, "cartoon "))
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=1)
