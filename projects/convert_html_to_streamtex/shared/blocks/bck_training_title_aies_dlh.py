import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #1b4587 -> s.project.colors.navy_blue
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
    Dropped colors:
      #00ff00
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
        (s.project.colors.gold + s.bold, "AI "),
        (s.bold, "E"),
        (s.project.colors.navy_blue + s.bold, "S"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold + s.bold, "AI, "),
        (s.bold, "E"),
        (s.project.colors.gold + s.bold, "thics, and "),
        (s.project.colors.navy_blue + s.bold, "S"),
        (s.project.colors.gold + s.bold, "ociety "),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.italic, "Live With and Develop AI ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
