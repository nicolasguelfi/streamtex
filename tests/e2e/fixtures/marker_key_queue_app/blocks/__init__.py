"""Fixture deck for the marker key-queue e2e (``test_marker_key_queue.py``).

Twelve paginated pages:

* pages 0..7 — ONE marker each, so every next/prev key is a page change
  (a Streamlit rerun + widget re-injection = the window where a key used
  to be dropped);
* pages 8..11 — TWO markers each, separated by a tall spacer, so that
  ``prev`` from the first marker of a page lands on the LAST marker of the
  previous page by *scrolling* — the behaviour that depends on the widget
  init running after book.py's scroll resets (must stay intact).
"""
from __future__ import annotations

import types

from streamtex import st_block, st_marker, st_space, st_write
from streamtex.enums import Tags as t
from streamtex.styles import Style

_PAGE = Style("background:#0b1020; padding:24px; color:#f0f0f0; min-height:300px;", "kq_page")
_TALL = Style("background:#101a33; padding:24px; color:#f0f0f0; min-height:1400px;", "kq_tall")
_H1 = Style("color:#FFD700; font-size:26pt; font-weight:bold;", "kq_h1")
_BODY = Style("color:#d8d8d8; font-size:13pt;", "kq_body")

SINGLE_PAGES = 8
DOUBLE_PAGES = 4
TOTAL_PAGES = SINGLE_PAGES + DOUBLE_PAGES


def _single(sid: str, title: str):
    def build():  # noqa: ANN202 — st_book calls build() with no args
        st_marker(sid)
        with st_block(_PAGE):
            st_write(_H1, title, tag=t.div, toc_lvl="1", label=title)
            st_space("v", 1)
            st_write(_BODY, f"Body for {sid}.")
    return build


def _double(sid: str, title: str):
    def build():  # noqa: ANN202
        st_marker(f"{sid}-a")
        with st_block(_TALL):
            st_write(_H1, f"{title} (a)", tag=t.div, toc_lvl="1", label=f"{title} (a)")
            st_write(_BODY, f"Top of {sid}.")
        st_marker(f"{sid}-b")
        with st_block(_PAGE):
            st_write(_H1, f"{title} (b)", tag=t.div, toc_lvl="1", label=f"{title} (b)")
            st_write(_BODY, f"Bottom of {sid}.")
    return build


MODULE_LIST: list[types.ModuleType] = []
for _i in range(TOTAL_PAGES):
    _mod = types.ModuleType(f"kq_page_{_i}")
    _mod.build = (_single if _i < SINGLE_PAGES else _double)(f"kq-{_i}", f"Page {_i}")
    MODULE_LIST.append(_mod)
