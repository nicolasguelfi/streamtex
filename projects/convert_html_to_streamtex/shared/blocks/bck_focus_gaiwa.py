import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0b5394 -> s.project.colors.navy_blue
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #85200c -> s.project.colors.deep_red
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #cc4125 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "Our Focus ")
    st_space(size=2)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.salmon, "AI"), "&", (s.project.colors.bright_red, " Ethics  "), "&", (s.project.colors.olive_green, "Society"))
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red, "Generative "), (s.project.colors.salmon, "AI"), (s.project.colors.dark_purple + s.bold, "From "), (s.project.colors.navy_blue + s.bold, "text & media"), (s.project.colors.dark_purple + s.bold, "to "), (s.project.colors.navy_blue + s.bold, "text & media"))
    st_space(size=3)
    st_space(size=5)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "WordPress ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.forest_green, "Plugins ")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.dark_purple + s.bold, "Website development")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.deep_red + s.bold, "ChatBot Integration ")
    st_space(size=3)
    st_space(size=2)
    st_space(size=2)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
