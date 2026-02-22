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
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 2 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Overview ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "DEEP LEARNING PART 1 ", tag=t.h4)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.bright_red, "MNIST", "https://en.wikipedia.org/wiki/MNIST_database"),
        (s.project.colors.bright_red, " running example "),
        tag=t.h5,
    )
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Setting up computers ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "DL basic concepts ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "artificial neural network, architecture, input, output, dataset, parameters, weight, bias, activation function, layer ")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Practice ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Break (15') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "DEEP LEARNING PART 2 ", tag=t.h4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "DL basic concepts ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "learning process, metrics, cost function, loss, accuracy, cost minimization, epochs, training/validation/test datasets, fitting, over/under fitting ")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Practice ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
