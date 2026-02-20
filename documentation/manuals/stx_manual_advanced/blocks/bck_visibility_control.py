"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_visibility = stx.load_atomic_block("bck_visibility", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_visibility)
