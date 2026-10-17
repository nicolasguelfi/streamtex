"""Sized videos and an autoplay without muted: live and export fixture (#126, #35)."""
import blocks
import streamlit as st

from streamtex import MarkerConfig, st_book

st.set_page_config(page_title="media e2e", layout="wide")
st_book(blocks.MODULE_LIST, marker_config=MarkerConfig())
