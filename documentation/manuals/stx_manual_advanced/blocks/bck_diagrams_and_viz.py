"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_graphviz_diagrams = stx.load_atomic_block("bck_graphviz_diagrams", __file__)
bck_mermaid_diagrams = stx.load_atomic_block("bck_mermaid_diagrams", __file__)
bck_tikz_diagrams = stx.load_atomic_block("bck_tikz_diagrams", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_graphviz_diagrams)
    st_include(bck_mermaid_diagrams)
    st_include(bck_tikz_diagrams)
