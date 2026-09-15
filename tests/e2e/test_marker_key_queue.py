"""Real-browser regression net for the marker key queue (0.7.31).

Bug: in a PAGINATED book the floating-widget script (``marker.py``) is
re-injected on every rerun and only flips ``_initialized`` after a fixed
delay.  A next/prev key (or a ▶/◀ click) arriving in that window was
silently dropped — measured at 15–20 presses lost out of 40 when each
press followed the previous page change by ~100 ms.

Fix: the request is queued on ``hostWin._stxPendingStep`` (net step count,
capped at ±2, 3 s TTL) and replayed once at init; the init keeps its
500 ms floor (it must run after book.py's scroll resets) and only waits
longer when the marker elements are not in the DOM yet.

The tests trigger the window DETERMINISTICALLY: they wait for the page
index to change (that instant is the widget re-injection) and press
50 ms later — no machine-dependent wall-clock delay.

Run:
    uv run pytest -m e2e tests/e2e/test_marker_key_queue.py -v
CI prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, read_state, streamlit_deck, wait_ready  # noqa: E402

pytestmark = pytest.mark.e2e

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "marker_key_queue_app"
VIEWPORT = {"width": 1600, "height": 1000}
SINGLE_PAGES = 8          # pages 0..7 have one marker (see fixture)
CHANGE_TIMEOUT_MS = 5000  # a page change must land within this


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck(FIXTURE_DIR) as url:
        yield url


def _open(p, url):
    browser = launch_browser(p)
    ctx = browser.new_context(viewport=VIEWPORT)
    page = ctx.new_page()
    page.set_default_timeout(60_000)
    wait_ready(page, url)
    return browser, page


def _page_idx(page) -> int:
    return page.evaluate("() => window._stxPrevPage")


def _wait_page_change(page, before: int, timeout_ms: int = CHANGE_TIMEOUT_MS) -> int:
    """Poll the page index every 20 ms; return it as soon as it differs."""
    waited = 0
    while waited < timeout_ms:
        page.wait_for_timeout(20)
        waited += 20
        now = _page_idx(page)
        if now != before:
            return now
    return before


# --------------------------------------------------------------------------
# 1. A key pressed 50 ms after a page change (inside the init window) must
#    not be lost.  Pre-fix: every second press is dropped.
# --------------------------------------------------------------------------
def test_key_in_init_window_is_replayed(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            lost = []
            for k in range(SINGLE_PAGES - 1):
                before = _page_idx(page)
                page.keyboard.press("ArrowRight")
                got = _wait_page_change(page, before)
                if got != before + 1:
                    lost.append((k, before, got))
                page.wait_for_timeout(50)   # next press lands inside the window
            print(f"\nkey-queue: lost={lost}")
            assert not lost, f"presses lost inside the init window: {lost}"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# 2. Two presses inside the window advance by two (0.7.10 coalescing
#    semantics, same as S3/S4 in test_nav_active_state.py).
# --------------------------------------------------------------------------
def test_double_press_in_init_window_advances_two(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            before = _page_idx(page)
            page.keyboard.press("ArrowRight")
            landed = _wait_page_change(page, before)
            assert landed == before + 1
            page.wait_for_timeout(50)
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(30)
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(3500)
            final = _page_idx(page)
            print(f"\nkey-queue double: landed={landed} final={final}")
            assert final == landed + 2, f"expected +2, got {final - landed}"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# 3. ▶ click inside the window is honoured too (same path as the keys).
# --------------------------------------------------------------------------
def test_next_arrow_click_in_init_window_is_replayed(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    click_next = """() => {
      const nav = document.getElementById('streamtex-marker-nav');
      if (!nav) return false;
      const b = [...nav.querySelectorAll('button')]
        .find(x => (x.textContent || '').trim() === '\\u25B6');
      if (!b) return false;
      b.click(); return true;
    }"""
    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            before = _page_idx(page)
            assert page.evaluate(click_next)
            landed = _wait_page_change(page, before)
            assert landed == before + 1
            page.wait_for_timeout(50)
            assert page.evaluate(click_next)
            got = _wait_page_change(page, landed)
            assert got == landed + 1, "▶ click inside the init window was dropped"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# 4. Dead time per page: pressing every 250 ms until it takes stays < 2 s.
# --------------------------------------------------------------------------
def test_dead_time_per_page_under_two_seconds(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            dead = []
            for _ in range(4):
                page.wait_for_timeout(2500)
                before = _page_idx(page)
                t0 = time.time()
                for _try in range(20):
                    page.keyboard.press("ArrowRight")
                    page.wait_for_timeout(250)
                    if _page_idx(page) != before:
                        break
                dead.append(time.time() - t0)
            print(f"\nkey-queue dead times: {[round(d, 2) for d in dead]}")
            assert max(dead) < 2.0, f"dead time too long: {dead}"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# 5. GUARD — behaviour that must NOT change: ``prev`` from the first marker
#    of a page lands on the LAST marker of the previous page by scrolling.
#    This depends on the widget init running AFTER book.py's scroll resets
#    (the 500 ms floor).  Page 10 (1-based) → ArrowLeft → page index 8,
#    marker "kq-8-b" (global index 9, counter shows 10), scrolled down.
# --------------------------------------------------------------------------
def test_prev_lands_on_last_marker_of_previous_page(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url + "/?page=10")
        try:
            assert _page_idx(page) == 9
            page.keyboard.press("ArrowLeft")
            landed = _wait_page_change(page, 9)
            assert landed == 8
            page.wait_for_timeout(1800)   # init (500 ms) + smooth scroll
            st = read_state(page)
            scroll_top = page.evaluate(
                "() => { const m = document.querySelector('.stMain'); return m ? m.scrollTop : -1; }")
            print(f"\nkey-queue prev: counterIdx={st['counterIdx']} scrollTop={scroll_top}")
            assert st["counterIdx"] == 10, "prev did not land on the last marker of page 8"
            assert scroll_top > 200, "widget did not scroll down to the last marker"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# 6. Three presses in ~1 s: A (page change), B inside A's rerun (handled by
#    the old instance -> book.py pending page), C inside the init window of
#    the intermediate page while B's navigation is in flight.  C must be
#    replayed on the page that LANDS, not on the intermediate page where
#    book.py would coalesce it away.  From page 6: A -> page 7, B -> page 8
#    (first marker, counter 9), C -> second marker of page 8 (counter 10).
# --------------------------------------------------------------------------
def test_press_during_intermediate_init_survives_in_flight_navigation(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url + "/?page=7")
        try:
            assert _page_idx(page) == 6
            page.keyboard.press("ArrowRight")           # A
            page.wait_for_timeout(60)
            page.keyboard.press("ArrowRight")           # B — inside A's rerun
            landed = _wait_page_change(page, 6)
            assert landed == 7, f"A did not land on page 7 (got {landed})"
            page.wait_for_timeout(50)
            page.keyboard.press("ArrowRight")           # C — page 7 init window
            page.wait_for_timeout(4000)
            st = read_state(page)
            final = _page_idx(page)
            print(f"\nkey-queue triple: final page={final} counterIdx={st['counterIdx']}")
            assert final == 8, f"expected page 8, got {final}"
            assert st["counterIdx"] == 10, f"C was lost: counter {st['counterIdx']} != 10"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# 7. The widget iframe is destroyed by Streamlit while a page change is in
#    flight (observed on real decks: ~150 ms with no listener at all before
#    the new script runs).  Chromium neuters every listener registered by a
#    destroyed iframe, so only the persistent host-realm guard can catch a
#    key in that gap.  Simulated deterministically: press A, kill the widget
#    iframe (blank srcdoc), press B 150 ms later -> both must count.
# --------------------------------------------------------------------------
def test_key_while_widget_iframe_is_dead_is_caught_by_host_guard(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            assert page.evaluate("() => typeof window._stxMarkerKeyGuard === 'function'"), \
                "host-realm key guard not installed"
            before = _page_idx(page)
            page.keyboard.press("ArrowRight")                       # A
            killed = page.evaluate(
                "() => { const f = window._stxMarkerFrame; if (!f) return false; f.srcdoc = ''; return true; }")
            assert killed, "could not locate the widget iframe"
            page.wait_for_timeout(150)
            page.keyboard.press("ArrowRight")                       # B — no instance alive
            page.wait_for_timeout(4000)
            final = _page_idx(page)
            print(f"\nkey-queue dead-iframe: before={before} final={final}")
            assert final == before + 2, f"expected +2, got {final - before} (B lost in the dead-iframe gap)"
        finally:
            browser.close()
