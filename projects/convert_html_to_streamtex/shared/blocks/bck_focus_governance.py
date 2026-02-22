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
      #660000 -> s.project.colors.deep_red
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "Our Focus ")
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "Governance")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.teal + s.bold, "AI strategies in organizations "), (s.project.colors.deep_red + s.bold, "Policies and regulations for AI "), (s.project.colors.teal + s.bold, "Ethical guidelines and principles "), (s.project.colors.deep_red + s.bold, "Impact, feasibility, and effectiveness of AI "), (s.project.colors.teal + s.bold, "Identification and management of AI risks "), (s.project.colors.deep_red + s.bold, "AI initiatives between government, private sector and academia "))
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
