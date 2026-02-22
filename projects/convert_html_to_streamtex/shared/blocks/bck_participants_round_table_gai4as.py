import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #063763 -> s.project.colors.navy_blue
      #1155cc -> s.project.colors.link_blue
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Participant(s) ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Individual presentations", tag=t.h3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "First name ", "Main activities ", "Motivations for participating to ", (s.project.colors.forest_green + s.bold, "G"), (s.project.colors.burnt_orange + s.bold, "AI"), (s.project.colors.dark_purple + s.bold, "4"), (s.project.colors.navy_blue + s.bold, "AS"))
        with g.cell():
            st_write(s.project.pres.tables.cell, "Experience (if any) ", "Generative AI / ChatBots ", "Technologies ", "Sciences ")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
