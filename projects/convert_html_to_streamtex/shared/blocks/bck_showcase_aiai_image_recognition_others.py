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
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Other examples ", tag=t.h4)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Play Rock-Paper-Scissors with an AI ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "HERE", "https://tenso.rs/demos/rock-paper-scissors/"),
    )
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
