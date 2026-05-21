"""Real-browser regression net for the navigation active-state subsystem.

Phase 0 of ``navigation-refactor-plan-v01.md``.  These tests drive
Chromium (headed when ``STX_E2E_HEADED=1`` — the real gate) against a
paginated, search-enabled deck and assert on DOM/CSS state.

The three ACCEPTANCE scenarios reproduce the open bugs and are marked
``xfail(strict=True)`` so they:
  * stay green-as-xfail today (documenting the bug reproduces), and
  * turn into a HARD failure the moment a later phase fixes them — at
    which point the ``xfail`` marker must be removed (plan §2.4):
      - S3 (double PageDown counter desync)   → fixed in Phase 2
      - S4 (double-click ▶ counter desync)    → fixed in Phase 2
      - S6 (multi-heading group-highlight)    → fixed in Phase 4

Run:
    uv run pytest -m e2e tests/e2e/test_nav_active_state.py -v
    STX_E2E_HEADED=1 uv run pytest -m e2e tests/e2e/test_nav_active_state.py -v   # the gate
    STX_NAV_E2E_DECK=/abs/deck uv run pytest -m e2e ... -k smoke                  # external deck

CI prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import (  # noqa: E402
    check_active_matches_page,
    check_counter_parity,
    check_single_active,
    dispatch_key,
    double_key,
    launch_browser,
    read_state,
    select_tab,
    streamlit_deck,
    wait_ready,
)

pytestmark = pytest.mark.e2e

VIEWPORT = {"width": 1600, "height": 1000}


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck() as url:
        yield url


def _open(p, url):
    browser = launch_browser(p)
    ctx = browser.new_context(viewport=VIEWPORT)
    page = ctx.new_page()
    page.set_default_timeout(60_000)
    wait_ready(page, url)
    return browser, page


# --------------------------------------------------------------------------
# Smoke — validates the harness itself before any scenario is trusted.
# --------------------------------------------------------------------------
def test_smoke_baseline(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            st = read_state(page)
            print("\nSMOKE state:", {k: st[k] for k in (
                "observer", "scrollspy", "currentPage", "n_entries",
                "n_visible", "counterIdx", "counterTotal", "markerLabel")})
            assert st["observer"], "marker observer not installed"
            assert st["scrollspy"], "scroll-spy not installed (STX_USE_MARKER_RUNTIME?)"
            assert st["n_entries"] > 0, "no sidebar entries found"
            assert any(e["block"] is not None for e in st["entries"]), \
                "no data-stx-block entries (search=True not honoured?)"
            assert st["counterTotal"] is not None, "floating widget counter not found"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# S1 — click a cross-page sidebar entry.
# --------------------------------------------------------------------------
def test_s1_click_cross_page_entry(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            # Click the entry that targets the last page (cross-page jump).
            target = page.eval_on_selector_all(
                '[data-testid="stSidebar"] a[href^="#stx-goto-"]',
                "els => els.length ? els[els.length - 1].getAttribute('href') : null",
            )
            assert target, "no cross-page (#stx-goto-N) link present"
            page.click(f'[data-testid="stSidebar"] a[href="{target}"]')
            page.wait_for_timeout(2200)
            st = read_state(page)
            ok1, d1 = check_single_active(st, cue="inline")
            ok2, d2 = check_active_matches_page(st, cue="inline")
            assert ok1, d1
            assert ok2, d2
        finally:
            browser.close()


# --------------------------------------------------------------------------
# S2 — single PageDown → next marker (cross-page).
# --------------------------------------------------------------------------
def test_s2_single_pagedown(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            dispatch_key(page, "PageDown")
            st = read_state(page)
            ok1, d1 = check_active_matches_page(st, cue="inline")
            ok2, d2 = check_counter_parity(st)
            assert ok1, d1
            assert ok2, d2
        finally:
            browser.close()


# --------------------------------------------------------------------------
# S3 — ACCEPTANCE — double PageDown inside one rerun window.
#
# Desired (post-Phase-2, coalesce): two presses advance two pages and the
# widget counter stays consistent with the rendered page.  At 0.7.8 the
# second navigation hits the `if (navigating) return;` re-entry guard and
# is silently DROPPED — the deck advances only one page while the widget's
# currentIdx has already moved to +2 (companion §5.3 / §6.2 / §6.10).
# --------------------------------------------------------------------------
def test_s3_double_pagedown_advances_two(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            start = read_state(page)["currentPage"]
            double_key(page, "PageDown")
            st = read_state(page)
            print(f"\nS3: start_page={start} end_page={st['currentPage']} "
                  f"counterIdx={st['counterIdx']}")
            ok, d = check_counter_parity(st)
            assert st["currentPage"] == start + 2, \
                f"two PageDowns advanced {st['currentPage'] - start} page(s), expected 2"
            assert ok, d
        finally:
            browser.close()


# --------------------------------------------------------------------------
# S4 — ACCEPTANCE — double-click the floating ▶ arrow (same root cause).
# --------------------------------------------------------------------------
def test_s4_double_click_next_arrow(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            start = read_state(page)["currentPage"]
            clicked = page.evaluate(
                """() => {
                  const nav = document.getElementById('streamtex-marker-nav');
                  if (!nav) return false;
                  // The ▶ next button is a <button> whose OWN text is the glyph.
                  const b = [...nav.querySelectorAll('button')]
                    .find(x => (x.textContent || '').trim() === '\\u25B6');
                  if (!b) return false;
                  b.click(); setTimeout(() => b.click(), 60);
                  return true;
                }"""
            )
            assert clicked, "could not locate the ▶ next button"
            page.wait_for_timeout(2600)
            st = read_state(page)
            print(f"\nS4: start_page={start} end_page={st['currentPage']} "
                  f"counterIdx={st['counterIdx']}")
            assert st["currentPage"] == start + 2, \
                f"two ▶ clicks advanced {st['currentPage'] - start} page(s), expected 2"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# S6 — ACCEPTANCE — multi-heading page lights ONE entry, not the whole group.
# Measured on the CONTENTS tab (the TOC), where page index 1 ("section-a")
# emits three entries (H1 + two H2).  At 0.7.8 all three receive the inline
# active color (companion §6.13).
# --------------------------------------------------------------------------
@pytest.mark.xfail(strict=True, reason="group-highlight: all same-page entries lit — fixed in Phase 4")
def test_s6_multi_heading_single_highlight(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            dispatch_key(page, "PageDown")          # → page 1 (section-a)
            select_tab(page, "Contents")            # measure the TOC, not Markers
            st = read_state(page)
            assert st["currentPage"] == 1, f"expected page 1, got {st['currentPage']}"
            lit = [e["text"] for e in st["inlineActiveVisible"]]
            print(f"\nS6: currentPage={st['currentPage']} inline-lit={lit}")
            ok, d = check_single_active(st, cue="inline")
            assert ok, d
        finally:
            browser.close()


# --------------------------------------------------------------------------
# S7 — cross-tab consistency: the active page must be reflected in BOTH the
# Markers and the Contents tab.  Baseline (inline color) renders both tabs
# server-side per page, so this holds today; it guards against Phase 5/6
# regressions where the scroll-spy class must stay cross-tab consistent
# (companion §6.9).
# --------------------------------------------------------------------------
def test_s7_cross_tab_active_consistency(deck_url: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _open(p, deck_url)
        try:
            dispatch_key(page, "PageDown")
            dispatch_key(page, "PageDown")          # → page 2 (single-heading)
            select_tab(page, "Markers")
            mk = read_state(page)
            select_tab(page, "Contents")
            tc = read_state(page)
            cp = tc["currentPage"]
            mk_blocks = {e["block"] for e in mk["inlineActiveVisible"]}
            tc_blocks = {e["block"] for e in tc["inlineActiveVisible"]}
            print(f"\nS7: page={cp} markers_active={mk_blocks} contents_active={tc_blocks}")
            assert mk_blocks == {str(cp)}, f"Markers tab active blocks={mk_blocks}, expected {{{cp}}}"
            assert tc_blocks == {str(cp)}, f"Contents tab active blocks={tc_blocks}, expected {{{cp}}}"
        finally:
            browser.close()


# Follow-ons within Phase 0 (lower priority, not acceptance-critical):
#   * S5 — mouse-wheel / synthetic-touch at the bottom boundary.  Deferred:
#     trackpad-inertia cooldown logic (COOLDOWN_*) makes a deterministic
#     headless assertion brittle; revisit under STX_E2E_HEADED with a tuned
#     wheel-event sequence.
#   * S9 — static-HTML export scroll-spy parity.  Deferred: needs an export
#     build step (stx-export:html) + file:// load; add once Phase 4b makes
#     the .stx-nav-active class the single active cue in both contexts.
