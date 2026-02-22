import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #351b75 -> s.project.colors.dark_purple
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Introduction to "),
        (s.project.colors.dark_purple, "Quasible "),
        tag=t.h5,
    )
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=2)
    st_space(size=2)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_space(size=2)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
