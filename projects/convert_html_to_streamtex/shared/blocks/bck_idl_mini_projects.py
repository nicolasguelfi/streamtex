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
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "MINI PROJECT", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "check "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "COURSEPACK", "https://docs.google.com/document/d/1eYtoLVpYgCrSpr8n75-jxqx3hrcnm1qUYYU0A4WXztY/edit?pli=1#heading=h.tryek5glxgkx"),
        tag=t.h5,
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://docs.google.com/document/d/1eYtoLVpYgCrSpr8n75-jxqx3hrcnm1qUYYU0A4WXztY/edit?pli=1#heading=h.tryek5glxgkx")
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
