"""Shared style basics block for training courses."""

import streamlit as st
from streamtex import *
import streamtex as sx


class BlockStyles:
    """Style basics block styles."""
    pass


def build():
    """Teach fundamental styling concepts."""
    st_write(
        sx.StreamTeX_Styles.large + sx.StreamTeX_Styles.text.colors.reset,
        "Understanding the Style System",
        toc_lvl="2"
    )
    st_space("v", 1)

    st_write(
        sx.StreamTeX_Styles.large,
        "StreamTeX styles are composable, reusable CSS rules."
    )
    st_space("v", 1)

    st_write(
        sx.StreamTeX_Styles.medium + sx.StreamTeX_Styles.text.colors.reset,
        (
            "Key concepts:",
        )
    )

    with st_list(list_type="ul"):
        st_write(sx.StreamTeX_Styles.medium, "Styles combine using the + operator")
        st_write(sx.StreamTeX_Styles.medium, "Custom styles inherit from StreamTeX_Styles")
        st_write(sx.StreamTeX_Styles.medium, "No hardcoded colors — let Streamlit handle themes")
        st_write(sx.StreamTeX_Styles.medium, "Reuse generic styles instead of creating duplicates")

    st_space("v", 2)
