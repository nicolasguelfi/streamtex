"""One slide per rack (#52). Durations are seconds long so the tests can watch them end."""
from __future__ import annotations

import types

from streamtex import CountdownConfig, st_countdown, st_marker, st_space, st_write

S3 = 3 / 60          # 3 seconds, in minutes


def _slide(name, body):
    def build():  # noqa: ANN202 — st_book calls build() with no args
        st_marker(name)
        st_write(f"case-{name}", toc_lvl="1")
        body()
        st_space("v", "30vh")
    mod = types.ModuleType(f"bck_{name}")
    mod.build = build
    return mod


MODULE_LIST = [
    _slide("chain", lambda: st_countdown([("Intro", S3), ("Talk", S3), ("Questions", 1)],
                                         "chain", grid=(1, 3), rack_vh=40)),
    _slide("parallel", lambda: st_countdown([("Team A", S3), ("Team B", 1)], "parallel", rack_vh=35)),
    _slide("types", lambda: st_countdown([
        ("Tokyo", None, {"type": "clock", "tz": "Asia/Tokyo"}),
        ("Luxembourg", None, {"type": "clock", "tz": "Europe/Luxembourg"}),
        ("Free stopwatch", None, {"type": "stopwatch"}),
        ("Warm-up", S3),
        ("Overtime", S3, {"type": "stopwatch"}),
        ("Resume at", "00:00", {"type": "clock", "tz": "Europe/Luxembourg"}),
    ], "chain", grid=(2, 3), rack_vh=60)),
    _slide("break", lambda: st_countdown([("Back in", 15)], config=CountdownConfig(
        autostart=True, show_global_buttons=False), rack_vh=40)),
    _slide("alarms", lambda: st_countdown([("Bell", S3), ("Gong", S3, {"alarm": "gong", "duration": 2}),
                                           ("Silent", S3, "off")], "parallel", rack_vh=35,
                                          config=CountdownConfig(alarm="bell"))),
    _slide("end", lambda: st_write("after the racks")),
]
