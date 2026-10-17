"""Lists whose item text is in st_zoom (#112): live and export fixture."""
import blocks
import streamlit as st

from streamtex import MarkerConfig, st_book

st.set_page_config(page_title="list zoom e2e", layout="wide")
st_book(blocks.MODULE_LIST, marker_config=MarkerConfig())
