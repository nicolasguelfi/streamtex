"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_interactive_widgets = stx.load_atomic_block("bck_interactive_widgets", __file__)
bck_forms_and_state = stx.load_atomic_block("bck_forms_and_state", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_interactive_widgets)
    st_include(bck_forms_and_state)
