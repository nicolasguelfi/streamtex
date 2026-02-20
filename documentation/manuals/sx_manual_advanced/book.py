"""StreamTeX Advanced Course - Test Project (Advanced Level + Phase 1/2 Features)."""

import streamlit as st
import setup
import streamtex as sx
from streamtex import st_book, TOCConfig, MarkerConfig

from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts
import blocks

# ============================================================================
# PHASE 1 & 2 DEMO: Multi-source blocks and static resolution
# ============================================================================

# Configure shared blocks (Phase 1: LazyBlockRegistry)
from pathlib import Path
_shared_blocks_path = str(Path(__file__).parent.parent / "sx_manuals_shared-blocks" / "blocks")
_static_shared_path = str(Path(__file__).parent.parent / "sx_manuals_shared-blocks" / "static")

shared_blocks = sx.LazyBlockRegistry([_shared_blocks_path])

# Configure static sources for multi-directory resolution
sx.set_static_sources([
    str(Path(__file__).parent / "static"),
    _static_shared_path,
])

# ============================================================================
# Page configuration
# ============================================================================
st.set_page_config(
    page_title="StreamTeX - Advanced",
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

# ============================================================================
# Orchestrate composites in pedagogical order
#
# Note: This includes 3 new demo blocks that showcase Phase 1 (shared blocks)
# and Phase 2 (collections) features
# ============================================================================
st_book([
    # Welcome page (gradient header + level badge)
    blocks.bck_level_badge,

    # Phase 1: Multi-source blocks and static resolution
    blocks.bck_lazy_block_registry_demo,
    blocks.bck_shared_blocks_usage,
    blocks.bck_static_resolution_demo,

    # Advanced features (continued from intro)
    blocks.bck_overlays_positioning,
    blocks.bck_visibility_control,
    blocks.bck_custom_themes,
    blocks.bck_navigation_markers,

    # Library patterns and best practices
    blocks.bck_block_helpers_patterns,

    # Phase 2: Collections and multi-project management
    blocks.bck_collections_and_discovery,

    blocks.bck_static_assets_loading,
    blocks.bck_export_aware_widgets,
    blocks.bck_hover_and_preview,
    blocks.bck_deployment_strategies,
    blocks.bck_interactive_and_state,
    blocks.bck_data_and_charts,
    blocks.bck_ui_components,
    blocks.bck_diagrams_and_viz,

    # Shared block footer
    shared_blocks.bck_footer_training,
], toc_config=toc, marker_config=marker_config, paginate=True)
