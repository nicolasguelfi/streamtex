"""Three slides with intentionally different zoom + grid-template values.

The bleed-through bug we're hunting is the one visible on FC-260507-NG-SLIDES
when the user navigates forward then back: the previously visible slide's
inline ``grid-template-columns`` and ``zoom`` written by the marker
observer survive on a ``stVerticalBlock`` that React reuses across the
paginated navigation, so the new slide inherits the previous slide's
layout instead of its own.

Each slide here exposes:
  * a unique ``data-slide-id`` on the outermost ``st_block`` (read from
    the DOM by the e2e test so it can correlate "what's visible" with
    "what should be visible");
  * a distinctive ``st_grid(cols=...)`` template;
  * a distinctive ``st_zoom`` factor.

Bleed-through manifests as inline-styles on the visible cells whose
values match a previous slide's marker rather than the current one.
"""
from __future__ import annotations

import types

from streamtex import (
    st_block,
    st_grid,
    st_list,
    st_marker,
    st_space,
    st_write,
    st_zoom,
)
from streamtex.enums import ListTypes as lt
from streamtex.enums import Tags as t
from streamtex.styles import Style

_PAGE = Style(
    "background: #0b1020; padding: 20px; color: #f0f0f0; min-height: 240px;",
    "bleed_page",
)
_PANEL = Style(
    "background: #1565C0; padding: 12px; color: white; "
    "border: 2px solid #FFD700; min-height: 100px;",
    "bleed_panel",
)
_TITLE = Style(
    "color: #FFD700; font-size: 24pt; font-weight: bold;",
    "bleed_title",
)


# Each tuple drives one slide.  Each slide nests two grids (mirroring
# the FC-260507-NG-SLIDES ``bck_knowledge_first.py``-style layout that
# triggers the bleed-through):
#
#   (slide_id, title_grid_cols, title_zoom,  body_grid_cols, body_zoom)
#
# Every column-template and every zoom factor is unique across slides,
# so any leak of an inline ``grid-template-columns`` / ``zoom`` from a
# previously visited slide is detectable in the assertions below.
SLIDE_SPECS = [
    ("slide-A", "92% 8%",  90, "45% 55%", 100),
    ("slide-B", "80% 20%", 85, "50% 50%",  75),
    ("slide-C", "70% 30%", 95, "33% 67%",  65),
]


def _make_build(slide_id: str, title_cols: str, title_zoom: int,
                body_cols: str, body_zoom: int):
    """Closure producing the build() callable for one specific slide.

    Mirrors the two-grid / two-zoom structure of FC-260507-NG-SLIDES
    slides like ``bck_knowledge_first`` and ``bck_enterprise_vs_academic``
    that exhibited the bleed visible in the user-reported screenshots:
      * outer page block,
      * a "title" grid with one zoom-scoped title cell + one decoration
        cell,
      * an outer "body" zoom wrapping a second grid that itself nests
        list + block primitives inside each cell.

    The grid templates and zoom factors are unique across slides so the
    e2e test can detect any stray inline-style from a previous slide.
    """

    def build():  # noqa: ANN001 — st_book just calls build() with no args
        st_marker(slide_id)
        with st_block(_PAGE):
            with st_block(_PANEL):
                pass  # header-strip mimic
            # ── Title grid (title in zoom, decoration on the side) ──
            with st_block(_PAGE):
                with st_grid(cols=title_cols, gap="0px") as g:
                    with g.cell():
                        with st_zoom(title_zoom):
                            st_write(
                                _TITLE,
                                f"{slide_id} (title={title_cols}/{title_zoom}"
                                f" body={body_cols}/{body_zoom})",
                                tag=t.div,
                                toc_lvl="2",
                                label=slide_id,
                            )
                    with g.cell():
                        with st_block(_PANEL):
                            st_write(_PANEL, "tip")

            st_space("v", 1)

            # ── Body — outer zoom wrapping a second grid ──
            with st_zoom(body_zoom):
                with st_grid(cols=body_cols, gap="64px") as g:
                    with g.cell():
                        with st_block(_PANEL):
                            st_write(_PANEL, f"LEFT — {slide_id}")
                    with g.cell():
                        with st_block(_PANEL):
                            with st_list(list_type=lt.unordered,
                                          l_style=_PANEL,
                                          li_style=_PANEL) as ll:
                                with ll.item():
                                    st_write(_PANEL, f"Item 1 — {slide_id}")
                                with ll.item():
                                    st_write(_PANEL, f"Item 2 — {slide_id}")
                                with ll.item():
                                    st_write(_PANEL, f"Item 3 — {slide_id}")

            st_space("v", 1)
            st_write(_PANEL, f"Footer / source for {slide_id}")

    return build


MODULE_LIST: list[types.ModuleType] = []
for _spec in SLIDE_SPECS:
    _id = _spec[0]
    _mod = types.ModuleType(f"bleed_{_id.replace('-', '_')}")
    _mod.build = _make_build(*_spec)
    _mod._slide_spec = _spec
    MODULE_LIST.append(_mod)
