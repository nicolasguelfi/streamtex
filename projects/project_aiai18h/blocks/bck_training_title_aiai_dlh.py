import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


def build():
    lime = s.text.colors.lime
    bold = s.text.weights.bold_weight
    
    st_image(uri = "logo_ros.png", width="287px",  height="248px")
    
    with st_block(style=s.project.titles.subtitle_intro_bronze_01 + s.text.alignments.center_align):
        st_space("v", 4)
        st_write(s.project.titles.title_intro_green_lime_01, "AI AI", tag=t.h2, toc_lvl="1")
        st_space(size="2em")
        st_write(bold, (lime, "A"),"rtificial ",(lime, "I"),"ntelligence")
        st_space("v", 0)
        st_write(bold, "- ",(lime, "A"),"pplied ",(lime, "I"),"ntroduction:")
        st_space()
        st_write(s.text.decors.italic_text, "Concepts, Applications and Challenges")