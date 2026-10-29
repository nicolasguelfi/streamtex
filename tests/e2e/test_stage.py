"""Real-Chromium e2e: the stage gives the document the projector's viewport (#105).

A window of 1000×600 opens a page with ``?stage=1920x1080`` that runs the
stage script (the live app injects the same one): inside the frame the
document measures 1920×1080, a 50vw×50vh box 960×540 px, the frame is scaled
to 0.52 and centred, the deep link reaches the frame and the frame has the
keyboard focus. "Exit stage" brings the page back without the stage (0.7.81).

Run:  uv run pytest -m e2e tests/e2e/test_stage.py -v
Prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from streamtex.stage import stage_script  # noqa: E402

pytestmark = pytest.mark.e2e

RAW = ("<html><head><title>deck</title><style>body{margin:0}</style></head><body>"
       "<h1 id='a'>A</h1><div id='probe' style='width:50vw;height:50vh;background:#c33'></div>"
       "<script>" + stage_script() +
       "if (new URLSearchParams(location.search).get('stage')) stxStage(window, 1920, 1080);</script>"
       "</body></html>")


@pytest.fixture
def page(tmp_path):
    f = tmp_path / "deck.html"
    f.write_text(RAW, encoding="utf-8")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1000, "height": 600})
        pg.goto(f.as_uri() + "?stage=1920x1080#a")
        pg.wait_for_selector("#stx-stage iframe")
        pg.frame_locator("#stx-stage iframe").locator("#probe").wait_for()
        yield pg
        browser.close()


def test_the_frame_has_the_projector_viewport(page):
    inner = page.frames[1]
    assert inner.evaluate("[innerWidth, innerHeight]") == [1920, 1080]
    assert inner.evaluate("(() => { const r = document.getElementById('probe').getBoundingClientRect();"
                          " return [r.width, r.height]; })()") == [960, 540]
    assert inner.url.endswith("deck.html?stage_frame=1#a")            # stage removed, deep link kept
    assert inner.evaluate("!document.getElementById('stx-stage')")   # no stage inside the stage


def test_the_frame_is_scaled_centred_and_focused(page):
    assert float(page.evaluate("document.getElementById('stx-stage').dataset.scale")) == pytest.approx(1000 / 1920)
    box = page.locator("#stx-stage .stx-stage-box").bounding_box()
    assert box["width"] == pytest.approx(1000, abs=1) and box["y"] == pytest.approx((600 - 562.5) / 2, abs=1)
    assert page.evaluate("document.activeElement.tagName") == "IFRAME"
    assert "1920×1080 · 52 %" in page.locator("#stx-stage .stx-stage-bar").inner_text()


def test_resizing_the_window_fits_again(page):
    page.set_viewport_size({"width": 800, "height": 900})
    page.wait_for_timeout(100)
    box = page.locator("#stx-stage .stx-stage-box").bounding_box()
    assert box["width"] == pytest.approx(800, abs=1) and box["height"] == pytest.approx(450, abs=1)


def test_exit_stage_brings_the_page_back(page):
    page.get_by_role("button", name="Exit stage").click()
    page.wait_for_load_state()
    assert "stage=" not in page.url and page.url.endswith("deck.html#a")
    assert page.locator("#stx-stage").count() == 0
    assert page.evaluate("innerWidth") == 1000
