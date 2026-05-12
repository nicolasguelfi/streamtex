"""E2E regression — paginated navigation must not leak marker styles.

Reported on FC-260507-NG-SLIDES after 0.6.26: when the user navigates
forward then back, some slides render with the *previous* slide's
``zoom`` / ``grid-template-columns`` written inline on the visible
``stVerticalBlock``.  React reuses the parent DOM element across
paginated reruns, the new slide's marker observer applies the *new*
values, but stray inline-styles from the old slide that don't get
re-written (or get re-written and then re-applied with the old value
by an obsolete marker still in DOM) survive and skew the layout.

This test pins the *intended* invariant: after every navigation, the
single visible ``.stx-grid`` parent has the ``grid-template-columns``
of the currently displayed slide (read from the slide's marker label),
and the single visible ``.stx-zoom`` parent has the matching ``zoom``
factor.  Sibling parents from prior pages must either be absent from
the DOM or have inline styles cleared.

Fixture: ``tests/e2e/fixtures/paginated_bleedthrough_app`` defines 3
slides whose grid columns and zoom factors differ on every axis
(slide-A: 92%/8% + zoom 60, slide-B: 50%/50% + zoom 85, slide-C:
30%/70% + zoom 100).  The test navigates A→B→C→A and checks each step.

Run with:
    uv run pytest -m e2e tests/e2e/test_paginated_bleedthrough.py -v -s
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from contextlib import closing
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

FIXTURE_DIR = (
    Path(__file__).resolve().parent / "fixtures" / "paginated_bleedthrough_app"
)

pytestmark = pytest.mark.e2e


# Mirror the SLIDE_SPECS tuples in the fixture's blocks/__init__.py.
#   (slide_id, title_cols, title_zoom, body_cols, body_zoom)
SLIDE_SPECS = [
    ("slide-A", "92% 8%",  90, "45% 55%", 100),
    ("slide-B", "80% 20%", 85, "50% 50%",  75),
    ("slide-C", "70% 30%", 95, "33% 67%",  65),
]


def _free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_http(url: str, timeout_s: float = 60.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 — connection refused is normal
            last_err = exc
        time.sleep(0.4)
    raise TimeoutError(f"streamlit never became ready on {url}: {last_err}")


@pytest.fixture(scope="module")
def streamlit_server():
    """Launch ``streamlit run book.py`` on a free port; tear down at end."""
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "book.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=str(FIXTURE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_http(url)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# JS that reads, from the parent DOM, the visible grid + zoom inline
# styles and the visible slide title.  The visible slide is identified
# via the marker label text rendered in the page heading by
# ``st_write(_TITLE, f"{slide_id} (...)", ...)``.
_READ_VISIBLE_JS = r"""
() => {
  // The marker observer writes inline styles on every .stx-grid and
  // .stx-zoom in the DOM.  We're only interested in those that belong
  // to the currently visible page, which we identify by the slide's
  // title text rendered via st_write.
  // The fixture renders each slide's title via st_write(_TITLE, "slide-X (...)").
  // Search broadly across the visible page text for a "slide-[ABC] (" prefix.
  const allText = Array.from(document.querySelectorAll('div, span, h1, h2, h3, h4'))
    .map(el => (el.textContent || '').trim())
    .filter(t => /\bslide-[ABC]\s*\(/.test(t));
  // Use the shortest matching text — longer ones are typically wrappers
  // that contain the title plus more body text.
  allText.sort((a, b) => a.length - b.length);
  const titleText = allText[0] || null;

  function readInline(sel) {
    const els = Array.from(document.querySelectorAll(sel));
    return els.map(el => ({
      display:               el.style.getPropertyValue('display'),
      grid_template_columns: el.style.getPropertyValue('grid-template-columns'),
      zoom:                  el.style.getPropertyValue('zoom'),
      gap:                   el.style.getPropertyValue('gap'),
    }));
  }
  return {
    title:     titleText,
    grids:     readInline('.stx-grid'),
    zooms:     readInline('.stx-zoom'),
    n_blocks:  document.querySelectorAll('.stx-block').length,
    observer:  window.__stxMarkerObs === true,
  };
}
"""


def _dispatch_key(page, key: str) -> None:
    """Dispatch a keydown KeyboardEvent on the host document.

    The marker.py JS registers ``hostDoc.addEventListener('keydown', …,
    true)``; dispatching via Playwright's ``keyboard.press`` requires the
    page to be focused, which is flaky under headless Streamlit because
    of the overlay z-index dance.  Dispatching the event directly on
    ``document`` bypasses focus and reliably triggers the navigation
    handler in capture phase.
    """
    page.evaluate(
        "(key) => document.dispatchEvent(new KeyboardEvent("
        "'keydown', {key: key, bubbles: true, cancelable: true}))",
        key,
    )
    # Streamlit needs a moment for the rerun + re-render to land.
    page.wait_for_timeout(900)


def _go_next(page) -> None:
    _dispatch_key(page, "PageDown")


def _go_prev(page) -> None:
    _dispatch_key(page, "PageUp")


def _norm_zoom(s: str) -> float | None:
    """Parse a CSS ``zoom`` string into a float for tolerant compare.

    Browsers serialize ``zoom: 1`` and ``zoom: 1.0`` interchangeably,
    so we cannot string-compare.  Returns None when the value is empty
    (which means the marker observer never wrote a zoom on this node)."""
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _assert_visible_matches(state: dict, expected) -> None:
    """Check the visible grid/zoom inline-styles match the expected slide.

    The fixture renders TWO grids and TWO zooms per slide.  We assert
    that the SET of inline ``grid-template-columns`` values matches the
    expected slide's two templates exactly (no extras leaking from a
    previous slide, no missing values from a failed marker apply), and
    likewise for ``zoom`` factors.
    """
    slide_id, title_cols, title_zoom, body_cols, body_zoom = expected
    expected_cols = sorted([title_cols, body_cols])
    expected_zooms = sorted([title_zoom / 100, body_zoom / 100])

    assert state["title"] is not None, (
        f"could not locate the slide title heading for expected slide "
        f"{slide_id!r}; state={state}"
    )
    assert slide_id in state["title"], (
        f"visible title {state['title']!r} does not contain expected "
        f"slide id {slide_id!r}"
    )

    actual_cols = sorted([g["grid_template_columns"] for g in state["grids"]
                          if g["grid_template_columns"]])
    assert actual_cols == expected_cols, (
        f"BLEED on {slide_id}: visible grids have "
        f"grid-template-columns={actual_cols!r} but the slide's markers "
        f"are {expected_cols!r}.  state={state}"
    )

    actual_zooms_raw = [_norm_zoom(z["zoom"]) for z in state["zooms"]]
    actual_zooms = sorted([z for z in actual_zooms_raw if z is not None])
    same_count = len(actual_zooms) == len(expected_zooms)
    same_values = all(
        abs(a - e) < 1e-6 for a, e in zip(actual_zooms, expected_zooms)
    )
    assert same_count and same_values, (
        f"BLEED on {slide_id}: visible zooms are {actual_zooms!r} but "
        f"the slide's markers are {expected_zooms!r}.  state={state}"
    )


def test_paginated_navigation_does_not_bleed_marker_styles(
    streamlit_server: str,
) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = ctx.new_page()
        page.set_default_timeout(30_000)

        page.goto(streamlit_server, wait_until="networkidle")
        page.wait_for_selector('[data-testid="stSidebar"]', state="visible")
        page.wait_for_function("window.__stxMarkerObs === true", timeout=15_000)
        # Wait for the cache-build loading overlay to disappear, otherwise
        # it covers the body (z-index 99999) and the focus click below
        # times out.
        page.wait_for_function(
            "() => !document.getElementById('stx-loading-overlay')",
            timeout=30_000,
        )
        page.wait_for_timeout(1500)

        # Focus into the document so PageDown/PageUp keyboard handler picks
        # up (it's registered via document.addEventListener('keydown', ...)
        # on the parent document by streamtex/marker.py).  We dispatch the
        # key event directly on hostDoc to bypass any focus quirks in the
        # headless browser.
        page.evaluate("() => document.body.focus()")

        # The user-reported bleed on FC-260507-NG-SLIDES appears only
        # after several back-and-forth navigations.  We cycle through a
        # forward sweep, then a backward sweep, asserting at every step
        # that the inline styles on visible grids/zooms still match the
        # currently visible slide.  Any leak from a previous slide trips
        # one of the assertions immediately.
        N = len(SLIDE_SPECS)
        # 1. Forward sweep A → B → C
        for i in range(N):
            if i > 0:
                _go_next(page)
            state = page.evaluate(_READ_VISIBLE_JS)
            print(f"\nFORWARD step {i} (expect {SLIDE_SPECS[i][0]}): {state}")
            _assert_visible_matches(state, SLIDE_SPECS[i])

        # 2. Backward sweep C → B → A
        for i in range(N - 2, -1, -1):
            _go_prev(page)
            state = page.evaluate(_READ_VISIBLE_JS)
            print(f"\nBACKWARD step {i} (expect {SLIDE_SPECS[i][0]}): {state}")
            _assert_visible_matches(state, SLIDE_SPECS[i])

        # 3. Second forward sweep — repeats the path that produced the
        #    bleed in the reported screenshots (A → B → A → B → …).
        for i in range(N):
            if i > 0:
                _go_next(page)
            state = page.evaluate(_READ_VISIBLE_JS)
            print(f"\nFORWARD-2 step {i} (expect {SLIDE_SPECS[i][0]}): {state}")
            _assert_visible_matches(state, SLIDE_SPECS[i])

        # 4. Rapid oscillation between slide 1 and 0
        for k in range(3):
            _go_prev(page)
            state = page.evaluate(_READ_VISIBLE_JS)
            print(f"\nOSC prev k={k} (expect {SLIDE_SPECS[N - 2 - k % 1][0]})")
            _go_next(page)
            state = page.evaluate(_READ_VISIBLE_JS)
            print(f"OSC next k={k}: {state}")
            _assert_visible_matches(state, SLIDE_SPECS[N - 1])

        browser.close()
