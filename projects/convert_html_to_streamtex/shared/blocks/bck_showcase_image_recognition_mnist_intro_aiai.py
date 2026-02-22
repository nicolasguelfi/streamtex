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
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Image Recognition ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Handwritten Digits ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Demo ", tag=t.h5)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "2DANN", "https://adamharley.com/nn_vis/mlp/2d.html"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "2DCNN", "https://adamharley.com/nn_vis/cnn/2d.html"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "3DANN", "https://adamharley.com/nn_vis/mlp/3d.html"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "3DCNN", "https://adamharley.com/nn_vis/cnn/3d.html"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
