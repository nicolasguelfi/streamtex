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
      #1155cc -> s.project.colors.link_blue
      #2f5a1b -> s.project.colors.forest_green
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #00ff00
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Intuitive introduction to AI ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=5)
    st_space(size=5)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "Training ")
    st_space(size=3)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.teal + s.bold, "X ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.teal + s.bold, "Y ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "1 ")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "no ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "2 ")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "no")
        with g.cell():
            st_write(s.project.pres.tables.cell, "3 ")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "no")
        with g.cell():
            st_write(s.project.pres.tables.cell, "4 ")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, "yes ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "... ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "... ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "... ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "Learning?")
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img16.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "BUT ")
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://ar5iv.labs.arxiv.org/html/1712.09913v3")
    st_space(size=3)
    st_space(size=3)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
