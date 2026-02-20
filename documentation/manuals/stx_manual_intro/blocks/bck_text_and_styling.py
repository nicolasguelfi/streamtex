"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_text_basics = stx.load_atomic_block("bck_text_basics", __file__)
bck_text_styles = stx.load_atomic_block("bck_text_styles", __file__)
bck_text_inline = stx.load_atomic_block("bck_text_inline", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_text_basics)
    st_include(bck_text_styles)
    st_include(bck_text_inline)
