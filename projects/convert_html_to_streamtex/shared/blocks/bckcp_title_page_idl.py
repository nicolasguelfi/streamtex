import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #063763 -> s.project.colors.navy_blue
      #1155cc -> s.project.colors.link_blue
      #37761c -> s.project.colors.olive_green
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #85200c -> s.project.colors.deep_red
      #be9000 -> s.project.colors.gold
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.gold + s.bold, "IDL")
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.olive_green + s.bold, "COURSEPACK ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.navy_blue + s.bold, "LEARNER ")
    st_space(size=2)
    st_write(
        s.project.doc.paragraphs.p_lg,
        (s.project.colors.gold + s.bold, "I"),
        (s.project.colors.gold + s.bold, "ntroduction to "),
        (s.project.colors.gold + s.bold, "D"),
        (s.project.colors.gold + s.bold, "eep "),
        (s.project.colors.gold + s.bold, "L"),
        (s.project.colors.gold + s.bold, "earning"),
    )
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.burnt_orange + s.italic, "for Artificial Intelligence ")
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
    st_space(size=2)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
