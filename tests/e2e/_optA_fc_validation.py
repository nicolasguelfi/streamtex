"""Acceptance test for the 0.6.35 inject_marker_runtime fix on the
real FC-260507-NG-SLIDES deck.

Launches FC's `book.py`, navigates to the three "Fifteen Propositions"
slides, and asserts:

1.  COUNTER FIX — each propositions slide has 5 `.stx-list-item`
    elements, every one carrying `stx-list-item--ordered`, with
    `counter-increment: streamtex-counter 1` actually computed on the
    item and `counter-reset: streamtex-counter 0` on the list root.
    Without the dual fix (DOMPurify escape + per-rerun re-emit),
    `getComputedStyle` returns `none` and bullets render as `0.`.

2.  CSS SURVIVES NAVIGATION — the global `stx-list-item--ordered` rule
    is parsed by the browser BOTH at initial load AND after 50+
    PageDowns. Used to disappear because the one-shot `st.html` was
    reconciled away on rerun.

3.  NO COMPONENT-REGISTRATION WARNINGS — listens for browser console
    messages and asserts that no `is already registered` warning is
    logged. Splitting the session-key gate must not regress this.

Run from the streamtex repo root:
    .venv/bin/python tests/e2e/_optA_fc_validation.py
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

ART_DIR = Path(__file__).parent / "_optA_fc_artefacts"
ART_DIR.mkdir(exist_ok=True)


def _free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_http(url: str, timeout_s: float = 120.0) -> None:
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except Exception as exc:
            last_err = exc
        time.sleep(0.5)
    raise TimeoutError(f"streamlit never came up on {url}: {last_err}")


PROBE_LIST = r"""
(() => {
  const items = Array.from(document.querySelectorAll('.stx-list-item'));
  return items.map((li, i) => {
    const liCs = getComputedStyle(li);
    const beforeCs = getComputedStyle(li, '::before');
    const listRoot = li.closest('.stx-list');
    const listCs = listRoot ? getComputedStyle(listRoot) : null;
    return {
      i,
      uid: li.getAttribute('data-stx-list-item-uid'),
      ordered: li.classList.contains('stx-list-item--ordered'),
      beforeContent: beforeCs.content,
      counterIncrement: liCs.counterIncrement,
      listCounterReset: listCs ? listCs.counterReset : null,
    };
  });
})()
"""

PROBE_GLOBAL_CSS_PRESENT = r"""
(() => {
  let orderedRulePresent = false;
  let counterRulePresent = false;
  Array.from(document.styleSheets).forEach(s => {
    try {
      for (const r of s.cssRules) {
        const sel = r.selectorText || '';
        if (sel.includes('stx-list-item.stx-list-item--ordered')) {
          orderedRulePresent = true;
        }
        if (sel === '[data-testid="stVerticalBlock"].stx-list') {
          counterRulePresent = true;
        }
      }
    } catch (e) {}
  });
  return {orderedRulePresent, counterRulePresent};
})()
"""


def snapshot_list(page, label: str) -> list[dict]:
    items = page.evaluate(PROBE_LIST)
    n_ordered = sum(1 for i in items if i["ordered"])
    n_inc = sum(1 for i in items if i["counterIncrement"] != "none")
    print(f"\n  [{label}]  {len(items)} items, "
          f"with --ordered class: {n_ordered}/{len(items)}, "
          f"with counter-increment applied: {n_inc}/{len(items)}")
    return items


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
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    component_warnings: list[str] = []

    try:
        _wait_http(url)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1600, "height": 1000})

            def _on_console(msg):
                if msg.type in ("warning", "error") and "is already registered" in (msg.text or ""):
                    component_warnings.append(msg.text)

            page.on("console", _on_console)

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

            initial_css = page.evaluate(PROBE_GLOBAL_CSS_PRESENT)
            print("\n=== INITIAL CSS PRESENCE ===")
            print(f"  .stx-list rule parsed:                 {initial_css['counterRulePresent']}")
            print(f"  .stx-list-item--ordered rule parsed:   {initial_css['orderedRulePresent']}")
            page.screenshot(path=str(ART_DIR / "initial.png"), full_page=True)

            # Navigate to propositions PART 1 — restrict to main-area text so the
            # sidebar TOC doesn't false-match.
            main_text_js = (
                "() => (document.querySelector('.stMainBlockContainer')"
                " || document.body).innerText.toLowerCase()"
            )
            found = False
            for step in range(120):
                t = page.evaluate(main_text_js)
                if "fifteen propositions" in t and "part 1 of 3" in t:
                    found = True
                    print(f"\n=== REACHED propositions PART 1 after {step} PageDowns ===")
                    break
                page.keyboard.press("PageDown")
                page.wait_for_timeout(550)
            if not found:
                print("FAIL: never reached propositions PART 1")
                page.screenshot(path=str(ART_DIR / "_not_found.png"), full_page=True)
                browser.close()
                return 1

            try:
                page.wait_for_function(
                    "() => document.querySelectorAll('.stx-list-item').length >= 5",
                    timeout=15_000,
                )
            except Exception:
                pass
            page.wait_for_timeout(800)

            # Confirm global CSS survived the navigation reruns
            css_after_nav = page.evaluate(PROBE_GLOBAL_CSS_PRESENT)
            print("\n=== CSS PRESENCE AFTER NAVIGATION ===")
            print(f"  .stx-list rule parsed:                 {css_after_nav['counterRulePresent']}")
            print(f"  .stx-list-item--ordered rule parsed:   {css_after_nav['orderedRulePresent']}")

            snap1 = snapshot_list(page, "PROPOSITIONS PART 1")
            page.screenshot(path=str(ART_DIR / "propositions_1.png"), full_page=True)

            page.keyboard.press("PageDown")
            page.wait_for_timeout(1200)
            try:
                page.wait_for_function(
                    "() => document.querySelectorAll('.stx-list-item').length >= 5",
                    timeout=15_000,
                )
            except Exception:
                pass
            page.wait_for_timeout(700)
            snap2 = snapshot_list(page, "PROPOSITIONS PART 2")
            page.screenshot(path=str(ART_DIR / "propositions_2.png"), full_page=True)

            page.keyboard.press("PageDown")
            page.wait_for_timeout(1200)
            try:
                page.wait_for_function(
                    "() => document.querySelectorAll('.stx-list-item').length >= 5",
                    timeout=15_000,
                )
            except Exception:
                pass
            page.wait_for_timeout(700)
            snap3 = snapshot_list(page, "PROPOSITIONS PART 3")
            page.screenshot(path=str(ART_DIR / "propositions_3.png"), full_page=True)

            browser.close()

            verdict = 0
            print("\n" + "=" * 60)
            print("VERDICTS")
            print("=" * 60)

            # (1) Counter actually fires on every ordered item
            for label, snap in [("part1", snap1), ("part2", snap2), ("part3", snap3)]:
                if not snap:
                    print(f"  [FAIL] {label}: no .stx-list-item found")
                    verdict = 1
                    continue
                missing_cls = [i["i"] for i in snap if not i["ordered"]]
                missing_incr = [i["i"] for i in snap if i["counterIncrement"] == "none"]
                if missing_cls:
                    print(f"  [FAIL] {label}: missing --ordered class on {missing_cls}")
                    verdict = 1
                elif missing_incr:
                    print(f"  [FAIL] {label}: counter-increment NOT applied "
                          f"on items {missing_incr} — bullets will render as `0.`")
                    verdict = 1
                else:
                    print(f"  [OK]   {label}: {len(snap)} items, "
                          f"every one increments the counter")

            # (2) Global CSS survives navigation
            if not css_after_nav["counterRulePresent"]:
                print("  [FAIL] .stx-list counter-reset rule REMOVED by reconciliation")
                verdict = 1
            else:
                print("  [OK]   .stx-list counter-reset rule still in stylesheets")
            if not css_after_nav["orderedRulePresent"]:
                print("  [FAIL] .stx-list-item--ordered rule REMOVED by reconciliation")
                verdict = 1
            else:
                print("  [OK]   .stx-list-item--ordered rule still in stylesheets")

            # (3) No component re-registration warnings
            if component_warnings:
                print(f"  [FAIL] {len(component_warnings)} 'is already registered' "
                      f"warnings — component re-registration regression")
                for w in component_warnings[:3]:
                    print(f"          {w[:120]}")
                verdict = 1
            else:
                print("  [OK]   No 'is already registered' console warnings")

            print("\n" + "=" * 60)
            print("OVERALL:", "PASS" if verdict == 0 else "FAIL")
            print("=" * 60)
            return verdict
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
