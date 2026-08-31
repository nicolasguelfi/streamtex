"""Real-Chromium e2e for the EXPORT marker bar — hidden-marker parity (#45).

There was no e2e coverage of the static-export floating bar (the
10-scenario harness covers the live app only).  This file drives an
enriched export in Chromium over ``file://`` and pins the app-parity
contract of ``st_marker(hidden=True)``: absent from the popup, ALWAYS a
keyboard stop.

Fixture: 6 markers — V0, h1, h2, V3, h4, V5 (V = visible, h = hidden;
h1 carries an explicit ``key`` for the deep-link scenario).

Run:  uv run pytest -m e2e tests/e2e/test_export_marker_nav.py -v
Prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from streamtex.export_enrich import enrich_export_html  # noqa: E402

pytestmark = pytest.mark.e2e

VIEWPORT = {"width": 1280, "height": 720}

MARKERS = [
    {"index": 0, "label": "Vis zero", "anchor": "a0", "hidden": False},
    {"index": 1, "label": "", "anchor": "a1", "hidden": True, "key": "sub-one"},
    {"index": 2, "label": "", "anchor": "a2", "hidden": True},
    {"index": 3, "label": "Vis three", "anchor": "a3", "hidden": False},
    {"index": 4, "label": "", "anchor": "a4", "hidden": True},
    {"index": 5, "label": "Vis five", "anchor": "a5", "hidden": False},
]

MARKERS_ALL_VISIBLE = [
    {"index": 0, "label": "One", "anchor": "a0", "hidden": False},
    {"index": 1, "label": "Two", "anchor": "a1", "hidden": False},
    {"index": 2, "label": "Three", "anchor": "a2", "hidden": False},
]


def _raw_html(n_anchors: int) -> str:
    sections = "\n".join(
        f'<div id="a{i}">Section {i}</div><div style="height:1400px"></div>'
        for i in range(n_anchors)
    )
    return ("<html><head><title>deck</title><style>body{margin:0}</style>"
            f"</head>\n<body>\n{sections}\n</body></html>")


@pytest.fixture(scope="module")
def export_page(tmp_path_factory):
    out = tmp_path_factory.mktemp("export") / "deck.html"
    out.write_text(enrich_export_html(_raw_html(6), markers=MARKERS),
                   encoding="utf-8")
    return out


@pytest.fixture(scope="module")
def export_page_no_hidden(tmp_path_factory):
    out = tmp_path_factory.mktemp("export2") / "deck.html"
    out.write_text(
        enrich_export_html(_raw_html(3), markers=MARKERS_ALL_VISIBLE),
        encoding="utf-8")
    return out


@pytest.fixture(scope="module")
def browser():
    with playwright.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _open(browser, url: str):
    page = browser.new_page(viewport=VIEWPORT)
    page.goto(url)
    page.wait_for_selector("#stx-marker-nav")
    return page


def _counter(page) -> str:
    return page.locator("#stx-marker-nav .stx-mn-counter").text_content().strip()


def _label(page) -> str:
    return page.locator("#stx-marker-nav .stx-mn-label").text_content().strip()


def _anchor_top(page, anchor: str) -> float:
    return page.evaluate(
        f"document.getElementById('{anchor}').getBoundingClientRect().top")


def _wait_at(page, anchor: str) -> None:
    """Wait until the smooth scroll parked *anchor* at the top, then let
    the bar's 400 ms navigating window close and its scroll tracker's
    debounce settle on the same index (no snap-back)."""
    page.wait_for_function(
        "(a) => Math.abs(document.getElementById(a)"
        ".getBoundingClientRect().top) < 8",
        arg=anchor, timeout=5000)
    page.wait_for_timeout(650)


def _open_popup(page) -> None:
    page.locator("#stx-marker-nav .stx-mn-counter").click()
    page.wait_for_selector("#stx-marker-nav .stx-mn-popup", state="visible")


def test_pagedown_visits_every_marker_in_order(browser, export_page):
    """(a) N PageDown presses visit N anchors, hidden included."""
    page = _open(browser, export_page.as_uri())
    assert _counter(page) == "1 / 6"
    for expected_idx in range(1, 6):
        page.keyboard.press("PageDown")
        _wait_at(page, f"a{expected_idx}")
        assert _counter(page) == f"{expected_idx + 1} / 6"
    # At the end, PageDown clamps (no wrap) — app parity
    page.keyboard.press("PageDown")
    page.wait_for_timeout(650)
    assert _counter(page) == "6 / 6"
    page.close()


def test_pageup_walks_back_through_hidden(browser, export_page):
    page = _open(browser, export_page.as_uri())
    for i in range(1, 6):
        page.keyboard.press("PageDown")
        _wait_at(page, f"a{i}")
    page.keyboard.press("PageUp")
    _wait_at(page, "a4")
    assert _counter(page) == "5 / 6"
    page.close()


def test_bar_buttons_share_keyboard_traversal(browser, export_page):
    """The ◀ ▶ buttons stop on hidden markers too (app parity)."""
    page = _open(browser, export_page.as_uri())
    page.locator("#stx-marker-nav button", has_text="▶").click()
    _wait_at(page, "a1")
    assert _counter(page) == "2 / 6"
    page.close()


def test_label_between_visibles_shows_nearest_visible(browser, export_page):
    """On a hidden stop the label shows the next visible marker's label."""
    page = _open(browser, export_page.as_uri())
    page.keyboard.press("PageDown")  # -> a1 (hidden, label "")
    _wait_at(page, "a1")
    assert _label(page) == "Vis three"
    page.close()


def test_popup_lists_visible_only_numbered_globally(browser, export_page):
    """(b) Popup: 3 rows, global numbers 1. / 4. / 6."""
    page = _open(browser, export_page.as_uri())
    _open_popup(page)
    rows = page.locator("#stx-marker-nav .stx-mn-popup-item")
    assert rows.count() == 3
    texts = [rows.nth(i).text_content().strip() for i in range(3)]
    assert texts == ["1. Vis zero", "4. Vis three", "6. Vis five"]
    page.close()


def test_popup_click_navigates_to_global_index(browser, export_page):
    page = _open(browser, export_page.as_uri())
    _open_popup(page)
    page.locator("#stx-marker-nav .stx-mn-popup-item",
                 has_text="4. Vis three").click()
    _wait_at(page, "a3")
    assert _counter(page) == "4 / 6"
    page.close()


def test_deep_link_to_hidden_marker_lands_on_it(browser, export_page):
    """(c) ?marker=<key> of a HIDDEN marker still lands on it (0.7.27)."""
    page = _open(browser, export_page.as_uri() + "?marker=sub-one")
    _wait_at(page, "a1")
    assert _counter(page) == "2 / 6"
    page.close()


def test_hash_anchor_of_hidden_marker_lands_on_it(browser, export_page):
    page = _open(browser, export_page.as_uri() + "#a2")
    _wait_at(page, "a2")
    assert _counter(page) == "3 / 6"
    page.close()


def test_document_without_hidden_markers_unchanged(browser, export_page_no_hidden):
    """(d) No hidden markers -> behaviour identical to before."""
    page = _open(browser, export_page_no_hidden.as_uri())
    assert _counter(page) == "1 / 3"
    assert _label(page) == "One"
    page.keyboard.press("PageDown")
    _wait_at(page, "a1")
    assert _counter(page) == "2 / 3"
    _open_popup(page)
    rows = page.locator("#stx-marker-nav .stx-mn-popup-item")
    assert rows.count() == 3
    assert rows.nth(0).text_content().strip() == "1. One"
    page.close()
