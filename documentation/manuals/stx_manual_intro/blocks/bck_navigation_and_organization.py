"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_toc = stx.load_atomic_block("bck_toc", __file__)
bck_markers = stx.load_atomic_block("bck_markers", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_toc)
    st_include(bck_markers)
