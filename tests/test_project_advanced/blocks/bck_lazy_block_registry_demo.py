"""Composite: Lazy Block Registry Demo."""

import streamlit as st
from streamtex import st_write, st_space, st_block
import streamtex as sx


class BlockStyles:
    """Composite block styles."""
    main_title = sx.StreamTeX_Styles.large + sx.StreamTeX_Styles.bold


def build():
    """Demo section - custom content for Phase 1/2 features."""
    st_write(
        BlockStyles.main_title,
        "Lazy Block Registry Demo",
        toc_lvl="1"
    )
    st_space("v", 1)
    st_write(
        sx.StreamTeX_Styles.large,
        "This section demonstrates the feature. Content coming soon!"
    )
    st_space("v", 2)
