"""Paginated fixture for the bleed-through e2e regression."""
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
    page_title="paginated bleed-through e2e",
    layout="wide",
    initial_sidebar_state="expanded",
)

set_presentation_config(PresentationConfig(
    title="paginated bleed-through e2e",
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
        search=False,
    ),
    marker_config=MarkerConfig(
        next_keys=["PageDown", "ArrowRight"],
        prev_keys=["PageUp", "ArrowLeft"],
        draggable=True, collapsible=True,
    ),
    banner=BannerConfig.hidden(),
    page_width=100,
    zoom=100,
)
