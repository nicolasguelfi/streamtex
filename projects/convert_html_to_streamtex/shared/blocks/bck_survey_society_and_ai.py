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
      #7f6000 -> s.project.colors.gold
      #85200c -> s.project.colors.deep_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Society & AI Survey ", tag=t.h3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.gold + s.bold, "Jeu - société")
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Click HERE & RightClick & ", "https://docs.google.com/forms/d/e/1FAIpQLScpadKQ-p1iwCxSCs1UUmVHT14ekKnbekASJFn9K3Gi3y0AMA/viewform"), (s.project.pres.links.link_lg + s.project.colors.deep_red + s.bold, "Open in Private Window!", "https://docs.google.com/forms/d/e/1FAIpQLScpadKQ-p1iwCxSCs1UUmVHT14ekKnbekASJFn9K3Gi3y0AMA/viewform"))
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
