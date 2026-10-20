"""Countdown racks: chain, parallel, card types, break screen, alarms — live and export fixture (#52)."""
import blocks
import streamlit as st

from streamtex import MarkerConfig, TOCConfig, st_book

st.set_page_config(page_title="countdown e2e", layout="wide")
st_book(blocks.MODULE_LIST, toc_config=TOCConfig(), marker_config=MarkerConfig())
