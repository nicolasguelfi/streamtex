"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_grid_basics = stx.load_atomic_block("bck_grid_basics", __file__)
bck_grid_cell_styles = stx.load_atomic_block("bck_grid_cell_styles", __file__)
bck_lists = stx.load_atomic_block("bck_lists", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_grid_basics)
    st_include(bck_grid_cell_styles)
    st_include(bck_lists)
