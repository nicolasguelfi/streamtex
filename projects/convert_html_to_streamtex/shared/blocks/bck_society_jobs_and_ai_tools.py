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
      #980000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.pwc.co.uk/services/economics/insights/the-impact-of-automation-on-jobs.html")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.pwc.co.uk/services/economics/insights/the-impact-of-automation-on-jobs.html")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "By Job Title ", tag=t.h5)
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.bbc.com/news/technology-34066941")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
