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
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "13.3.1. Sources - Institutions ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "UNESCO - AI Home ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.unesco.org/fr/artificial-intelligence")
        with g.cell():
            st_write(s.project.doc.tables.cell, "UNESCO - Recommendation on the Ethics of Artificial Intelligence ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.unesco.org/en/articles/recommendation-ethics-artificial-intelligence")
        with g.cell():
            st_write(s.project.doc.tables.cell, "OCDE - AI Home ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.oecd.org/digital/artificial-intelligence/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "EU -  European Parliament Special Committee on Artificial Intelligence in a Digital Age ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.europarl.europa.eu/committees/en/aida/home/highlights")
        with g.cell():
            st_write(s.project.doc.tables.cell, "EU -  European Commission A European approach to artificial intelligence ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence")
        with g.cell():
            st_write(s.project.doc.tables.cell, "EU -  European CouncilA trustworthy artificial intelligence ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.consilium.europa.eu/en/your-online-life-and-the-eu/#group-section-trustworthy-AI-tBusxga6wd")
        with g.cell():
            st_write(s.project.doc.tables.cell, "AI Standards Hub ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://aistandardshub.org/")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
