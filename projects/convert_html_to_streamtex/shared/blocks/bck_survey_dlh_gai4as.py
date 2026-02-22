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
      #9900ff -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "DLH Training Survey(s) ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://forms.office.com/Pages/ResponsePage.aspx?id=xQ4KNpTw8UWjGcbcNWAnBK4vRZeTXIFMubZVA_OeG3ZUQkw1R1RLODhSSUdEQTdBVjZaSUlZRkQ0Ti4u&origin=QRCode")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
