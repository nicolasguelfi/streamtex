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
      #351b75 -> s.project.colors.dark_purple
      #37761c -> s.project.colors.olive_green
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "DEEP LEARNING PART 3 ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "	CNN - Convolutional Neural Network ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Architecture ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Convolution ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://github.com/vdumoulin/conv_arithmetic"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://towardsdatascience.com/intuitively-understanding-convolutions-for-deep-learning-1f6f42faee1"),
    )
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Principle ", tag=t.h5)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Convolution Computation(Kernel, Stride, Padding, Feature) ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Input size = 5 x 5 ")
        with lst.item():
            st_write("Kernel size = 3 x 3 ")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Padding = 1",
                (s.project.colors.olive_green + s.italic, "(how many rows and columns are added at the borders) "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Stride = 1",
                (s.project.colors.olive_green + s.italic, "(how many columns and rows are jumped at each step) "),
            )
        with lst.item():
            st_write("output (feature) size = 5 x 5 ")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Input size = 5 x 5 ")
        with lst.item():
            st_write("Kernel size = 3 x 3 ")
        with lst.item():
            st_write("Padding = 1 ")
        with lst.item():
            st_write("Stride = 1 ")
        with lst.item():
            st_write("output (feature) size = 5 x 5 ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Convolution Computation Wrap-up ", tag=t.h6)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Image Layers ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Bias ", tag=t.h5)
    st_space(size=3)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Pooling ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://computersciencewiki.org/index.php/Max-pooling_/_Pooling")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "More on CNN ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Stanford CCS230 ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://stanford.edu/~shervine/teaching/cs-230/cheatsheet-convolutional-neural-networks"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "MearnOpenCV ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://learnopencv.com/understanding-convolutional-neural-networks-cnn/"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Convolution arithmetic ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://github.com/vdumoulin/conv_arithmetic"),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
