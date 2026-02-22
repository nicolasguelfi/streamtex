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
      #274e13 -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #7f6000 -> s.project.colors.gold
      #85200c -> s.project.colors.deep_red
      #990000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #00ff00
    """
    pass

bs = BlockStyles

def build():
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_write(
        s.project.doc.paragraphs.p_lg,
        (s.project.colors.gold + s.bold, "CHAT"),
        (s.bold, "1D"),
    )
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.olive_green + s.bold, "COURSEPACK ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.gold + s.bold, "Using and Specializing  ")
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.forest_green + s.bold, "Large Language Models ")
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.bright_red + s.bold + s.italic, "such as ChatGPT")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.link_blue + s.bold, "aiai.ros.lu", link="https://aiai.ros.lu")
    st_space(size=1)
    st_space(size=1)
    st_space(size=2)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.bright_red + s.bold, " Confidential  ")
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.bright_red + s.bold, "DO NOT DISTRIBUTE ")
    st_space(size=2)
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.deep_red + s.bold + s.italic, "NO EDIT RIGHTS CAN BE GRANTED ")
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.deep_red + s.bold + s.italic, "Thus please do not request them ;) ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
