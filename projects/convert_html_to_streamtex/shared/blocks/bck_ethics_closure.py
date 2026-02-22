import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #134f5c -> s.project.colors.teal
      #37761c -> s.project.colors.olive_green
      #990000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "A "),
        (s.project.colors.teal, "Positive"),
        (s.project.colors.burnt_orange, " Ending Thought "),
        tag=t.h4,
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Big Mankind Problems"),
        "=> ",
        (s.project.colors.olive_green + s.bold, "Big Impact of AI"),
        (s.project.colors.bright_red + s.bold, "Big Impact of AI"),
        " => ",
        (s.project.colors.olive_green + s.bold, "Big Caution of AI"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Big Caution of AI"),
        "=> ",
        (s.project.colors.olive_green + s.bold, "Big Caution of Human Rights "),
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Big Caution of Human Rights"),
        "=> ",
        (s.project.colors.olive_green + s.bold, "Big Caution of Human Rights "),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
