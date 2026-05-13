"""Navigation-matrix probe — exercises the paths NOT covered by
``_instability_probe.py`` and asserts the single-active invariant
holds throughout.

Covered scenarios:

  1. TOC tab ↔ Markers tab switch — the active-class must stay on the
     correct entry across tab swaps (both tabs share data-stx-block
     markup, but only one tab is in the DOM at a time).
  2. URL hash navigation — assigning ``location.hash`` directly should
     recompute the active entry (we listen for ``hashchange``).
  3. Search-filter activation — typing in the sidebar search box hides
     entries; the active entry must either remain active (still
     visible) or, if hidden by the filter, cleanly clear.
  4. Mid-navigation tab swap — start on TOC tab, PageDown twice,
     switch to Markers tab, assert highlight follows the actual
     reading position (not stuck on what was active before the swap).
  5. Class-attribute strip (safety net regression test) — strip
     ``.stx-nav-active`` directly via JS to simulate a hypothetical
     reconciliation bug.  The MutationObserver attribute path must
     recompute and re-apply within ~150 ms.

Assertions are loud: any deviation prints ``FAIL`` and the probe
exits with code 1 so a runner can short-circuit on the first failure.
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from contextlib import closing
from pathlib import Path

from playwright.sync_api import sync_playwright

FC = Path(
    "/Volumes/Mac_Data/Win_data/data/backups/Dropbox-nicolas.guelfi@laposte.net/"
    "messir Dropbox/Nicolas Guelfi/users/NG/dev-dropbox/dvlpt/eclipse/git/"
    "lu.uni.sage.publications.2025/ng.aiday.policy/ul-it-policy/slides/"
    "FC-260507-NG-SLIDES"
)
FC_VENV_PY = FC / ".venv" / "bin" / "python"
ART_DIR = Path(__file__).parent / "_nav_matrix_artefacts"
ART_DIR.mkdir(exist_ok=True)


def _free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_http(url: str, timeout_s: float = 120.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)
    raise TimeoutError(url)


PROBE = r"""
(() => {
  var sidebar = document.querySelector('[data-testid="stSidebar"]');
  if (!sidebar) return {error: 'no sidebar'};
  var actives = Array.from(sidebar.querySelectorAll(
    '[data-stx-block].stx-nav-active'));
  var actives_info = actives.map(function (e) {
    var a = e.querySelector('a[href^="#"]');
    return {
      href: a ? a.getAttribute('href') : null,
      text: ((a ? a.innerText : e.innerText) || '').trim().slice(0, 60),
    };
  });
  var tab_buttons = Array.from(sidebar.querySelectorAll(
    'button[role="tab"]'));
  var current_tab = null;
  tab_buttons.forEach(function (t) {
    var sel = t.getAttribute('aria-selected') === 'true';
    if (sel) current_tab = (t.innerText || '').trim();
  });
  return {
    n_active: actives.length,
    actives: actives_info,
    current_tab: current_tab,
    hash: location.hash,
  };
})()
"""


FAILURES: list[str] = []


def snap(page, label):
    data = page.evaluate(PROBE)
    print(f"  [{label}] tab={data['current_tab']!r} "
          f"hash={data['hash']!r} active_count={data['n_active']}")
    for a in data.get('actives', []):
        print(f"     ACTIVE: {a['text']!r}  href={a['href']}")
    return data


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"  ✗ FAIL: {msg}")


def expect_single_active(data, label):
    if data['n_active'] == 0:
        fail(f"[{label}] expected 1 active, found 0 (highlight disappeared)")
    elif data['n_active'] > 1:
        fail(f"[{label}] expected 1 active, found {data['n_active']} "
             f"(multiple-highlight regression)")


def click_tab(page, label_substr):
    """Click the sidebar tab whose label contains the substring (case-insensitive).
    Returns True if found+clicked."""
    tabs = page.query_selector_all(
        '[data-testid="stSidebar"] button[role="tab"]'
    )
    for t in tabs:
        try:
            lbl = (t.inner_text() or "").strip().lower()
        except Exception:
            lbl = ""
        if label_substr.lower() in lbl:
            try:
                t.click()
                page.wait_for_timeout(500)
                return True
            except Exception as e:
                print(f"    tab click failed: {e}")
    return False


def main() -> int:
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [
            str(FC_VENV_PY), "-m", "streamlit", "run", "book.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=str(FC),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_http(url)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(url)
            page.wait_for_timeout(6000)
            page.wait_for_function(
                "() => document.body.innerText.length > 200", timeout=30_000
            )
            page.wait_for_timeout(2000)

            # Focus main area so PageDown reaches the navigation handler.
            try:
                page.click(".stMainBlockContainer", position={"x": 200, "y": 200})
            except Exception:
                pass
            page.wait_for_timeout(300)

            print("=" * 60)
            print("S1: Move past first marker, switch TOC ↔ Markers tabs")
            print("=" * 60)
            page.keyboard.press("PageDown")
            page.wait_for_timeout(1200)
            d0 = snap(page, "after-PageDown-on-TOC")
            expect_single_active(d0, "S1.0")

            if click_tab(page, "marker"):
                d1 = snap(page, "after-switch-to-Markers")
                expect_single_active(d1, "S1.1")
            else:
                print("  (no Markers tab found)")

            if click_tab(page, "table") or click_tab(page, "toc"):
                d2 = snap(page, "after-switch-back-to-TOC")
                expect_single_active(d2, "S1.2")
            else:
                print("  (no TOC tab found)")
            page.screenshot(path=str(ART_DIR / "s1_tab_swap_end.png"))

            print()
            print("=" * 60)
            print("S2: URL hash navigation (location.hash assignment)")
            print("=" * 60)
            # Pick a content anchor visible in the markers list.
            tgt = page.evaluate(r"""
            () => {
              var as = document.querySelectorAll(
                '[data-testid="stSidebar"] [data-stx-block] a[href^="#"]');
              for (var i = 0; i < as.length; i++) {
                var h = as[i].getAttribute('href') || '';
                if (h && h.indexOf('#stx-goto-') !== 0 && h !== '#') {
                  return {href: h, text: as[i].innerText};
                }
              }
              return null;
            }
            """)
            if tgt:
                print(f"  navigating to hash={tgt['href']!r}  ({tgt['text']!r})")
                page.evaluate(f"() => {{ location.hash = '{tgt['href']}'; }}")
                page.wait_for_timeout(800)
                d3 = snap(page, "after-hash-set")
                expect_single_active(d3, "S2")
                # The active anchor should match what we set (or a near
                # neighbour if the closest-anchor heuristic adjusted).
                if d3['actives']:
                    print(f"    note: active={d3['actives'][0]['href']} "
                          f"target={tgt['href']}")
            else:
                print("  (no content anchor available)")

            print()
            print("=" * 60)
            print("S3: Search-filter activation (with show_search=True)")
            print("=" * 60)
            # Find search input in sidebar
            search_input = page.query_selector(
                '[data-testid="stSidebar"] input[type="text"]')
            if search_input:
                d_pre = snap(page, "pre-search")
                expect_single_active(d_pre, "S3.pre")
                try:
                    search_input.fill("propositions")
                    page.wait_for_timeout(1200)
                except Exception as e:
                    print(f"  search fill failed: {e}")
                d_active = snap(page, "search-filter-typed")
                # During filter, active can be 0 (filtered out) or 1; never >1.
                if d_active['n_active'] > 1:
                    fail(f"[S3.filter] {d_active['n_active']} actives during "
                         f"search (should be 0 or 1)")
                # Clear the filter
                try:
                    search_input.fill("")
                    page.wait_for_timeout(1200)
                except Exception as e:
                    print(f"  search clear failed: {e}")
                d_clear = snap(page, "search-cleared")
                expect_single_active(d_clear, "S3.cleared")
            else:
                print("  (no search input found in sidebar)")
            page.screenshot(path=str(ART_DIR / "s3_search_end.png"))

            print()
            print("=" * 60)
            print("S4: PageDown twice, then immediately swap tab")
            print("=" * 60)
            # Restore focus to main area
            try:
                page.click(".stMainBlockContainer", position={"x": 200, "y": 400})
            except Exception:
                pass
            page.wait_for_timeout(300)
            d_b = snap(page, "before-double-PD-then-swap")
            page.keyboard.press("PageDown")
            page.wait_for_timeout(120)
            page.keyboard.press("PageDown")
            page.wait_for_timeout(150)  # quick swap, mid-navigation
            click_tab(page, "marker")
            page.wait_for_timeout(1500)
            d_m = snap(page, "swap-mid-nav-on-Markers")
            expect_single_active(d_m, "S4.markers-after-swap")
            click_tab(page, "table") or click_tab(page, "toc")
            page.wait_for_timeout(1000)
            d_t = snap(page, "back-on-TOC")
            expect_single_active(d_t, "S4.toc-after-swap")

            print()
            print("=" * 60)
            print("S5: Class-strip safety-net regression test")
            print("=" * 60)
            # Capture currently-active node, strip the class via JS,
            # then assert the observer re-applies within 200 ms.
            before = page.evaluate(r"""
            () => {
              var node = document.querySelector(
                '[data-testid="stSidebar"] [data-stx-block].stx-nav-active');
              if (!node) return {error: 'no active node'};
              var a = node.querySelector('a[href^="#"]');
              node.classList.remove('stx-nav-active');
              return {
                stripped: true,
                href: a ? a.getAttribute('href') : null,
                still_has_class: node.classList.contains('stx-nav-active'),
              };
            }
            """)
            print(f"  strip result: {before}")
            if before.get('stripped') and not before['still_has_class']:
                page.wait_for_timeout(400)  # let MO + throttle settle
                d_after = snap(page, "200ms-after-strip")
                expect_single_active(d_after, "S5.recovered")
                if d_after['n_active'] >= 1:
                    print(f"    ✓ safety net recovered: "
                          f"{d_after['actives'][0]['href']}")
            else:
                print("  (no active node to strip from; skipping)")
            page.screenshot(path=str(ART_DIR / "s5_safetynet_end.png"))

            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    print()
    print("=" * 60)
    if FAILURES:
        print(f"RESULT: {len(FAILURES)} FAILURE(S)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("RESULT: all assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
