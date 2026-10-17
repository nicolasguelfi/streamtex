"""Videos sized with width= / align= (#126), one autoplay without muted and one
with an explicit muted=False (#35).

``clip.mp4``: 2 s, 160×90, with an audio track (a video without one is not
held by the browsers' autoplay rule).
"""
from __future__ import annotations

import types
from pathlib import Path

from streamtex import st_marker, st_video, st_write

CLIP = str(Path(__file__).resolve().parent.parent / "clip.mp4")
CASES = [("full", {}), ("half", {"width": "50%"}), ("px400", {"width": 400}),
         ("halfleft", {"width": "50%", "align": "left"})]


def build():  # noqa: ANN202 — st_book calls build() with no args
    st_marker("media")
    st_write("case-autoplay")                         # first: Chrome pauses a muted video off screen
    st_video(CLIP, autoplay=True, loop=True, width=400)   # no muted: started muted (#35)
    st_write("case-sound")
    st_video(CLIP, autoplay=True, loop=True, muted=False, width=400)   # kept: sound if allowed
    for name, kw in CASES:
        st_write(f"case-{name}")
        st_video(CLIP, **kw)


bck_media = types.ModuleType("bck_media")
bck_media.build = build
MODULE_LIST = [bck_media]
