"""StreamTeX Collection - Test Hub with Modern Design."""

import blocks
import setup  # noqa: F401  (side-effect: adds project dir to sys.path)
import streamlit as st
from custom.themes import dark

import streamtex as stx
import streamtex.styles as sts
from streamtex import TOCConfig, st_book

st.set_page_config(
    page_title="StreamTeX Test Collection",
    layout="wide",
    initial_sidebar_state="collapsed"
)
sts.theme = dark

# Display the collection home (single page: header + cards)
toc = TOCConfig(numerate_titles=False, toc_position=None, search=True)

st_book([
    blocks.bck_home,
], toc_config=toc, paginate=False,
   inspector=stx.InspectorConfig(enabled=True))
