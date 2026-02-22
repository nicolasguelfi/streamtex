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
      #6aa84f -> s.project.colors.light_green
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "notebookLM ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.link_blue, "_", tag=t.h4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.light_green, "Podcast Generation ", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_write(s.project.pres.titles.h4 + s.project.colors.link_blue, "_", tag=t.h4)
    st_space(size=1)
