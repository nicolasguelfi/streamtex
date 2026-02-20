"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_tabs_expanders_popover = stx.load_atomic_block("bck_tabs_expanders_popover", __file__)
bck_dynamic_content = stx.load_atomic_block("bck_dynamic_content", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_tabs_expanders_popover)
    st_include(bck_dynamic_content)
