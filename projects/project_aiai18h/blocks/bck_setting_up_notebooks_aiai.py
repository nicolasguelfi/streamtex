import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    """Custom styles defined locally and used only for this block"""
    content = s.Large + s.center_txt + s.container.layouts.center
    lime_bold = s.text.colors.lime + s.bold
    bold_green = s.project.colors.green_01 + s.bold
    green_title = bold_green + s.huge + s.center_txt
    brown_title = s.project.colors.brown_01 + s.LARGE
    orange_emphasis = s.project.colors.orange_01 + s.bold
    pink_title = s.project.colors.pink_01 + s.LARGE + s.bold
    link_style = s.text.colors.blue + s.text.decors.underline_text
bs = BlockStyles

def build():

    # Title
    with st_block(s.center_txt):
        st_write(bs.green_title, 
                 "Setting up the ", (bs.brown_title, 'NOTEBOOKS'), 
                 toc_lvl="2")
        st_space(size=3)

    # Main List
    with st_block(s.center_txt):
        with st_list(lt.ordered, li_style=bs.content) as l:
            
            # Item 1
            with l.item():
                st_write("open the ", (s.bold, "COURSEPACK"))
                st_write(" in a new tab in your browser")
                
            # Item 2
            with l.item():
                link_url = "https://docs.google.com/document/d/1eYtoLVpYgCrSpr8n75-jxqx3hrcnm1qUYYU0A4WXztY/edit?pli%3D1%23heading%3Dh.fhxl49mk9k3e"
                st_write("Go to section: ", (s.none, "Notebooks links", link_url))

            # Item 3
            with l.item():
                st_write('click on "link" of YOUR ', 
                         (bs.orange_emphasis, "Notebook URL"))
                st_write(s.project.colors.brown_01 + s.bold,
                         " (use your number printed on the paper sheet)")

            # Item 4
            with l.item():
                st_write("connect using ", 
                         (bs.lime_bold, 'YOUR gmail'), 
                         " account ")
                st_write("(same one used in the resources access form)")

            # Item 5 
            with l.item():
                st_write("You should see a screen close to this one:")
                st_image(uri="notebook_folder_01.png", width="1150px", height="735.34px")

            # Item 6
            with l.item():
                st_write((s.italic, "(optional)"), (s.project.bronze_01_bold, " Discover "), "the NOTEBOOK environment")

            # Item 7 (Complex Image/Text sequence)
            with l.item():
                st_write((s.italic, "(optional)"), " Bookmark the notebook")
                with st_span():
                    st_write("drag the ")
                    st_image(uri="key_lock_01.png", width="60px", height="64px")
                    st_write(" below in the bookmarks bar")
                
                st_image(uri="browser_bar_01.png", width="532px", height="230px")
                st_space(size=2)

            # Item 8 
            with l.item():
                st_write((s.italic,"(optional)"), " Backup notebooks folder")
                st_write(bs.bold_green, 'cf. section "Backup notebooks folder"') 
                st_write("in the ", (s.bold, "COURSEPACK"))
            
            # Item 9 
            with l.item():
                st_write("Open Notebook")
                st_write(bs.green_title, "-> ask the trainer")
                st_space(size=2)

            # Item 10 (Nested List)
            with l.item():
                st_write(bs.pink_title, "Duplicate the notebook")
                with st_list(lt.ordered,
                             l_style=s.container.lists.ordered_lowercase,
                             li_style=bs.content) as l2:
                    with l2.item(): st_write("right click + Duplicate")
                    with l2.item(): st_write("set a smart name")
   