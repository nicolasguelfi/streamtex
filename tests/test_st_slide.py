"""st_slide(): slide break then slide container, set_slide_container() (#81)."""

from unittest.mock import patch

import streamtex as stx
from streamtex.styles import Style


def test_st_slide_writes_exactly_break_then_container():
    calls = []
    import contextlib

    @contextlib.contextmanager
    def fake_block(style):
        calls.append(("block", str(style)))
        yield

    with patch("streamtex.slide.st_slide_break", lambda: calls.append(("break",))), \
         patch("streamtex.container.st_block", fake_block):
        with stx.st_slide():
            calls.append(("content",))
        with stx.st_slide(cut=True, style=Style("min-height: 60vh;", "short")):
            calls.append(("content",))
    box = str(stx.SLIDE_CONTAINER)
    assert calls[0] == ("block", box)
    assert calls[1] == ("content",)
    assert calls[2] == ("break",)
    assert calls[3][0] == "block" and box in calls[3][1] and "min-height: 60vh;" in calls[3][1]


def test_set_slide_container():
    mine = Style("min-height: 70vh;", "mine")
    try:
        stx.set_slide_container(mine)
        assert stx.get_slide_container() is mine
    finally:
        stx.set_slide_container(None)
    assert stx.get_slide_container() is stx.SLIDE_CONTAINER
