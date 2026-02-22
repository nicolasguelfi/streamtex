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
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "MNIST Running Example ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.italic, "(main source for animations: "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.italic, "3blue1brown", "https://www.3blue1brown.com/topics/neural-networks"),
        (s.italic, ") "),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
