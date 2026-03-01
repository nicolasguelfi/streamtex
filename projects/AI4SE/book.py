"""AI4SE — Generative Software Engineering course."""

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
    page_title="AI4SE — Generative Software Engineering",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject dark theme
sts.theme = dark

# Table of Contents
toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.section_title + s.center_txt + s.text.wrap.nowrap,
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
        blocks.bck_title,
        blocks.bck_survey_ai_tools,
        blocks.bck_survey_dev_ides,
    ],
    toc_config=toc,
    marker_config=marker_config,
    paginate=True,
    banner=BannerConfig.full(),
    inspector=stx.InspectorConfig(enabled=True),
)
