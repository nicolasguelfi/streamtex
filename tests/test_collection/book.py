"""StreamTeX Collection - Test Hub with Modern Design."""

import streamlit as st
import setup
from streamtex import st_book
from custom.themes import dark
import streamtex.styles as sts
import blocks

st.set_page_config(
    page_title="StreamTeX Test Collection",
    layout="wide",
    initial_sidebar_state="collapsed"
)
sts.theme = dark

# Display the collection home with modern design
st_book([
    blocks.bck_home_collection,
], paginate=False)
