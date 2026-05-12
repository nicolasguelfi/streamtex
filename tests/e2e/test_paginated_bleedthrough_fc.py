"""E2E test pointed at the FC-260507-NG-SLIDES deck — captures the
bleed-through visible in the user-reported screenshots in situ.

This complements the synthetic ``test_paginated_bleedthrough.py``: that
fixture doesn't reproduce the regression because the FC deck has
characteristics (40+ slides, ``st_image`` widgets with async-loaded
content, multiple nested zooms/grids per slide, custom tooltip widget)
that interact with the marker observer differently from a 3-slide
synthetic deck.

The FC project lives at a fixed path in the developer's workspace
(``slides/FC-260507-NG-SLIDES`` under the laptop's Dropbox tree).  The
test is auto-skipped when that path isn't present, so it doesn't trip
on CI runners or other dev machines.

Run with:
    uv run pytest -m e2e tests/e2e/test_paginated_bleedthrough_fc.py -v -s
"""
from __future__ import annotations

import os
import socket
import subprocess
import time
import urllib.request
from contextlib import closing
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

# Path is intentionally fixed — only the laptop running the FC deck has
# the project at this location.  CI / other devs skip cleanly.
FC_PROJECT = Path(
    "/Volumes/Mac_Data/Win_data/data/backups/"
    "Dropbox-nicolas.guelfi@laposte.net/messir Dropbox/Nicolas Guelfi/"
    "users/NG/dev-dropbox/dvlpt/eclipse/git/lu.uni.sage.publications.2025/"
    "ng.aiday.policy/ul-it-policy/slides/FC-260507-NG-SLIDES"
)
FC_BOOK = FC_PROJECT / "book.py"
FC_VENV_PY = FC_PROJECT / ".venv" / "bin" / "python"

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not (FC_BOOK.exists() and FC_VENV_PY.exists()),
        reason="FC-260507-NG-SLIDES project not present on this machine",
    ),
]


def _free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_http(url: str, timeout_s: float = 90.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 — connection refused is normal
            last_err = exc
        time.sleep(0.5)
    raise TimeoutError(f"streamlit never became ready on {url}: {last_err}")


@pytest.fixture(scope="module")
def fc_server():
    """Launch ``streamlit run book.py`` from the FC project's own venv."""
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    # Force the cache to a clean state so we always exercise the
    # Tier-3 ``_build_page_cache`` rebuild path the user reported on.
    cache_dir = FC_PROJECT / ".stx_cache"
    if cache_dir.exists():
        for f in cache_dir.iterdir():
            try:
                f.unlink()
            except OSError:
                pass
    # Don't auto-generate AI images — the test isn't about images.
    env = os.environ.copy()
    env.setdefault("STX_DISABLE_AI_AUTOGEN", "1")
    proc = subprocess.Popen(
        [
            str(FC_VENV_PY), "-m", "streamlit", "run", "book.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=str(FC_PROJECT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    try:
        _wait_for_http(url)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


# Read the inline styles on every visible .stx-grid and .stx-zoom.  We
# also pull the slide marker label from the streamtex marker navigation
# widget (which tracks the current slide for the user).
_READ_VISIBLE_JS = r"""
() => {
  function readInline(sel) {
    return Array.from(document.querySelectorAll(sel)).map(el => ({
      grid_template_columns: el.style.getPropertyValue('grid-template-columns'),
      zoom: el.style.getPropertyValue('zoom'),
      gap: el.style.getPropertyValue('gap'),
    }));
  }
  // The current marker label appears in #streamtex-marker-nav span.label.
  const label = document.querySelector('#streamtex-marker-nav .marker-label, #streamtex-marker-nav .label, #streamtex-marker-nav') || null;
  return {
    grids: readInline('.stx-grid'),
    zooms: readInline('.stx-zoom'),
    n_blocks: document.querySelectorAll('.stx-block').length,
    observer: window.__stxMarkerObs === true,
    marker_label: label ? (label.textContent || '').trim().slice(0, 200) : null,
  };
}
"""


def _dispatch_key(page, key: str) -> None:
    page.evaluate(
        "(key) => document.dispatchEvent(new KeyboardEvent("
        "'keydown', {key: key, bubbles: true, cancelable: true}))",
        key,
    )
    # Streamlit's paginated rerun on the FC deck takes 1–2 s end-to-end.
    page.wait_for_timeout(1500)


def test_fc_paginated_round_trip_keeps_inline_styles_stable(fc_server: str) -> None:
    """Navigate forward 10 slides, then backward to slide 0, recording the
    inline grid-template-columns and zoom values on each step.  When the
    user returns to slide N the visible inline styles MUST match the
    values seen the first time slide N was rendered — any difference is
    the bleed-through.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = ctx.new_page()
        page.set_default_timeout(60_000)

        page.goto(fc_server, wait_until="networkidle")
        page.wait_for_function("window.__stxMarkerObs === true", timeout=30_000)
        page.wait_for_function(
            "() => !document.getElementById('stx-loading-overlay')",
            timeout=60_000,
        )
        page.wait_for_timeout(1500)

        # Forward sweep — collect "first-visit" snapshots.
        N = 10
        first_visit: list[dict] = []
        for i in range(N):
            if i > 0:
                _dispatch_key(page, "PageDown")
            snap = page.evaluate(_READ_VISIBLE_JS)
            first_visit.append(snap)
            print(f"\nFORWARD slide #{i}: grids="
                  f"{[g['grid_template_columns'] for g in snap['grids']]}, "
                  f"zooms={[z['zoom'] for z in snap['zooms']]}, "
                  f"label={snap['marker_label']!r}")

        # Backward sweep — compare each "second-visit" snapshot against
        # the first-visit one for the same slide.
        bleeds: list[dict] = []
        for i in range(N - 2, -1, -1):
            _dispatch_key(page, "PageUp")
            snap = page.evaluate(_READ_VISIBLE_JS)
            first = first_visit[i]
            cols_first = [g["grid_template_columns"] for g in first["grids"]]
            cols_now = [g["grid_template_columns"] for g in snap["grids"]]
            zooms_first = [z["zoom"] for z in first["zooms"]]
            zooms_now = [z["zoom"] for z in snap["zooms"]]
            print(f"\nBACKWARD slide #{i}: first={cols_first} {zooms_first}; "
                  f"now={cols_now} {zooms_now}")
            if cols_first != cols_now or zooms_first != zooms_now:
                bleeds.append({
                    "slide": i,
                    "first_cols": cols_first, "now_cols": cols_now,
                    "first_zooms": zooms_first, "now_zooms": zooms_now,
                })

        browser.close()

    assert not bleeds, (
        f"Paginated bleed-through detected on {len(bleeds)} slide(s) "
        f"returning via PageUp:\n" + "\n".join(repr(b) for b in bleeds)
    )
