import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #7f6000 -> s.project.colors.gold
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "!! WARNING !!  SCHEDULE CHANGES ")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.gold + s.bold, "week")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.gold + s.bold, "content")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Course Presentation")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Showcase")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Projects Presentation & Start")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Intuitive introduction to AI")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "DEEP LEARNING")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "break")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Projects Q/A")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "Prompt Engineering")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Prompt Engineering - Practicals")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "AI & Ethics")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Projects Q/A")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "Projects Presentations & Discussions")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Projects Presentations & Discussions - ctnd")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Projects Q/A")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
