"""Bisection probe for centering on slide 7.1 (regulation_landscape).

Pure observation, no mutation. Runs FC's book.py, paginates to the
"Regulation — Three Frameworks, One Principle" slide, and reports:

* Which `[data-stx-block-uid]` ancestors enclose the title element
* The computed `text-align` on every such ancestor
* The full ancestor chain (title → body) for context

Used to compare main vs fix branch: if main shows centering working
(title is inside a block-uid element with text-align:center), then my
fix caused the regression. If main shows the same broken state, the
regression pre-existed.
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
  const main = document.querySelector('.stMainBlockContainer') || document.body;
  const all = Array.from(main.querySelectorAll('*'));
  const matches = all.filter(el => {
    const txt = (el.innerText || '').toLowerCase().trim();
    return txt.includes('regulation — three frameworks, one principle');
  });
  // Want the DEEPEST element that contains JUST the title (no extra prefix/suffix)
  // — its innerText should equal the title plus possibly a trailing newline.
  const titleString = 'Regulation — Three Frameworks, One Principle';
  let titleEl = matches
    .filter(el => el.innerText.trim() === titleString)
    .sort((a, b) => {
      // Among exact matches, pick the one deepest in the tree
      let aDepth = 0, bDepth = 0, x;
      for (x = a; x; x = x.parentElement) aDepth++;
      for (x = b; x; x = x.parentElement) bDepth++;
      return bDepth - aDepth;
    })[0];
  if (!titleEl) {
    // fallback: smallest innerText match
    matches.sort((a, b) => a.innerText.length - b.innerText.length);
    titleEl = matches[0];
  }
  if (!titleEl) return {found: false};
  // For each block-uid'd element, report its DOM position relative to the title.
  const positionRelToTitle = [];
  Array.from(main.querySelectorAll('[data-stx-block-uid]')).forEach(b => {
    const uid = b.getAttribute('data-stx-block-uid');
    const rel = (
      b === titleEl ? 'is-title' :
      b.contains(titleEl) ? 'ancestor-of-title' :
      titleEl.contains(b) ? 'descendant-of-title' :
      'sibling-or-cousin'
    );
    positionRelToTitle.push({uid, rel});
  });
  const chain = [];
  let el = titleEl;
  while (el && el !== document.body) {
    const cs = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    chain.push({
      tag: el.tagName,
      testid: el.getAttribute('data-testid'),
      stxBlockUid: el.getAttribute('data-stx-block-uid'),
      stxClass: Array.from(el.classList || []).filter(c => c.startsWith('stx-')).join(' '),
      computedTextAlign: cs.textAlign,
      computedDisplay: cs.display,
      computedAlignSelf: cs.alignSelf,
      computedAlignItems: cs.alignItems,
      width: Math.round(rect.width),
      left: Math.round(rect.left),
      right: Math.round(rect.right),
    });
    el = el.parentElement;
  }
  const styledBlocks = Array.from(main.querySelectorAll('[data-stx-block-uid]')).map(b => ({
    uid: b.getAttribute('data-stx-block-uid'),
    computedTextAlign: getComputedStyle(b).textAlign,
    containsTitle: b.contains(titleEl),
  }));
  return {
    found: true,
    titleText: (titleEl.innerText || '').slice(0, 100),
    chain,
    styledBlocks,
    positionRelToTitle,
  };
})()
"""


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "current"
    out_dir = Path(__file__).parent / "_centering_artefacts"
    out_dir.mkdir(exist_ok=True)
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
            try:
                page.wait_for_function(
                    "() => document.body.innerText.length > 200",
                    timeout=30_000,
                )
            except Exception:
                pass
            page.wait_for_timeout(2000)
            main_text_js = (
                "() => (document.querySelector('.stMainBlockContainer')"
                " || document.body).innerText.toLowerCase()"
            )
            found = False
            for step in range(120):
                t = page.evaluate(main_text_js)
                if "regulation — three frameworks, one principle" in t:
                    print(f"Reached the slide after {step} PageDowns")
                    found = True
                    break
                page.keyboard.press("PageDown")
                page.wait_for_timeout(550)
            if not found:
                print("NEVER FOUND THE SLIDE")
                browser.close()
                return 2
            page.wait_for_timeout(1500)
            page.screenshot(path=str(out_dir / f"{label}_slide_sidebar_open.png"), full_page=True)
            # Now collapse the sidebar (user's regression environment) and re-screenshot.
            # Just hide it via CSS — the Streamlit collapse button is hard to
            # target reliably across versions, but the visual effect we care
            # about is the wider main area.
            page.evaluate(r"""
            (() => {
              const s = document.querySelector('[data-testid="stSidebar"]');
              if (s) { s.style.display = 'none'; }
            })()
            """)
            page.wait_for_timeout(1200)
            print("Sidebar hidden via CSS")
            data_patched = None
            page.screenshot(path=str(out_dir / f"{label}_slide_sidebar_closed.png"), full_page=True)
            # And do a fresh probe with sidebar closed
            data_closed = page.evaluate(PROBE)
            data = page.evaluate(PROBE)
            print(f"\n=== CENTERING PROBE — label={label!r} ===")
            if not data["found"]:
                print("FAIL: title element not located in DOM")
                browser.close()
                return 1
            print(f"Title text: {data['titleText']!r}")
            print()
            print("Ancestor chain (title → body):")
            for i, lvl in enumerate(data["chain"][:12]):
                print(f"  [{i:2d}] {lvl['tag']:10s} testid={lvl['testid']!r:>22s}  "
                      f"uid={lvl.get('stxBlockUid')!r:>12s}  "
                      f"stx={lvl['stxClass']!r:18s}  "
                      f"text-align={lvl['computedTextAlign']!r}")
            print()
            print("All [data-stx-block-uid] elements in main + position relative to title:")
            for b, rel in zip(data.get("styledBlocks", []), data.get("positionRelToTitle", [])):
                print(f"  uid={b['uid']:>12s}  text-align={b['computedTextAlign']!r:10s}  position={rel['rel']}")
            print()
            print("=== SAME PROBE, SIDEBAR COLLAPSED ===")
            if data_closed and data_closed.get("found"):
                print("Ancestor chain (title → body), sidebar closed:")
                for i, lvl in enumerate(data_closed["chain"][:12]):
                    print(f"  [{i:2d}] {lvl['tag']:10s} uid={lvl.get('stxBlockUid')!r:>12s} "
                          f"text-align={lvl['computedTextAlign']!r:8s} "
                          f"display={lvl.get('computedDisplay'):8s} "
                          f"align-self={lvl.get('computedAlignSelf'):>10s} "
                          f"width={lvl.get('width')!r:>6s}  left={lvl.get('left')!r:>5s}")
                print()
                print("All [data-stx-block-uid] elements, sidebar closed:")
                for b in data_closed.get("styledBlocks", []):
                    marker = " *contains title* " if b["containsTitle"] else ""
                    print(f"  uid={b['uid']:>12s}  text-align={b['computedTextAlign']!r}{marker}")
                if 'data_patched' in dir() or True:
                    try:
                        print("\n=== AFTER PATCHING width:auto → width:100% ===")
                        for i, lvl in enumerate(data_patched["chain"][:8]):
                            print(f"  [{i:2d}] {lvl['tag']:10s} uid={lvl.get('stxBlockUid')!r:>12s} "
                                  f"width={lvl.get('width')!r:>6s}  left={lvl.get('left')!r:>5s}")
                    except Exception as e:
                        print(f"(patched probe failed: {e})")
            else:
                print("(sidebar-closed probe didn't find the title)")
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
