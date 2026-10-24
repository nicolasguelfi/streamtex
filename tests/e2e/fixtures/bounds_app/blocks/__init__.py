"""Videos bounded by max_vw / max_vh (#141), with the 16:9 clip of media_app.

In order: both bounds, a width bound that wins in a wide window, a height
bound inside st_zoom(130) (multiplied by the zoom), and a bounded video
with fullscreen=True (the box applies).
"""
from __future__ import annotations

import types
from pathlib import Path

from streamtex import st_marker, st_video, st_write, st_zoom

CLIP = str(Path(__file__).resolve().parents[2] / "media_app" / "clip.mp4")


def build():  # noqa: ANN202 — st_book calls build() with no args
    st_marker("bounds")
    st_write("case-both")
    st_video(CLIP, max_vw=100, max_vh=50)
    st_write("case-vw")
    st_video(CLIP, max_vw=40, max_vh=50)
    st_write("case-zoom")
    with st_zoom(130):
        st_video(CLIP, max_vh=30)
    st_write("case-fullscreen")
    st_video(CLIP, max_vh=25, fullscreen=True)


bck_bounds = types.ModuleType("bck_bounds")
bck_bounds.build = build
MODULE_LIST = [bck_bounds]
