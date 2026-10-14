"""Four pages of 1, 3, 2 and 1 slides (slides 1 | 2-4 | 5-6 | 7).

A press that turns the page and the next press, which must stay inside the
new page, is the case where a press made while the page changes got lost.
"""
from __future__ import annotations

import types

from streamtex import st_block, st_marker, st_slide_break, st_write
from streamtex.enums import Tags as t
from streamtex.styles import Style

_PAGE = Style("background:#0b1020; padding:24px; color:#f0f0f0; min-height:100vh;", "nav_page")
_H1 = Style("color:#FFD700; font-size:26pt; font-weight:bold;", "nav_h1")


def _page(pid: str, n: int):
    def build():  # noqa: ANN202 — st_book calls build() with no args
        for k in range(n):
            if k:
                st_slide_break(marker=False)
            st_marker(f"{pid}-{k + 1}")
            with st_block(_PAGE):
                st_write(_H1, f"{pid} slide {k + 1}", tag=t.div,
                         toc_lvl="1" if k == 0 else None, label=pid)

    return build


MODULE_LIST = []
for _pid, _n in (("p0", 1), ("p1", 3), ("p2", 2), ("p3", 1)):
    _m = types.ModuleType(f"bck_{_pid}")
    _m.build = _page(_pid, _n)
    MODULE_LIST.append(_m)
