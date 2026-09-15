"""Paginated presentation fixture (see blocks/__init__.py).

The presentation flags come from the environment so the same deck can be
launched in several configurations by the e2e test:

* ``STX_E2E_CENTER``  — center_content  (default 1)
* ``STX_E2E_RATIO``   — enforce_ratio   (default 0)
* ``STX_E2E_FOOTER``  — footer          (default 1)
"""
import os

import blocks
import streamlit as st

from streamtex import BannerConfig, MarkerConfig, PresentationConfig, set_presentation_config, st_book

_flag = lambda name, default: os.environ.get(name, default) == "1"  # noqa: E731

st.set_page_config(page_title="presentation center e2e", layout="wide",
                   initial_sidebar_state="expanded")

set_presentation_config(PresentationConfig(
    title="presentation center e2e",
    aspect_ratio="16/9",
    center_content=_flag("STX_E2E_CENTER", "1"),
    enforce_ratio=_flag("STX_E2E_RATIO", "0"),
    footer=_flag("STX_E2E_FOOTER", "1"),
    hide_streamlit_header=False,
))

st_book(
    blocks.MODULE_LIST,
    paginate=True,
    marker_config=MarkerConfig(next_keys=["PageDown"], prev_keys=["PageUp"]),
    banner=BannerConfig.hidden(),
)
