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
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #85200c -> s.project.colors.deep_red
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "Our Focus ")
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "Ethics ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.forest_green, "Society ")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.dark_purple + s.bold, "Is AI good or bad? "), (s.project.colors.teal + s.bold, "Is humanity threatened by AI? "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.burnt_orange + s.bold, "What about AI and my personal life? "), (s.project.colors.deep_red + s.bold, "Will AI impact my professional life? "))
    st_space(size=3)
    st_space(size=2)
    st_space(size=2)
    st_space(size=1)
