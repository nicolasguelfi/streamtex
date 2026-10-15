"""A sidebar link to another page names its slide (#127).

The live check (a real browser clicks the links) is
``tests/e2e/test_nav_sidebar_target.py``.
"""
from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pytest

import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex.book import _build_paginated_sidebar, _goto_href, _toc_target_marker
from streamtex.marker import MarkerConfig, marker_entries, reset_marker_registry, st_marker
from streamtex.toc import TOCConfig, reset_toc_registry, toc_entries
from streamtex.write import st_write


@pytest.fixture(autouse=True)
def registries():
    toc_mod.toc = None
    mk._registry = None
    reset_toc_registry(TOCConfig())
    reset_marker_registry(MarkerConfig())
    with patch("streamtex.marker._render"), patch("streamtex.write._render"), \
         patch("streamtex.write.consume_block_top_injected", return_value=True):
        yield
    mk._registry = None
    toc_mod.toc = None


def _on_page(page: int, n_markers: int, n_toc: int) -> None:
    """Give the last *n_markers* markers and *n_toc* headings the page *page*."""
    for e in marker_entries()[len(marker_entries()) - n_markers:]:
        e["page_idx"] = page
    for e in toc_entries()[len(toc_entries()) - n_toc:]:
        e["page_idx"] = page


def _deck():
    """Page 0: s1 + heading « Intro ». Page 1: s2, heading « Top », s3, s4,
    heading « Detail » (inside s4's slide), s5."""
    st_marker("s1")
    st_write("Intro", toc_lvl="1")
    _on_page(0, 1, 1)
    st_write("Top", toc_lvl="1")        # before every stop of page 1
    st_marker("s2")
    st_marker("s3")
    st_marker("s4")
    st_write("Detail", toc_lvl="2")
    st_marker("s5")
    _on_page(1, 4, 2)
    return {"markers": marker_entries(), "toc": toc_entries()}


def _toc(cache, title):
    return next(e for e in cache["toc"] if e["title"].endswith(title))


def test_a_heading_records_the_markers_registered_before_it():
    cache = _deck()
    assert [e["_markers_before"] for e in cache["toc"]] == [1, 1, 4]


def test_a_heading_lands_on_the_slide_that_holds_it():
    cache = _deck()
    assert _toc_target_marker(_toc(cache, "Detail"), cache["markers"]) == 3     # s4


def test_a_heading_before_every_stop_of_its_page_opens_the_page():
    cache = _deck()
    # the last marker before « Top » is s1, on page 0: the page's first marker
    assert _toc_target_marker(_toc(cache, "Top"), cache["markers"]) is None


def test_a_heading_with_its_own_marker_lands_on_it():
    st_marker("s1")
    _on_page(0, 1, 0)
    st_marker("s2")
    st_write("Own", toc_lvl="1", marker=True)       # registers its marker after the heading
    _on_page(1, 2, 1)
    own = toc_entries()[-1]
    assert _toc_target_marker(own, marker_entries()) == 2


def test_a_cache_written_before_the_field_opens_the_page():
    cache = _deck()
    detail = dict(_toc(cache, "Detail"))
    del detail["_markers_before"]
    assert _toc_target_marker(detail, cache["markers"]) is None


def test_goto_href():
    assert _goto_href(3, None) == "#stx-goto-3"
    assert _goto_href(3, 57) == "#stx-goto-3-57"


def _sidebar_html(cache, current_page):
    calls = []
    fake = MagicMock()
    fake.tabs.return_value = (MagicMock(), MagicMock())
    fake.markdown.side_effect = lambda html, **kw: calls.append(html)
    fake.session_state = {}
    with patch("streamtex.book.st", fake):
        _build_paginated_sidebar(cache, current_page, 2, TOCConfig(sidebar_max_level=2), MarkerConfig())
    return "\n".join(calls)


def _href(html, text):
    """The href of the sidebar link whose text ends with *text*."""
    links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]*)</a>', html)
    return next(h for h, t in links if t.strip().endswith(text))


def test_sidebar_links_to_another_page_name_their_marker():
    html = _sidebar_html(_deck(), 0)
    assert _href(html, "s4") == "#stx-goto-1-3"
    assert _href(html, "Detail") == "#stx-goto-1-3"      # the slide that holds it
    assert _href(html, "Top") == "#stx-goto-1"           # the page's first marker, as before


def test_sidebar_links_on_the_current_page_stay_anchors():
    cache = _deck()
    html = _sidebar_html(cache, 1)
    assert "#stx-goto-1" not in html
    assert "#stx-goto-0" in html                     # page 0 entries: s1 is its first marker
