"""Continuous fixture book for the list-alignment e2e (see blocks/__init__.py)."""
import blocks
import streamlit as st

from streamtex import st_book

st.set_page_config(page_title="list alignment e2e", layout="wide",
                   initial_sidebar_state="expanded")

st_book(blocks.MODULE_LIST)
