"""Cache-build freeze fixture — paginated deck of 40 synthetic slides.

The shape mimics FC-260507-NG-SLIDES: paginate=True, marker navigation,
TOC sidebar, ~40 modules each emitting markers + styled blocks + grid
cells + ordered list items.  Used by tests/e2e/test_cache_build_freeze.py
to measure cold-load timing on Chromium.

No images / TikZ / LaTeX — the test isolates the marker_runtime observer
cost from heavyweight rendering primitives.
"""
import blocks
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
    page_title="cache-build freeze e2e",
    layout="wide",
    initial_sidebar_state="expanded",
)

set_presentation_config(PresentationConfig(
    title="cache-build freeze e2e",
    aspect_ratio="16/10",
    footer=False,
    hide_streamlit_header=False,
))
set_slide_break_config(SlideBreakConfig(
    mode=SlideBreakMode.FULL, space="1vh", space_before="1vh",
))

st_book(
    blocks.MODULE_LIST,
    paginate=True,
    toc_config=TOCConfig(
        numbering=NumberingMode.SIDEBAR_ONLY,
        sidebar_max_level=2,
        search=True,
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
