"""Paginated, search-enabled fixture for the navigation active-state e2e.

``search=True`` is required so ``data-stx-block`` is emitted on every
sidebar entry — that is what makes the cross-context scroll-spy live (it
is a no-op without it).  ``STX_USE_MARKER_RUNTIME=1`` must be set in the
environment (the harness does this) or ``inject_marker_runtime()`` is a
no-op and scroll-spy never installs.
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
    page_title="nav active-state e2e",
    layout="wide",
    initial_sidebar_state="expanded",
)

set_presentation_config(PresentationConfig(
    title="nav active-state e2e",
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
    zoom=100,
)
