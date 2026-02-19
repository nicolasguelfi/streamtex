import streamlit as st
import setup
from streamtex import st_book, TOCConfig, MarkerConfig
import blocks
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts


st.set_page_config(
    page_title="StreamTeX Training Course",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.course_title + s.center_txt + s.text.wrap.nowrap,
    content_style=s.large + s.text.colors.reset
)

sts.theme = dark

marker = MarkerConfig(
    auto_marker_on_toc=1,
    show_nav_ui=True,
    popup_open=False,
    next_keys=["PageDown", "n", "m"],
    prev_keys=["PageUp", "p", "l"],
)

st_book([
    blocks.bck_00_welcome,
    blocks.bck_01_architecture,
    blocks.bck_02_style_system,
    blocks.bck_03_custom_styles,
    blocks.bck_04_spacing,
    blocks.bck_05_text_basics,
    blocks.bck_06_containers,
    blocks.bck_07_text_styles,
    blocks.bck_08_container_styles,
    blocks.bck_09_text_inline,
    blocks.bck_10_grid_basics,
    blocks.bck_11_grid_cell_styles,
    blocks.bck_12_lists,
    blocks.bck_13_images,
    blocks.bck_14_overlays,
    blocks.bck_15_toc,
    blocks.bck_16_visibility,
    blocks.bck_17_themes,
    blocks.bck_18_best_practices,
    blocks.bck_19_static_assets,
    blocks.bck_21_export_html,
    blocks.bck_22_deploy_docker,
    blocks.bck_23_deploy_huggingface,
    blocks.bck_24_deploy_cloud,
    blocks.bck_25_interactive_widgets,
    blocks.bck_26_forms_and_state,
    blocks.bck_27_charts_builtin,
    blocks.bck_28_dataframes_and_tables,
    blocks.bck_29_tabs_expanders_popover,
    blocks.bck_30_dynamic_content,
    blocks.bck_31_graphviz_diagrams,
], toc_config=toc, marker_config=marker, separator=blocks.separator,
    export_title="StreamTeX Training Course", paginate=True)
