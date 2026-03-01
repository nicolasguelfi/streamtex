"""Test project — Sample document blocks (bckcp_*).

Reduced to ~20 representative blocks for debugging.
Full list is commented out below.

Run with:
    uv run streamlit run projects/convert_html_to_streamtex/tests/test_doc/book.py
"""

import streamlit as st
import setup  # noqa: F401 — configures sys.path
import streamtex as stx
from streamtex import st_book, TOCConfig, MarkerConfig, BannerConfig
from pathlib import Path

from shared.custom.styles import Styles as s
from shared.custom.themes import doc_dark
import streamtex.styles as sts
from shared import blocks

# Configure static sources (for images)
stx.set_static_sources([
    str(Path(__file__).resolve().parent.parent.parent / "shared" / "static"),
])

# Page configuration
st.set_page_config(
    page_title="Test — Document Blocks (bckcp_*)",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# NOTE: sts.theme = doc_dark does NOT work (Python module rebinding issue).
# Must mutate the dict in-place so core.theme sees the overrides.
sts.theme.update(doc_dark)

# TOC configuration
toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.doc.titles.h2,
    sidebar_max_level=2,
    search=True,
)

# Marker configuration for PageUp/PageDown navigation
marker_config = MarkerConfig(
    auto_marker_on_toc=1,
    next_keys=["PageDown"],
    prev_keys=["PageUp"],
)

# ~20 representative bckcp_* blocks (diverse categories)
st_book([
    # --- Title pages ---
    blocks.bckcp_title_page_aiai,
    blocks.bckcp_title_part_01,
    blocks.bckcp_title_session_01,
    blocks.bckcp_title_ethics,
    # --- Content ---
    blocks.bckcp_ai_domain,
    blocks.bckcp_definition_intelligence,
    blocks.bckcp_general_information,
    blocks.bckcp_ai_technical_tools,
    # --- Ethics ---
    blocks.bckcp_ethics_ai_act,
    blocks.bckcp_ethics_human_rights,
    blocks.bckcp_ethics_stats,
    # --- Deep learning ---
    blocks.bckcp_cnn_basics,
    blocks.bckcp_neural_networls_intro_basics,
    blocks.bckcp_mnist,
    # --- Practice / Links ---
    blocks.bckcp_practice_access_link_aiai,
    blocks.bckcp_practice_prompt_engineering,
    blocks.bckcp_notebooks_links,
    # --- Schedule / Tables ---
    blocks.bckcp_schedule_aiai,
    blocks.bckcp_references_ai4ec,
    # --- Misc ---
    blocks.bckcp_useful_information_aiai,
    blocks.bckcp_python_libraries,
], toc_config=toc, marker_config=marker_config, paginate=True,
   banner=BannerConfig.full(),
   inspector=stx.InspectorConfig(enabled=True))
