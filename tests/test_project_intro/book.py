"""StreamTeX Introduction Course - Test Project (Intro Level)."""

import streamlit as st
import setup
import streamtex as sx
from streamtex import st_book, TOCConfig, MarkerConfig

from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts
import blocks

# Page configuration
st.set_page_config(
    page_title="StreamTeX - Introduction",
    layout="wide",
    initial_sidebar_state="collapsed"
)
sts.theme = dark

# Table of Contents configuration
toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.course_title + s.center_txt,
    content_style=s.large + s.text.colors.reset
)

# Marker configuration for navigation
marker_config = MarkerConfig(
    auto_marker_on_toc=True,
    keyboard_nav={"next": "Page_Down", "prev": "Page_Up"},
)

# Orchestrate composites in pedagogical order
st_book([
    blocks.bck_welcome_intro,
    blocks.bck_architecture_guide,

    # Text & styling
    blocks.bck_text_and_styling,
    blocks.bck_tags_enum,
    blocks.bck_style_composition,

    # Layout & content
    blocks.bck_containers_and_layout,
    blocks.bck_grids_and_lists,
    blocks.bck_list_styles,

    # Media & advanced
    blocks.bck_media_rendering,
    blocks.bck_navigation_and_organization,
    blocks.bck_zoom_and_responsive,
    blocks.bck_export_and_sharing,
], toc_config=toc, marker_config=marker_config, paginate=True)
