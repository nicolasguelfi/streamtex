"""Fixture slides for the navigation active-state e2e harness.

Purpose: exercise the FIVE navigation surfaces (sidebar TOC + Markers
tabs, floating widget, banner buttons, keyboard, wheel) in PAGINATED +
search-enabled mode, where ``data-stx-block`` is emitted so the
cross-context scroll-spy is live.

The deck is shaped to reproduce the three open navigation bugs the
refactor must fix (companion doc ``navigation-system-maintenance-v01.md``):

  * S6 — GROUP-HIGHLIGHT.  Page index 1 (``section-a``) deliberately
    emits THREE TOC entries (one H1 + two H2) on a single paginated
    page.  At 0.7.8 every entry whose ``page_idx == current_page`` is
    given an inline ``color:var(--stx-link-active-color)``, so all three
    light up simultaneously — the user-reported bug.  Every other page
    has a single heading.

  * S3 / S4 — COUNTER DESYNC after a double PageDown / double-click ▶.
    Five single-marker pages give the widget a clean 1..5 counter whose
    drift is measurable when two navigations are fired inside one rerun
    window.

The harness correlates "what is rendered" with "what is highlighted"
via the current page index (``window._stxPrevPage``), the marker label
shown in the floating widget, and the per-entry ``data-stx-block``
attribute on each sidebar link.
"""
from __future__ import annotations

import types

from streamtex import (
    st_block,
    st_marker,
    st_space,
    st_write,
)
from streamtex.enums import Tags as t
from streamtex.styles import Style

_PAGE = Style(
    "background:#0b1020; padding:24px; color:#f0f0f0; min-height:300px;",
    "nav_page",
)
_H1 = Style("color:#FFD700; font-size:26pt; font-weight:bold;", "nav_h1")
_H2 = Style("color:#9ecbff; font-size:18pt; font-weight:bold;", "nav_h2")
_BODY = Style("color:#d8d8d8; font-size:13pt;", "nav_body")


def _single_heading_slide(slide_id: str, title: str):
    """One marker + one H1 TOC entry — the common case."""

    def build():  # noqa: ANN202 — st_book calls build() with no args
        st_marker(slide_id)
        with st_block(_PAGE):
            st_write(_H1, title, tag=t.div, toc_lvl="1", label=title)
            st_space("v", 1)
            st_write(_BODY, f"Body content for {slide_id}.")

    return build


def _multi_heading_slide(slide_id: str, title: str, subs: list[str]):
    """One marker + one H1 + N H2 TOC entries on a SINGLE page.

    This is the page that reproduces the group-highlight bug: all N+1
    entries share ``page_idx == current_page`` and so all receive the
    inline active color at 0.7.8.
    """

    def build():  # noqa: ANN202
        st_marker(slide_id)
        with st_block(_PAGE):
            st_write(_H1, title, tag=t.div, toc_lvl="1", label=title)
            for sub in subs:
                st_space("v", 1)
                st_write(_H2, sub, tag=t.div, toc_lvl="2", label=sub)
                st_write(_BODY, f"Body for {sub}.")

    return build


# (slide_id, title, optional sub-headings)
_SPECS: list[tuple] = [
    ("intro",     "Introduction", None),
    ("section-a", "Section A",     ["A.1 Overview", "A.2 Details"]),  # multi-entry page → S6
    ("section-b", "Section B",     None),
    ("section-c", "Section C",     None),
    ("outro",     "Conclusion",    None),
]

MODULE_LIST: list[types.ModuleType] = []
for _spec in _SPECS:
    _sid, _title = _spec[0], _spec[1]
    _subs = _spec[2]
    _mod = types.ModuleType(f"nav_{_sid.replace('-', '_')}")
    if _subs:
        _mod.build = _multi_heading_slide(_sid, _title, _subs)
    else:
        _mod.build = _single_heading_slide(_sid, _title)
    _mod._slide_id = _sid
    MODULE_LIST.append(_mod)
