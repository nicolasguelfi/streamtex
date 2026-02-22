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
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "Our Focus ")
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "Artificial Intelligence", (s.project.colors.bright_red, "&Citizen"))
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.deep_red + s.bold, "Introduction "), (s.project.colors.deep_red + s.bold, "Concepts "), (s.project.colors.deep_red + s.bold, "Generative AI applied to"), (s.bold, "E"), (s.project.colors.bright_red + s.bold, "ntrepreneurship & "), (s.bold, "I"), (s.project.colors.bright_red + s.bold, "nnovation"))
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
