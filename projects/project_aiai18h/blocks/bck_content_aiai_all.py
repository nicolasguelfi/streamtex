import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BStyles:
    blue = s.project.colors.blue_01
    orange = s.project.colors.orange_02
    bronze = s.project.colors.bronze_01
    red = s.project.colors.red_02
    green = s.project.colors.green_01
    huge = s.text.sizes.huge_size

    center =  s.text.alignments.center_align

    s_list = s.text.sizes.Large_size + s.reset_bold + s.container.layouts.center
    title = blue + huge
bs = BStyles

def build():

    with st_block(bs.center + s.text.sizes.LARGE_size + s.bold):
        st_write(bs.title, "Session 1", label="Session 1", toc_lvl="+1")
        st_space()
        
        st_write(bs.orange, "Training Group Discovery  (60')", toc_lvl="+2")
        st_br()
        st_write(bs.orange, "Training Presentation (15')", toc_lvl="+2")
        st_br()
        st_write(bs.orange, "Setting up NOTEBOOKS  (30')", toc_lvl="+2")
        st_br()
        st_space()
        
        st_write(bs.bronze, "Break (15')", toc_lvl="+2")
        st_space()
        st_write(bs.orange, "Showcase (45')", toc_lvl="+2")

        with st_list(li_style=bs.s_list) as l:
            with l.item(): st_write("Text Generation")
            with l.item(): st_write("Image Recognition")
            with l.item(): st_write("Image&Video Generation")
            with l.item(): st_write("Music Generation")
        
        st_write(bs.orange, "Intuitive introduction to AI  (45')", toc_lvl="+2")
        st_space()
        
        st_write(bs.title, "Session 2", toc_lvl="+1")
        st_space()
        st_write(bs.orange, "Practice and understanding of deep learning basic concepts using the MNIST running example", toc_lvl="+2")
        st_space()
        
        st_write(bs.title, "Session 3", toc_lvl="+1")
        st_space()
        st_write(bs.orange, "Practice and understanding of deep learning basic concepts - ctnd", toc_lvl="+2")
        st_space()
        st_write(bs.orange, "Practice and understanding of other deep learning architectures", toc_lvl="+2")
        st_space()
        
        st_write(bs.title, "Session 4", toc_lvl="+1")
        st_space()
        
        st_write(bs.orange, (bs.red, 'Ethics'), " & Artificial Intelligence", toc_lvl="+2")
        st_space()
        st_write(bs.orange, (bs.green, 'Society'), " & Artificial Intelligence", toc_lvl="+2")