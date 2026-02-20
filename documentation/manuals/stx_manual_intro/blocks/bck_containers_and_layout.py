"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_containers = stx.load_atomic_block("bck_containers", __file__)
bck_container_styles = stx.load_atomic_block("bck_container_styles", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_containers)
    st_include(bck_container_styles)
