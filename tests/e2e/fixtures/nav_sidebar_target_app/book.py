"""Paginated deck whose middle page holds 20 slides (sidebar targets, #127).

Pages: slide 1 | slides 2-21 | slides 22-24. Every slide has a marker named
``s<n>`` (its slide number); slide 12 also holds a level-2 heading
``detail twelve`` that is not a marker. ``STX_E2E_CONTINUOUS=1`` renders
the same deck in continuous mode.
"""
import os

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
    page_title="nav sidebar target e2e",
    layout="wide",
    initial_sidebar_state="expanded",
)

set_presentation_config(PresentationConfig(
    title="nav sidebar target e2e",
    aspect_ratio="16/10",
    enforce_ratio=False,          # a page of 20 slides scrolls (the default clips it)
    footer=False,
    hide_streamlit_header=False,
))
set_slide_break_config(SlideBreakConfig(
    mode=SlideBreakMode.FULL, space="1vh", space_before="1vh",
))

st_book(
    blocks.MODULE_LIST,
    paginate=os.environ.get("STX_E2E_CONTINUOUS") != "1",
    toc_config=TOCConfig(
        numbering=NumberingMode.NONE,
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
