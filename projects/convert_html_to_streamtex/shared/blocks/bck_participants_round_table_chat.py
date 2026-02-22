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
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Participant(s) ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Individual presentations", tag=t.h3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "First name ", "Main activities ", (s.bold, "Motivations"), " for participating")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Experience (if any) ", (s.project.colors.bright_red + s.bold, "AI / ChatBots "), "Sciences / Technologies ")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=1)
