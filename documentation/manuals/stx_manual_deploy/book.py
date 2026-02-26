"""StreamTeX Deployment Guide — Manual covering all deployment options."""

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
    page_title="StreamTeX - Deployment Guide",
    layout="wide",
    initial_sidebar_state="collapsed"
)
sts.theme = dark

# Table of Contents configuration
toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.course_title + s.center_txt,
    content_style=s.large + s.text.colors.reset,
    search=True,
)

# Marker configuration for navigation
marker_config = MarkerConfig(
    auto_marker_on_toc=1,
    next_keys=["PageDown"],
    prev_keys=["PageUp"],
)

# Orchestrate blocks in deployment-logical order:
#   1. Overview & decision matrix
#   2. Preflight checks (common to all)
#   3. Docker local (the foundation)
#   4. Streamlit Cloud (simplest cloud, no Docker)
#   5. HuggingFace Spaces (free cloud with Docker)
#   6. Render.com (production cloud with Docker)
#   7. GCP VM + Ansible (full control)
#   8. CI/CD (ties everything together)
st_book([
    blocks.bck_level_badge,
    blocks.bck_welcome,
    blocks.bck_preflight,
    blocks.bck_docker_local,
    blocks.bck_streamlit_cloud,
    blocks.bck_huggingface,
    blocks.bck_render,
    blocks.bck_gcp_ansible,
    blocks.bck_ci_cd,
], toc_config=toc, marker_config=marker_config, paginate=True,
   banner=BannerConfig.full(),
   inspector=stx.InspectorConfig(enabled=True))
