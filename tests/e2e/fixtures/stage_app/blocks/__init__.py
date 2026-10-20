"""One slide per staged video (#56), between two text slides.

``clip.mp4``: 2 s, 160×90 (16:9), with an audio track.
"""
from __future__ import annotations

import types
from pathlib import Path

from streamtex import st_marker, st_space, st_video, st_write

CLIP = str(Path(__file__).resolve().parent.parent / "clip.mp4")


def _slide(name, body):
    def build():  # noqa: ANN202 — st_book calls build() with no args
        st_marker(name)
        st_write(f"case-{name}", toc_lvl="1")
        body()
        st_space("v", "60vh")
    mod = types.ModuleType(f"bck_{name}")
    mod.build = build
    return mod


MODULE_LIST = [
    _slide("intro", lambda: st_write("before the videos")),
    _slide("slide", lambda: st_video(CLIP, theater="slide", loop=True)),
    _slide("cover", lambda: st_video(CLIP, theater=True, fit="cover", loop=True)),
    _slide("window", lambda: st_video(CLIP, theater="window", autoplay=True, loop=True)),
    _slide("fullscreen", lambda: st_video(CLIP, fullscreen=True)),
    _slide("end", lambda: st_write("after the videos")),
]
