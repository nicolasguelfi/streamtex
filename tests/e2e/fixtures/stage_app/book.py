"""Videos that dominate the screen: theater, fit, fullscreen — live and export fixture (#56).

``STAGE_PAGINATE=1`` shows the same slides one page at a time.
"""
import os

import blocks
import streamlit as st

from streamtex import MarkerConfig, TOCConfig, st_book

st.set_page_config(page_title="stage e2e", layout="wide")
st_book(blocks.MODULE_LIST, toc_config=TOCConfig(), marker_config=MarkerConfig(),
        paginate=os.environ.get("STAGE_PAGINATE") == "1")
