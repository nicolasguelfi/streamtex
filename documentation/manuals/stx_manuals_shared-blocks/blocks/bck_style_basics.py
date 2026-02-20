"""Shared style basics block for training courses."""

import streamlit as st
from streamtex import *
import streamtex as stx


class BlockStyles:
    """Style basics block styles."""
    pass


def build():
    """Teach fundamental styling concepts."""
    st_write(
        stx.StxStyles.large + stx.StxStyles.text.colors.reset,
        "Understanding the Style System",
        toc_lvl="2"
    )
    st_space("v", 1)

    st_write(
        stx.StxStyles.large,
        "StreamTeX styles are composable, reusable CSS rules."
    )
    st_space("v", 1)

    st_write(
        stx.StxStyles.medium + stx.StxStyles.text.colors.reset,
        (
            "Key concepts:",
        )
    )

    with st_list(list_type="ul"):
        st_write(stx.StxStyles.medium, "Styles combine using the + operator")
        st_write(stx.StxStyles.medium, "Custom styles inherit from StxStyles")
        st_write(stx.StxStyles.medium, "No hardcoded colors — let Streamlit handle themes")
        st_write(stx.StxStyles.medium, "Reuse generic styles instead of creating duplicates")

    st_space("v", 2)
