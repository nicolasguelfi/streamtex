"""StreamTeX Collection - Test Hub with Modern Design."""

import streamlit as st
import setup
from streamtex import st_book, TOCConfig
from custom.themes import dark
import streamtex.styles as sts
import blocks

st.set_page_config(
    page_title="StreamTeX Test Collection",
    layout="wide",
    initial_sidebar_state="collapsed"
)
sts.theme = dark

# Display the collection home with modern design and management guide
toc = TOCConfig(numerate_titles=False, search=True)

st_book([
    blocks.bck_home_collection,
    blocks.bck_collection_management,
], toc_config=toc, paginate=False)
