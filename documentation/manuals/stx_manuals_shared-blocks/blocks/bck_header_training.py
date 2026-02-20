"""Shared header block for training courses."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style
from streamtex.enums import Tags as t


class BlockStyles:
    """Shared header styles."""
    pass


def build():
    """Render a standard training course header."""
    st_space("v", 1)
    
    # Header style with gradient background
    header_style = Style(
        "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        "padding: 40px 20px; border-radius: 8px;",
        "training_header"
    )
    
    with st_block(header_style):
        st_write(
            stx.StxStyles.huge + stx.StxStyles.text.colors.white,
            "StreamTeX Training Course",
            tag=t.div
        )
        st_write(
            stx.StxStyles.large + stx.StxStyles.text.colors.white,
            "A Streamlit-based content rendering framework",
            tag=t.div
        )
    st_space("v", 1)
