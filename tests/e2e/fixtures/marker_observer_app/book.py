"""Minimal streamtex app — fixture for the marker-observer e2e regression test.

The actual slide lives in slide_grid_with_blocks.py (st_book expects modules
that expose a `build()` function).
"""
import slide_grid_with_blocks
import streamlit as st

from streamtex import (
    BannerConfig,
    MarkerConfig,
    NumberingMode,
    PresentationConfig,
    SlideBreakConfig,
    SlideBreakMode,
    TOCConfig,
    set_presentation_config,
    set_slide_break_config,
    st_book,
)

st.set_page_config(
    page_title="marker observer e2e",
    layout="wide",
    initial_sidebar_state="expanded",
)

set_presentation_config(PresentationConfig(
    title="marker observer e2e",
    aspect_ratio="16/10",
    footer=False,
    hide_streamlit_header=False,
))
set_slide_break_config(SlideBreakConfig(
    mode=SlideBreakMode.FULL, space="1vh", space_before="1vh",
))

st_book(
    [slide_grid_with_blocks],
    paginate=True,
    toc_config=TOCConfig(
        numbering=NumberingMode.SIDEBAR_ONLY, sidebar_max_level=2, search=False
    ),
    marker_config=MarkerConfig(
        next_keys=["PageDown", "ArrowRight"],
        prev_keys=["PageUp", "ArrowLeft"],
        draggable=True, collapsible=True,
    ),
    banner=BannerConfig.hidden(),
    page_width=100,
    zoom=85,
)
