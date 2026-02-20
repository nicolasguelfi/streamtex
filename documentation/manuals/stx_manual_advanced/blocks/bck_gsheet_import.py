"""Composite block: Google Sheets Data Import."""
import streamtex as stx
from streamtex import st_include

bck_gsheet_import = stx.load_atomic_block("bck_gsheet_import", __file__)


class BlockStyles:
    pass


def build():
    st_include(bck_gsheet_import)
