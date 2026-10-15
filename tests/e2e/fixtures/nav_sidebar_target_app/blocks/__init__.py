"""Three pages of 1, 20 and 3 slides (slides 1 | 2-21 | 22-24).

Each slide's marker is ``s<n>``; each page's first slide carries a level-1
heading; slide 12 carries the level-2 heading ``detail twelve``.
"""
from __future__ import annotations

import types

from streamtex import st_block, st_marker, st_slide_break, st_write
from streamtex.enums import Tags as t
from streamtex.styles import Style

_PAGE = Style("background:#0b1020; padding:24px; color:#f0f0f0; min-height:100vh;", "nav_page")
_H1 = Style("color:#FFD700; font-size:26pt; font-weight:bold;", "nav_h1")
_H2 = Style("color:#9fd3ff; font-size:18pt;", "nav_h2")


def _page(pid: str, first: int, n: int):
    def build():  # noqa: ANN202 — st_book calls build() with no args
        for k in range(n):
            num = first + k
            if k:
                st_slide_break(marker=False)
            st_marker(f"s{num}")
            with st_block(_PAGE):
                st_write(_H1, f"slide {num}", tag=t.div,
                         toc_lvl="1" if k == 0 else None, label=f"page {pid}")
                if num == 12:
                    st_write(_H2, "detail twelve", tag=t.div, toc_lvl="2")

    return build


MODULE_LIST = []
for _pid, _first, _n in (("a", 1, 1), ("b", 2, 20), ("c", 22, 3)):
    _m = types.ModuleType(f"bck_{_pid}")
    _m.build = _page(_pid, _first, _n)
    MODULE_LIST.append(_m)
