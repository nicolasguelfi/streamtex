"""E2E test for the "first list-item invisible on first render" bug.

User-observed symptom (FC-260507-NG-SLIDES, slide "Operational, Not
Theoretical — The Luxembourg Framework"):
  * After ``rm -rf .stx_cache`` and a fresh ``streamlit run``, the first
    bullet of that slide's list shows the bullet character but the text
    content is missing.  The other items render correctly.
  * A browser force-reload makes the missing text appear.

Root cause: Streamlit's first-paint reconciliation transiently places
the list-item marker span inside the stElementContainer that ultimately
hosts the user content.  ``hideMarkerCell`` correctly sees the canonical
``EC > stHtml > span.stx-marker`` structure at that moment and stamps
``display: none !important`` on the EC.  Streamlit then replaces the
EC's content with the user's ``st_write`` output, but the inline hide
persists — and Streamlit also strips the ``stx-marker-cell`` class as
part of its reconciliation, leaving the EC invisible to any
class-based recovery scan.  See the fix in
``streamtex/static/js/stx_marker_observer.js`` (``auditMarkerCells``).

This test wipes ``.stx_cache`` before launching streamlit and verifies
every ``.stx-list-item`` on the affected slide reports non-empty text.

Run with:
    uv run pytest -m e2e tests/e2e/test_first_item_invisible_fc.py -v -s
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

FC_PROJECT = Path(
    "/Volumes/Mac_Data/Win_data/data/backups/"
    "Dropbox-nicolas.guelfi@laposte.net/messir Dropbox/Nicolas Guelfi/"
    "users/NG/dev-dropbox/dvlpt/eclipse/git/lu.uni.sage.publications.2025/"
    "ng.aiday.policy/ul-it-policy/slides/FC-260507-NG-SLIDES"
)
FC_BOOK = FC_PROJECT / "book.py"
FC_VENV_PY = FC_PROJECT / ".venv" / "bin" / "python"

TARGET_SLIDE_TITLE_FRAGMENT = "operational, not theoretical"  # matched lower-cased
MAX_NAV_STEPS = 60  # the deck has ~45 slides; safety margin

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
    """Launch ``streamlit run book.py`` from the FC project's own venv.

    .stx_cache is wiped at every test-module invocation so we always hit
    the Tier-3 cache rebuild path — the same condition under which the
    user reported the first-item-invisible bug.
    """
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    cache_dir = FC_PROJECT / ".stx_cache"
    if cache_dir.exists():
        for f in cache_dir.iterdir():
            try:
                f.unlink()
            except OSError:
                pass
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


# JS that reports, for every visible .stx-list-item:
#   * uid, classList (so we can see if a single stVerticalBlock has BOTH
#     .stx-list-item and .stx-block — i.e. multiple markers collapsed
#     onto the same parent),
#   * computed display of the .stx-list-item itself,
#   * innerText AND textContent (innerText respects display:none; textContent
#     ignores it — divergence tells us "the content is here, just hidden"),
#   * for each direct stElementContainer child: display, what kind of
#     marker (if any) it carries, whether it transitively contains an
#     stMarkdown, AND a longer html slice so we can see nested structure,
#   * a list of every span.stx-marker found ANYWHERE inside this item
#     so we can tell whether multiple markers landed on the same parent.
# Also returns the current marker label so we know which slide we're on.
_READ_LIST_ITEMS_JS = r"""
() => {
  function snapshotCell(ec) {
    const ecDisplay = getComputedStyle(ec).display;
    const ownMarker = ec.querySelector(':scope > .stHtml > span.stx-marker, :scope > [data-testid="stHtml"] > span.stx-marker');
    const hasMarker = !!ec.querySelector(':scope span.stx-marker');
    const hasStyle = !!ec.querySelector(':scope style');
    const stMarkdown = !!ec.querySelector(':scope .stMarkdown, :scope [data-testid="stMarkdown"]');
    const html = (ec.innerHTML || '');
    const cellInner = (ec.innerText || '').replace(/\s+/g, ' ').trim();
    const cellTextContent = (ec.textContent || '').replace(/\s+/g, ' ').trim();
    return {
      display: ecDisplay,
      is_marker_cell: hasMarker,
      own_marker_kind: ownMarker ? ownMarker.getAttribute('data-stx-kind') : null,
      own_marker_uid: ownMarker ? ownMarker.getAttribute('data-stx-uid') : null,
      has_style_tag: hasStyle,
      has_st_markdown: stMarkdown,
      text_len: cellInner.length,
      textcontent_len: cellTextContent.length,
      html_preview: html.slice(0, 400),
      html_total_len: html.length,
    };
  }
  function snapshotItem(li) {
    const uid = li.getAttribute('data-stx-list-item-uid');
    const display = getComputedStyle(li).display;
    const cls = Array.from(li.classList || []);
    const text = (li.innerText || '').replace(/\s+/g, ' ').trim();
    const textContent = (li.textContent || '').replace(/\s+/g, ' ').trim();
    const ecChildren = Array.from(li.children)
      .filter(c => c.matches('[data-testid="stElementContainer"], .element-container'));
    const cells = ecChildren.map(snapshotCell);
    // All markers anywhere inside this item — kind + uid.
    const allMarkers = Array.from(li.querySelectorAll(':scope span.stx-marker'))
      .map(m => ({ kind: m.getAttribute('data-stx-kind'),
                   uid:  m.getAttribute('data-stx-uid') }));
    // stMarkdown elements anywhere inside.
    const allMarkdowns = Array.from(li.querySelectorAll(':scope [data-testid="stMarkdown"], :scope .stMarkdown'))
      .map(md => ({
        display: getComputedStyle(md).display,
        text: (md.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 80),
        textcontent: (md.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80),
      }));
    // ALL element-containers anywhere inside — their display, classes, and
    // a brief content marker so we can see exactly which ECs got hidden.
    const allECs = Array.from(li.querySelectorAll(':scope [data-testid="stElementContainer"], :scope .element-container'))
      .map(ec => {
        const owns = ec.querySelector(':scope > [data-testid="stHtml"] > span.stx-marker, :scope > .stHtml > span.stx-marker');
        const desc = ec.querySelector(':scope span.stx-marker');
        const tc = (ec.textContent || '').replace(/\s+/g, ' ').trim();
        return {
          display: getComputedStyle(ec).display,
          inline_display: ec.style.display || '',
          inline_style_full: ec.getAttribute('style') || '',
          parent_classes: ec.parentElement ? Array.from(ec.parentElement.classList || []) : [],
          parent_testid: ec.parentElement ? (ec.parentElement.getAttribute('data-testid') || '') : '',
          classes: Array.from(ec.classList || []),
          is_own_marker_cell: !!owns,
          desc_marker_kind: desc ? desc.getAttribute('data-stx-kind') : null,
          desc_marker_uid: desc ? desc.getAttribute('data-stx-uid') : null,
          textcontent_preview: tc.slice(0, 80),
        };
      });
    // Inner stVerticalBlocks anywhere inside.
    const innerVBs = Array.from(li.querySelectorAll(':scope [data-testid="stVerticalBlock"]'))
      .map(vb => ({
        display: getComputedStyle(vb).display,
        cls: Array.from(vb.classList || []),
      }));
    return {
      uid: uid, display: display, classes: cls,
      text: text, textcontent: textContent,
      cells: cells, n_direct_ec: ecChildren.length,
      all_markers: allMarkers,
      all_markdowns: allMarkdowns,
      all_ecs: allECs,
      inner_vbs: innerVBs,
    };
  }
  const items = Array.from(document.querySelectorAll('.stx-list-item'))
    .map(snapshotItem);
  const labelNode = document.querySelector('#streamtex-marker-nav .marker-label, #streamtex-marker-nav .label, #streamtex-marker-nav');
  // Hunt for "Supervisory authority" anywhere in the document to locate
  // where the first item's content actually ended up.
  function describePath(el) {
    const path = [];
    let cur = el;
    let depth = 0;
    while (cur && depth < 14) {
      const allCls = (cur.classList && cur.classList.length)
        ? Array.from(cur.classList).join(',')
        : '';
      const tid = cur.getAttribute ? (cur.getAttribute('data-testid') || '') : '';
      const display = cur.nodeType === 1 ? getComputedStyle(cur).display : '';
      const inlineDisplay = (cur.style && cur.style.display) || '';
      const isStxMarkerCell = cur.classList && cur.classList.contains('stx-marker-cell');
      path.push({
        tag: cur.tagName || cur.nodeName,
        classes: allCls,
        testid: tid,
        display: display,
        inlineDisplay: inlineDisplay,
        isStxMarkerCell: isStxMarkerCell,
      });
      cur = cur.parentNode;
      depth++;
    }
    return path;
  }
  const allTextNodes = [];
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = tw.nextNode())) {
    if (n.nodeValue && n.nodeValue.includes('Supervisory authority')) {
      allTextNodes.push({
        text: n.nodeValue.slice(0, 120),
        parent_path: describePath(n.parentElement),
      });
    }
  }
  return {
    marker_label: labelNode ? (labelNode.textContent || '').trim().slice(0, 200) : null,
    list_items: items,
    n_blocks: document.querySelectorAll('.stx-block').length,
    observer: window.__stxMarkerObs === true,
    supervisory_text_hits: allTextNodes,
  };
}
"""


def _dispatch_key(page, key: str) -> None:
    page.evaluate(
        "(key) => document.dispatchEvent(new KeyboardEvent("
        "'keydown', {key: key, bubbles: true, cancelable: true}))",
        key,
    )
    page.wait_for_timeout(1500)


def test_fc_first_list_item_text_present_on_first_render(fc_server: str) -> None:
    """Navigate to the "Operational, Not Theoretical" slide on the very
    first render (post .stx_cache wipe).  Every ``.stx-list-item`` on
    that slide MUST report a non-empty text content.

    Pre-fix, the first item's text is empty (the visible bullet is the
    CSS ::before; the actual ``stMarkdown`` is either missing or its
    element-container is ``display:none``).  The dumped per-cell
    diagnostics tell us which hypothesis applies — H2 (text in marker
    cell), H3 (wrong ancestor hidden), or H4 (markdown loading state).
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
            timeout=120_000,
        )
        # Allow the first frame to fully reconcile.
        page.wait_for_timeout(1500)

        # Walk forward until the target slide title appears in the marker label.
        target_snap = None
        snaps_seen: list[dict] = []
        for step in range(MAX_NAV_STEPS):
            snap = page.evaluate(_READ_LIST_ITEMS_JS)
            snaps_seen.append({
                "step": step,
                "label": snap["marker_label"],
                "n_items": len(snap["list_items"]),
            })
            label = (snap.get("marker_label") or "").lower()
            if TARGET_SLIDE_TITLE_FRAGMENT in label:
                target_snap = snap
                break
            if step < MAX_NAV_STEPS - 1:
                _dispatch_key(page, "PageDown")

        browser.close()

    assert target_snap is not None, (
        f"Target slide containing {TARGET_SLIDE_TITLE_FRAGMENT!r} not "
        f"reached in {MAX_NAV_STEPS} PageDown steps.  Visited slides:\n"
        + "\n".join(repr(s) for s in snaps_seen[-15:])
    )

    items = target_snap["list_items"]
    print(f"\nReached slide: {target_snap['marker_label']!r}")
    print(f"Found {len(items)} .stx-list-item element(s)")
    print(f"\n'Supervisory authority' text hits in document: "
          f"{len(target_snap['supervisory_text_hits'])}")
    for hit in target_snap["supervisory_text_hits"]:
        print(f"  text={hit['text']!r}")
        print("  parent_path (up to 14 levels):")
        for level, p in enumerate(hit["parent_path"]):
            print(
                f"    [{level}] <{p['tag']}> testid={p['testid']!r} "
                f"display={p['display']!r} inline_display={p['inlineDisplay']!r} "
                f"is_stx_marker_cell={p['isStxMarkerCell']}\n"
                f"          classes={p['classes']!r}"
            )
    print()
    for i, it in enumerate(items):
        print(
            f"  item #{i}: uid={it['uid']!r} display={it['display']!r} "
            f"classes={it['classes']!r}\n"
            f"           innerText_len={len(it['text'])} text={it['text'][:80]!r}\n"
            f"           n_direct_ec={it['n_direct_ec']} "
            f"all_markers={it['all_markers']!r}\n"
            f"           inner_vbs={it['inner_vbs']!r}"
        )
        for ei, ec in enumerate(it.get("all_ecs", [])):
            print(
                f"    EC[{ei}]: display={ec['display']!r} "
                f"inline_display={ec['inline_display']!r} "
                f"own_marker={ec['is_own_marker_cell']}\n"
                f"           parent_testid={ec['parent_testid']!r} "
                f"parent_classes={ec['parent_classes']!r}\n"
                f"           classes={ec['classes']!r}\n"
                f"           inline_style_full={ec['inline_style_full']!r}\n"
                f"           tc_preview={ec['textcontent_preview']!r}"
            )

    assert items, "no .stx-list-item found on target slide"
    empty = [(i, it) for i, it in enumerate(items) if not it["text"]]
    assert not empty, (
        f"First-item-invisible bug reproduced: {len(empty)} list-item(s) "
        f"have empty text on first render.\n"
        + "\n".join(
            f"  item #{i}: uid={it['uid']!r} cells="
            f"{[(c['display'], c['is_marker_cell'], c['text_len']) for c in it['cells']]}"
            for i, it in empty
        )
    )
