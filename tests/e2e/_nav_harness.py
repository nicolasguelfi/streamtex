"""Shared real-browser harness for navigation active-state e2e tests.

Phase 0 of ``navigation-refactor-plan-v01.md``.  The reverted
0.6.36→0.6.40 series proved that headless probes do NOT reproduce the
frozen-highlight / counter-desync bugs (their Streamlit-rerun timing
diverges from a real browser).  This harness drives Chromium against a
paginated, search-enabled deck and asserts on DOM/CSS state — the five
invariants in ``§2.3`` of the plan.

Deck selection:
  * default — the in-repo fixture ``fixtures/nav_active_app`` (CI-safe,
    self-contained).
  * ``STX_NAV_E2E_DECK=/abs/path/to/deck`` — point the harness at an
    external deck (e.g. the draft bench ``FC-260507-NG-SLIDES``) for
    richer manual verification during development.

Headed runs (the real gate) — set ``STX_E2E_HEADED=1``; otherwise the
launch is headless for a fast smoke pass.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.request
from contextlib import closing, contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DECK = Path(__file__).resolve().parent / "fixtures" / "nav_active_app"


def resolve_deck() -> Path:
    """In-repo fixture by default; ``STX_NAV_E2E_DECK`` to override."""
    override = os.environ.get("STX_NAV_E2E_DECK")
    if override:
        p = Path(override).expanduser().resolve()
        if not (p / "book.py").is_file():
            raise FileNotFoundError(f"STX_NAV_E2E_DECK has no book.py: {p}")
        return p
    return DEFAULT_DECK


def free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_http(url: str, timeout_s: float = 90.0) -> None:
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


@contextmanager
def streamlit_deck(deck: Path | None = None):
    """Launch ``streamlit run book.py`` for *deck* on a free port.

    Forces ``STX_USE_MARKER_RUNTIME=1`` so the scroll-spy / marker
    observer bundle actually installs (it is env-gated and otherwise a
    no-op — see ``book.py: inject_marker_runtime``).
    """
    deck = deck or resolve_deck()
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    env = dict(os.environ)
    env["STX_USE_MARKER_RUNTIME"] = "1"
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "book.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=str(deck),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_http(url)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def launch_browser(p):
    """Headed when ``STX_E2E_HEADED=1`` (the real gate); headless smoke otherwise."""
    headed = os.environ.get("STX_E2E_HEADED") == "1"
    slow_mo = int(os.environ.get("STX_E2E_SLOWMO", "0"))
    return p.chromium.launch(headless=not headed, slow_mo=slow_mo)


# --------------------------------------------------------------------------
# DOM readout — the single source of truth the assertions read.
# --------------------------------------------------------------------------
# For each sidebar link we record:
#   block            — the data-stx-block value of its entry (page index)
#   text             — trimmed link text
#   inlineActive     — entry rendered with inline color:var(--stx-link-active-color)
#                      (the SERVER group-highlight cue — multiple lit = bug 6.13)
#   navActiveClass   — entry carries .stx-nav-active (the SCROLL-SPY cue)
#   visible          — entry is in the currently-shown tab (offsetParent != null)
#   href             — anchor target (#stx-goto-N for cross-page, #anchor same-page)
NAV_READOUT_JS = r"""
() => {
  const sb = document.querySelector('[data-testid="stSidebar"]');
  const entries = [];
  if (sb) {
    sb.querySelectorAll('a[href^="#"]').forEach(a => {
      const entry = a.closest('[data-stx-block]');
      const styleAttr = (a.getAttribute('style') || '');
      entries.push({
        block: entry ? entry.getAttribute('data-stx-block') : null,
        text: (a.textContent || '').trim().slice(0, 80),
        inlineActive: styleAttr.indexOf('stx-link-active-color') !== -1,
        navActiveClass: entry ? entry.classList.contains('stx-nav-active') : false,
        visible: a.offsetParent !== null,
        href: a.getAttribute('href'),
      });
    });
  }
  const visible = entries.filter(e => e.visible);
  // Floating widget counter: textContent "  N / total".
  const nav = document.getElementById('streamtex-marker-nav');
  let counterIdx = null, counterTotal = null, markerLabel = null;
  if (nav) {
    const m = (nav.textContent || '').match(/(\d+)\s*\/\s*(\d+)/);
    if (m) { counterIdx = parseInt(m[1], 10); counterTotal = parseInt(m[2], 10); }
    const lbl = nav.querySelector('.stx-marker-label');
    markerLabel = lbl ? (lbl.textContent || '').trim() : null;
  }
  return {
    observer: window.__stxMarkerObs === true,
    scrollspy: window.__stxScrollSpy === true,
    currentPage: (typeof window._stxPrevPage === 'number') ? window._stxPrevPage : null,
    entries: entries,
    n_entries: entries.length,
    n_visible: visible.length,
    inlineActiveVisible: visible.filter(e => e.inlineActive),
    navActiveVisible: visible.filter(e => e.navActiveClass),
    counterIdx: counterIdx,            // 1-based index shown to the user
    counterTotal: counterTotal,
    markerLabel: markerLabel,
  };
}
"""


def read_state(page) -> dict:
    return page.evaluate(NAV_READOUT_JS)


def dispatch_key(page, key: str, settle_ms: int = 1600) -> None:
    """Fire a keydown on the host document and wait for the rerun to settle."""
    page.evaluate(
        "(key) => document.dispatchEvent(new KeyboardEvent("
        "'keydown', {key: key, bubbles: true, cancelable: true}))",
        key,
    )
    page.wait_for_timeout(settle_ms)


def double_key(page, key: str, gap_ms: int = 60, settle_ms: int = 2200) -> None:
    """Fire the SAME key twice within one rerun window (the S3 bug trigger)."""
    js = ("(key) => document.dispatchEvent(new KeyboardEvent("
          "'keydown', {key: key, bubbles: true, cancelable: true}))")
    page.evaluate(js, key)
    page.wait_for_timeout(gap_ms)
    page.evaluate(js, key)
    page.wait_for_timeout(settle_ms)


def select_tab(page, label: str) -> None:
    """Click a sidebar tab ('Markers' or 'Contents') and let it paint."""
    page.evaluate(
        """(label) => {
          const sb = document.querySelector('[data-testid="stSidebar"]');
          if (!sb) return false;
          const tabs = [...sb.querySelectorAll('button[role="tab"]')];
          const t = tabs.find(b => (b.textContent || '').trim() === label);
          if (t) { t.click(); return true; }
          return false;
        }""",
        label,
    )
    page.wait_for_timeout(400)


def wait_ready(page, url: str) -> None:
    """Navigate + wait for the marker runtime and loading overlay to clear."""
    page.goto(url, wait_until="networkidle")
    page.wait_for_selector('[data-testid="stSidebar"]', state="visible")
    page.wait_for_function("window.__stxMarkerObs === true", timeout=30_000)
    page.wait_for_function(
        "() => !document.getElementById('stx-loading-overlay')",
        timeout=60_000,
    )
    page.wait_for_timeout(1500)


# --------------------------------------------------------------------------
# Invariant assertions (plan §2.3).  Each returns (ok: bool, detail: str)
# so callers can use them under xfail without raising.
# --------------------------------------------------------------------------
def check_single_active(state: dict, cue: str = "inline") -> tuple[bool, str]:
    """I1 — exactly one VISIBLE entry carries the active cue.

    cue='inline' → the server group-highlight color (today's baseline cue).
    cue='class'  → the scroll-spy .stx-nav-active class (post-cutover cue).
    """
    lit = state["inlineActiveVisible"] if cue == "inline" else state["navActiveVisible"]
    n = len(lit)
    texts = [e["text"] for e in lit]
    return n == 1, f"{cue} active count={n} (expected 1); lit={texts}"


def check_active_matches_page(state: dict, cue: str = "inline") -> tuple[bool, str]:
    """I2 — the single active entry maps to the rendered current page."""
    lit = state["inlineActiveVisible"] if cue == "inline" else state["navActiveVisible"]
    cp = state["currentPage"]
    if len(lit) != 1:
        return False, f"not single-active ({len(lit)}), cannot match page"
    blk = lit[0]["block"]
    return str(blk) == str(cp), f"active entry block={blk}, currentPage={cp}"


def check_counter_parity(state: dict) -> tuple[bool, str]:
    """I3 — widget counter (1-based) matches the rendered current page.

    Single-marker pages: counter index == currentPage + 1.
    """
    ci, cp = state["counterIdx"], state["currentPage"]
    if ci is None or cp is None:
        return False, f"counter={ci}, currentPage={cp} (one is None)"
    return ci == cp + 1, f"counterIdx={ci}, currentPage+1={cp + 1}"
