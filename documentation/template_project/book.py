import streamlit as st 
import setup
from streamtex import st_book, TOCConfig
import blocks
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts

st.set_page_config(page_title="Web Book Name",
                    page_icon=None,
                    layout="wide",
                    initial_sidebar_state="collapsed",
                    menu_items=None)

st.sidebar.title("Table of Contents")

toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.title_giant_green_01 + s.center_txt + s.text.wrap.nowrap,
    content_style=s.large + s.text.colors.reset)

sts.theme = dark


module_list = [
    blocks.base,
    blocks.show_off,
]

st_book(module_list, toc_config=toc)



