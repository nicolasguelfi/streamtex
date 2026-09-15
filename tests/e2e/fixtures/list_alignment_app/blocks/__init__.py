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
  ``text-align: center``: the list must inherit it (0.7.33).
* ``dep``      — the deprecated ``align="center"``, which must now behave
  exactly like ``block_align="center"`` (it was inert from 0.6.13 to
  0.7.32).  It is the one scenario expressible in both versions, so it is
  what makes this file a genuine before/after test.
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

# The test identifies each list by its position in document order, which is
# the order of SPECS below; the rendered label is there for headed debugging.
LABELS = ("ctl", "ta", "ta_long", "ba", "ba_long", "inh", "dep")


def _fill(controller, items):
    for text in items:
        with controller.item():
            st_write(TXT, text)


def _build():  # noqa: ANN202 — st_book calls build() with no args
    specs = [
        ("ctl", SHORT_ITEMS, {}, False),
        ("ta", SHORT_ITEMS, {"text_align": "center"}, False),
        ("ta_long", LONG_ITEMS, {"text_align": "center"}, False),
        ("ba", SHORT_ITEMS, {"block_align": "center"}, False),
        ("ba_long", LONG_ITEMS, {"block_align": "center"}, False),
        ("inh", SHORT_ITEMS, {}, True),
        ("dep", SHORT_ITEMS, {"align": "center"}, False),
    ]
    with st_grid(2, GRID, [CELL_CENTER if inherit else CELL
                           for _, _, _, inherit in specs]) as g:
        for label, items, kwargs, _inherit in specs:
            with g.cell():
                st_write(Style("font-size:12px;color:#888;text-align:left;", "la_lbl"),
                         label)
                with st_list(lt.unordered, **kwargs) as lst:
                    _fill(lst, items)


MODULE_LIST: list[types.ModuleType] = []
_mod = types.ModuleType("list_alignment_page")
_mod.build = _build
MODULE_LIST.append(_mod)
