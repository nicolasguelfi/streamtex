"""Composite block — Marker Navigation (groups 3 atomic blocks)."""

import streamtex as stx
from streamtex import st_include


bck_markers = stx.load_atomic_block("bck_markers", __file__)
bck_marker_config = stx.load_atomic_block("bck_marker_config", __file__)
bck_marker_pagination = stx.load_atomic_block("bck_marker_pagination", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for the Marker Navigation section."""
    st_include(bck_markers)
    st_include(bck_marker_config)
    st_include(bck_marker_pagination)
