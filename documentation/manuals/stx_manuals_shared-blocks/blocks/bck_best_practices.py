"""Shared best practices block for training courses."""

import streamlit as st
from streamtex import *
import streamtex as stx


class BlockStyles:
    """Best practices block styles."""
    pass


def build():
    """Share best practices and patterns."""
    st_write(
        stx.StxStyles.large + stx.StxStyles.text.colors.reset,
        "Best Practices",
        toc_lvl="2"
    )
    st_space("v", 1)

    st_write(
        stx.StxStyles.large,
        "Follow these patterns for clean, maintainable code:"
    )
    st_space("v", 1)

    with st_list(list_type="ol"):
        st_write(
            stx.StxStyles.medium,
            "Use stx.* functions for ALL content (st.* only for interactivity)"
        )
        st_write(
            stx.StxStyles.medium,
            "Define one generic style, reuse everywhere"
        )
        st_write(
            stx.StxStyles.medium,
            "Use a single st_write() with tuples for inline mixed-style text"
        )
        st_write(
            stx.StxStyles.medium,
            "Never hardcode colors — let Streamlit handle dark/light mode"
        )
        st_write(
            stx.StxStyles.medium,
            "Use st_block() and st_span() for layout, not raw HTML"
        )
        st_write(
            stx.StxStyles.medium,
            "Keep blocks atomic and composable"
        )

    st_space("v", 2)
