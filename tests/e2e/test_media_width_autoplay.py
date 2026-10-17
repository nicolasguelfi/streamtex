"""st_video(width=, align=) draws the same box live and in the export (#126);
autoplay=True without muted starts, muted (#35).

Widths are compared with the full-width video of the same page: 50% is half
of it, 400 px is 400 px, align="left" starts at its left edge. The autoplay
check reads the page only once the video exists: every Playwright call into a
page counts as a user gesture, which would let any video play.

Run:  uv run pytest -m e2e tests/e2e/test_media_width_autoplay.py -v
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import streamlit_deck  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "media_app"
VIEWPORT = {"width": 1920, "height": 1080}
READ = """() => [...document.querySelectorAll('video')].map(v => {
  const r = v.getBoundingClientRect();
  return {left: r.left, right: r.right, width: r.width, paused: v.paused, muted: v.muted, t: v.currentTime}; })"""


def _check(videos: list[dict]) -> None:
    auto, full, half, px400, halfleft = videos
    assert abs(half["width"] - full["width"] / 2) <= 2
    assert abs((half["left"] - full["left"]) - (full["right"] - half["right"])) <= 2      # centred
    assert abs(px400["width"] - 400) <= 1
    assert abs(halfleft["left"] - full["left"]) <= 1 and abs(halfleft["width"] - half["width"]) <= 1
    assert auto["muted"] and not auto["paused"] and auto["t"] > 0


def _read_after(page, url: str) -> list[dict]:
    page.goto(url, wait_until="load")
    time.sleep(10)                           # no call into the page before the videos exist
    return page.evaluate(READ)


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck(DECK) as url:
        yield url


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html

    root = tmp_path_factory.mktemp("media")
    deck = root / "deck"
    shutil.copytree(DECK, deck)
    out = root / "out"
    result = CliRunner().invoke(export_html, [str(deck), "--html-mode", "continuous", "-o", str(out)])
    assert result.exit_code == 0, result.output
    return out / "deck" / "deck.html"


def test_live_sizes_and_autoplay(deck_url):
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            _check(_read_after(browser.new_page(viewport=VIEWPORT), deck_url))
        finally:
            browser.close()


def test_export_sizes_and_autoplay(exported):
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            _check(_read_after(browser.new_page(viewport=VIEWPORT), exported.as_uri()))
        finally:
            browser.close()
