"""Real-browser regression net for ``PresentationConfig.center_content``.

Bug (0.7.31 and earlier): with ``center_content=True, enforce_ratio=False``
the page container got ``display:flex; justify-content:center`` but no
height — its height was that of its content — so nothing was centred.

Fix (0.7.32): with ``enforce_ratio=False`` the container gets
``min-height: calc(100vh - <footer_height>)`` (``100vh`` without footer)
and its direct children ``flex: 0 0 auto`` (otherwise Streamlit's
``stVerticalBlock`` flex item stretches and its content stays at the
top).  ``min-height`` does not cap anything, so a page taller than the
viewport keeps growing and scrolling.  ``enforce_ratio=True`` is left
untouched.

Run:
    uv run pytest -m e2e tests/e2e/test_presentation_center.py -v
CI prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, streamlit_deck, wait_ready  # noqa: E402

pytestmark = pytest.mark.e2e

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "presentation_center_app"
VIEWPORT = {"width": 1920, "height": 1080}
FOOTER_PX = 48  # PresentationConfig.footer_height default

# Geometry of the page container and of its first content block.
GEOM_JS = """() => {
  const bc = document.querySelector('.stMain .block-container');
  const cs = getComputedStyle(bc);
  const r = bc.getBoundingClientRect();
  const vb = bc.querySelector('[data-testid="stVerticalBlock"]');
  const c = vb.getBoundingClientRect();
  const pt = parseFloat(cs.paddingTop), pb = parseFloat(cs.paddingBottom);
  return {
    container_top: r.top, container_height: r.height,
    box_top: r.top + pt, box_bottom: r.bottom - pb,     // content box (inside paddings)
    content_top: c.top, content_bottom: c.bottom,
    min_height: cs.minHeight, max_height: cs.maxHeight, overflow: cs.overflowY,
    display: cs.display, justify: cs.justifyContent,
    scroll_height: document.querySelector('.stMain').scrollHeight,
  };
}"""


@contextmanager
def _deck(center: bool, ratio: bool = False, footer: bool = True):
    saved = {k: os.environ.get(k) for k in ("STX_E2E_CENTER", "STX_E2E_RATIO", "STX_E2E_FOOTER")}
    os.environ["STX_E2E_CENTER"] = "1" if center else "0"
    os.environ["STX_E2E_RATIO"] = "1" if ratio else "0"
    os.environ["STX_E2E_FOOTER"] = "1" if footer else "0"
    try:
        with streamlit_deck(FIXTURE_DIR) as url:
            yield url
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _open(p, url):
    browser = launch_browser(p)
    ctx = browser.new_context(viewport=VIEWPORT)
    page = ctx.new_page()
    page.set_default_timeout(60_000)
    wait_ready(page, url)
    page.wait_for_timeout(1000)
    return browser, page


def _geom(page) -> dict:
    return page.evaluate(GEOM_JS)


# --------------------------------------------------------------------------
# 1. Short page, center_content=True, enforce_ratio=False, footer=True:
#    the content sits in the vertical middle of the container's content box,
#    and the container fills the viewport minus the footer.
# --------------------------------------------------------------------------
def test_short_page_is_vertically_centered() -> None:
    from playwright.sync_api import sync_playwright

    with _deck(center=True) as url, sync_playwright() as p:
        browser, page = _open(p, url + "/?page=1")
        try:
            g = _geom(page)
            box_center = (g["box_top"] + g["box_bottom"]) / 2
            content_center = (g["content_top"] + g["content_bottom"]) / 2
            print(f"\npresentation-center short: {g}\n  box_center={box_center:.0f} content_center={content_center:.0f}")
            assert g["display"] == "flex" and g["justify"] == "center"
            expected_h = VIEWPORT["height"] - FOOTER_PX
            assert abs(g["container_height"] - expected_h) < 2, \
                f"container height {g['container_height']} != 100vh - footer ({expected_h})"
            assert abs(content_center - box_center) < 8, \
                f"content not centred: content {g['content_top']:.0f}→{g['content_bottom']:.0f}, " \
                f"box {g['box_top']:.0f}→{g['box_bottom']:.0f}"
        finally:
            browser.close()


# --------------------------------------------------------------------------
# 2. Tall page: scrollHeight identical with and without center_content, and
#    the last element is reachable by scrolling (no truncation).
# --------------------------------------------------------------------------
def test_tall_page_scrolls_and_height_is_unchanged() -> None:
    from playwright.sync_api import sync_playwright

    heights = {}
    for center in (False, True):
        with _deck(center=center) as url, sync_playwright() as p:
            browser, page = _open(p, url + "/?page=2")
            try:
                g = _geom(page)
                heights[center] = g["scroll_height"]
                reached = page.evaluate("""() => {
                  const el = document.getElementById('stx-e2e-end');
                  if (!el) return null;
                  el.scrollIntoView({block: 'end'});
                  const r = el.getBoundingClientRect();
                  return r.top >= -2 && r.bottom <= window.innerHeight + 2;
                }""")
                print(f"\npresentation-center tall center={center}: scrollHeight={g['scroll_height']} "
                      f"container={g['container_height']:.0f} end_reachable={reached}")
                assert g["scroll_height"] > VIEWPORT["height"] * 2, "fixture page is not tall"
                assert reached, "sentinel at the end of the tall page is not reachable"
            finally:
                browser.close()
    assert abs(heights[True] - heights[False]) <= 2, \
        f"center_content changed the tall page height: {heights}"


# --------------------------------------------------------------------------
# 3. GUARD — enforce_ratio=True is untouched: max-height 100vh + overflow
#    hidden, no min-height, container height = content height (< 100vh).
# --------------------------------------------------------------------------
def test_enforce_ratio_true_is_unchanged() -> None:
    from playwright.sync_api import sync_playwright

    with _deck(center=True, ratio=True) as url, sync_playwright() as p:
        browser, page = _open(p, url + "/?page=1")
        try:
            g = _geom(page)
            print(f"\npresentation-center ratio=True: {g}")
            assert g["max_height"] == f"{VIEWPORT['height']}px"
            assert g["overflow"] == "hidden"
            assert g["min_height"] in ("auto", "0px"), f"unexpected min-height {g['min_height']}"
            assert g["container_height"] < VIEWPORT["height"] - FOOTER_PX - 2, \
                "container should still wrap its content when enforce_ratio=True"
        finally:
            browser.close()
