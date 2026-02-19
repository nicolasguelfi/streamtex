import streamlit as st
import setup
from streamtex import st_book, TOCConfig, MarkerConfig
import blocks
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts

st.set_page_config(
    page_title="My Project",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

st.sidebar.title("Table of Contents")

toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.main_title + s.center_txt + s.text.wrap.nowrap,
    content_style=s.large + s.text.colors.reset
)

marker = MarkerConfig(
    auto_marker_on_toc=1,
    show_nav_ui=True,
    popup_open=False,
    next_keys=["PageDown", "n"],
    prev_keys=["PageUp", "p"],
)

sts.theme = dark

module_list = [
    blocks.bck_01_welcome,
    blocks.bck_02_text_and_styles,
    blocks.bck_03_containers_and_spacing,
    blocks.bck_04_grids,
    blocks.bck_05_lists,
    blocks.bck_06_images,
    blocks.bck_07_code_blocks,
    blocks.bck_08_overlays_and_includes,
    blocks.bck_09_interactivity,
]

st_book(module_list, toc_config=toc, marker_config=marker,
        separator=blocks.separator, paginate=True)
