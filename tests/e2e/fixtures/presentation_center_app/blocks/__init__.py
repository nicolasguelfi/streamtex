"""Fixture deck for the presentation vertical-centering e2e
(``test_presentation_center.py``).

Two paginated pages:

* page 0 — ``short``: a single title, far shorter than the viewport.  With
  ``center_content=True`` it must sit in the vertical middle of the page
  container.
* page 1 — ``tall``: several screens of content ending with a sentinel
  element ``#stx-e2e-end``; the page must keep scrolling and its height
  must not depend on ``center_content``.
"""
from __future__ import annotations

import types

from streamtex import st_block, st_html, st_marker, st_write
from streamtex.enums import Tags as t
from streamtex.styles import Style

_H1 = Style("color:#FFD700; font-size:40pt; font-weight:bold;", "pc_h1")
_TALL = Style("background:#101a33; color:#f0f0f0; padding:24px; min-height:3200px;", "pc_tall")
_BODY = Style("color:#d8d8d8; font-size:14pt;", "pc_body")


def _short():
    st_marker("short")
    st_write(_H1, "Title only", tag=t.div)


def _tall():
    st_marker("tall")
    st_write(_H1, "Tall page", tag=t.div)
    with st_block(_TALL):
        st_write(_BODY, "Several screens of content.")
    st_html('<div id="stx-e2e-end" style="height:24px;background:#c33;color:#fff;">END</div>')


MODULE_LIST: list[types.ModuleType] = []
for _name, _fn in (("short", _short), ("tall", _tall)):
    _mod = types.ModuleType(f"pc_{_name}")
    _mod.build = _fn
    MODULE_LIST.append(_mod)
