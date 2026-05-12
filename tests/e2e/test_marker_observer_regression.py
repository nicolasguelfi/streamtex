"""End-to-end regression test for the marker observer.

Bug this test guards against (introduced 0.6.21, fixed 0.6.24):

    When the user changed a sidebar control (e.g. the Width % or Zoom %
    number inputs in streamtex's Settings panel), Streamlit's
    reconciliation stripped our `class` / `data-stx-*-uid` / inline
    `style` from existing `stVerticalBlock` elements WITHOUT adding or
    removing children.  The marker observer was watching `childList`
    only, so it never re-applied — per-instance CSS rules targeting
    `[data-stx-block-uid="…"]` no longer matched, and cells lost their
    backgrounds, borders, and 2-column grid layout.

The test:

  1. Launches the minimal fixture under `fixtures/marker_observer_app/`.
  2. Opens Chromium via Playwright, waits for the marker observer to
     install (`window.__stxMarkerObs === true`).
  3. Reads DOM state #1 (class counts, uid attributes, computed display
     on the first .stx-grid, computed backgroundColor on the first
     .stx-block).
  4. Opens the Settings expander and clicks the Width % minus button 3
     times → 3 Streamlit reruns.
  5. Reads DOM state #2.
  6. Asserts:
       - all class counts preserved
       - all uid attribute counts preserved
       - first .stx-grid keeps `display: grid`
       - first colored .stx-block keeps its backgroundColor
       - grid track count preserved (column widths may shrink with width)

Run with:
    uv run pytest -m e2e tests/e2e/test_marker_observer_regression.py -v

CI prerequisite (one-time per runner):
    uv run playwright install chromium
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from contextlib import closing
from pathlib import Path  # noqa: E402

import pytest

playwright = pytest.importorskip("playwright.sync_api")

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "marker_observer_app"
REPO_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.e2e


def _free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_http(url: str, timeout_s: float = 60.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 — connection refused is normal
            last_err = exc
        time.sleep(0.4)
    raise TimeoutError(f"streamlit never became ready on {url}: {last_err}")


_READOUT_JS = r"""
() => {
  const counts = (sel) => document.querySelectorAll(sel).length;
  const first_grid = document.querySelector('.stx-grid');
  let grid_info = null;
  if (first_grid) {
    const cs = getComputedStyle(first_grid);
    grid_info = {
      display: cs.display,
      gridTemplateColumns: cs.gridTemplateColumns,
      inline_tpl: first_grid.style.getPropertyValue('--stx-grid-template'),
      track_count: cs.gridTemplateColumns.split(' ').length,
    };
  }
  let first_styled_block = null;
  const blocks = document.querySelectorAll('.stx-block');
  for (let i = 0; i < blocks.length && i < 10; i++) {
    const b = blocks[i];
    const cs = getComputedStyle(b);
    const bg = cs.backgroundColor;
    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
      first_styled_block = {
        backgroundColor: bg,
        borderTopWidth: cs.borderTopWidth,
        borderTopColor: cs.borderTopColor,
      };
      break;
    }
  }
  return {
    observer_installed: window.__stxMarkerObs === true,
    classes: {
      block: counts('.stx-block'),
      grid: counts('.stx-grid'),
      zoom: counts('.stx-zoom'),
    },
    uid_set: {
      block: counts('[data-stx-block-uid]'),
      grid: counts('[data-stx-grid-uid]'),
    },
    first_grid: grid_info,
    first_styled_block: first_styled_block,
  };
}
"""


@pytest.fixture(scope="module")
def streamlit_server():
    """Launch `streamlit run book.py` on a free port; tear down at session end."""
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "book.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=str(FIXTURE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_http(url)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_observer_survives_settings_change(streamlit_server: str) -> None:
    """After moving the Width % number input, every marker must still have
    its class / uid / inline grid display intact, and the first styled
    block must still have its colored background."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = ctx.new_page()
        page.set_default_timeout(30_000)

        page.goto(streamlit_server, wait_until="networkidle")
        page.wait_for_selector('[data-testid="stSidebar"]', state="visible")
        page.wait_for_function("window.__stxMarkerObs === true", timeout=15_000)

        # Let the observer + any post-mount reflow settle.
        page.wait_for_timeout(2000)

        state_before = page.evaluate(_READOUT_JS)
        if state_before["classes"]["block"] == 0:
            # Capture artefacts for debugging (committed to .gitignore'd dir).
            artefact_dir = Path(__file__).parent / "_artefacts"
            artefact_dir.mkdir(exist_ok=True)
            page.screenshot(path=str(artefact_dir / "before_failure.png"), full_page=True)
            (artefact_dir / "before_failure_state.json").write_text(
                __import__("json").dumps(state_before, indent=2)
            )
            html_snippet = page.evaluate(
                "() => document.body.innerHTML.length + ' bytes; main='"
                " + (document.querySelector('[data-testid=\"stMain\"]')?.textContent?.slice(0,200) || '<none>')"
            )
            raise AssertionError(
                f"no .stx-block in DOM before rerun\n"
                f"state: {state_before}\n"
                f"page body excerpt: {html_snippet}\n"
                f"artefacts saved to {artefact_dir}"
            )
        assert state_before["observer_installed"], "observer never installed"
        assert state_before["classes"]["block"] >= 1, "no .stx-block in DOM before rerun"
        assert state_before["classes"]["grid"] >= 1, "no .stx-grid in DOM before rerun"
        assert state_before["first_grid"] is not None
        assert state_before["first_grid"]["display"] == "grid"
        assert state_before["first_styled_block"] is not None
        assert state_before["first_styled_block"]["backgroundColor"] not in (
            "rgba(0, 0, 0, 0)", "transparent",
        )

        # Open the Settings expander.  The streamtex panel uses <details>.
        settings = page.locator(
            '[data-testid="stSidebar"] details:has(summary:has-text("Settings"))'
        )
        if settings.count() > 0 and not settings.first.evaluate("el => el.open"):
            settings.first.locator("summary").click()
            page.wait_for_timeout(400)

        # Find the Width % number input and click its minus button 3 times.
        number_inputs = page.locator(
            '[data-testid="stSidebar"] [data-testid="stNumberInput"]'
        )
        assert number_inputs.count() > 0, "no number inputs in sidebar — fixture broken?"
        minus_btn = number_inputs.first.locator("button").first
        for _ in range(3):
            minus_btn.click()
            page.wait_for_timeout(800)

        # Wait for the final rerun + observer's rAF-scheduled scan.
        page.wait_for_timeout(2500)

        state_after = page.evaluate(_READOUT_JS)
        browser.close()

    # Counts must be preserved (the bug stripped them silently).
    assert state_after["observer_installed"], "observer was destroyed by rerun"
    for kind in ("block", "grid", "zoom"):
        assert state_after["classes"][kind] == state_before["classes"][kind], (
            f"{kind} class count regressed: "
            f"{state_before['classes'][kind]} → {state_after['classes'][kind]}"
        )
    for kind in ("block", "grid"):
        assert state_after["uid_set"][kind] == state_before["uid_set"][kind], (
            f"data-stx-{kind}-uid attribute count regressed: "
            f"{state_before['uid_set'][kind]} → {state_after['uid_set'][kind]}"
        )

    # First .stx-grid still has grid display + same number of tracks.
    fg_b, fg_a = state_before["first_grid"], state_after["first_grid"]
    assert fg_a is not None, "first .stx-grid disappeared after rerun"
    assert fg_a["display"] == "grid", (
        f"first .stx-grid lost grid display: {fg_a['display']!r}"
    )
    assert fg_a["track_count"] == fg_b["track_count"], (
        f"grid track count changed: {fg_b['track_count']} → {fg_a['track_count']}"
    )

    # First styled block kept its background (the failure mode was
    # transparent / inherited background because per-instance CSS no
    # longer matched).
    sb_b, sb_a = state_before["first_styled_block"], state_after["first_styled_block"]
    assert sb_a is not None, "no styled block found after rerun (background stripped?)"
    assert sb_a["backgroundColor"] == sb_b["backgroundColor"], (
        f"first styled block lost its background: "
        f"{sb_b['backgroundColor']} → {sb_a['backgroundColor']}"
    )


def test_observer_recovers_from_attribute_strip(streamlit_server: str) -> None:
    """Direct unit-level test of the observer's attribute-watching path.

    The 0.6.21-0.6.23 bug was specifically that Streamlit's reconciliation
    could strip our class / uid / inline style from a parent stVerticalBlock
    WITHOUT touching its children — invisible to a childList-only observer.

    This test simulates that exact strip programmatically (so we don't rely
    on Streamlit happening to do it in a given flow) and asserts the
    observer restores the affected state within one animation frame.  It
    FAILS against any observer that only watches childList.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = ctx.new_page()
        page.set_default_timeout(30_000)

        page.goto(streamlit_server, wait_until="networkidle")
        page.wait_for_selector('[data-testid="stSidebar"]', state="visible")
        page.wait_for_function("window.__stxMarkerObs === true", timeout=15_000)
        page.wait_for_timeout(2000)

        # Capture the initial applied state.
        before = page.evaluate(_READOUT_JS)
        assert before["classes"]["grid"] >= 1
        assert before["classes"]["block"] >= 1
        assert before["uid_set"]["block"] >= 1

        # Strip + measure-immediately in a single evaluate, so we capture
        # the post-strip state BEFORE the observer's rAF-debounced re-apply
        # has a chance to fire.  (Two separate evaluates leave enough event-
        # loop slack for the observer to be done by the time we read.)
        stripped = page.evaluate(
            """
            () => {
              document.querySelectorAll('.stx-grid').forEach(el => el.classList.remove('stx-grid'));
              document.querySelectorAll('[data-stx-block-uid]').forEach(el => el.removeAttribute('data-stx-block-uid'));
              document.querySelectorAll('.stx-block').forEach(el => el.classList.remove('stx-block'));
              return {
                grid: document.querySelectorAll('.stx-grid').length,
                block: document.querySelectorAll('.stx-block').length,
                block_uid: document.querySelectorAll('[data-stx-block-uid]').length,
              };
            }
            """
        )
        # Sanity: the synchronous strip+read must show a wiped state.  If
        # the observer somehow re-applied in the same tick, this assertion
        # surfaces it.
        assert stripped["grid"] == 0, f"strip didn't take effect: {stripped}"
        assert stripped["block"] == 0, f"strip didn't take effect: {stripped}"
        assert stripped["block_uid"] == 0, f"strip didn't take effect: {stripped}"

        # The observer's mutation handler is debounced via rAF — give it
        # several frames to fire and re-apply.
        page.wait_for_timeout(500)

        recovered = page.evaluate(_READOUT_JS)
        browser.close()

    assert recovered["classes"]["grid"] == before["classes"]["grid"], (
        f"observer failed to re-add .stx-grid: "
        f"post-strip={stripped['grid']} → recovered={recovered['classes']['grid']} "
        f"(expected {before['classes']['grid']}) — attribute-watching path broken"
    )
    assert recovered["classes"]["block"] == before["classes"]["block"], (
        f"observer failed to re-add .stx-block: "
        f"post-strip={stripped['block']} → recovered={recovered['classes']['block']} "
        f"(expected {before['classes']['block']}) — attribute-watching path broken"
    )
    assert recovered["uid_set"]["block"] == before["uid_set"]["block"], (
        f"observer failed to re-add data-stx-block-uid: "
        f"post-strip={stripped['block_uid']} → recovered={recovered['uid_set']['block']} "
        f"(expected {before['uid_set']['block']}) — attribute-watching path broken"
    )
