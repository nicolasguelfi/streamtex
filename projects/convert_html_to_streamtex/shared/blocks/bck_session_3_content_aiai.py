import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #2f5a1b -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 3 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Session content ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Session introduction (15') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up computers (15') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "DEEP LEARNING PART 3 (60') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, " CNN basic concepts ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "Architecture, convolution layer, pooling layer ")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Transfer Learning ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "ResNet, ResNet for MNIST ")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Practice ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Break (15') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "DEEP LEARNING PART 4 (60') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Other Deep Learning Architectures ", tag=t.h5)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "GAN - Generative Adversarial Network ", tag=t.h6)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "LSTM - Long Short-Term Memory ", tag=t.h6)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Transformers ", tag=t.h6)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Practice ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Session Survey (15') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
