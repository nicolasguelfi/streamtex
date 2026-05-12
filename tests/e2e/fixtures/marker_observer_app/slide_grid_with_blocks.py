"""Single-slide fixture: a 2-column grid containing two styled blocks
(blue + teal with gold borders), each wrapped in a zoom.  Exercises
every marker kind targeted by the regression: block, grid, zoom.
"""
import streamlit as st

from streamtex import st_block, st_grid, st_marker, st_write, st_zoom
from streamtex.styles import Style

_BLUE = Style(
    "background: #1565C0 !important; padding: 24px; color: white !important; "
    "min-height: 180px; border: 4px solid #FFD700;",
    "e2e_blue",
)
_TEAL = Style(
    "background: #00695C !important; padding: 24px; color: white !important; "
    "min-height: 180px; border: 4px solid #FFD700;",
    "e2e_teal",
)


def build():
    st_marker("Grid with styled blocks")
    st.markdown("## Grid with styled blocks")
    with st_zoom(100):
        with st_grid(cols="49% 49%", gap="2%") as g:
            with g.cell():
                with st_zoom(80):
                    with st_block(_BLUE):
                        st_write("**Left** — blue with gold border")
            with g.cell():
                with st_zoom(80):
                    with st_block(_TEAL):
                        st_write("**Right** — teal with gold border")
