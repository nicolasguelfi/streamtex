"""The sidebar entry in cyan follows the floating bar, slide by slide (#130).

Deck (``nav_sidebar_target_app``): pages of 1, 20 and 3 slides (slides 1 |
2-21 | 22-24); every slide's marker is ``s<n>``; the Contents tab lists
« page a » (slide 1), « page b » (slide 2), « detail twelve » (slide 12) and
« page c » (slide 22). At every step, each tab has exactly one entry in cyan:
the Markers row of the bar's slide and the heading in force on it.

The gate is a headed run, where Streamlit is as slow as for a reader (the
highlight of 0.6.36-0.6.40 only broke there):

    STX_E2E_HEADED=1 uv run pytest -m e2e tests/e2e/test_nav_sidebar_highlight.py -v
"""
from __future__ import annotations

from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, streamlit_deck, wait_ready  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "nav_sidebar_target_app"
VIEWPORT = {"width": 1600, "height": 1000}

# every sidebar link painted in the cyan, hidden tab included
CYAN_JS = """() => {
  const sb = document.querySelector('[data-testid="stSidebar"]');
  const probe = document.createElement('a');
  probe.style.color = 'var(--stx-link-active-color)';
  sb.appendChild(probe);
  const cyan = getComputedStyle(probe).color;
  probe.remove();
  return [...sb.querySelectorAll('[data-stx-nav] a')]
    .filter(a => getComputedStyle(a).color === cyan)
    .map(a => a.closest('[data-stx-nav]').getAttribute('data-stx-nav').slice(0, 2)
              + ':' + (a.textContent || '').trim());
}"""

COUNTER_JS = """() => {
  const m = ((document.querySelector('#streamtex-marker-nav') || {}).innerText || '')
    .match(/(\\d+)\\s*\\/\\s*\\d+/);
  return m ? parseInt(m[1], 10) : null;
}"""


def _heading(n: int) -> str:
    return "page a" if n == 1 else "page b" if n < 12 else "detail twelve" if n < 22 else "page c"


def _expected(n: int) -> list[str]:
    return sorted([f"mk:{n}. s{n}", f"to:{_heading(n)}"])


def _cyan(page) -> list[str]:
    return sorted(page.evaluate(CYAN_JS))


def _settle(page, n: int, timeout_s: float = 20.0) -> None:
    """Wait until counter and cyan both name slide n for one second in a row.

    A page change shows the new counter at once, then reruns: the bar leaves
    the page for a moment, so a single matching read is not enough.
    """
    want, stable = (n, _expected(n)), 0
    for _ in range(int(timeout_s / 0.2)):
        stable = stable + 1 if (page.evaluate(COUNTER_JS), _cyan(page)) == want else 0
        if stable >= 5:
            return
        page.wait_for_timeout(200)


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck(DECK) as url:
        yield url


@pytest.fixture
def page(deck_url):
    with playwright.sync_playwright() as p:
        browser = launch_browser(p)
        pg = browser.new_context(viewport=VIEWPORT).new_page()
        pg.set_default_timeout(60_000)
        pg.deck_url = deck_url
        try:
            yield pg
        finally:
            browser.close()


def _check(page, n: int, how: str) -> None:
    assert page.evaluate(COUNTER_JS) == n, f"{how}: counter"
    assert _cyan(page) == _expected(n), f"{how}: slide {n}"


def test_every_arrow_press_moves_the_cyan(page):
    """Real ArrowRight presses through the 24 slides, then back over a page boundary."""
    wait_ready(page, f"{page.deck_url}/?slide=1")
    _settle(page, 1)
    _check(page, 1, "start")
    for n in range(2, 25):
        page.keyboard.press("ArrowRight")
        _settle(page, n)
        _check(page, n, "ArrowRight")
    for n in (23, 22, 21, 20):
        page.keyboard.press("ArrowLeft")
        _settle(page, n)
        _check(page, n, "ArrowLeft")


@pytest.mark.parametrize("start,expected", [(5, 7), (20, 22)])
def test_a_double_press_keeps_bar_and_cyan_together(page, start, expected):
    """Two presses in one rerun: inside a page, and across a page change."""
    wait_ready(page, f"{page.deck_url}/?slide={start}")
    _settle(page, start)
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(60)
    page.keyboard.press("ArrowRight")
    _settle(page, expected)
    _check(page, expected, "double press")


def test_a_sidebar_click_moves_the_cyan(page):
    wait_ready(page, f"{page.deck_url}/?slide=1")
    _settle(page, 1)
    page.evaluate("""() => [...document.querySelectorAll('[data-stx-nav^="mk"] a')]
                     .find(a => a.textContent.trim().endsWith('s15')).click()""")
    _settle(page, 15)
    _check(page, 15, "sidebar click")


def test_a_deep_link_lights_its_slide(page):
    wait_ready(page, f"{page.deck_url}/?slide=13")
    _settle(page, 13)
    _check(page, 13, "?slide=13")


def test_the_cyan_survives_a_rerun_that_rebuilds_the_sidebar(page):
    """« Refresh search index » reruns the app and redraws every sidebar entry."""
    wait_ready(page, f"{page.deck_url}/?slide=1")
    for n in range(2, 6):
        page.keyboard.press("ArrowRight")
        _settle(page, n)
    page.get_by_role("button", name="Refresh search index").click()
    page.wait_for_timeout(4000)
    _check(page, 5, "after rerun")
