"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_charts_builtin = stx.load_atomic_block("bck_charts_builtin", __file__)
bck_dataframes_and_tables = stx.load_atomic_block("bck_dataframes_and_tables", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_charts_builtin)
    st_include(bck_dataframes_and_tables)
