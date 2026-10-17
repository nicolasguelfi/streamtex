"""A centred list keeps its bullet on the line of a zoomed item's text (#112).

In the "inside" marker mode the bullet is the first inline box of the item's
first line. When the item's text is wrapped in ``st_zoom``, the zoom
container was a block: the bullet stood alone on a line above the text, live
and in the HTML export. Measured here as the distance from the item's top to
its text (about 0 when they share the line) and the item's height (the same
as in a left-aligned list, where the bullet sits in its own column).

Run:  uv run pytest -m e2e tests/e2e/test_list_zoom_inside.py -v
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, streamlit_deck  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "list_zoom_app"
VIEWPORT = {"width": 1280, "height": 900}
NAMES = ["zoom-center", "plain-center", "zoom-left", "plain-left", "title-nested", "child-nested"]

MEASURE = """([names, itemSel]) => { const out = {};
  for (const name of names) {
    const el = [...document.querySelectorAll('div, span, p')].find(
      d => d.children.length === 0 && (d.textContent || '').trim() === name);
    if (!el) { out[name] = null; continue; }
    const item = el.closest(itemSel);
    const r = el.getBoundingClientRect(), ir = item.getBoundingClientRect();
    out[name] = {offset: Math.round(r.top - ir.top), height: Math.round(r.bottom - ir.top),
                 top: Math.round(r.top), bottom: Math.round(r.bottom)};
  } return out; }"""
LIVE_ITEM = '[data-testid="stVerticalBlock"][class*="stx-list-item"]'


def _check(m: dict) -> None:
    assert all(m[n] is not None for n in NAMES), m
    # the zoomed text starts on the item's first line, as in a left-aligned list
    assert abs(m["zoom-center"]["offset"] - m["zoom-left"]["offset"]) <= 3, m
    assert abs(m["zoom-center"]["height"] - m["zoom-left"]["height"]) <= 3, m
    assert abs(m["plain-center"]["offset"] - m["plain-left"]["offset"]) <= 3, m
    assert abs(m["title-nested"]["offset"] - m["zoom-left"]["offset"]) <= 3, m
    # the nested list stays below its zoomed title
    assert m["child-nested"]["top"] >= m["title-nested"]["bottom"] - 2, m


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck(DECK) as url:
        yield url


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html

    root = tmp_path_factory.mktemp("listzoom")
    deck = root / "deck"
    shutil.copytree(DECK, deck)
    out = root / "out"
    result = CliRunner().invoke(export_html, [str(deck), "--html-mode", "continuous", "-o", str(out)])
    assert result.exit_code == 0, result.output
    return out / "deck" / "deck.html"


def test_live_zoomed_item_shares_the_bullet_line(deck_url):
    with playwright.sync_playwright() as p:
        browser = launch_browser(p)
        try:
            page = browser.new_page(viewport=VIEWPORT)
            page.goto(deck_url, wait_until="load")
            page.wait_for_function(
                "() => document.querySelectorAll('.stx-list-item--inside').length >= 4", timeout=60_000)
            page.wait_for_timeout(1500)
            _check(page.evaluate(MEASURE, [NAMES, LIVE_ITEM]))
        finally:
            browser.close()


def test_export_zoomed_item_shares_the_bullet_line(exported):
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport=VIEWPORT)
            page.goto(exported.as_uri())
            page.wait_for_timeout(1000)
            _check(page.evaluate(MEASURE, [NAMES, "li"]))
        finally:
            browser.close()
