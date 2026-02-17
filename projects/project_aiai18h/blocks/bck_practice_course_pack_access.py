import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    """Custom styles defined locally and used only for this block"""
    center_txt = s.text.alignments.center_align
    content = s.Large + center_txt
    green = s.project.colors.green_01
    pink = s.project.colors.pink_01
    gold = s.project.colors.bronze_01
    huge_green_title = green + s.huge
    large_italic_text = s.text.decors.italic_text + s.text.sizes.large_size
    blue = s.project.colors.blue_01
    link_style = s.project.titles.subtitle_blue_01
    red_emphasis = s.project.colors.red_01 + s.bold + s.LARGE
    purple_subtitle = s.project.colors.purple_02 + content + s.bold
bs = BlockStyles

def build():

    with st_block(bs.center_txt):
        st_write(bs.huge_green_title + bs.center_txt + s.bold, 
                 "Practice - CoursePack Access", 
                 toc_lvl='2')
        st_space(size=5)

        st_write(bs.center_txt + bs.blue + s.bold + s.huge, 
                 "Process", 
                 toc_lvl='+1')
        st_space(size=5)

        st_write(bs.purple_subtitle, "Please proceed to the following process:")
        st_space(size=3)
        
        with st_list(lt.ordered, li_style=bs.content + s.container.layouts.center) as l:
            
            with l.item(): st_write("Start your computer (if not started)")
            with l.item(): st_write("Open a session using the institution identification information (if not already opened)")
            with l.item(): st_write("Launch firefox application")
            
            with l.item(): 
                st_write("Go to ", (bs.link_style, "aiai.ros.lu", 'https://aiai.ros.lu'))
            with l.item():
                st_write("Click on ", (bs.red_emphasis, '"Go"'))
            
            with l.item(s.bold):
                st_write("Fill the form with ", 
                         (s.LARGE, "YOUR "),
                         (bs.green, "gmail email address "),
                         (bs.pink, "USE "), 
                         (bs.gold, "YOUR "), 
                         (bs.pink, "VALUES(S) PRINTED ON PAPER"))
            
            with l.item():
                st_write("Check your email at ", (bs.link_style, "mail.google.com", 'https://mail.google.com'))
                
            with l.item():
                st_write("Click on the ", (bs.gold + s.LARGE + s.bold, "COURSEPACK"), " link")


