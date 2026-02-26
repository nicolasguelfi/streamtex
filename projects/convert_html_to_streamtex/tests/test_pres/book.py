"""Test project — Sample presentation blocks (bck_*).

Reduced to ~20 representative blocks for debugging.
Full list is commented out below.

Run with:
    uv run streamlit run projects/convert_html_to_streamtex/tests/test_pres/book.py
"""

import streamlit as st
import setup  # noqa: F401 — configures sys.path
import streamtex as stx
from streamtex import st_book, TOCConfig, MarkerConfig, BannerConfig
from pathlib import Path

from shared.custom.styles import Styles as s
from shared.custom.themes import pres_dark
import streamtex.styles as sts
from shared import blocks

# Configure static sources (for images)
stx.set_static_sources([
    str(Path(__file__).resolve().parent.parent.parent / "shared" / "static"),
])

# Page configuration
st.set_page_config(
    page_title="Test — Presentation Blocks (bck_*)",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# NOTE: sts.theme = pres_dark does NOT work (Python module rebinding issue).
# Must mutate the dict in-place so core.theme sees the overrides.
sts.theme.update(pres_dark)

# TOC configuration
toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.pres.titles.h2,
    search=True,
)

# Marker configuration for PageUp/PageDown navigation
marker_config = MarkerConfig(
    auto_marker_on_toc=1,
    next_keys=["PageDown"],
    prev_keys=["PageUp"],
)

# ~20 representative bck_* blocks (diverse categories)
st_book([
    # --- Titles / Welcome ---
    blocks.bck_title_basic_concepts,
    blocks.bck_title_break,
    blocks.bck_training_title_aiai_dlh,
    blocks.bck_welcome_screen_aiai,
    # --- Content / Sessions ---
    blocks.bck_content_aiai_all,
    blocks.bck_session_2_content_aiai,
    blocks.bck_course_pack_reminder,
    # --- Deep learning ---
    blocks.bck_deep_learning_part_2,
    blocks.bck_deep_learning_part_3_a_cnn,
    blocks.bck_basic_concepts_mnist,
    # --- Diagrams ---
    blocks.bck_diagram_cnn,
    blocks.bck_diagram_ann,
    blocks.bck_diagram_activation_functions,
    # --- Ethics ---
    blocks.bck_ethics_frameworks_eu,
    blocks.bck_ethics_overview,
    # --- Images ---
    blocks.bck_image_break_dolphins,
    blocks.bck_image_gif_yolo,
    # --- Practice / Workshop ---
    blocks.bck_practice_mnist_keras_1,
    blocks.bck_designing_your_chatbot_practice,
    # --- Society ---
    blocks.bck_society_overview,
    # --- Showcase ---
    blocks.bck_showcase_text_generation_all,
], toc_config=toc, marker_config=marker_config, paginate=True,
   banner=BannerConfig.full(),
   inspector=stx.InspectorConfig(enabled=True))
