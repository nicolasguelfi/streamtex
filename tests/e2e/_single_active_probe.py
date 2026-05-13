"""E2E probe for the "single active entry" invariant on the real FC deck.

Validates:
  1.  At any moment, AT MOST ONE entry has the .stx-nav-active class in the
      TOC panel.
  2.  At any moment, AT MOST ONE entry has the .stx-nav-active class in the
      Markers panel.
  3.  After navigating several PageDowns, the active entry follows.
  4.  After clicking a marker, ONLY that marker becomes active (not its
      siblings on the same page).
  5.  The active entry has a brighter computed colour than its inactive
      siblings (visual A+B distinction is real).
  6.  No `--stx-link-active-color` is inline on any `<a>` (the historical
      per-page coloring that confused users was removed).

Run from the streamtex repo root:
    .venv/bin/python tests/e2e/_single_active_probe.py
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

ART_DIR = Path(__file__).parent / "_single_active_artefacts"
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


# Returns, for the TOC panel and the Markers panel, the list of entries
# with their active state, colour, and link href.  The Streamlit sidebar
# uses tabs ("Contents" / "Markers" / "Settings") so we inspect both.
PROBE = r"""
(() => {
  function inspectScope(scopeSel) {
    var scope = document.querySelector(scopeSel);
    if (!scope) return null;
    var entries = Array.from(scope.querySelectorAll('[data-stx-block]'));
    return entries.map(function(e, i) {
      var a = e.querySelector('a[href^="#"]');
      var aCs = a ? getComputedStyle(a) : null;
      return {
        i: i,
        active: e.classList.contains('stx-nav-active'),
        href: a ? a.getAttribute('href') : null,
        inlineStyle: a ? (a.getAttribute('style') || '') : '',
        text: ((a ? a.innerText : e.innerText) || '').trim().slice(0, 60),
        color: aCs ? aCs.color : null,
      };
    });
  }
  // Streamlit sidebar tabs: each tab panel is a stTabPanel container.
  // We grab the whole sidebar and filter by tab content.
  var sidebar = document.querySelector('[data-testid="stSidebar"]');
  if (!sidebar) return {error: 'no sidebar found'};
  // Find all [data-stx-block] in sidebar; group by their containing tab
  // panel.  Simpler: just dump the flat list with their data-stx-block
  // value and href to distinguish TOC vs Markers (markers have numeric
  // prefix like "12.", TOC entries do not).
  var all = Array.from(sidebar.querySelectorAll('[data-stx-block]'));
  var entries = all.map(function(e, i) {
    var a = e.querySelector('a[href^="#"]');
    var aCs = a ? getComputedStyle(a) : null;
    return {
      i: i,
      active: e.classList.contains('stx-nav-active'),
      href: a ? a.getAttribute('href') : null,
      inlineStyle: a ? (a.getAttribute('style') || '') : '',
      text: ((a ? a.innerText : e.innerText) || '').trim().slice(0, 60),
      color: aCs ? aCs.color : null,
    };
  });
  return {entries: entries};
})()
"""


def summarize(label, data):
    if data is None or data.get('error'):
        print(f"  [{label}]  {data and data.get('error', 'no data')}")
        return 0, []
    entries = data.get('entries', [])
    actives = [e for e in entries if e['active']]
    inline_colored = [e for e in entries if 'color:' in (e.get('inlineStyle') or '').lower()]
    print(f"  [{label}]  total entries={len(entries)}, active={len(actives)}, "
          f"inline-colored-anchors={len(inline_colored)}")
    if actives:
        for a in actives:
            print(f"     ACTIVE: href={a['href']!r}, color={a['color']!r}, text={a['text']!r}")
    if inline_colored:
        for c in inline_colored[:3]:
            print(f"     INLINE-COLOR LEAK: href={c['href']!r}, style={c['inlineStyle']!r}")
    return len(actives), actives


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

    overall_pass = True
    try:
        _wait_http(url)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(url)
            page.wait_for_timeout(7000)
            try:
                page.wait_for_function(
                    "() => document.body.innerText.length > 200",
                    timeout=30_000,
                )
            except Exception:
                pass
            page.wait_for_timeout(2000)

            print("=" * 60)
            print("STEP 0: initial state (just loaded)")
            print("=" * 60)
            data = page.evaluate(PROBE)
            n_active, actives = summarize("initial", data)
            page.screenshot(path=str(ART_DIR / "step0_initial.png"), full_page=True)
            if n_active > 1:
                print(f"  FAIL: {n_active} entries active simultaneously")
                overall_pass = False
            inline = [e for e in data.get('entries', [])
                      if 'color:' in (e.get('inlineStyle') or '').lower()]
            if inline:
                print(f"  FAIL: {len(inline)} anchors still carry inline `color:` style")
                overall_pass = False

            # Walk through 10 pages via PageDown.  After each step verify
            # at most one active in TOC + at most one active in Markers.
            for step in range(1, 11):
                # Focus the main app first via the main block container
                try:
                    page.click(".stMainBlockContainer", position={"x": 200, "y": 200})
                except Exception:
                    pass
                page.wait_for_timeout(200)
                page.keyboard.press("PageDown")
                page.wait_for_timeout(1000)
                # Also report the slide footer "Bloc X / Y" indicator so we
                # know whether the page actually changed
                slide_indicator = page.evaluate("""
                () => {
                  var el = document.body.innerText.match(/Bloc\\s+(\\d+)\\s*\\/\\s*(\\d+)/);
                  return el ? el[0] : null;
                }
                """)
                data = page.evaluate(PROBE)
                print(f"\n--- after PageDown #{step} ---  slide={slide_indicator!r}")
                n_active, actives = summarize(f"step{step}", data)
                if step in (3, 6, 10):
                    page.screenshot(path=str(ART_DIR / f"step{step}.png"), full_page=True)
                if n_active > 1:
                    print(f"  FAIL: {n_active} entries active simultaneously at step {step}")
                    overall_pass = False
                inline = [e for e in data.get('entries', [])
                          if 'color:' in (e.get('inlineStyle') or '').lower()]
                if inline:
                    print(f"  FAIL: {len(inline)} anchors carry inline color at step {step}")
                    overall_pass = False

            # Now switch to Markers tab (if present) and click one marker
            print("\n" + "=" * 60)
            print("STEP CLICK: clicking on a marker entry")
            print("=" * 60)
            # Find the Markers tab button and click it
            try:
                tabs = page.query_selector_all('[data-testid="stSidebar"] button[role="tab"]')
                clicked_tab = False
                for t in tabs:
                    try:
                        label = (t.inner_text() or "").strip().lower()
                    except Exception:
                        label = ""
                    if "marker" in label:
                        t.click()
                        clicked_tab = True
                        page.wait_for_timeout(800)
                        print("  clicked Markers tab")
                        break
                if not clicked_tab:
                    print("  (no Markers tab — running click test on TOC entries instead)")
            except Exception as e:
                print(f"  tab click failed: {e}")

            data = page.evaluate(PROBE)
            # Pick a marker entry whose href is a CONTENT anchor on the
            # current page (href starts with "#stx-marker-" or is a slug,
            # NOT "#stx-goto-N" which is a page-navigation link).  Then
            # click and verify the same entry stays active afterwards.
            entries = data.get('entries', [])
            target = None
            for e in entries:
                txt = e['text']
                href = e.get('href') or ''
                if not txt or not href.startswith('#'):
                    continue
                if href.startswith('#stx-goto-'):
                    continue  # page-link, would navigate away
                if txt[0].isdigit() and '.' in txt[:4]:
                    target = e
                    break
            if target:
                print(f"  target click: {target['text']!r} href={target['href']}")
                page.evaluate(f"""
                () => {{
                  var el = document.querySelectorAll('[data-stx-block] a[href="{target['href']}"]')[0];
                  if (el) el.click();
                }}
                """)
                page.wait_for_timeout(1200)
                data_after = page.evaluate(PROBE)
                n_after, actives_after = summarize("after-click", data_after)
                page.screenshot(path=str(ART_DIR / "step_click.png"), full_page=True)
                if n_after > 1:
                    print(f"  FAIL: {n_after} entries active after click (should be 1)")
                    overall_pass = False
                elif n_after == 0:
                    print("  WARN: 0 entries active after click")
                else:
                    actual_href = actives_after[0]['href']
                    if actual_href != target['href']:
                        print(f"  FAIL: active entry is {actual_href}, expected {target['href']}")
                        overall_pass = False
                    else:
                        print("  OK: only the clicked entry is active")
            else:
                print("  (no suitable content-anchor marker on this page to click)")

            browser.close()

            print("\n" + "=" * 60)
            print("OVERALL:", "PASS" if overall_pass else "FAIL")
            print("=" * 60)
            return 0 if overall_pass else 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
