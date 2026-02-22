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
    st_write(s.project.doc.titles.h2, "20.8. SOCIETY ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "20.8.1. Main sources ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "McKinseyNotes from the AI frontier: Modeling the impact of AI on the world economy ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.mckinsey.com/featured-insights/artificial-intelligence/notes-from-the-ai-frontier-modeling-the-impact-of-ai-on-the-world-economy")
        with g.cell():
            st_write(s.project.doc.tables.cell, "McKinseyHarnessing automation for a future that works ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.mckinsey.com/featured-insights/digital-disruption/harnessing-automation-for-a-future-that-works")
        with g.cell():
            st_write(s.project.doc.tables.cell, "McKinseyDefining the skills citizens will need in the future world of work ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.mckinsey.com/industries/public-and-social-sector/our-insights/defining-the-skills-citizens-will-need-in-the-future-world-of-work")
        with g.cell():
            st_write(s.project.doc.tables.cell, "WEFFuture of Jobs Report 2023 ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www3.weforum.org/docs/WEF_Future_of_Jobs_2023.pdf")
        with g.cell():
            st_write(s.project.doc.tables.cell, "AI Readiness Index 2020 ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.oxfordinsights.com/government-ai-readiness-index-2020")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "20.8.2. Simulations ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "BBCWill a robot take your job? ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.bbc.com/news/technology-34066941")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
