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
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "UML"),
        (s.project.colors.gold + s.bold, " Profile Survey "),
    )
    st_space(size=4)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Fill the survey", link="https://forms.gle/BZJtv3USE3RRUJMs6")
        with g.cell():
            pass
    st_space(size=4)
    st_space(size=1)
