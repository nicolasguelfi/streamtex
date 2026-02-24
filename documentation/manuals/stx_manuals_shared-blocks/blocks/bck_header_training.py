"""Shared header block for training courses."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style
from streamtex.enums import Tags as t


class BlockStyles:
    """Shared header styles."""
    header = Style(
        "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        "padding: 40px 20px; border-radius: 8px;",
        "training_header"
    )
    header_text = Style("color: white;", "training_header_text")


def build():
    """Render a standard training course header."""
    st_space("v", 1)

    with st_block(BlockStyles.header):
        st_write(
            stx.StxStyles.huge + stx.StxStyles.bold + BlockStyles.header_text,
            "StreamTeX Training Course",
            tag=t.div
        )
        st_write(
            stx.StxStyles.large + BlockStyles.header_text,
            "A Streamlit-based content rendering framework",
            tag=t.div
        )
    st_space("v", 1)
