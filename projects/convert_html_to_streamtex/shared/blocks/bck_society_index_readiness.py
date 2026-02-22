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
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "AI Readiness Index ", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_lg + s.project.colors.link_blue + s.italic, "(2024)", link="https://www.oxfordinsights.com/government-ai-readiness-index-2020")
    st_space(size=2)
    st_space(size=2)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://oxfordinsights.com/ai-readiness/ai-readiness-index/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://oxfordinsights.com/wp-content/uploads/2024/12/2024-Government-AI-Readiness-Index-2.pdf"),
    )
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.oxfordinsights.com/government-ai-readiness-index-2020")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
