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
      #434343 -> s.project.colors.gray
      #674ea7 -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "5.8.1. Stuart Russel ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Wisdom declaration ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://www.rightonskill.com/data/video/russel/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "On Wikipedia ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://fr.wikipedia.org/wiki/Stuart_Russell")
    st_space(size=1)
    st_space(size=1)
