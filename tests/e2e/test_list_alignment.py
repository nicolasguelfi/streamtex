"""Real-browser regression net for list alignment (0.7.33).

Three defects this guards against, all of which passed the HTML-string unit
tests of 0.7.32 unnoticed:

* ``st_list(align="center")`` was INERT: list.py put
  ``data-stx-list-width="fit-content"`` on the sentinel span, the observer
  forwarded it as the custom property ``--stx-list-width``, but the global
  stylesheet selected on the ATTRIBUTE ``[data-stx-list-width=…]``, which
  the parent never carries.  The rule never matched.
* There was no equivalent of ``list-style-position: inside``: the live list
  is a flex row whose text cell has ``flex-grow: 1``, i.e. permanently
  "outside", so centring text left the bullet behind at the far left.
* A hard-coded inline ``text-align: left`` on every list root blocked
  inheritance, so a centred container could not centre its lists.

The measurements below are geometric, not string-based, on a two-column
grid whose cells all share one width.

Run:
    uv run pytest -m e2e tests/e2e/test_list_alignment.py -v
CI prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, streamlit_deck, wait_ready  # noqa: E402

pytestmark = pytest.mark.e2e

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "list_alignment_app"
VIEWPORT = {"width": 1920, "height": 1080}
LABELS = ("ctl", "ta", "ta_long", "ba", "ba_long", "inh", "dep")

# Per list: the root box, its cell, and for every item the glyph box of the
# text plus the computed right edge of the bullet cell.  The bullet is a
# ::before pseudo-element, so it has no client rect of its own: its cell ends
# exactly one flex `column-gap` before the text cell starts, and the glyph is
# right-aligned inside it (see stx_global.css).
MEASURE_JS = r"""() => {
  const out = [];
  for (const root of document.querySelectorAll('[data-testid="stVerticalBlock"].stx-list')) {
    const rr = root.getBoundingClientRect();
    const cell = root.parentElement.getBoundingClientRect();
    const items = [];
    for (const row of root.querySelectorAll('.stx-list-item')) {
      const inner = row.querySelector('[data-testid="stVerticalBlock"], [data-testid="stLayoutWrapper"]');
      if (!inner) continue;
      const rowBox = row.getBoundingClientRect();
      const innerBox = inner.getBoundingClientRect();
      const rcs = getComputedStyle(row);
      const gap = parseFloat(rcs.columnGap) || 0;
      const bulletW = parseFloat(getComputedStyle(row, '::before').width) || 0;
      // Glyph box of the first text node, i.e. where the text really paints.
      const walker = document.createTreeWalker(inner, NodeFilter.SHOW_TEXT);
      let textBox = null, node;
      while ((node = walker.nextNode())) {
        if (!node.nodeValue.trim()) continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        const b = range.getBoundingClientRect();
        if (b.width > 0) { textBox = b; break; }
      }
      if (!textBox) continue;
      const bulletRight = innerBox.left - gap;
      items.push({
        row_left: rowBox.left - rr.left, row_width: rowBox.width,
        inner_left: innerBox.left - rr.left, inner_width: innerBox.width,
        text_left: textBox.left - rr.left, text_right: textBox.right - rr.left,
        bullet_left: bulletRight - bulletW - rr.left,
        bullet_right: bulletRight - rr.left,
        bullet_to_text: textBox.left - bulletRight,
        font_size: parseFloat(rcs.fontSize),
      });
    }
    out.push({
      root_left: rr.left - cell.left, root_width: rr.width, cell_width: cell.width,
      text_align: getComputedStyle(root).textAlign,
      justify: root.querySelector('.stx-list-item')
        ? getComputedStyle(root.querySelector('.stx-list-item')).justifyContent : null,
      items: items,
    });
  }
  return out;
}"""


@pytest.fixture(scope="module")
def measured():
    from playwright.sync_api import sync_playwright

    with streamlit_deck(FIXTURE_DIR) as url, sync_playwright() as p:
        browser = launch_browser(p)
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()
        page.set_default_timeout(60_000)
        try:
            wait_ready(page, url)
            page.wait_for_timeout(1500)
            rows = page.evaluate(MEASURE_JS)
            assert len(rows) == len(LABELS), \
                f"expected {len(LABELS)} lists, measured {len(rows)}"
            data = dict(zip(LABELS, rows))
            for label, row in data.items():
                print(f"\n{label}: root_left={row['root_left']:.0f} "
                      f"root_w={row['root_width']:.0f} cell_w={row['cell_width']:.0f} "
                      f"text_align={row['text_align']} justify={row['justify']}")
                for it in row["items"]:
                    print(f"    bullet[{it['bullet_left']:.0f}→{it['bullet_right']:.0f}] "
                          f"text[{it['text_left']:.0f}→{it['text_right']:.0f}] "
                          f"gap={it['bullet_to_text']:.1f} inner_w={it['inner_width']:.0f}")
            yield data
        finally:
            browser.close()


# --------------------------------------------------------------------------
# (d) Non-regression — a list with no alignment parameter renders as in
#     0.7.32: full cell width, text-align untouched, bullet outside the text
#     column (the text cell fills the row).
# --------------------------------------------------------------------------
def test_d_plain_list_is_unchanged(measured) -> None:
    row = measured["ctl"]
    assert abs(row["root_width"] - row["cell_width"]) < 1, "plain list is no longer full width"
    assert abs(row["root_left"]) < 1, "plain list is no longer flush left in its cell"
    assert row["text_align"] in ("start", "left")
    assert row["justify"] == "flex-start"
    for it in row["items"]:
        assert abs(it["inner_width"] - (it["row_width"] - it["inner_left"])) < 1, \
            "the text cell no longer fills the row (flex-grow changed)"
        assert abs(it["text_left"] - it["inner_left"]) < 1, "text no longer starts at the text cell"


# --------------------------------------------------------------------------
# (a) text_align="center" — every line is centred in the cell AND the bullet
#     travels with its text (the `list-style-position: inside` equivalent).
# --------------------------------------------------------------------------
def test_a_text_align_center_centers_bullet_and_text_together(measured) -> None:
    row = measured["ta"]
    assert row["text_align"] == "center"
    assert row["justify"] == "center"
    for it in row["items"]:
        group_center = (it["bullet_left"] + it["text_right"]) / 2
        row_center = it["row_left"] + it["row_width"] / 2
        assert abs(group_center - row_center) < 2, (
            f"line not centred: bullet+text {it['bullet_left']:.0f}→{it['text_right']:.0f} "
            f"in row {it['row_left']:.0f}→{it['row_left'] + it['row_width']:.0f}"
        )
        assert it["bullet_to_text"] < 2 * it["font_size"], (
            f"bullet detached from its text: {it['bullet_to_text']:.0f}px "
            f"(limit {2 * it['font_size']:.0f}px)"
        )


# --------------------------------------------------------------------------
# (b) text_align does NOT resize the list: the root keeps the cell width,
#     whatever the length of the items.  This is what makes it safe in a
#     grid whose geometry must stay stable.
# --------------------------------------------------------------------------
def test_b_text_align_keeps_full_width_whatever_the_content(measured) -> None:
    short, long_ = measured["ta"], measured["ta_long"]
    for label, row in (("ta", short), ("ta_long", long_)):
        assert abs(row["root_width"] - row["cell_width"]) < 1, \
            f"{label}: text_align changed the list width ({row['root_width']} != {row['cell_width']})"
    assert abs(short["root_width"] - long_["root_width"]) < 1, \
        "text_align list width moved when an item got longer"


# --------------------------------------------------------------------------
# (c) block_align="center" — the box shrinks to its content and is centred,
#     so its width DOES follow the content.  The documented trade-off.
# --------------------------------------------------------------------------
def test_c_block_align_center_sizes_to_content(measured) -> None:
    short, long_ = measured["ba"], measured["ba_long"]
    assert short["root_width"] < short["cell_width"] - 1, \
        "block_align did not shrink the list to its content"
    assert abs(short["root_left"] - (short["cell_width"] - short["root_width"]) / 2) < 2, \
        "block_align did not centre the list box"
    assert long_["root_width"] > short["root_width"] + 1, \
        "block_align width did not follow a longer item"


# --------------------------------------------------------------------------
# 0.7.33 — a list with no parameter inherits the alignment of its container
#   (plain CSS behaviour, previously blocked by an inline `text-align: left`).
#   Without the "inside" mode the bullet stays outside, exactly like
#   `ul { text-align: center }` in ordinary HTML.
# --------------------------------------------------------------------------
def test_inherited_alignment_reaches_the_list(measured) -> None:
    row = measured["inh"]
    assert row["text_align"] == "center", \
        "a list still refuses to inherit text-align from its container"
    assert row["justify"] == "flex-start", \
        "inherited alignment must not switch on the inside-marker mode"
    for it in row["items"]:
        assert it["text_left"] > it["inner_left"] + 1, "text was not centred inside its cell"


# --------------------------------------------------------------------------
# The deprecated align="center" is now an exact synonym of block_align.
#   THIS is the before/after case: it is spelled the same in 0.7.32, where
#   it produced no geometric change at all.
# --------------------------------------------------------------------------
def test_deprecated_align_behaves_like_block_align(measured) -> None:
    dep, ba = measured["dep"], measured["ba"]
    assert dep["root_width"] < dep["cell_width"] - 1, \
        'align="center" is inert: the list still spans the whole cell'
    assert abs(dep["root_left"] - (dep["cell_width"] - dep["root_width"]) / 2) < 2, \
        'align="center" did not centre the list box'
    assert abs(dep["root_width"] - ba["root_width"]) < 1, \
        'align="center" and block_align="center" no longer agree'
