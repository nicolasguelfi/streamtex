"""A sidebar link to another page lands on its own slide (#127).

Deck: pages of 1, 20 and 3 slides (slides 1 | 2-21 | 22-24); every slide's
marker is ``s<n>``, and slide 12 holds the heading ``detail twelve``, which
is not a marker. From another page, a Markers entry lands on its marker and
a Contents heading on the slide that holds it, not on the page's first slide.

Continuous mode and the paginated HTML export already link each entry to its
own anchor; they are checked here so they stay that way.

Run:  uv run pytest -m e2e tests/e2e/test_nav_sidebar_target.py -v
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, select_tab, streamlit_deck, wait_ready  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "nav_sidebar_target_app"
VIEWPORT = {"width": 1600, "height": 1000}

CLICK_ENTRY = """(text) => {
  const sb = document.querySelector('[data-testid="stSidebar"]');
  const a = [...sb.querySelectorAll('a[href^="#"]')].find(
    x => x.offsetParent !== null && (x.textContent || '').trim().endsWith(text));
  if (!a) return null;
  const href = a.getAttribute('href');
  a.click();
  return href;
}"""


@pytest.fixture(scope="module")
def deck_url():
    with streamlit_deck(DECK) as url:
        yield url


def _slide(page) -> int:
    text = page.evaluate(
        "(document.querySelector('#streamtex-marker-nav') || {}).innerText || ''")
    counter = next(x for x in text.split("\n") if "/" in x)
    return int(counter.split("/")[0].strip().replace(" ", ""))


def _wait_slide(page, n: int) -> None:
    try:
        page.wait_for_function(
            "(n) => { const t = (document.querySelector('#streamtex-marker-nav') || {})"
            ".innerText || ''; return new RegExp('(^|\\\\D)' + n + ' /').test(t); }",
            arg=n, timeout=15_000)
    except Exception:  # noqa: BLE001 — the assertion below reports the slide reached
        pass
    page.wait_for_timeout(1500)                         # and it stays there


def _on_screen(page, n: int) -> bool:
    """The heading ``slide <n>`` reaches the upper half of the viewport (smooth scroll)."""
    try:
        page.wait_for_function(
            """(n) => {
              const el = [...document.querySelectorAll('div')].find(
                d => d.children.length === 0 && (d.textContent || '').trim() === 'slide ' + n);
              if (!el) return false;
              const r = el.getBoundingClientRect();
              return r.top >= -5 && r.top < window.innerHeight * 0.5;
            }""", arg=n, timeout=10_000)
        return True
    except Exception:  # noqa: BLE001 — the caller asserts
        return False


@pytest.mark.parametrize("start,tab,entry,expected", [
    (1, "Markers", "s15", 15),               # first page -> a slide in the middle of page 2
    (22, "Markers", "s15", 15),              # last page -> the same slide
    (1, "Markers", "s2", 2),                 # the first slide of the page: as before
    (1, "Contents", "detail twelve", 12),    # a heading that is not a marker: its slide
    (22, "Contents", "detail twelve", 12),
    (1, "Contents", "page c", 22),           # a heading on the page's first slide: as before
])
def test_cross_page_sidebar_link_lands_on_its_slide(deck_url, start, tab, entry, expected):
    with playwright.sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_context(viewport=VIEWPORT).new_page()
        page.set_default_timeout(60_000)
        try:
            wait_ready(page, f"{deck_url}/?slide={start}")
            assert _slide(page) == start
            select_tab(page, tab)
            href = page.evaluate(CLICK_ENTRY, entry)
            assert href and href.startswith("#stx-goto-"), href
            _wait_slide(page, expected)
            assert _slide(page) == expected, f"{tab} {entry!r} ({href})"
            assert _on_screen(page, expected), f"slide {expected} is not on screen"
        finally:
            browser.close()


@pytest.mark.parametrize("start", [1, 22])
def test_heading_far_down_a_tall_slide_is_shown(deck_url, start):
    """A Contents heading 2400 px down its slide (#131): its slide start would leave
    it below the screen, so the link shows the heading itself; the counter shows
    its slide, and stays there."""
    with playwright.sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_context(viewport=VIEWPORT).new_page()
        page.set_default_timeout(60_000)
        try:
            wait_ready(page, f"{deck_url}/?slide={start}")
            select_tab(page, "Contents")
            href = page.evaluate(CLICK_ENTRY, "far eighteen")
            assert href and href.startswith("#stx-goto-"), href
            _wait_slide(page, 18)
            page.wait_for_function(
                """() => { const el = [...document.querySelectorAll('div')].find(
                     d => d.children.length === 0 && (d.textContent || '').trim() === 'far eighteen');
                   if (!el) return false; const r = el.getBoundingClientRect();
                   return r.top >= -5 && r.bottom <= window.innerHeight; }""", timeout=10_000)
            page.wait_for_timeout(1500)                 # the tracker must not take it back
            assert _slide(page) == 18
        finally:
            browser.close()


def test_link_clicked_while_a_page_opens_keeps_its_slide(deck_url):
    """A link to page C clicked while page B is still opening is queued with its
    marker: the reader ends on that slide of page C, not on its first."""
    with playwright.sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_context(viewport=VIEWPORT).new_page()
        page.set_default_timeout(60_000)
        try:
            wait_ready(page, f"{deck_url}/?slide=1")
            select_tab(page, "Markers")
            page.evaluate("""() => {
              const sb = document.querySelector('[data-testid="stSidebar"]');
              const find = t => [...sb.querySelectorAll('a[href^="#stx-goto-"]')].find(
                x => (x.textContent || '').trim().endsWith(t));
              const a15 = find('s15'), a23 = find('s23');
              a15.click();               // page B starts opening...
              a23.click();               // ...and page C is queued with its marker
            }""")
            _wait_slide(page, 23)
            assert _slide(page) == 23
            assert _on_screen(page, 23)
        finally:
            browser.close()


@pytest.fixture(scope="module")
def continuous_url():
    os.environ["STX_E2E_CONTINUOUS"] = "1"          # read by the deck's book.py
    try:
        with streamlit_deck(DECK) as url:
            yield url
    finally:
        os.environ.pop("STX_E2E_CONTINUOUS", None)


@pytest.mark.parametrize("tab,entry,expected", [
    ("Markers", "s15", 15),
    ("Contents", "detail twelve", 12),
    ("Markers", "s23", 23),
])
def test_continuous_sidebar_link_lands_on_its_slide(continuous_url, tab, entry, expected):
    with playwright.sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_context(viewport=VIEWPORT).new_page()
        page.set_default_timeout(60_000)
        try:
            wait_ready(page, continuous_url)
            select_tab(page, tab)
            assert page.evaluate(CLICK_ENTRY, entry)
            _wait_slide(page, expected)
            assert _slide(page) == expected
        finally:
            browser.close()


@pytest.fixture(scope="module")
def export_pages(tmp_path_factory):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html

    root = tmp_path_factory.mktemp("export127")
    deck = root / "deck"
    shutil.copytree(DECK, deck)
    out = root / "out"
    result = CliRunner().invoke(export_html, [str(deck), "--html-mode", "paginated", "-o", str(out)])
    assert result.exit_code == 0, result.output
    return out / "deck" / "pages"


EXPORT_COUNTER = "(() => { const m = (document.body.innerText || '').match(/(\\d+) \\/ \\d+/);" \
                 " return m ? parseInt(m[1], 10) : null; })()"


@pytest.mark.parametrize("start", ["bck_a.html", "bck_c.html"])
def test_export_links_land_on_their_slide(export_pages, start):
    """The TOC heading and the counter's menu row, clicked from another page file."""
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport=VIEWPORT)
            page.goto((export_pages / start).as_uri())
            page.wait_for_timeout(1000)
            page.evaluate("(t) => [...document.querySelectorAll('#stx-sidebar a')]"
                          ".find(a => a.textContent.trim().endsWith(t)).click()", "detail twelve")
            page.wait_for_timeout(2000)
            assert page.url.endswith("bck_b.html#2-1-detail-twelve")
            assert page.evaluate(EXPORT_COUNTER) == 12
            page.goto((export_pages / start).as_uri())
            page.wait_for_timeout(1000)
            page.evaluate("[...document.querySelectorAll('.stx-mn-popup-item')]"
                          ".find(r => r.textContent.trim().endsWith('s15')).click()")
            page.wait_for_timeout(2000)
            assert page.evaluate(EXPORT_COUNTER) == 15
            assert _on_screen(page, 15)
        finally:
            browser.close()
