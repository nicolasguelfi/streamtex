"""E2E regression — cache-build freeze on Chromium.

Reproduces the freeze reported on the FC-260507-NG-SLIDES deck (Chrome
stalls at ~73 % of the loading overlay, while Firefox/Safari load
cleanly).  The fixture under ``fixtures/cache_build_freeze_app/`` has 40
synthetic styled slides matching that deck's shape (paginate=True,
marker nav, TOC, search).

What the test does
------------------
1. Boots ``streamlit run book.py`` on a free port.
2. Drives Chromium via Playwright with a fresh user-data-dir each run
   so we always exercise the Tier 3 ``_build_page_cache`` rebuild path.
3. Instruments the page on ``init`` (before the streamtex observer
   installs):

     * Hooks ``MutationObserver`` so every fire bumps
       ``window.__stxObsFireCount`` and we can correlate observer
       activity with the freeze window.
     * Hooks ``requestAnimationFrame`` so we count debounced scans.
     * Patches ``document.querySelectorAll`` so we count ``.stx-marker``
       lookups (a proxy for ``scan(hostDoc)`` calls).
     * Installs a ``PerformanceObserver`` for long tasks
       (``entryTypes: ['longtask']``).

4. Waits for ``#stx-loading-overlay`` to appear, then to disappear,
   timing the interval.  This window IS the cache-build duration that
   was reported as a freeze.

5. Reads the instrumented counters and asserts thresholds.  On the
   current 0.6.25 code we expect this to **fail** (cold load >> 1.5 s,
   thousands of marker querySelectorAll, etc.) — that failure is the
   reproduction.  After the fix, the same thresholds should pass.

The thresholds are deliberately generous; on the FC project Chrome
freezes for many seconds.  We pin a soft ceiling on cold-load duration
plus several proxy counters; CI runners vary, so keep the absolute
numbers loose and rely on the ratios in the failure message to
characterize the regression precisely.

Run with:
    uv run pytest -m e2e tests/e2e/test_cache_build_freeze.py -v -s

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
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "cache_build_freeze_app"

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


# JavaScript installed BEFORE the streamtex observer runs.  Hooks the
# globals the observer relies on so we can count its activity from
# Python.  All counters live on ``window`` so they survive reruns.
_INSTRUMENT_JS = r"""
() => {
  if (window.__cbfreezeInstrumented) return;
  window.__cbfreezeInstrumented = true;

  window.__stxObsFireCount = 0;
  window.__stxObsMutationCount = 0;
  window.__stxRafCount = 0;
  window.__stxMarkerScanCount = 0;
  window.__stxLongTaskCount = 0;
  window.__stxLongTaskTotalMs = 0;
  window.__stxLongTaskMaxMs = 0;
  window.__stxIframeCreatedCount = 0;

  // Hook MutationObserver: every fire bumps counters before delegating.
  const _MO = window.MutationObserver;
  window.MutationObserver = function (cb) {
    const wrapped = function (muts, obs) {
      window.__stxObsFireCount++;
      window.__stxObsMutationCount += muts.length;
      return cb(muts, obs);
    };
    return new _MO(wrapped);
  };
  window.MutationObserver.prototype = _MO.prototype;

  // Hook requestAnimationFrame: counts scheduled scans.
  const _raf = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = function (cb) {
    window.__stxRafCount++;
    return _raf(cb);
  };

  // Hook document.querySelectorAll('span.stx-marker'): counts scan() calls.
  const _qsa = Document.prototype.querySelectorAll;
  Document.prototype.querySelectorAll = function (sel) {
    if (typeof sel === 'string' && sel.indexOf('span.stx-marker') !== -1) {
      window.__stxMarkerScanCount++;
    }
    return _qsa.call(this, sel);
  };

  // Hook iframe creation: a per-block ``st.iframe(...)`` shows up here.
  const _create = Document.prototype.createElement;
  Document.prototype.createElement = function (tag) {
    if (typeof tag === 'string' && tag.toLowerCase() === 'iframe') {
      window.__stxIframeCreatedCount++;
    }
    return _create.apply(this, arguments);
  };

  // PerformanceObserver for long tasks.
  try {
    const po = new PerformanceObserver(list => {
      for (const e of list.getEntries()) {
        window.__stxLongTaskCount++;
        window.__stxLongTaskTotalMs += e.duration;
        if (e.duration > window.__stxLongTaskMaxMs) {
          window.__stxLongTaskMaxMs = e.duration;
        }
      }
    });
    po.observe({ entryTypes: ['longtask'] });
  } catch (_) { /* longtask not supported in headless */ }
}
"""


# Snapshot the counters at the end of cache build.
_READOUT_JS = r"""
() => ({
  obs_fires:         window.__stxObsFireCount || 0,
  obs_mutations:     window.__stxObsMutationCount || 0,
  raf_calls:         window.__stxRafCount || 0,
  marker_scans:      window.__stxMarkerScanCount || 0,
  iframes_created:   window.__stxIframeCreatedCount || 0,
  long_task_count:   window.__stxLongTaskCount || 0,
  long_task_total_ms: window.__stxLongTaskTotalMs || 0,
  long_task_max_ms:  window.__stxLongTaskMaxMs || 0,
  dom_size:          document.querySelectorAll('*').length,
  stx_blocks:        document.querySelectorAll('.stx-block').length,
  stx_grids:         document.querySelectorAll('.stx-grid').length,
  stx_zooms:         document.querySelectorAll('.stx-zoom').length,
  stx_lists:         document.querySelectorAll('.stx-list').length,
  marker_observer_installed: window.__stxMarkerObs === true,
})
"""


@pytest.fixture(scope="module")
def streamlit_server():
    """Launch ``streamlit run book.py`` on a free port; tear down at end."""
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


def _clear_disk_cache() -> None:
    """Tier 2 cache lives next to ``book.py``.  Clear before every run so
    we always exercise the Tier 3 ``_build_page_cache`` path that triggers
    the freeze."""
    cache = FIXTURE_DIR / ".stx_cache"
    if cache.exists():
        for f in cache.iterdir():
            f.unlink()
        cache.rmdir()


def _measure_cold_load(streamlit_url: str) -> dict:
    """Drive Chromium through a cold load, return measured counters."""
    from playwright.sync_api import sync_playwright

    _clear_disk_cache()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        # init script runs BEFORE any page script — must precede the
        # marker observer's installation.
        ctx.add_init_script(script=f"({_INSTRUMENT_JS})();")
        page = ctx.new_page()
        page.set_default_timeout(60_000)

        t_goto = time.monotonic()
        page.goto(streamlit_url, wait_until="domcontentloaded")

        # Wait for the loading overlay to appear (signals cache build start).
        page.wait_for_function(
            "() => !!document.getElementById('stx-loading-overlay')",
            timeout=30_000,
        )
        t_overlay_visible = time.monotonic()

        # Wait for the overlay to be removed (signals cache build end).
        # Budget = 45 s — generous enough that a properly-fixed build
        # always finishes here; the test asserts cache_build_window_s
        # against a tighter ceiling below.  We want the wall-clock to
        # show the natural completion time rather than be clipped by
        # this timeout.
        # Budget = 30 s — plenty for a properly cached build of 60 blocks
        # (typical wall-clock under 2 s on developer hardware) and short
        # enough that any regression of the freeze surfaces fast.
        try:
            page.wait_for_function(
                "() => !document.getElementById('stx-loading-overlay')",
                timeout=30_000,
            )
            overlay_removed = True
        except Exception:
            overlay_removed = False
        t_overlay_gone = time.monotonic()

        readout = page.evaluate(_READOUT_JS)

        # Capture a screenshot for artefacts on extreme failures.
        try:
            art_dir = Path(__file__).parent / "_artefacts"
            art_dir.mkdir(exist_ok=True)
            page.screenshot(path=str(art_dir / "cache_build_end.png"),
                            full_page=False)
        except Exception:
            pass

        browser.close()

    return {
        "goto_to_overlay_s":        t_overlay_visible - t_goto,
        "cache_build_window_s":     t_overlay_gone - t_overlay_visible,
        "total_cold_load_s":        t_overlay_gone - t_goto,
        "overlay_removed":          overlay_removed,
        **readout,
    }


# ---------------------------------------------------------------------------
# The test itself
# ---------------------------------------------------------------------------

# Threshold for the cache-build window (overlay visible → overlay removed).
# On the 60-block fixture, an unfreezed cold load completes in roughly
# 1-2 s on developer hardware; on a slower CI runner allow ~5×.  Any
# regression of the marker_runtime feedback loop or of the
# ``_suppress_cache_build_dom`` guard would push this far past 8 s.
COLD_LOAD_BUDGET_S = 8.0

# Scan-call ceiling.  ``scan(hostDoc)`` walks every marker in the DOM,
# so excessive counts indicate the observer is performing a full scan
# on every Streamlit mutation rather than the surgical per-record
# handling installed in 0.6.26.  The bootstrap pass legitimately runs
# one scan; anything north of a few dozen means the regression is back.
MARKER_SCAN_BUDGET = 100


def test_cache_build_does_not_freeze_chromium(streamlit_server: str) -> None:
    metrics = _measure_cold_load(streamlit_server)

    # Pretty-print for the test log (-s) regardless of pass/fail.
    print("\n=== cache-build freeze metrics ===")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k:>26s} : {v:9.3f}")
        else:
            print(f"  {k:>26s} : {v}")

    assert metrics["overlay_removed"], (
        "loading overlay never disappeared — cache build did not complete "
        "within 60 s (hard freeze).  metrics=" + repr(metrics)
    )
    assert metrics["marker_observer_installed"], (
        "marker observer never installed — fixture is misconfigured "
        "or marker_runtime regressed.  metrics=" + repr(metrics)
    )

    # Soft thresholds — characterize the freeze without flapping CI.
    assert metrics["cache_build_window_s"] < COLD_LOAD_BUDGET_S, (
        f"cache build window {metrics['cache_build_window_s']:.2f}s exceeds "
        f"budget {COLD_LOAD_BUDGET_S}s.  full metrics=" + repr(metrics)
    )
    assert metrics["marker_scans"] < MARKER_SCAN_BUDGET, (
        f"observer ran {metrics['marker_scans']} scan() passes during cache "
        f"build (budget {MARKER_SCAN_BUDGET}). Each scan walks every marker "
        f"on the page — high counts indicate the rAF-debounced scan is "
        f"firing on every Streamlit attribute reconciliation, not just on "
        f"structural mutations.  full metrics=" + repr(metrics)
    )
