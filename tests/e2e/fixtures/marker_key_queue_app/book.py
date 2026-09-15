"""Paginated fixture for the marker key-queue e2e (see blocks/__init__.py)."""
import blocks
import streamlit as st

from streamtex import BannerConfig, MarkerConfig, NumberingMode, TOCConfig, st_book

st.set_page_config(page_title="marker key-queue e2e", layout="wide",
                   initial_sidebar_state="expanded")

st_book(
    blocks.MODULE_LIST,
    paginate=True,
    toc_config=TOCConfig(numbering=NumberingMode.SIDEBAR_ONLY, sidebar_max_level=1),
    marker_config=MarkerConfig(
        next_keys=["PageDown", "ArrowRight"],
        prev_keys=["PageUp", "ArrowLeft"],
    ),
    banner=BannerConfig.hidden(),
)
