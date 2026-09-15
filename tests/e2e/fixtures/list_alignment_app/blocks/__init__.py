"""Fixture deck for the list-alignment e2e (``test_list_alignment.py``).

A two-column grid whose cells all share one style, so every list sits in a
cell of the SAME width and the measurements compare like with like.  Each
list has three items of very different lengths, which is what makes the
difference between the two alignment notions visible:

* ``ctl``      — no alignment parameter: the 0.7.32 rendering (control).
* ``ta``       — ``text_align="center"``: text centred, bullet moved into
  the line, list width untouched.
* ``ta_long``  — same, with a much longer item: the width must NOT move.
* ``ba``       — ``block_align="center"``: the list box shrinks to its
  content and is centred.
* ``ba_long``  — same, with a much longer item: the width MUST follow.
* ``inh``      — no parameter, inside a cell that declares
  ``text-align: center``: the list must inherit it (0.7.33) AND take its
  markers into the line, exactly as ``ta`` does (0.7.34).
* ``dep``      — the deprecated ``align="center"``, which must now behave
  exactly like ``block_align="center"`` (it was inert from 0.6.13 to
  0.7.32).  It is the one scenario expressible in both versions, so it is
  what makes this file a genuine before/after test.
* ``nest``     — inherited centring with a NESTED list under the first
  item (0.7.34): the marker goes with the item's own first line, and the
  nested list keeps the full width of the item's content.
* ``nest_long`` — same with a longer item: no width may move.
* ``nest_ctl`` — the same nesting with no alignment at all: the outside
  marker and the 0.7.33 geometry, untouched.
* ``nest_ta``  — the same nesting, this time with an explicit
  ``text_align="center"`` in a cell that declares nothing.  This is the
  case where the 0.7.33 procedure shrank the nested list to a fraction of
  the cell, because the nested list lived inside the text cell it had
  shrunk to fit the parent item's own text.

The item texts are long enough to wrap inside a cell: a marker that only
travels with a single-line item is the easy half of the problem.
"""
from __future__ import annotations

import types

from streamtex import st_grid, st_list, st_write
from streamtex.enums import ListTypes as lt
from streamtex.styles import Style

CELL = Style("background:#101a33; color:#f0f0f0; padding:0;", "la_cell")
CELL_CENTER = CELL + Style("text-align:center;", "la_cell_center")
TXT = Style("color:#eee; font-size:16px;", "la_txt")
GRID = Style("gap:16px;", "la_grid")

SHORT_ITEMS = ("alpha", "beta gamma", "delta")
LONG_ITEMS = ("alpha", "beta gamma delta epsilon zeta eta theta iota kappa", "delta")

# Deliberately wider than a cell, so it wraps: the first line then has to
# carry the marker with it, which is what the 0.7.33 procedure could not do.
WRAPPING = ("a considerably longer activity label that has to wrap onto "
            "at least two lines inside its cell")
SUB_ITEMS = ("sub one", WRAPPING)

LABELS = ("ctl", "ta", "ta_long", "ba", "ba_long", "inh", "dep",
          "nest", "nest_long", "nest_ctl", "nest_ta")


def _fill(controller, items):
    for text in items:
        with controller.item():
            st_write(TXT, text)


def _fill_nested(controller, lead):
    """One item carrying a nested list, then a plain item."""
    with controller.item():
        st_write(TXT, lead)
        with st_list(lt.unordered) as sub:
            _fill(sub, SUB_ITEMS)
    with controller.item():
        st_write(TXT, "Contexts")


def _build():  # noqa: ANN202 — st_book calls build() with no args
    specs = [
        ("ctl", SHORT_ITEMS, {}, False),
        ("ta", SHORT_ITEMS, {"text_align": "center"}, False),
        ("ta_long", LONG_ITEMS, {"text_align": "center"}, False),
        ("ba", SHORT_ITEMS, {"block_align": "center"}, False),
        ("ba_long", LONG_ITEMS, {"block_align": "center"}, False),
        ("inh", SHORT_ITEMS, {}, True),
        ("dep", SHORT_ITEMS, {"align": "center"}, False),
        ("nest", None, {}, True),
        ("nest_long", None, {}, True),
        ("nest_ctl", None, {}, False),
        ("nest_ta", None, {"text_align": "center"}, False),
    ]
    leads = {"nest": "Activities", "nest_long": WRAPPING,
             "nest_ctl": "Activities", "nest_ta": "Activities"}
    with st_grid(2, GRID, [CELL_CENTER if inherit else CELL
                           for _, _, _, inherit in specs]) as g:
        for label, items, kwargs, _inherit in specs:
            with g.cell():
                st_write(Style("font-size:12px;color:#888;text-align:left;", "la_lbl"),
                         label)
                with st_list(lt.unordered, **kwargs) as lst:
                    if items is None:
                        _fill_nested(lst, leads[label])
                    else:
                        _fill(lst, items)


MODULE_LIST: list[types.ModuleType] = []
_mod = types.ModuleType("list_alignment_page")
_mod.build = _build
MODULE_LIST.append(_mod)
