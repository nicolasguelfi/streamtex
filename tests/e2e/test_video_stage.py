"""st_video(theater=, fit=, fullscreen=) in a real browser, live and exported (#56).

- theater="slide" fills the screen height in the flow; fit="cover" crops;
- theater="window" covers the window while its slide is on screen, leaves
  when the slide does (pausing the video), comes back with it, and closes
  with its × button; the sidebars stop covering it while it is open;
- fullscreen=True enters fullscreen on the first Play only and leaves it
  when the video ends;
- a page zoom does not shrink the stage;
- printing never shows the window overlay.

Playwright calls count as user gestures, which is what fullscreen needs.

Run:  uv run pytest -m e2e tests/e2e/test_video_stage.py -v
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import streamlit_deck  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "stage_app"
VIEWPORT = {"width": 1600, "height": 900}
BOXES = """() => [...document.querySelectorAll('.stx-vbox')].map(b => {
  const r = b.getBoundingClientRect(), v = b.querySelector('video');
  return {cls: b.className, w: Math.round(r.width), h: Math.round(r.height), top: Math.round(r.top),
          fit: getComputedStyle(v).objectFit, paused: v.paused, pos: getComputedStyle(b).position}; })"""
FLAG = "() => document.documentElement.classList.contains('stx-video-open')"
FULL = "() => document.fullscreenElement ? document.fullscreenElement.tagName : null"
PLAY_LAST = """() => { const v = [...document.querySelectorAll('.stx-vbox')].pop().querySelector('video');
  v.muted = true; v.play(); }"""


@pytest.fixture(scope="module")
def live_url():
    with streamlit_deck(DECK) as url:
        yield url


@pytest.fixture(scope="module")
def paginated_url():
    os.environ["STAGE_PAGINATE"] = "1"
    try:
        with streamlit_deck(DECK) as url:
            yield url
    finally:
        del os.environ["STAGE_PAGINATE"]


@pytest.fixture(scope="module")
def export_url(tmp_path_factory):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html
    out = tmp_path_factory.mktemp("stage_export")
    r = CliRunner().invoke(export_html, [str(DECK), "-o", str(out)])
    assert r.exit_code == 0, r.output
    return (out / "stage_app" / "stage_app.html").as_uri()


@pytest.fixture
def page():
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser.new_page(viewport=VIEWPORT)
        browser.close()


def _open(page, url, main):
    page.goto(url)
    page.locator(main).get_by_text("case-end").first.wait_for(state="attached", timeout=60000)
    time.sleep(2)


def _go(page, main, name):
    page.locator(main).get_by_text(f"case-{name}").first.evaluate("e => e.scrollIntoView({block: 'start'})")
    time.sleep(1.2)


def _window(page):
    return next(b for b in page.evaluate(BOXES) if "stx-theater-window" in b["cls"])


def _check_stage(page, main):
    slide, cover, window, plain = page.evaluate(BOXES)
    assert "stx-theater-slide" in slide["cls"] and slide["h"] == VIEWPORT["height"]
    assert slide["fit"] == "contain" and cover["fit"] == "cover" and cover["h"] == VIEWPORT["height"]
    assert window["pos"] == "static" and "stx-open" not in window["cls"]   # off screen: closed
    assert plain["h"] < VIEWPORT["height"] and plain["fit"] == "contain"

    _go(page, main, "window")
    w = _window(page)
    assert "stx-open" in w["cls"] and w["pos"] == "fixed"
    assert (w["w"], w["h"]) == (VIEWPORT["width"], VIEWPORT["height"]) and not w["paused"]
    assert page.evaluate(FLAG)

    _go(page, main, "end")                                 # leaving the slide closes and pauses
    w = _window(page)
    assert "stx-open" not in w["cls"] and w["paused"] and not page.evaluate(FLAG)

    _go(page, main, "window")                              # coming back opens, autoplay resumes
    w = _window(page)
    assert "stx-open" in w["cls"] and not w["paused"]
    page.locator(".stx-vbox-close").first.click()
    time.sleep(0.3)
    assert "stx-open" not in _window(page)["cls"] and not page.evaluate(FLAG)

    _go(page, main, "fullscreen")
    page.evaluate(PLAY_LAST)
    time.sleep(0.8)
    assert page.evaluate(FULL) == "VIDEO"                  # the first Play
    time.sleep(3)                                          # clip.mp4 lasts 2 s
    assert page.evaluate(FULL) is None                     # left at the end
    page.evaluate(PLAY_LAST)
    time.sleep(0.8)
    assert page.evaluate(FULL) is None                     # only the first Play

    page.emulate_media(media="print")
    _go(page, main, "window")
    assert _window(page)["pos"] == "static"


def test_live(live_url, page):
    _open(page, live_url, "[data-testid=stMain]")
    _check_stage(page, "[data-testid=stMain]")


def test_export(export_url, page):
    _open(page, export_url, ".streamtex-page")
    _check_stage(page, ".streamtex-page")


@pytest.mark.parametrize("zoom", ["0.8", "1.25"])
def test_export_zoom_does_not_shrink_the_stage(export_url, page, zoom):
    _open(page, export_url, ".streamtex-page")
    page.evaluate(f"() => document.querySelector('.streamtex-page').style.zoom = '{zoom}'")
    _go(page, ".streamtex-page", "slide")
    assert page.evaluate(BOXES)[0]["h"] == VIEWPORT["height"]
    _go(page, ".streamtex-page", "window")
    w = _window(page)
    assert (w["w"], w["h"]) == (VIEWPORT["width"], VIEWPORT["height"])


def test_paginated_page_change_gives_the_sidebar_back(paginated_url, page):
    page.goto(f"{paginated_url}/?page=4")
    page.locator("[data-testid=stMain]").get_by_text("case-window").first.wait_for(timeout=60000)
    time.sleep(3)
    assert "stx-open" in _window(page)["cls"] and page.evaluate(FLAG)
    page.get_by_text("▶").first.click()                   # the nav bar stays above the video
    page.locator("[data-testid=stMain]").get_by_text("case-fullscreen").first.wait_for(timeout=30000)
    time.sleep(1)
    assert not page.evaluate(FLAG)
