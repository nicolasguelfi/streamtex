"""Shared footer block for training courses."""

import streamlit as st
from streamtex import *
import streamtex as stx


class BlockStyles:
    """Shared footer styles."""
    pass


def build():
    """Render a standard training course footer."""
    st_space("v", 2)
    st.divider()
    st_write(
        stx.StxStyles.small + stx.StxStyles.text.colors.reset + stx.StxStyles.center_txt,
        "StreamTeX Training Course © 2026 | All rights reserved"
    )
    st_write(
        stx.StxStyles.small,
        "For more information, visit: https://github.com/streamtex"
    )
