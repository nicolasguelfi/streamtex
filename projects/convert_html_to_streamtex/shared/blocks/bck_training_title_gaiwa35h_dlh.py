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
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=2)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_space(size=2)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green + s.bold, "G"),
        (s.project.colors.burnt_orange + s.bold, "AI"),
        (s.project.colors.dark_purple + s.bold, "WA"),
    )
    st_space(size=2)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold + s.bold, "Applied "),
        (s.project.colors.forest_green + s.bold, "G"),
        (s.project.colors.gold + s.bold, "enerative "),
        (s.project.colors.burnt_orange + s.bold, "AI"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold + s.italic, "for "),
        (s.project.colors.dark_purple + s.bold, "W"),
        (s.project.colors.bright_red + s.bold + s.italic, "ebm"),
        (s.project.colors.dark_purple + s.bold, "A"),
        (s.project.colors.bright_red + s.bold + s.italic, "sters "),
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
