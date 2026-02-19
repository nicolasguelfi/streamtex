"""Visual separator between blocks. Used by st_book(separator=...) — not a content block."""

import streamlit as st


class BlockStyles:
    pass
bs = BlockStyles


def build():
    st.html(
        '<div style="padding: 3em 0;">'
        '<hr style="border: none;'
        ' border-top: 2px solid rgba(74, 144, 217, 0.3);'
        ' margin: 0 10%;">'
        '</div>'
    )
