import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    """Custom styles defined locally and used only for this block"""
    green_huge_title = s.project.colors.green_01 + s.huge + s.text.alignments.center_align + s.bold
    lime_bullet = s.text.colors.lime + s.bold
    debriefing_style = s.project.colors.brown_01 + s.LARGE + s.bold
bs = BlockStyles


def build():

    st_write(bs.green_huge_title, "Showcase", toc_lvl="2", tag=t.div)
    st_space(size=5)

    with st_list(lt.unordered, li_style=s.Large + s.container.layouts.center) as l:
        with l.item(): st_write("Text Generation")
        with l.item(): st_write("Image Recognition")
        with l.item(): st_write("Image Generation")
        with l.item(): st_write("Music Generation")
        with l.item(bs.debriefing_style): st_write("Debriefing")

