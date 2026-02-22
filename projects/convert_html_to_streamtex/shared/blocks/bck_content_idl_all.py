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
      #4c1130 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 1 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Group Discovery  (60')", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Content (15') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up NOTEBOOKS  (30') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Break (15') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Showcase (45') ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Text Generation ")
        with lst.item():
            st_write(" Image Recognition ")
        with lst.item():
            st_write(" Image & Video Generation ")
        with lst.item():
            st_write(" Music Generation ")
        with lst.item():
            st_write(" GenAI on your computer ")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, "Debriefing ")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Intuitive introduction to AI  (45') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Break (60')", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2 ", tag=t.h3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Practice and understanding of deep learning "),
        (s.project.colors.dark_purple, "basic concepts"),
        (s.project.colors.burnt_orange, " using the "),
        (s.project.colors.dark_purple, "MNIST"),
        (s.project.colors.burnt_orange, " running example  "),
        tag=t.h4,
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "with the "),
        (s.project.colors.forest_green, "Keras"),
        (s.project.colors.burnt_orange, " framework "),
        tag=t.h4,
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 3 ", tag=t.h3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green, "Scientific & Technical"),
        (s.project.colors.burnt_orange, " basis  "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "for Deep Learning ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Practice and understanding of deep learning basic concepts ... ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "- CONTINUED - ")
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Other"),
        (s.project.colors.dark_purple, " "),
        (s.project.colors.dark_purple, "deep learning  "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "architectures", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 4 ", tag=t.h3)
    st_space(size=3)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Practice and understanding of deep learning "),
        (s.project.colors.dark_purple, "basic concepts"),
        (s.project.colors.burnt_orange, " using the "),
        (s.project.colors.dark_purple, "MNIST"),
        (s.project.colors.burnt_orange, " running example  "),
        tag=t.h4,
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "with the "),
        (s.project.colors.bright_red, "Pytorch"),
        (s.project.colors.burnt_orange, " framework "),
        tag=t.h4,
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 5 ", tag=t.h3)
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "MINI PROJECT ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Advanced Practice and understanding of deep learning  ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "with the "),
        (s.project.colors.bright_red, "Pytorch"),
        (s.project.colors.burnt_orange, " framework "),
        tag=t.h4,
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 6 ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Ethics"),
        (s.project.colors.burnt_orange, " & Artificial Intelligence "),
        tag=t.h4,
    )
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Closure", tag=t.h4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
