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
      #1b4587 -> s.project.colors.navy_blue
      #274e13 -> s.project.colors.forest_green
      #783e04 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=2)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.forest_green, "4"),
        (s.project.colors.link_blue, "EC"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "Artificial Intelligence"),
        (s.project.colors.forest_green + s.bold, "for"),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.navy_blue, " the European Citizen ")
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_lg + s.project.colors.bright_red + s.bold + s.italic, "(no right to distribute outside this course context) ")
    st_space(size=2)
    st_space(size=2)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
