import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


def build(
    int_google="intelligence_google.png",
    link_1="https://lucid.app/lucidchart/6caf112b-a8f7-4ec5-bdc3-c51e679b4259/edit?page=0&v=94&s=1224",
    int_gpt="intelligence_gpt.png",
    link_2="https://lucid.app/lucidchart/21a95573-d25f-4dbb-81c1-3a3c90581f35/edit?page=0&v=345&s=1536",
    vision_training="vision_training.png",
    link_3="https://lucid.app/lucidchart/59426a8e-c582-4aa4-b11f-72acdeb11e56/edit?page=0&v=192&s=1224",
    combined_training="combined_training.png"
):
    blue_sub = s.project.titles.subtitle_blue_01
    
    with st_block(s.text.alignments.center_align):
        st_write(s.project.titles.title_green_01, "Computers are Man-Made", toc_lvl='2')
        st_space()
        
        st_write(blue_sub, "Generic Vision of IT", toc_lvl='+1')
        st_image(uri=int_google, link=link_1)
        
        st_write(blue_sub, "Simple Vision of IT With AI", toc_lvl='+1')
        st_image(uri=int_gpt, link=link_2)
        st_image(uri=vision_training, link=link_3)
        
        st_write(blue_sub, "Combined view", toc_lvl='+1')
        st_image(uri=combined_training)