"""st_video(max_vw=, max_vh=) draws the same bounded player live and in the export (#141).

The 16:9 clip in a 1920 × 1080 window: max_vw=100, max_vh=50 gives
960 × 540 (the height bound wins); max_vw=40 gives 768 wide (the width
bound wins). In an 800 px window, the first fills its column (below 50 vh), the second 40 vw.
Inside st_zoom(130), max_vh=30 is multiplied by the zoom: 30 vh × 1.3 of
the window on screen. With fullscreen=True the bounded box still applies.

Run:  uv run pytest -m e2e tests/e2e/test_video_bounds.py -v
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import streamlit_deck  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "bounds_app"
READ = """() => [...document.querySelectorAll('video')].map(v => {
  const r = v.getBoundingClientRect(); return {w: r.width, h: r.height}; })"""


def _read(url: str, width: int, height: int) -> list[dict]:
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(url, wait_until="load")
            time.sleep(10)
            return page.evaluate(READ)
        finally:
            browser.close()


def _check_wide(videos: list[dict]) -> None:
    both, vw, zoom, fs = videos
    assert abs(both["h"] - 540) <= 2 and abs(both["w"] - 960) <= 2, both
    assert abs(vw["w"] - 768) <= 2 and abs(vw["h"] - 432) <= 2, vw
    assert abs(zoom["h"] - 1080 * 0.30 * 1.3) <= 3, zoom
    assert abs(fs["h"] - 270) <= 2, fs


def _check_narrow(videos: list[dict]) -> None:
    both, vw = videos[0], videos[1]
    assert both["w"] >= vw["w"] and both["h"] < 540 - 2, both     # the column's width, not 50 vh
    assert abs(vw["w"] - 320) <= 2, vw


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck(DECK) as url:
        yield url


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html

    root = tmp_path_factory.mktemp("bounds")
    fixtures = root / "fixtures"
    shutil.copytree(DECK, fixtures / "bounds_app", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(DECK.parent / "media_app", fixtures / "media_app",
                    ignore=shutil.ignore_patterns("__pycache__"))
    out = root / "out"
    result = CliRunner().invoke(export_html, [str(fixtures / "bounds_app"), "--html-mode", "continuous",
                                              "-o", str(out)])
    assert result.exit_code == 0, result.output
    return out / "bounds_app" / "bounds_app.html"


@pytest.mark.parametrize("where", ["live", "export"])
def test_wide_window(where, deck_url, exported):
    _check_wide(_read(deck_url if where == "live" else exported.as_uri(), 1920, 1080))


@pytest.mark.parametrize("where", ["live", "export"])
def test_narrow_window(where, deck_url, exported):
    _check_narrow(_read(deck_url if where == "live" else exported.as_uri(), 800, 1080))
