import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #274e13 -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #4c1130 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #cc0000 -> s.project.colors.bright_red
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold, "AI"),
        (s.project.colors.forest_green, "4"),
        (s.project.colors.dark_purple, "EI"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "Introduction to "),
        (s.bold, "Artificial Intelligence"),
        (s.project.colors.burnt_orange + s.bold, " for the "),
        (s.project.colors.olive_green + s.bold, "citizen"),
    )
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_write(s.project.pres.paragraphs.p_lg + s.project.colors.bright_red + s.bold + s.italic, "(no right to distribute outside this course context) ")
    st_space(size=2)
    st_space(size=2)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
