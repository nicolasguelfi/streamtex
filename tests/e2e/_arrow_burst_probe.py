"""Fine-grained probe for the floating-arrow / arrow-key regression
reported by the user:

  "les fleches clavier ou boutons de la barre flottantes cassent la
   surbrillance et le petit trait, c'est même pire car si je fais
   deux clic il ne reapparait même pas"

Reproduces both inputs at high temporal resolution (samples every
50 ms) so we can pinpoint exactly when the highlight goes missing
and whether it returns.

Two scenarios:
  S1: TWO floating-arrow clicks, 200 ms apart — was the user's bug
  S2: TWO ArrowRight keypresses, 200 ms apart — independent input path
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
  if (!sidebar) return {n_active: -1};
  var actives = Array.from(sidebar.querySelectorAll(
    '[data-stx-block].stx-nav-active'));
  var slide_match = document.body.innerText.match(/Bloc\s+(\d+)\s*\/\s*(\d+)/);
  return {
    n_active: actives.length,
    href: actives.length ? (actives[0].querySelector('a[href^="#"]') || {}).getAttribute &&
          actives[0].querySelector('a[href^="#"]').getAttribute('href') : null,
    slide: slide_match ? slide_match[0] : null,
  };
})()
"""


def sample_fine(page, total_ms: int, label: str):
    """Sample state every 50 ms for total_ms; report only state CHANGES."""
    start = time.time()
    last_state = None
    samples = []
    while (time.time() - start) * 1000 < total_ms:
        d = page.evaluate(PROBE)
        state = (d['slide'], d['n_active'], d['href'])
        if state != last_state:
            elapsed = int((time.time() - start) * 1000)
            samples.append((elapsed, d['slide'], d['n_active'], d['href']))
            last_state = state
        page.wait_for_timeout(50)
    print(f"  [{label}] state changes over {total_ms} ms:")
    for ms, slide, n, h in samples:
        marker = "✗" if n == 0 else ("✓" if n == 1 else "!!")
        print(f"    +{ms:4d}ms  {marker}  slide={slide!r}  "
              f"n_active={n}  href={h}")
    # Return the FINAL settled state
    return samples[-1] if samples else None


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
    failures = []
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
            try:
                page.click(".stMainBlockContainer", position={"x": 200, "y": 200})
            except Exception:
                pass
            page.wait_for_timeout(300)

            print("=" * 60)
            print("S1: TWO floating-arrow clicks (200 ms apart)")
            print("=" * 60)
            # Snapshot baseline
            d = page.evaluate(PROBE)
            print(f"  baseline: slide={d['slide']!r} n_active={d['n_active']} "
                  f"href={d['href']}")
            # Click via JS to avoid element-detach across the rerun
            def click_arrow_js():
                return page.evaluate(r"""
                () => {
                  var btns = document.querySelectorAll(
                    "button, [role='button']");
                  for (var i = 0; i < btns.length; i++) {
                    var t = (btns[i].innerText || '').trim();
                    if (t === '▶') { btns[i].click(); return true; }
                  }
                  return false;
                }
                """)
            ok1 = click_arrow_js()
            print(f"  click #1 dispatched: {ok1}")
            page.wait_for_timeout(200)
            ok2 = click_arrow_js()
            print(f"  click #2 dispatched: {ok2}")
            final = sample_fine(page, 4000, "post-double-click")
            if not final or final[2] != 1:
                failures.append(
                    f"S1: highlight did NOT recover. Final state: {final}"
                )

            print()
            print("=" * 60)
            print("S2: TWO ArrowRight keypresses (200 ms apart)")
            print("=" * 60)
            try:
                page.click(".stMainBlockContainer", position={"x": 200, "y": 200})
            except Exception:
                pass
            page.wait_for_timeout(300)
            d = page.evaluate(PROBE)
            print(f"  baseline: slide={d['slide']!r} n_active={d['n_active']}")
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(200)
            page.keyboard.press("ArrowRight")
            final = sample_fine(page, 4000, "post-double-ArrowRight")
            if not final or final[2] != 1:
                failures.append(
                    f"S2: highlight did NOT recover. Final state: {final}"
                )

            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    print()
    print("=" * 60)
    if failures:
        print(f"RESULT: {len(failures)} FAILURE(S)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("RESULT: highlight recovered to single-active in both scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
