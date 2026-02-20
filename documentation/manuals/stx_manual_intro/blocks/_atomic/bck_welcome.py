import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Welcome screen styles."""
    welcome_title = s.project.titles.course_title + s.center_txt
    subtitle = s.project.colors.accent_teal + s.Large + s.center_txt
    description = s.large + s.center_txt + s.project.colors.neutral_gray
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_space("v", 3)
        st_write(bs.welcome_title, "StreamTeX Training Course",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)
        st_write(bs.subtitle,
                 "A Hands-On Guide to Every Feature", tag=t.div)
        st_space("v", 3)
        st_write(bs.description,
                 "This course teaches StreamTeX from basics to advanced patterns.")
        st_br()
        st_write(bs.description,
                 "Each section demonstrates one concept with live examples.")
        st_space("v", 2)
        st_write(bs.description,
                 "Navigate using the Table of Contents in the sidebar,")
        st_br()
        st_write(bs.description,
                 "or scroll through the blocks sequentially.")
        st_space("v", 3)
