import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0c343d -> s.project.colors.teal
      #274e13 -> s.project.colors.forest_green
      #660000 -> s.project.colors.deep_red
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_space(size=2)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "Our Focus ")
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "Languages ", (s.project.colors.bright_red, "& "), (s.project.colors.forest_green, "Cultures "), (s.project.colors.bright_red, "& "), (s.project.colors.teal, "Education "))
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.deep_red + s.bold, "AI as a Tool for "), (s.bold, "L"), (s.project.colors.bright_red + s.bold, "&"), (s.project.colors.forest_green + s.bold, "C"), (s.project.colors.bright_red + s.bold, "&"), (s.project.colors.teal + s.bold, "E"), (s.project.colors.burnt_orange + s.bold, "AI-Powered Product for "), (s.bold, "L"), (s.project.colors.bright_red + s.bold, "&"), (s.project.colors.forest_green + s.bold, "C"), (s.project.colors.bright_red + s.bold, "&"), (s.project.colors.teal + s.bold, "E"))
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=1)
