"""Real-browser regression net for list alignment (0.7.33, extended 0.7.34).

Defects this guards against, none of which the HTML-string unit tests could
see:

* ``st_list(align="center")`` was INERT (0.6.13 → 0.7.32): the stylesheet
  selected on an ATTRIBUTE the observer never copies onto the parent.
* A hard-coded inline ``text-align: left`` on every list root blocked
  inheritance, so a centred container could not centre its lists.
* The marker stayed OUTSIDE the text unless ``text_align=`` was passed
  explicitly (0.7.33): a list that merely inherited a centring kept its
  bullet at the far left of the row, the plain CSS defect of
  ``text-align: center`` without ``list-style-position: inside``.
* The 0.7.33 "inside" procedure — shrinking the item's text cell with
  ``--stx-list-grow: 0`` and re-justifying the row — changed widths: a
  nested list lives inside that cell and shrank with it, and an item
  carrying a nested list had its marker placed against the whole box
  instead of against its own first line.

The measurements are geometric, on a two-column grid whose cells all share
one width.

Where the marker really is
--------------------------
A ``::before`` has no client rect, so the marker is located through the
element that actually renders it — exactly one of the two the stylesheet
declares.  In the outside mode that is the item ROW, and the marker's box
is measured independently: it is the row's first flex item, so it ends one
``column-gap`` before the content wrapper starts.  In the inside mode it is
the content WRAPPER, where the marker is the first inline box of the first
line and its advance comes from the used ``::before`` width and margin.

The discriminating measurement is therefore not the gap alone but the pair
"which element renders the marker" + "is the [marker | text] group centred
in the row".  A marker left behind at the row's left edge fails both: it
renders on the row, and the group straddles the centre.
"""
from __future__ import annotations

from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser, streamlit_deck, wait_ready  # noqa: E402

pytestmark = pytest.mark.e2e

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "list_alignment_app"
VIEWPORT = {"width": 1920, "height": 1080}
LABELS = ("ctl", "ta", "ta_long", "ba", "ba_long", "inh", "dep",
          "nest", "nest_long", "nest_ctl", "nest_ta")

MEASURE_JS = r"""() => {
  function wrapperOf(row) {
    return row.querySelector(':scope > [data-testid="stVerticalBlock"]')
        || row.querySelector(':scope > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]');
  }
  function firstGlyph(el) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (!node.nodeValue.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      const rects = range.getClientRects();
      for (const b of rects) if (b.width > 0) return b;
    }
    return null;
  }
  function measureItem(row, origin) {
    const wrap = wrapperOf(row);
    if (!wrap) return null;
    const rowBox = row.getBoundingClientRect();
    const wrapBox = wrap.getBoundingClientRect();
    const rcs = getComputedStyle(row);
    const rowBefore = getComputedStyle(row, '::before');
    const wrapBefore = getComputedStyle(wrap, '::before');
    const rowOn = rowBefore.display !== 'none' && rowBefore.content !== 'none';
    const wrapOn = wrapBefore.display !== 'none' && wrapBefore.content !== 'none';
    // The item's own first line lives in the wrapper's first child; a nested
    // list is a later child and must not be mistaken for it.
    const lead = wrap.firstElementChild;
    const textBox = firstGlyph(lead || wrap);
    if (!textBox) return null;
    let bulletLeft, bulletWidth;
    if (wrapOn && !rowOn) {
      // Inside: the marker is the first inline box of the first line.
      bulletWidth = parseFloat(wrapBefore.width) || 0;
      bulletLeft = textBox.left - bulletWidth
                 - (parseFloat(wrapBefore.marginInlineEnd) || 0);
    } else {
      // Outside: the marker is the row's first flex item.
      bulletWidth = parseFloat(rowBefore.width) || 0;
      bulletLeft = wrapBox.left - (parseFloat(rcs.columnGap) || 0) - bulletWidth;
    }
    return {
      markers: (rowOn ? 1 : 0) + (wrapOn ? 1 : 0),
      inside: row.classList.contains('stx-list-item--inside'),
      renders_inside: wrapOn && !rowOn,
      row_left: rowBox.left - origin, row_width: rowBox.width,
      wrap_left: wrapBox.left - origin, wrap_width: wrapBox.width,
      bullet_left: bulletLeft - origin,
      bullet_right: bulletLeft + bulletWidth - origin,
      text_left: textBox.left - origin, text_right: textBox.right - origin,
      bullet_to_text: textBox.left - (bulletLeft + bulletWidth),
      font_size: parseFloat(getComputedStyle(lead || wrap).fontSize),
    };
  }
  function measureList(root) {
    const rr = root.getBoundingClientRect();
    const parentBox = root.parentElement.getBoundingClientRect();
    const items = [];
    root.querySelectorAll(
      ':scope > [data-testid="stVerticalBlock"].stx-list-item,' +
      ' :scope > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"].stx-list-item'
    ).forEach(row => {
      const m = measureItem(row, rr.left);
      if (m) items.push(m);
    });
    const nested = [];
    root.querySelectorAll(':scope [data-testid="stVerticalBlock"].stx-list')
        .forEach(sub => nested.push(measureList(sub)));
    return {
      root_left: rr.left - parentBox.left, root_width: rr.width,
      cell_width: parentBox.width,
      text_align: getComputedStyle(root).textAlign,
      items, nested,
    };
  }
  const out = [];
  document.querySelectorAll('[data-testid="stVerticalBlock"].stx-list')
    .forEach(root => {
      if (root.parentElement.closest('[data-testid="stVerticalBlock"].stx-list')) return;
      out.push(measureList(root));
    });
  const grid = document.querySelector('[data-testid="stVerticalBlock"].stx-grid');
  return { lists: out, grid_width: grid ? grid.getBoundingClientRect().width : null };
}"""


def _flatten(row):
    """Yield *row* and every list nested under it, at any depth."""
    yield row
    for sub in row["nested"]:
        yield from _flatten(sub)


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
            payload = page.evaluate(MEASURE_JS)
            rows = payload["lists"]
            assert len(rows) == len(LABELS), \
                f"expected {len(LABELS)} top-level lists, measured {len(rows)}"
            data = dict(zip(LABELS, rows))
            data["_grid_width"] = payload["grid_width"]
            for label, row in data.items():
                if label.startswith("_"):
                    continue
                for depth, lst in enumerate(_flatten(row)):
                    print(f"\n{label}{'.' * depth} root_left={lst['root_left']:.0f} "
                          f"root_w={lst['root_width']:.0f} cell_w={lst['cell_width']:.0f} "
                          f"text_align={lst['text_align']}")
                    for it in lst["items"]:
                        print(f"    inside={it['renders_inside']!s:5} "
                              f"bullet[{it['bullet_left']:.0f}→{it['bullet_right']:.0f}] "
                              f"text[{it['text_left']:.0f}→{it['text_right']:.0f}] "
                              f"gap={it['bullet_to_text']:.1f} wrap_w={it['wrap_width']:.0f}")
            yield data
        finally:
            browser.close()


# --------------------------------------------------------------------------
# Structural invariant — exactly one of the two declared markers renders.
# --------------------------------------------------------------------------
def test_every_item_draws_exactly_one_marker(measured) -> None:
    for label in LABELS:
        for lst in _flatten(measured[label]):
            for it in lst["items"]:
                assert it["markers"] == 1, (
                    f"{label}: {it['markers']} markers on one item — the row and "
                    "the content wrapper both declare the bullet, the stylesheet "
                    "must show exactly one"
                )
                assert it["inside"] == it["renders_inside"], (
                    f"{label}: the .stx-list-item--inside class and the rendered "
                    "marker disagree"
                )


# --------------------------------------------------------------------------
# (d) Non-regression — a list with no alignment parameter, in a container
#     with no alignment, renders as in 0.7.32/0.7.33: full cell width, the
#     marker outside the text column, the text cell filling the row.
# --------------------------------------------------------------------------
def test_d_plain_list_is_unchanged(measured) -> None:
    row = measured["ctl"]
    assert abs(row["root_width"] - row["cell_width"]) < 1, "plain list is no longer full width"
    assert abs(row["root_left"]) < 1, "plain list is no longer flush left in its cell"
    assert row["text_align"] in ("start", "left")
    for it in row["items"]:
        assert not it["renders_inside"], "a plain list must keep the outside marker"
        assert abs(it["wrap_width"] - (it["row_width"] - it["wrap_left"])) < 1, \
            "the text cell no longer fills the row (flex-grow changed)"
        assert abs(it["text_left"] - it["wrap_left"]) < 1, \
            "text no longer starts at the text cell"


# --------------------------------------------------------------------------
# (a) text_align="center" — every line is centred in the cell AND the marker
#     travels with its text (the `list-style-position: inside` equivalent).
# --------------------------------------------------------------------------
def _assert_marker_travels_with_text(label, lst) -> None:
    for it in lst["items"]:
        assert it["renders_inside"], f"{label}: the marker is still outside the line"
        group_center = (it["bullet_left"] + it["text_right"]) / 2
        row_center = it["row_left"] + it["row_width"] / 2
        assert abs(group_center - row_center) < 2, (
            f"{label}: line not centred: marker+text {it['bullet_left']:.0f}→"
            f"{it['text_right']:.0f} in row {it['row_left']:.0f}→"
            f"{it['row_left'] + it['row_width']:.0f}"
        )
        assert it["bullet_to_text"] < 2 * it["font_size"], (
            f"{label}: marker detached from its text: {it['bullet_to_text']:.0f}px "
            f"(limit {2 * it['font_size']:.0f}px)"
        )


def test_a_text_align_center_centers_bullet_and_text_together(measured) -> None:
    row = measured["ta"]
    assert row["text_align"] == "center"
    _assert_marker_travels_with_text("ta", row)


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
# 0.7.33 — a list with no parameter inherits the alignment of its container.
# 0.7.34 — and that inherited alignment now moves the marker into the line,
#          exactly as the explicit parameter does.  This is the headline
#          case: it is what a project gets by declaring the alignment once,
#          on the container or on PresentationConfig(text_align=…).
# --------------------------------------------------------------------------
def test_inherited_alignment_reaches_the_list(measured) -> None:
    row = measured["inh"]
    assert row["text_align"] == "center", \
        "a list still refuses to inherit text-align from its container"
    _assert_marker_travels_with_text("inh", row)


def test_inherited_and_declared_alignment_render_identically(measured) -> None:
    inherited, declared = measured["inh"], measured["ta"]
    for a, b in zip(inherited["items"], declared["items"]):
        assert abs(a["bullet_left"] - b["bullet_left"]) < 1
        assert abs(a["text_left"] - b["text_left"]) < 1


# --------------------------------------------------------------------------
# The deprecated align="center" is now an exact synonym of block_align.
# --------------------------------------------------------------------------
def test_deprecated_align_behaves_like_block_align(measured) -> None:
    dep, ba = measured["dep"], measured["ba"]
    assert dep["root_width"] < dep["cell_width"] - 1, \
        'align="center" is inert: the list still spans the whole cell'
    assert abs(dep["root_left"] - (dep["cell_width"] - dep["root_width"]) / 2) < 2, \
        'align="center" did not centre the list box'
    assert abs(dep["root_width"] - ba["root_width"]) < 1, \
        'align="center" and block_align="center" no longer agree'


# --------------------------------------------------------------------------
# 0.7.34 (a) — an item carrying a nested list keeps its marker on ITS OWN
#              first line, and every line still wraps with its marker.
# --------------------------------------------------------------------------
def test_nested_item_keeps_its_marker_on_its_own_first_line(measured) -> None:
    for label in ("nest", "nest_long", "nest_ta"):
        for lst in _flatten(measured[label]):
            assert lst["text_align"] == "center", \
                f"{label}: the inherited centring did not reach a nested list"
            _assert_marker_travels_with_text(label, lst)


# --------------------------------------------------------------------------
# 0.7.34 (b) — no width changes anywhere: every root, nested ones included,
#              fills 100% of its container.  The 0.7.33 procedure shrank the
#              nested lists to 46-66% of the cell.
# --------------------------------------------------------------------------
def test_nested_lists_keep_the_full_width_of_their_item(measured) -> None:
    for label in ("nest", "nest_long", "nest_ctl", "nest_ta"):
        for depth, lst in enumerate(_flatten(measured[label])):
            assert abs(lst["root_width"] - lst["cell_width"]) < 1, (
                f"{label} (depth {depth}): list is {lst['root_width']:.0f}px in a "
                f"{lst['cell_width']:.0f}px container — the marker mode changed a width"
            )
            assert abs(lst["root_left"]) < 1, \
                f"{label} (depth {depth}): list is no longer flush in its container"
            # The container of a nested list IS the parent item's content
            # cell, so measuring the ratio alone would miss a cell that has
            # itself been shrunk — which is exactly what `--stx-list-grow: 0`
            # did in 0.7.33 (nested lists at 46-66% of the grid cell).
            for it in lst["items"]:
                assert abs(it["wrap_width"]
                           - (it["row_width"] - (it["wrap_left"] - it["row_left"]))) < 1, (
                    f"{label} (depth {depth}): the item's content cell is "
                    f"{it['wrap_width']:.0f}px of a {it['row_width']:.0f}px row — "
                    "the marker mode took width away from the content"
                )


# --------------------------------------------------------------------------
# 0.7.34 (c) — lengthening an item moves neither the list nor the grid.
# --------------------------------------------------------------------------
def test_longer_item_moves_neither_the_list_nor_the_grid(measured) -> None:
    short, long_ = measured["nest"], measured["nest_long"]
    assert abs(short["root_width"] - long_["root_width"]) < 1, \
        "a longer item changed the list width"
    for a, b in zip(_flatten(short), _flatten(long_)):
        assert abs(a["root_width"] - b["root_width"]) < 1, \
            "a longer item changed a nested list width"
    assert abs(measured["ta"]["cell_width"] - measured["ctl"]["cell_width"]) < 1, \
        "the grid columns are no longer equal"
    assert measured["_grid_width"] is not None


# --------------------------------------------------------------------------
# 0.7.34 — the same nesting with no alignment at all keeps the 0.7.33
#          outside marker: the new mode is opt-in through the alignment.
# --------------------------------------------------------------------------
def test_unaligned_nesting_keeps_the_outside_marker(measured) -> None:
    for lst in _flatten(measured["nest_ctl"]):
        assert lst["text_align"] in ("start", "left")
        for it in lst["items"]:
            assert not it["renders_inside"]
            assert abs(it["text_left"] - it["wrap_left"]) < 1

