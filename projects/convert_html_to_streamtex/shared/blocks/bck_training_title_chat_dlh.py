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
        (s.project.colors.dark_purple + s.bold, "CHAT"),
        (s.project.colors.gold + s.bold, " "),
        (s.project.colors.olive_green + s.bold, "2D"),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.gold + s.bold, "Using and Specializing  ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "Large Language Models ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold + s.italic, "such as ChatGPT")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
