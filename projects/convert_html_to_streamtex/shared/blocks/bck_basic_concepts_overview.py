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
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Basic Concepts ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Initial Problem = Prediction ", tag=t.h3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Estimation ("),
        (s.project.colors.bright_red, "Quantity"),
        (s.project.colors.burnt_orange, ") "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "vs  ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Classification ("),
        (s.project.colors.forest_green, "Quality"),
        (s.project.colors.burnt_orange, ") "),
        tag=t.h4,
    )
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "-", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "Data Generation", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "= Estimation of the value of the generated data", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "(Artificial) Neural Network ", tag=t.h3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Convolutional Neural Network ", tag=t.h3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://adamharley.com/nn_vis/cnn/3d.html")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
