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
      #351b75 -> s.project.colors.dark_purple
      #cc4125 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.salmon, "World Economic Forum"),
        (s.project.colors.salmon + s.italic, "Future of Jobs Survey "),
        tag=t.h5,
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://www3.weforum.org/docs/WEF_Future_of_Jobs_2023.pdf")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Reskilling and Upskilling Priorities ", tag=t.h6)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
