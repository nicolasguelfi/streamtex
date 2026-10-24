"""Videos bounded by max_vw / max_vh: live and export fixture (#141)."""
import blocks
import streamlit as st

from streamtex import MarkerConfig, st_book

st.set_page_config(page_title="bounds e2e", layout="wide")
st_book(blocks.MODULE_LIST, marker_config=MarkerConfig())
