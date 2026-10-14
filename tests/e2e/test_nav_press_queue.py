"""One press = one slide, also while the page changes (paginated app).

The ◀ ▶ buttons and the host-document keys are taken by guards that live in
the host page: they queue the press and ask the current widget instance to
consume it. A live instance steps at once; an instance that is going away
(its iframe is being replaced, its listeners already dead) leaves the press
queued, and the instance that lands replays it.

Deck: pages of 1, 3, 2 and 1 slides (slides 1 | 2-4 | 5-6 | 7).

Run:  uv run pytest -m e2e tests/e2e/test_nav_press_queue.py -v
"""
from __future__ import annotations

from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, streamlit_deck, wait_ready  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "nav_multislide_app"
VIEWPORT = {"width": 1600, "height": 1000}

CLICKS = """([glyph, n, gap]) => {
  const nav = document.getElementById('streamtex-marker-nav');
  const b = [...nav.querySelectorAll('button')].find(x => (x.textContent || '').trim() === glyph);
  for (let i = 0; i < n; i++) setTimeout(() => b.click(), i * gap);
}"""

KEYS = """([key, n, gap]) => {
  const f = () => document.dispatchEvent(
    new KeyboardEvent('keydown', {key: key, bubbles: true, cancelable: true}));
  for (let i = 0; i < n; i++) setTimeout(f, i * gap);
}"""


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck(DECK) as url:
        yield url


def _slide(page) -> int:
    text = page.evaluate(
        "(document.querySelector('#streamtex-marker-nav') || {}).innerText || ''")
    counter = next(x for x in text.split("\n") if "/" in x)
    return int(counter.split("/")[0].strip().replace(" ", ""))


def _open(p, url, slide):
    browser = launch_browser(p)
    page = browser.new_context(viewport=VIEWPORT).new_page()
    page.set_default_timeout(60_000)
    wait_ready(page, f"{url}/?slide={slide}")
    assert _slide(page) == slide
    return browser, page


@pytest.mark.parametrize("how,start,n,expected", [
    ("next", 1, 2, 3),    # turns the page, then stays inside the new page
    ("next", 4, 2, 6),
    ("next", 3, 3, 6),
    ("prev", 5, 2, 3),    # back into the last slide of the previous page, then one more
])
@pytest.mark.parametrize("device", ["click", "key"])
def test_fast_presses_move_one_slide_each(deck_url, device, how, start, n, expected):
    with playwright.sync_playwright() as p:
        browser, page = _open(p, deck_url, start)
        try:
            if device == "click":
                page.evaluate(CLICKS, ["▶" if how == "next" else "◀", n, 60])
            else:
                page.evaluate(KEYS, ["ArrowRight" if how == "next" else "ArrowLeft", n, 60])
            page.wait_for_function(f"() => {{ const t = (document.querySelector("
                                   f"'#streamtex-marker-nav') || {{}}).innerText || '';"
                                   f" return t.indexOf('{expected} /') >= 0 || t.indexOf("
                                   f"' {expected} /') >= 0; }}", timeout=15_000)
            page.wait_for_timeout(1500)                     # and it stays there
            assert _slide(page) == expected
        finally:
            browser.close()


def test_press_left_by_a_dying_instance_is_replayed(deck_url):
    """The current instance cannot take the press (as when its iframe is being
    replaced): the press stays queued and the instance that lands replays it."""
    with playwright.sync_playwright() as p:
        browser, page = _open(p, deck_url, 1)
        try:
            page.evaluate("() => { window._stxMarkerConsume = function () {}; }")
            page.evaluate(CLICKS, ["▶", 1, 0])
            page.wait_for_timeout(300)
            assert page.evaluate("(window._stxPendingStep || {}).n") == 1
            assert _slide(page) == 1                        # nothing moved yet
            page.evaluate("() => window._stxMarkerGoToPage(1)")   # the page change lands
            page.wait_for_function("() => window._stxPendingStep === null", timeout=15_000)
            page.wait_for_timeout(1000)
            assert _slide(page) == 3                        # first slide of page 2, then the press
        finally:
            browser.close()
