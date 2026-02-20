"""Composite block: Bibliography & References."""
import streamtex as stx
from streamtex import st_include

bck_bibliography = stx.load_atomic_block("bck_bibliography_references", __file__)


class BlockStyles:
    pass


def build():
    st_include(bck_bibliography)
