import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #37761c -> s.project.colors.olive_green
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #93c47d -> s.project.colors.light_green
      #990000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #ea9999 -> s.project.colors.salmon
    Dropped colors:
      #b4a7d6 (unmapped)
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "Test"),
        (s.project.colors.burnt_orange, " the ChatBots& "),
        (s.project.colors.olive_green, "Evaluate"),
        (s.project.colors.burnt_orange, " the ChatBots "),
        tag=t.h4,
    )
    st_space(size=2)
    with st_grid(cols=5, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.bright_red + s.bold, "A ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.bright_red + s.bold, "B ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.bright_red + s.bold, "C ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.bright_red + s.bold, "D ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.salmon + s.bold, "Eval ")
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
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "E ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "F ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "G ")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.light_green + s.bold, "Res ")
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
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
