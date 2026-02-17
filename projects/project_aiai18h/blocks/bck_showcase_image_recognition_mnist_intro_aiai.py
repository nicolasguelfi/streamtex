import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    """Custom styles defined locally and used only for this block"""
    blue = s.project.colors.blue_01 + s.text.decors.underline_text
bs = BlockStyles


def build():
    with st_block(s.center_txt + s.LARGE + s.bold):
        st_write(s.project.colors.blue_01 + s.huge, "Image Recognition", toc_lvl="2")
        st_space(size=1)
        st_write(s.project.colors.orange_01, "Handwritten Digits", toc_lvl="+1")
        st_space(size=1)
        st_write(s.project.colors.red_01, "Demo", toc_lvl="+2")
        st_space(size=2)

    st_image(uri="digit_recognition_mnist_01.png", width="1541px", height="914px")
    st_space(size=3)

    with st_block(s.center_txt + s.Large + s.bold):
        st_write((bs.blue, "2DANN", "https://adamharley.com/nn_vis/mlp/2d.html"), 
                 " ",
                 (bs.blue, "2DCNN", "https://adamharley.com/nn_vis/cnn/2d.html"),
                 no_link_decor=True)
        
        st_write((bs.blue, "3DANN", "https://adamharley.com/nn_vis/mlp/3d.html"), 
                 " ",
                 (bs.blue, "3DCNN", "https://adamharley.com/nn_vis/cnn/3d.html"),
                 no_link_decor=True)

    st_space(size=5)