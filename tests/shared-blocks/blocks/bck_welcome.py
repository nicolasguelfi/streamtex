"""Shared welcome block for training courses."""

import streamlit as st
from streamtex import *
from streamtex.styles import Style
import streamtex as sx
from streamtex.enums import Tags as t


class BlockStyles:
    """Welcome block styles."""
    pass


def build():
    """Render a standard welcome message."""
    st_space("v", 2)
    with st_block(Style("text-align: center;", "inline_style")):
        st_write(
            sx.StreamTeX_Styles.huge + sx.StreamTeX_Styles.text.colors.reset,
            "Welcome!",
            tag=t.h1,
            toc_lvl="1"
        )
        st_space("v", 1)
        st_write(
            sx.StreamTeX_Styles.large,
            "This course teaches you everything about StreamTeX — "
            "from basic text rendering to advanced layout techniques."
        )
        st_space("v", 1)
        st_write(
            sx.StreamTeX_Styles.medium,
            "Navigate using the sidebar or scroll through sequentially."
        )
    st_space("v", 2)
