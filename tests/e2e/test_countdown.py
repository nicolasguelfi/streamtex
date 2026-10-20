"""st_countdown in a real browser, live and exported (#52) — the spec's acceptance list.

The fixture deck (fixtures/countdown_app) holds five racks, in this order:
0 chain 1×3 (3 s, 3 s, 1 min) · 1 parallel (3 s, 1 min) · 2 card types 2×3
(Tokyo and Luxembourg clocks, a free stopwatch, a 3 s countdown, a 3 s
stopwatch gate, a clock gate at 00:00, already past) · 3 break screen
(autostart, no global buttons) · 4 alarms (bell, gong, "off").

Run:  uv run pytest -m e2e tests/e2e/test_countdown.py -v
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import streamlit_deck  # noqa: E402

pytestmark = pytest.mark.e2e

DECK = Path(__file__).resolve().parent / "fixtures" / "countdown_app"
VIEWPORTS = [{"width": 1920, "height": 1080}, {"width": 1280, "height": 720}]
STATE = """([r, sel]) => [...document.querySelectorAll('.stx-cd')][r].querySelectorAll('.stx-cd-card').length &&
  [...[...document.querySelectorAll('.stx-cd')][r].querySelectorAll('.stx-cd-card')].map(c => ({
    digits: c.querySelector('.stx-cd-digits').textContent,
    run: c.classList.contains('stx-cd-running'), done: c.classList.contains('stx-cd-done'),
    at: c.querySelector('.stx-cd-at').textContent,
    atShown: getComputedStyle(c.querySelector('.stx-cd-at')).display !== 'none'}))"""


@pytest.fixture(scope="module")
def live_url():
    with streamlit_deck(DECK) as url:
        yield url


@pytest.fixture(scope="module")
def export_url(tmp_path_factory):
    from click.testing import CliRunner

    from streamtex.cli.export_cmd import export_html
    out = tmp_path_factory.mktemp("countdown_export")
    r = CliRunner().invoke(export_html, [str(DECK), "-o", str(out)])
    assert r.exit_code == 0, r.output
    return (out / "countdown_app" / "countdown_app.html").as_uri()


@pytest.fixture(params=["live", "export"])
def where(request, live_url, export_url):
    return request.param, (live_url if request.param == "live" else export_url)


@pytest.fixture
def browser():
    with playwright.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _open(browser, url, viewport=VIEWPORTS[0], context=None):
    page = context.new_page() if context else browser.new_page(viewport=viewport)
    page.goto(url)
    page.wait_for_function("() => document.querySelectorAll('.stx-cd').length === 5 && "
                           "[...document.querySelectorAll('.stx-cd')].every(e => e.__stxCd)", timeout=60000)
    time.sleep(1)
    return page


def _state(page, rack):
    return page.evaluate(STATE, [rack, None])


def _click(page, rack, selector, card=None):
    root = page.locator(".stx-cd").nth(rack)
    scope = root.locator(".stx-cd-card").nth(card) if card is not None else root
    scope.locator(selector).first.click()


def _show(page, rack):
    page.locator(".stx-cd").nth(rack).evaluate("e => e.scrollIntoView({block: 'center'})")
    time.sleep(0.3)


def test_nothing_runs_before_a_click_then_the_chain_hands_over(browser, where):
    page = _open(browser, where[1])
    time.sleep(1.5)
    s = _state(page, 0)
    assert [c["digits"] for c in s] == ["00:03", "00:03", "01:00"] and not any(c["run"] for c in s)
    assert not any(c["atShown"] for c in s)                     # the wall-time line collapses
    _show(page, 0)
    _click(page, 0, ".stx-cd-all-start")
    time.sleep(0.6)
    s = _state(page, 0)
    assert s[0]["run"] and not s[1]["run"] and s[0]["at"].startswith("ends at ") and s[0]["atShown"]
    time.sleep(3.2)
    s = _state(page, 0)
    assert s[0]["done"] and s[0]["digits"] == "00:03" and not s[0]["atShown"]   # initial duration, done tint
    assert s[1]["run"]                                           # handed over
    time.sleep(3.2)
    s = _state(page, 0)
    assert s[1]["done"] and s[2]["run"]
    opacity = page.evaluate("() => getComputedStyle(document.querySelector('.stx-cd')"
                            ".querySelector('.stx-cd-digits')).opacity")
    assert abs(float(opacity) - 0.45) < 0.01
    _click(page, 0, ".stx-cd-all-reset")
    s = _state(page, 0)
    assert [c["digits"] for c in s] == ["00:03", "00:03", "01:00"] and not any(c["run"] or c["done"] for c in s)


def test_parallel_cards_are_independent_and_racks_do_not_interfere(browser, where):
    page = _open(browser, where[1])
    _show(page, 1)
    _click(page, 1, ".stx-cd-go", card=1)
    time.sleep(0.6)
    s = _state(page, 1)
    assert s[1]["run"] and not s[0]["run"]
    assert not any(c["run"] for c in _state(page, 0))            # another rack of the page stays idle
    _click(page, 1, ".stx-cd-all-start")
    time.sleep(3.4)
    s = _state(page, 1)
    assert s[0]["done"] and s[1]["run"]                         # no hand-over in parallel


def test_pause_resume_recomputes_the_end_and_reset_restores(browser, where):
    page = _open(browser, where[1])
    _show(page, 0)
    _click(page, 0, ".stx-cd-go", card=2)
    time.sleep(0.5)
    first_end = _state(page, 0)[2]["at"]
    _click(page, 0, ".stx-cd-halt", card=2)
    paused = _state(page, 0)[2]
    assert not paused["run"] and not paused["atShown"]
    time.sleep(1.5)
    assert _state(page, 0)[2]["digits"] == paused["digits"]     # a paused card keeps its time
    _click(page, 0, ".stx-cd-go", card=2)
    time.sleep(0.4)
    resumed = _state(page, 0)[2]
    assert resumed["run"] and resumed["at"].startswith("ends at ") and resumed["digits"] == paused["digits"]
    assert first_end  # the end time is shown again (recomputed from now + time left)
    _click(page, 0, ".stx-cd-zero", card=2)
    s = _state(page, 0)[2]
    assert s["digits"] == "01:00" and not s["run"]


def test_autostart_starts_when_shown(browser, where):
    page = _open(browser, where[1])
    assert not _state(page, 3)[0]["run"]                        # off screen: waits
    assert page.locator(".stx-cd").nth(3).locator(".stx-cd-bar").count() == 0
    _show(page, 3)
    time.sleep(1.5)
    s = _state(page, 3)[0]
    assert s["run"] and s["digits"] < "15:00"


def test_types_cascade_overtime_and_a_past_clock_gate(browser, where):
    page = _open(browser, where[1])
    _show(page, 2)
    tz = page.evaluate("""() => [['Asia/Tokyo'], ['Europe/Luxembourg']].map(([z]) =>
        new Intl.DateTimeFormat('en-GB', {timeZone: z, hour12: false, hour: '2-digit', minute: '2-digit'})
        .format(new Date()))""")
    s = _state(page, 2)
    assert s[0]["digits"][:5] in _around(tz[0]) and s[0]["at"] == "Tokyo"
    assert s[1]["digits"][:5] in _around(tz[1]) and s[1]["at"] == "Luxembourg"
    assert s[5]["at"] == "Luxembourg · → 00:00"
    _click(page, 2, ".stx-cd-all-start")
    time.sleep(0.6)
    s = _state(page, 2)
    assert s[2]["run"] and s[3]["run"] and not s[4]["run"]     # free stopwatch passed, first gate runs
    time.sleep(3.2)
    s = _state(page, 2)
    assert s[3]["done"] and s[4]["run"]                         # countdown → next gate
    time.sleep(3.4)
    s = _state(page, 2)
    assert s[4]["done"] and s[4]["digits"] >= "00:03"           # overtime keeps counting, done tint
    time.sleep(1.6)                                             # > 1 s + one 250 ms tick
    assert _state(page, 2)[4]["digits"] > s[4]["digits"]
    assert s[5]["done"]                                         # 00:00 is past: hands over at once
    assert s[2]["run"]                                          # the free card still runs


def test_edit_apply_escape_and_targets(browser, where):
    page = _open(browser, where[1])
    _show(page, 0)
    digits = page.locator(".stx-cd").nth(0).locator(".stx-cd-digits").nth(2)
    _click(page, 0, ".stx-cd-go", card=2)
    digits.dblclick()
    inp = digits.locator("input")
    assert inp.input_value() in ("01:00", "00:59")
    time.sleep(0.6)
    assert inp.count() == 1                                     # ticks never overwrite the input
    inp.fill("40:30")
    inp.press("Enter")
    time.sleep(0.4)
    s = _state(page, 0)[2]
    assert s["run"] and s["digits"] in ("40:30", "40:29")       # a running card restarts from the value
    digits.dblclick()
    digits.locator("input").fill("5")
    digits.locator("input").press("Escape")
    assert _state(page, 0)[2]["digits"] in ("40:30", "40:29", "40:28")
    _click(page, 0, ".stx-cd-zero", card=2)
    assert _state(page, 0)[2]["digits"] == "01:00"              # ↺ returns to the original
    # a stopwatch: double-click sets its target in minutes; a clock: its target HH:MM
    _show(page, 2)
    free = page.locator(".stx-cd").nth(2).locator(".stx-cd-digits").nth(2)
    free.dblclick()
    assert free.locator("input").input_value() == ""
    free.locator("input").fill("0:02")
    free.locator("input").press("Enter")
    _click(page, 2, ".stx-cd-go", card=2)
    time.sleep(2.6)
    assert _state(page, 2)[2]["done"]
    clock = page.locator(".stx-cd").nth(2).locator(".stx-cd-digits").nth(5)
    clock.dblclick()
    assert clock.locator("input").input_value() == "00:00"
    clock.locator("input").fill("23:59")
    clock.locator("input").press("Enter")
    assert _state(page, 2)[5]["at"] == "Luxembourg · → 23:59"


def test_bells_card_global_and_reload(browser, where):
    ctx = browser.new_context(viewport=VIEWPORTS[0])
    page = _open(browser, where[1], context=ctx)
    _show(page, 4)
    rack = page.locator(".stx-cd").nth(4)
    bells = rack.locator(".stx-cd-card .stx-cd-bell")
    assert bells.count() == 2                                   # "off" has no bell
    glyphs = lambda: [b.text_content() for b in rack.locator(".stx-cd-bell").all()]  # noqa: E731
    assert set(glyphs()) == {"\U0001F515"}                     # an alarmed rack starts muted
    bells.nth(0).click()
    assert glyphs() == ["\U0001F515", "\U0001F514", "\U0001F515"]   # global: not all armed
    rack.locator(".stx-cd-all-bell").click()
    assert set(glyphs()) == {"\U0001F514"}
    rack.locator(".stx-cd-all-bell").click()
    assert set(glyphs()) == {"\U0001F515"}
    bells.nth(1).click()
    page.reload()
    page.wait_for_function("() => document.querySelectorAll('.stx-cd').length === 5 && "
                           "[...document.querySelectorAll('.stx-cd')].every(e => e.__stxCd)", timeout=60000)
    rack = page.locator(".stx-cd").nth(4)
    assert [b.text_content() for b in rack.locator(".stx-cd-bell").all()] == \
        ["\U0001F515", "\U0001F515", "\U0001F514"]              # remembered per card
    ctx.close()


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=["1920", "1280"])
def test_every_card_fits(browser, where, viewport):
    page = _open(browser, where[1], viewport)
    _show(page, 2)
    _click(page, 2, ".stx-cd-all-start")
    time.sleep(0.8)
    fits = page.evaluate("""() => [...document.querySelectorAll('.stx-cd-card')].map(c => {
        const r = c.getBoundingClientRect(), d = c.querySelector('.stx-cd-digits').getBoundingClientRect();
        return d.left >= r.left && d.right <= r.right && c.scrollHeight <= c.clientHeight + 1; })""")
    assert all(fits), fits
    assert page.evaluate("() => [...document.querySelectorAll('.stx-cd-card')].every("
                         "c => getComputedStyle(c).overflowY === 'hidden')")


def test_racks_survive_a_rerun(browser, live_url):
    page = _open(browser, live_url)
    _show(page, 0)
    _click(page, 0, ".stx-cd-go", card=2)
    time.sleep(0.5)
    page.evaluate("() => document.activeElement && document.activeElement.blur()")
    page.keyboard.press("r")                                    # Streamlit's rerun shortcut
    time.sleep(3)
    s = _state(page, 0)[2]
    assert s["run"] and s["digits"] < "01:00"


def _around(hhmm: str) -> set[str]:
    """*hhmm* and the minutes on each side (the page and the check are not one instant)."""
    h, m = map(int, hhmm.split(":"))
    t = h * 60 + m
    return {f"{(x // 60) % 24:02d}:{x % 60:02d}" for x in (t - 1, t, t + 1)}
