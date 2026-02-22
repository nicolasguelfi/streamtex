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
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "CoursePack  ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Overall Content Presentation ", tag=t.h3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://docs.google.com/document/d/1kXSRZ6Woi3gCVcOdjtluk-JcGZ-0gYj6RwGk_49gOIc/edit#heading=h.minxn3qja1ry")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
