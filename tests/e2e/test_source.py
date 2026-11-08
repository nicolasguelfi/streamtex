"""Real-Chromium e2e: copy where the slide is written, open it in the editor (#157).

The live app runs the gesture from the marker widget's sandboxed component
frame (the trap of "Exit stage", 0.7.81): the clipboard and the editor link
must work from there. The HTML export runs it from the page itself. Both are
measured here with the real clipboard and a real navigation.

Run:  uv run pytest -m e2e tests/e2e/test_source.py -v
Prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import functools
import http.server
import textwrap
import threading
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from tests.e2e._nav_harness import free_port, launch_browser, streamlit_deck  # noqa: E402

pytestmark = pytest.mark.e2e

BLOCK = '''
import streamtex as stx
def build(**k):
    with stx.st_slide(marker="One"):                    # @1
        stx.st_write("Slide one")
    with stx.st_slide(cut=True, marker="Two"):          # @2
        stx.st_write("Slide two")
'''
BOOK = '''
import streamlit as st
import streamtex as stx
from blocks import bck_deck
st.set_page_config(page_title="deck", layout="wide")
stx.set_presentation_config(stx.PresentationConfig(title="deck", footer=True, counter_mode="slide"))
stx.st_book([bck_deck], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
            source=SOURCE)
'''


def _deck(tmp_path: Path, source: dict) -> Path:
    root = tmp_path / "proj"
    deck = root / "docs" / "deck"
    (deck / "blocks").mkdir(parents=True)
    (root / ".git").mkdir()                                  # the project root
    (deck / "blocks" / "__init__.py").write_text("")
    (deck / "blocks" / "bck_deck.py").write_text(textwrap.dedent(BLOCK))
    (deck / "book.py").write_text(textwrap.dedent(BOOK).replace("SOURCE", repr(source)))
    return deck


def _line(deck: Path, tag: str) -> int:
    lines = (deck / "blocks" / "bck_deck.py").read_text().splitlines()
    return next(i for i, line in enumerate(lines, 1) if f"# {tag}" in line)


class _Probe(http.server.SimpleHTTPRequestHandler):
    """Serves the export, and records the editor link's request (/probe?...)."""
    hits: list[str] = []

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/probe"):
            _Probe.hits.append(self.path)
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, *a):
        pass


@pytest.fixture
def probe(tmp_path):
    _Probe.hits = []
    port = free_port()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port),
                                             functools.partial(_Probe, directory=str(tmp_path)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


def _clipboard(page) -> str:
    return page.evaluate("navigator.clipboard.readText()")


def test_the_live_app_copies_and_opens_from_the_widget(tmp_path, probe):
    deck = _deck(tmp_path, {"live": "on", "editor": probe + "/probe?f={abs}&l={line}"})
    with streamlit_deck(deck) as url, playwright.sync_playwright() as p:
        browser = launch_browser(p)
        ctx = browser.new_context(viewport={"width": 1200, "height": 800},
                                  permissions=["clipboard-read", "clipboard-write"])
        page = ctx.new_page()
        page.goto(url)
        counter = page.locator('#streamtex-marker-nav span[title*="copy where this slide is written"]')
        counter.wait_for(timeout=60000)
        page.wait_for_function("document.querySelector('#streamtex-marker-nav').textContent.includes('1 / 2')")

        counter.click(modifiers=["Alt"])                                  # ⌥-click: copy
        page.wait_for_selector("#stx-src-toast", state="attached")
        line = _clipboard(page)
        assert line.startswith("docs/deck · 1/2 · docs/deck/blocks/bck_deck.py:%d · deck#1 · « One »" % _line(deck, "@1"))
        assert not page.locator('#streamtex-marker-nav input[type="number"]').is_visible()   # no jump box

        page.locator('#streamtex-marker-nav [data-stx-step="1"]').click()  # slide 2
        page.wait_for_function("document.querySelector('#streamtex-marker-nav').textContent.includes('2 / 2')")
        page.mouse.click(600, 300)
        page.keyboard.press("Control+Alt+Meta+KeyL")                      # the shortcut
        page.wait_for_function("t => document.getElementById('stx-src-toast').textContent.includes(t)",
                               arg=":%d" % _line(deck, "@2"))
        assert " · 2/2 · " in _clipboard(page) and "deck#2" in _clipboard(page)

        page.locator(".stx-pf-counter").click()                           # the footer's counter
        page.wait_for_timeout(300)
        assert " · 2/2 · " in _clipboard(page)

        counter.click()                                                   # a plain click keeps its role
        assert page.locator('#streamtex-marker-nav input[type="number"]').is_visible()
        page.keyboard.press("Escape")

        with page.expect_request(lambda r: "/probe" in r.url, timeout=10000) as req:
            counter.click(modifiers=["Meta"])                             # ⌘-click: open in the editor
        assert req.value.url.endswith("/docs/deck/blocks/bck_deck.py&l=%d" % _line(deck, "@2"))
        assert str(deck / "blocks" / "bck_deck.py").replace(" ", "%20") in req.value.url
        browser.close()


def test_the_export_copies_the_line(tmp_path, probe):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html
    deck = _deck(tmp_path, {"html": "on"})
    r = CliRunner().invoke(export_html, [str(deck), "-o", str(tmp_path / "out")])
    assert r.exit_code == 0, r.output
    html = next((tmp_path / "out").rglob("deck.html"))
    with playwright.sync_playwright() as p:
        browser = launch_browser(p)
        ctx = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = ctx.new_page()
        page.goto(f"{probe}/{html.relative_to(tmp_path).as_posix()}")
        counter = page.locator("#stx-marker-nav .stx-mn-counter")
        counter.wait_for()
        counter.click(modifiers=["Alt"])
        page.wait_for_selector("#stx-src-toast", state="attached")
        assert _clipboard(page).startswith("docs/deck · 1/2 · docs/deck/blocks/bck_deck.py:%d · deck#1"
                                           % _line(deck, "@1"))
        assert not page.locator(".stx-mn-popup").is_visible()             # the list did not open
        counter.click()
        assert page.locator(".stx-mn-popup").is_visible()                 # a plain click still does
        page.keyboard.press("Escape")
        counter.click(modifiers=["Meta"])                                  # no editor in an export
        page.wait_for_function("document.getElementById('stx-src-toast').textContent.includes('live app')")
        assert _Probe.hits == []
        browser.close()
