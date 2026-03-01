"""Composite block — Document languages (Markdown & LaTeX)."""

import streamtex as stx
from streamtex import st_include

bck_markdown_rendering = stx.load_atomic_block("bck_markdown_rendering", __file__)
bck_latex_rendering = stx.load_atomic_block("bck_latex_rendering", __file__)
bck_syntax_highlighting = stx.load_atomic_block("bck_syntax_highlighting", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_markdown_rendering)
    st_include(bck_latex_rendering)
    st_include(bck_syntax_highlighting)
