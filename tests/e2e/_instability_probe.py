"""Instability reproducer for the active-entry indication.

Tests three navigation modes the user reported as unstable:
  1.  Click on a marker in the Markers sidebar
  2.  Click the floating nav arrows (▶ / ◀ widget bottom-right)
  3.  Two consecutive PageDowns (rapid)

At every meaningful moment, reports the number of entries with
`.stx-nav-active` and the value of `window.__stxScrollSpy___debug`
helpers (if exposed) so we can pin-point when the highlight goes
missing.

NO MUTATION on the streamtex library.
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
ART_DIR = Path(__file__).parent / "_instability_artefacts"
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
  var actives = Array.from(sidebar.querySelectorAll('[data-stx-block].stx-nav-active'));
  var actives_info = actives.map(function(e) {
    var a = e.querySelector('a[href^="#"]');
    return {
      href: a ? a.getAttribute('href') : null,
      text: ((a ? a.innerText : e.innerText) || '').trim().slice(0, 60),
    };
  });
  var slide_match = document.body.innerText.match(/Bloc\s+(\d+)\s*\/\s*(\d+)/);
  return {
    n_active: actives.length,
    actives: actives_info,
    slide: slide_match ? slide_match[0] : null,
    hash: location.hash,
  };
})()
"""


def snap(page, label):
    data = page.evaluate(PROBE)
    print(f"  [{label}] slide={data['slide']!r} hash={data['hash']!r} "
          f"active_count={data['n_active']}")
    for a in data.get('actives', []):
        print(f"     ACTIVE: {a['text']!r}  href={a['href']}")
    return data


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

            print("=" * 60)
            print("SCENARIO 1: SINGLE PageDown — baseline reference")
            print("=" * 60)
            try:
                page.click(".stMainBlockContainer", position={"x": 200, "y": 200})
            except Exception:
                pass
            page.wait_for_timeout(200)
            snap(page, "before")
            page.keyboard.press("PageDown")
            for delay in (50, 150, 250, 400, 800, 1500, 2500):
                page.wait_for_timeout(delay - (page.evaluate("0") and 0))
                snap(page, f"  +{delay}ms")
            page.screenshot(path=str(ART_DIR / "s1_single_pagedown_end.png"))

            print()
            print("=" * 60)
            print("SCENARIO 2: TWO RAPID PageDowns (the user's reported bug)")
            print("=" * 60)
            snap(page, "before-double")
            page.keyboard.press("PageDown")
            page.wait_for_timeout(120)  # Quick second press
            page.keyboard.press("PageDown")
            # Sample over time
            for delay in (100, 300, 500, 800, 1500, 2500, 4000):
                page.wait_for_timeout(delay - (page.evaluate("0") and 0))
                snap(page, f"  +{delay}ms after #2")
            page.screenshot(path=str(ART_DIR / "s2_double_pagedown_end.png"),
                            full_page=True)

            print()
            print("=" * 60)
            print("SCENARIO 2b: 5 RAPID PageDowns (extreme stress)")
            print("=" * 60)
            snap(page, "before-burst")
            for _ in range(5):
                page.keyboard.press("PageDown")
                page.wait_for_timeout(80)
            for delay in (100, 300, 500, 1000, 2000):
                page.wait_for_timeout(delay - (page.evaluate("0") and 0))
                snap(page, f"  +{delay}ms after #5")

            print()
            print("=" * 60)
            print("SCENARIO 3: Floating nav arrow forward (▶)")
            print("=" * 60)
            snap(page, "before-arrow")
            # Find the next-arrow button
            clicked_arrow = False
            arrows = page.query_selector_all(
                "button, [role='button']"
            )
            for btn in arrows:
                try:
                    txt = (btn.inner_text() or "").strip()
                    title = btn.get_attribute("title") or ""
                except Exception:
                    txt = ""
                    title = ""
                if "▶" in txt or "Next" in title or "next" in title.lower():
                    try:
                        btn.click()
                        clicked_arrow = True
                        print(f"  clicked arrow: text={txt!r} title={title!r}")
                        break
                    except Exception as e:
                        print(f"  arrow click failed: {e}")
            if not clicked_arrow:
                print("  (could not locate floating arrow; skipping)")
            else:
                for delay in (100, 300, 500, 1000, 2000, 3000):
                    page.wait_for_timeout(delay - (page.evaluate("0") and 0))
                    snap(page, f"  +{delay}ms after arrow")
            page.screenshot(path=str(ART_DIR / "s3_arrow_end.png"))

            print()
            print("=" * 60)
            print("SCENARIO 4: Click on a Marker entry in sidebar")
            print("=" * 60)
            # First switch to Markers tab if it exists
            try:
                tabs = page.query_selector_all(
                    '[data-testid="stSidebar"] button[role="tab"]'
                )
                for t in tabs:
                    try:
                        lbl = (t.inner_text() or "").strip().lower()
                    except Exception:
                        lbl = ""
                    if "marker" in lbl:
                        t.click()
                        page.wait_for_timeout(700)
                        break
            except Exception:
                pass
            snap(page, "before-click")
            # Click a marker entry — pick one that links to another page
            target = page.evaluate(r"""
            () => {
              var as = document.querySelectorAll('[data-testid="stSidebar"] [data-stx-block] a[href^="#stx-goto-"]');
              if (as.length >= 2) {
                var a = as[1];
                return {href: a.getAttribute('href'), text: a.innerText};
              }
              return null;
            }
            """)
            if target:
                print(f"  clicking marker entry: {target['text']!r} href={target['href']}")
                page.evaluate(f"""
                () => {{
                  var a = document.querySelectorAll(
                    '[data-testid="stSidebar"] [data-stx-block] a[href="{target['href']}"]')[0];
                  if (a) a.click();
                }}
                """)
                for delay in (100, 300, 500, 1000, 2000, 3000):
                    page.wait_for_timeout(delay - (page.evaluate("0") and 0))
                    snap(page, f"  +{delay}ms after click")
                page.screenshot(path=str(ART_DIR / "s4_marker_click_end.png"))
            else:
                print("  (no marker entry found; skipping)")

            browser.close()
            return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
