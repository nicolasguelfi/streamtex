"""A video under the app's static folder is served, live and in the export (#140).

The media deck of ``test_media_width_autoplay`` again, with ``clip.mp4``
moved to ``static/media/`` and static serving on. Live, every player plays
``/app/static/media/clip.mp4`` (Streamlit's static route, not its media
file manager); in the export, the file lands in ``data/`` instead of a
base64 ``data:`` URI. Sizes, autoplay and sound behave as before.

Run:  uv run pytest -m e2e tests/e2e/test_served_video.py -v
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import streamlit_deck  # noqa: E402
from .test_media_width_autoplay import DECK, VIEWPORT, _check, _read_after  # noqa: E402

pytestmark = pytest.mark.e2e

SOURCES = "() => [...document.querySelectorAll('video')].map(v => v.currentSrc)"


@pytest.fixture(scope="module")
def served_deck(tmp_path_factory) -> Path:
    deck = tmp_path_factory.mktemp("served") / "deck"
    shutil.copytree(DECK, deck, ignore=shutil.ignore_patterns("__pycache__"))
    (deck / "static" / "media").mkdir(parents=True)
    (deck / "clip.mp4").rename(deck / "static" / "media" / "clip.mp4")
    blocks = deck / "blocks" / "__init__.py"
    text = blocks.read_text()
    old = 'CLIP = str(Path(__file__).resolve().parent.parent / "clip.mp4")'
    assert old in text
    blocks.write_text(text.replace(old, 'CLIP = "static/media/clip.mp4"'))
    (deck / ".streamlit").mkdir()
    (deck / ".streamlit" / "config.toml").write_text("[server]\nenableStaticServing = true\n")
    return deck


def _read(url: str) -> tuple[list[dict], list[str]]:
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport=VIEWPORT)
            videos = _read_after(page, url)
            return videos, page.evaluate(SOURCES)
        finally:
            browser.close()


def test_live_plays_the_served_file(served_deck):
    with streamlit_deck(served_deck) as url:
        videos, sources = _read(url)
    _check(videos)
    assert len(sources) == 6
    assert all(s.endswith("/app/static/media/clip.mp4") for s in sources), sources


def test_export_copies_the_file_into_data(served_deck, tmp_path):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html

    result = CliRunner().invoke(export_html, [str(served_deck), "--html-mode", "continuous",
                                              "-o", str(tmp_path)])
    assert result.exit_code == 0, result.output
    page = tmp_path / "deck" / "deck.html"
    assert "data:video" not in page.read_text()
    videos, sources = _read(page.as_uri())
    _check(videos)
    assert len(sources) == 6
    assert all("/deck/data/" in s and s.endswith(".mp4") for s in sources), sources
