import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #7f6000 -> s.project.colors.gold
    Dropped colors:
      #00ff00
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "IDL ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.bold, "I"),
        (s.project.colors.gold + s.bold, "ntroduction to "),
        (s.bold, "D"),
        (s.project.colors.gold + s.bold, "eep "),
        (s.bold, "L"),
        (s.project.colors.gold + s.bold, "earning"),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.gold + s.italic, "for Artificial Intelligence")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
