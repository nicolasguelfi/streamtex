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
      #2f5a1b -> s.project.colors.forest_green
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Other Architectures ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Stable Diffusion ", tag=t.h3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Image Generation ", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://erdem.pl/2023/11/step-by-step-visual-introduction-to-diffusion-models")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
