import streamlit as st
import setup
import streamtex as stx
from streamtex import st_book, TOCConfig, MarkerConfig, BannerConfig
from pathlib import Path

from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts
import blocks

# Configure static sources
stx.set_static_sources([str(Path(__file__).parent / "static")])

# Page configuration
st.set_page_config(
    page_title="My Project",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject dark theme
sts.theme = dark

# Table of Contents
toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.main_title + s.center_txt + s.text.wrap.nowrap,
    content_style=s.large + s.text.colors.reset,
    sidebar_max_level=2,
    search=True,
)

# Marker navigation (PageUp/PageDown)
marker_config = MarkerConfig(
    auto_marker_on_toc=1,
    next_keys=["PageDown"],
    prev_keys=["PageUp"],
)

# Orchestrate blocks
st_book(
    [
        blocks.bck_01_welcome,
        blocks.bck_02_text_and_styles,
        blocks.bck_03_containers_and_spacing,
        blocks.bck_04_grids,
        blocks.bck_05_lists,
        blocks.bck_06_images,
        blocks.bck_07_code_blocks,
        blocks.bck_08_overlays_and_includes,
        blocks.bck_09_interactivity,
    ],
    toc_config=toc,
    marker_config=marker_config,
    paginate=True,
    banner=BannerConfig.full(),
    inspector=stx.InspectorConfig(enabled=True),
)
