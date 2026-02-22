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
    st_write(s.project.doc.titles.h2, "7.3. AI & Sustainability ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "7.3.1. SDG ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "UNSustainable Development Goals ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.un.org/sustainabledevelopment/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "UNThe Sustainable Development Goals Report 2022 ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://unstats.un.org/sdgs/report/2022/The-Sustainable-Development-Goals-Report-2022.pdf")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "7.4. Studies ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Can AI Help Achieve Environmental Sustainability? ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://earth.org/data_visualization/ai-can-it-help-achieve-environmental-sustainable/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "The role of artificial intelligence in achieving the Sustainable Development Goals ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.nature.com/articles/s41467-019-14108-y")
        with g.cell():
            st_write(s.project.doc.tables.cell, "PwCFourth Industrial Revolution for the Earth ", "Harnessing Artificial Intelligence for the Earth ", "2018 ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.pwc.com/gx/en/sustainability/assets/ai-for-the-earth-jan-2018.pdf")
    st_space(size=1)
    st_space(size=1)
