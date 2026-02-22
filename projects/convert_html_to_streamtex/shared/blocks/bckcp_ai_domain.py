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
      #674ea7 -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "9.1. Artificial Intelligence Domain ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "History Diagram ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://xuezheku.aminer.cn/ai-history")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Artificial Intelligence Landscape ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.retrocube.com/blog/ai-redefined-types-components-benefits-and-examples/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
