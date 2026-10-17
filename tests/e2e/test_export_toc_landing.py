"""Real-Chromium e2e: where a Contents link lands in an HTML export (#128).

A Contents link leads to the start of the slide holding the heading (its
marker), as in the live app (#127), unless the heading would then sit below
the screen (a long section of a text page): then to the heading itself.  The
counter shows the heading's slide in both cases.  The
landing stays in place while content above it grows (late images, videos,
diagrams) until the reader's first gesture.

Fixture: 24 slides of 700 px; page file p0 holds slides 1-2, p1 slides
3-24.  "Twelve" sits 350 px down slide 12, "Fifteen" at the top of slide 15,
"Twenty far" 1500 px down slide 20 (2200 px high).
Slide 5 holds a block that ``window.__grow()`` makes 1500 px taller, with
scroll anchoring off (``overflow-anchor: none``), so a late layout shift
is not hidden by the browser.

Run:  uv run pytest -m e2e tests/e2e/test_export_toc_landing.py -v
Prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from streamtex.export_enrich import enrich_export_html  # noqa: E402

pytestmark = pytest.mark.e2e

VIEWPORT = {"width": 1280, "height": 720}
SLIDES = 24
FILES = ["p0.html", "p1.html"]


def _page_of(i: int) -> int:
    return 0 if i < 2 else 1


MARKERS = [{"index": i, "label": f"s{i + 1}", "anchor": f"mk{i}", "page_idx": _page_of(i)}
           for i in range(SLIDES)]
TOC = [
    {"level": 1, "title": "One", "key_anchor": "h1", "page_idx": 0, "_markers_before": 1},
    {"level": 1, "title": "Twelve", "key_anchor": "h12", "page_idx": 1, "_markers_before": 12},
    {"level": 1, "title": "Fifteen", "key_anchor": "h15", "page_idx": 1, "_markers_before": 15},
    {"level": 2, "title": "Twenty far", "key_anchor": "h20", "page_idx": 1, "_markers_before": 20},
]


def _slide(i: int) -> str:
    inner = f"Slide {i + 1}"
    if i == 0:
        inner = '<h2 id="h1">One</h2>'
    elif i == 11:
        inner += '<div style="height:350px"></div><h2 id="h12">Twelve</h2>'
    elif i == 14:
        inner = '<h2 id="h15">Fifteen</h2>'
    elif i == 19:
        inner += '<div style="height:1500px"></div><h2 id="h20">Twenty far</h2>'
    height = 2200 if i == 19 else 700
    grow = '<div id="grow" style="height:0"></div>' if i == 4 else ""
    return (f'<div id="mk{i}"></div>'
            f'<section style="height:{height}px;box-sizing:border-box;border-top:1px solid">{inner}</section>{grow}')


def _raw(slides: range) -> str:
    body = "\n".join(_slide(i) for i in slides)
    return ("<html><head><title>deck</title>"
            "<style>body{margin:0} html{overflow-anchor:none}</style></head>\n<body>\n"
            f"{body}\n<script>window.__grow = function() {{"
            " var g = document.getElementById('grow'); if (g) g.style.height = '1500px'; };"
            "</script>\n</body></html>")


@pytest.fixture(scope="module")
def paginated(tmp_path_factory):
    d = tmp_path_factory.mktemp("paged")
    for page, slides in ((0, range(0, 2)), (1, range(2, SLIDES))):
        nav = {"mode": "paginated", "files": FILES, "here": [page], "prefix": "", "other": None}
        (d / FILES[page]).write_text(
            enrich_export_html(_raw(slides), toc=TOC, markers=MARKERS, page_nav=nav),
            encoding="utf-8")
    return d


@pytest.fixture(scope="module")
def continuous(tmp_path_factory):
    out = tmp_path_factory.mktemp("cont") / "deck.html"
    out.write_text(enrich_export_html(_raw(range(SLIDES)), toc=TOC, markers=MARKERS),
                   encoding="utf-8")
    return out


@pytest.fixture(scope="module")
def browser():
    with playwright.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _open(browser, url: str):
    page = browser.new_page(viewport=VIEWPORT)
    page.goto(url)
    page.wait_for_selector("#stx-marker-nav")
    return page


def _state(page) -> tuple[str, int, int]:
    """Counter text, top of slide 12's marker, top of slide 15's marker."""
    return tuple(page.evaluate("""() => [
        document.querySelector('#stx-marker-nav .stx-mn-counter').textContent.trim(),
        Math.round(document.getElementById('mk11').getBoundingClientRect().top),
        Math.round(document.getElementById('mk14').getBoundingClientRect().top)]"""))


def _settle(page) -> tuple[str, int, int]:
    """The state once it has not changed for 1 s (5 reads 200 ms apart)."""
    last, same = None, 0
    for _ in range(60):
        page.wait_for_timeout(200)
        s = _state(page)
        same = same + 1 if s == last else 0
        last = s
        if same >= 5:
            break
    return last


def _click_contents(page, title: str) -> None:
    page.locator(".stx-toc-entry a", has_text=title).click()


def test_link_from_another_file_lands_on_the_slide_start(browser, paginated):
    page = _open(browser, (paginated / "p0.html").as_uri())
    _click_contents(page, "Twelve")
    page.wait_for_url("**/p1.html#h12")
    counter, top12, _ = _settle(page)
    assert counter == "12 / 24"
    assert abs(top12) <= 2, f"slide 12 starts {top12}px from the top"


def test_landing_holds_while_content_above_grows(browser, paginated):
    page = _open(browser, (paginated / "p0.html").as_uri())
    _click_contents(page, "Twelve")
    page.wait_for_url("**/p1.html#h12")
    _settle(page)
    page.evaluate("window.__grow()")                       # a late image above
    counter, top12, _ = _settle(page)
    assert counter == "12 / 24"
    assert abs(top12) <= 2, f"slide 12 pushed {top12}px down"


def test_reader_gesture_ends_the_hold(browser, paginated):
    page = _open(browser, (paginated / "p0.html").as_uri())
    _click_contents(page, "Twelve")
    page.wait_for_url("**/p1.html#h12")
    _settle(page)
    page.mouse.move(640, 360)
    page.mouse.wheel(0, 300)
    _settle(page)
    page.evaluate("window.__grow()")
    _, top12, _ = _settle(page)
    assert top12 > 1000, "the page was pulled back after the reader scrolled"


def test_link_in_the_same_file_lands_on_the_slide_start_twice(browser, paginated):
    page = _open(browser, (paginated / "p1.html").as_uri() + "?slide=20")
    _settle(page)
    for _ in range(2):                    # the second click: same hash, no hashchange
        _click_contents(page, "Twelve")
        counter, top12, _ = _settle(page)
        assert counter == "12 / 24"
        assert abs(top12) <= 2, f"slide 12 starts {top12}px from the top"
        page.mouse.move(640, 360)
        page.mouse.wheel(0, 900)
        _settle(page)


def test_heading_at_the_top_of_its_slide_unchanged(browser, paginated):
    page = _open(browser, (paginated / "p0.html").as_uri())
    _click_contents(page, "Fifteen")
    page.wait_for_url("**/p1.html#h15")
    counter, _, top15 = _settle(page)
    assert counter == "15 / 24"
    assert abs(top15) <= 2


def test_continuous_export_lands_on_the_slide_start(browser, continuous):
    page = _open(browser, continuous.as_uri())
    _click_contents(page, "Twelve")
    counter, top12, _ = _settle(page)
    assert counter == "12 / 24"
    assert abs(top12) <= 2, f"slide 12 starts {top12}px from the top"
    page.evaluate("window.__grow()")
    counter, top12, _ = _settle(page)
    assert counter == "12 / 24" and abs(top12) <= 2


def test_heading_far_down_a_long_slide_lands_on_the_heading(browser, paginated):
    page = _open(browser, (paginated / "p0.html").as_uri())
    _click_contents(page, "Twenty far")
    page.wait_for_url("**/p1.html#h20")
    _settle(page)
    page.evaluate("window.__grow()")
    _settle(page)
    counter, top20 = page.evaluate("""() => [
        document.querySelector('#stx-marker-nav .stx-mn-counter').textContent.trim(),
        Math.round(document.getElementById('h20').getBoundingClientRect().top)]""")
    assert counter == "20 / 24"
    assert abs(top20) <= 2, f"the heading is {top20}px from the top"
