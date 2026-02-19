"""Shared footer block for training courses."""

import streamlit as st
from streamtex import *
import streamtex as sx


class BlockStyles:
    """Shared footer styles."""
    pass


def build():
    """Render a standard training course footer."""
    st_space("v", 2)
    st.divider()
    st_write(
        sx.StreamTeX_Styles.small + sx.StreamTeX_Styles.text.colors.reset + "center",
        "StreamTeX Training Course © 2026 | All rights reserved"
    )
    st_write(
        sx.StreamTeX_Styles.small,
        "For more information, visit: https://github.com/streamtex"
    )
