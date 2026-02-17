import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BStyles:
    blue = s.project.colors.blue_01
    orange = s.project.colors.orange_02
    red = s.project.colors.red_02
    green = s.project.colors.green_01
    purple = s.project.colors.purple_01


    Huge = s.text.sizes.Huge_size
    huge = s.text.sizes.huge_size

    center =  s.text.alignments.center_align

    s_list = s.reset_bold + s.container.layouts.center + s.text.sizes.Large_size 
bs = BStyles 

def build():

    with st_block(bs.center + s.text.sizes.Large_size + s.bold):
        st_write(bs.purple + bs.Huge, "Session 1", toc_lvl="1")
        st_space(size=2)
        
        st_write(bs.green + bs.huge, "Course documentation", toc_lvl="+1")
        st_br()
        st_write(bs.red, "©  DO NOT DISTRIBUTE")
        st_br()
        st_write(bs.blue + bs.huge, "Main Documents & Usage", toc_lvl="+1")
        st_br()
        st_space(size=2)

        # First List
        with st_list(li_style = bs.orange + s.text.sizes.LARGE_size + s.bold + s.container.layouts.center) as l:
            with l.item():
                st_write("Course Pack Document", toc_lvl="+1")
        
        # Second List (Details)
        with st_list(li_style = bs.s_list) as l:
            with l.item(): st_write("all material for self study")
            with l.item(): st_write("access to online board")
            with l.item(): st_write("access to surveys")
            with l.item(): st_write("access to notebooks")
            
        st_write(bs.blue, "_", link="https://docs.google.com/document/d/1kXSRZ6Woi3gCVcOdjtluk-JcGZ-0gYj6RwGk_49gOIc/edit")