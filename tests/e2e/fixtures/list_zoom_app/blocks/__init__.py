"""Centred and left lists whose first item's text is in st_zoom(150) (#112).

``zoom-<align>`` / ``plain-<align>``: one list per alignment; ``title-nested``
is a zoomed level-1 item of a centred list, followed by a nested list whose
item is ``child-nested``.
"""
from __future__ import annotations

import types

from streamtex import st_list, st_marker, st_write, st_zoom
from streamtex.enums import ListTypes as lt


def build():  # noqa: ANN202 — st_book calls build() with no args
    st_marker("lists")
    for align in ("center", "left"):
        with st_list(list_type=lt.unordered, text_align=align) as lst:
            with lst.item():
                with st_zoom(150):
                    st_write(f"zoom-{align}")
            with lst.item():
                st_write(f"plain-{align}")
    with st_list(list_type=lt.unordered, text_align="center") as lst:
        with lst.item():
            with st_zoom(150):
                st_write("title-nested")
            with st_list(list_type=lt.unordered) as sub:
                with sub.item():
                    st_write("child-nested")


bck_lists = types.ModuleType("bck_lists")
bck_lists.build = build
MODULE_LIST = [bck_lists]
