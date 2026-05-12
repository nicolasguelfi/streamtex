"""Programmatically built block modules for the cache-build freeze fixture.

Each module exposes a ``build()`` callable expected by ``st_book``.  We
generate N modules sharing a common shape (marker + 2-column grid + a
few zoomed/styled blocks + a short ordered list).  Their cumulative DOM
footprint approximates the FC-260507-NG-SLIDES deck (~40 blocks, ~3-7
markers each) that triggers the Chrome freeze.

Importing this package eagerly creates ``MODULE_LIST`` so ``book.py``
can just hand it to ``st_book(...)``.
"""
from __future__ import annotations

import types

from streamtex import (
    st_block,
    st_grid,
    st_list,
    st_marker,
    st_write,
    st_zoom,
)
from streamtex.enums import ListTypes as lt
from streamtex.enums import Tags as t
from streamtex.styles import Style

# Styled palettes used across the generated blocks — every Style.create
# emits a per-instance attribute-selector <style> in the rendered HTML.
_PAGE = Style(
    "background: #0b1020; padding: 24px; color: #f0f0f0; min-height: 220px;",
    "cbfreeze_page",
)
_PANEL_A = Style(
    "background: #1565C0; padding: 16px; color: white; "
    "border: 3px solid #FFD700; border-radius: 8px;",
    "cbfreeze_panel_a",
)
_PANEL_B = Style(
    "background: #00695C; padding: 16px; color: white; "
    "border: 3px solid #FFD700; border-radius: 8px;",
    "cbfreeze_panel_b",
)
_TITLE = Style(
    "color: #FFD700; font-size: 28pt; font-weight: bold; text-align: center;",
    "cbfreeze_title",
)
_ITEM = Style(
    "color: #FFFFFF; font-size: 18pt; line-height: 1.30;",
    "cbfreeze_item",
)
_LABEL = Style(
    "color: #7AB8F5; font-weight: bold; font-size: 18pt; line-height: 1.30;",
    "cbfreeze_label",
)


def _make_build(idx: int):
    """Return a closure that renders a single slide for module *idx*.

    Each slide emits ~25–30 markers (matching the FC-260507-NG-SLIDES
    deck's per-slide density): nested zoom + grid + block + list + spans,
    so the cache-build accumulator hits realistic DOM volume by mid-deck.
    """

    def build():  # noqa: ANN001 — st_book just calls build() with no args
        st_marker(f"Slide {idx}")
        with st_block(_PAGE):
            # ── Header strip + title ──
            with st_block(_PANEL_A):
                with st_zoom(95):
                    st_write(_TITLE, f"Cache-build freeze repro — slide {idx}",
                             tag=t.div, toc_lvl="2")

            # ── Two-column body, each column nests grid > 3 cells > block ──
            with st_grid(cols="50% 50%", gap="2%") as outer:
                with outer.cell():
                    with st_zoom(85):
                        with st_block(_PANEL_A):
                            with st_grid(cols="1fr 1fr 1fr", gap="0.5rem") as inner:
                                for sub in range(3):
                                    with inner.cell():
                                        with st_zoom(90):
                                            with st_block(_PANEL_B):
                                                st_write(
                                                    _ITEM,
                                                    (_LABEL, f"L{sub} "),
                                                    f"slide {idx} left.{sub} body.",
                                                )
                with outer.cell():
                    with st_zoom(85):
                        with st_block(_PANEL_B):
                            with st_grid(cols="1fr 1fr 1fr", gap="0.5rem") as inner:
                                for sub in range(3):
                                    with inner.cell():
                                        with st_zoom(90):
                                            with st_block(_PANEL_A):
                                                st_write(
                                                    _ITEM,
                                                    (_LABEL, f"R{sub} "),
                                                    f"slide {idx} right.{sub} body.",
                                                )

            # ── Ordered list — 6 items, each styled ──
            with st_list(list_type=lt.ordered, l_style=_ITEM, li_style=_ITEM) as ll:
                for letter in "ABCDEF":
                    with ll.item():
                        st_write(
                            _ITEM,
                            (_LABEL, f"Point {idx}.{letter} — "),
                            f"item body for slide {idx}, letter {letter}, "
                            "with a moderate-length sentence exercising the "
                            "list-item marker observer path through several "
                            "nested style attribute writes.",
                        )

            # ── Trailing styled blocks for additional marker volume ──
            with st_grid(cols="33% 33% 33%", gap="1%") as foot:
                for j, panel in enumerate((_PANEL_A, _PANEL_B, _PANEL_A)):
                    with foot.cell():
                        with st_block(panel):
                            st_write(_ITEM, (_LABEL, f"Foot {j} — "),
                                     f"trailing block {j} for slide {idx}.")

    return build


# Generate N synthetic block modules.  We expose them as module-like objects
# (types.ModuleType) so st_book's `getattr(module, '__name__', ...)` reads a
# sensible name in the loading-overlay updates.
N_BLOCKS = 60
MODULE_LIST: list[types.ModuleType] = []
for _i in range(1, N_BLOCKS + 1):
    _mod = types.ModuleType(f"cbfreeze_slide_{_i:02d}")
    _mod.build = _make_build(_i)
    MODULE_LIST.append(_mod)
