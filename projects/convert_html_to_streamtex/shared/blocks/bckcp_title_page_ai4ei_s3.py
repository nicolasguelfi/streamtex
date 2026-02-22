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
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #85200c -> s.project.colors.deep_red
      #cc0000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=2)
    st_write(
        s.project.doc.paragraphs.p_lg,
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.forest_green, "4"),
        (s.project.colors.dark_purple, "EI"),
        " S3",
    )
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.olive_green + s.bold, "COURSEPACK ")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_lg,
        (s.project.colors.burnt_orange + s.bold, "Artificial Intelligence"),
        (s.project.colors.forest_green + s.bold, "for"),
    )
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.dark_purple + s.bold, "Entrepreneurship and Innovation")
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.doc.paragraphs.p_sm + s.project.colors.bright_red + s.bold + s.italic, "(no right to distribute outside this course context)")
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
    st_space(size=1)
