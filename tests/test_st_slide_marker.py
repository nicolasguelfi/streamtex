"""st_slide as the single slide construction: marker=, break settings, box=False, per-session box (#122)."""

import contextlib
import textwrap
from unittest.mock import patch

import pytest

import streamtex as stx
import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex.marker import MarkerConfig, MarkerRoles, marker_entries, reset_marker_registry, st_marker
from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide, st_slide_break
from streamtex.spacing import Spacing
from streamtex.styles import Style
from streamtex.toc import TOCConfig, reset_toc_registry, toc_entries


@pytest.fixture
def out():
    toc_mod.toc = None
    mk._registry = None
    reset_toc_registry(TOCConfig())
    reset_marker_registry(MarkerConfig())
    rec = []

    @contextlib.contextmanager
    def fake_block(style):
        rec.append(("box", str(style)))
        yield

    with patch("streamtex.slide._render", side_effect=lambda h: rec.append(("html", h))), \
         patch("streamtex.marker._render", side_effect=lambda h: rec.append(("marker", h))), \
         patch("streamtex.space._render", side_effect=lambda h: rec.append(("space", h))), \
         patch("streamtex.container.st_block", fake_block), \
         patch("streamlit.session_state", {}):
        yield rec
    mk._registry = None
    toc_mod.toc = None


def _roles(e):
    return (e["stop"], e["listed"], e["toc"])


def _kinds(rec):
    out = []
    for kind, h in rec:
        if kind == "html":
            out.append("rule" if "slide-break-rule" in h else "spacer" if "spacer" in h else "html")
        else:
            out.append(kind)
    return out


class TestMarker:
    def test_false_keeps_rule_and_spacer(self, out):
        with st_slide(cut=True, marker=False):
            pass
        assert _kinds(out) == ["rule", "spacer", "box"] and marker_entries() == []

    @pytest.mark.parametrize("cut", [True, False])
    def test_true_is_a_stop_not_listed(self, out, cut):
        with st_slide(cut=cut, marker=True):
            pass
        (e,) = marker_entries()
        assert _roles(e) == (True, False, False)

    def test_label_with_cut_takes_the_break_marker_place(self, out):
        with st_slide(cut=True, marker="RAG", spacing=Spacing(top="2em")):
            pass
        (e,) = marker_entries()
        assert e["label"] == "RAG" and _roles(e) == (True, True, False)
        assert _kinds(out) == ["rule", "spacer", "marker", "space", "box"]

    def test_label_without_cut_comes_before_the_box(self, out):
        with st_slide(marker="Atom"):
            pass
        assert _kinds(out) == ["marker", "box"]
        assert marker_entries()[0]["label"] == "Atom"

    def test_key_and_roles(self, out):
        with st_slide(marker="RAG", key="rag", roles=MarkerRoles(listed=False, toc_lvl="2")):
            pass
        (e,) = marker_entries()
        assert e["key"] == "rag" and _roles(e) == (True, False, True)
        assert e["toc_anchor"] == toc_entries()[-1]["key_anchor"]

    def test_same_registry_as_st_marker(self, out):
        with st_slide(marker="X", roles=MarkerRoles.HIDDEN):
            pass
        a = marker_entries()[0]
        st_marker("X", roles=MarkerRoles.HIDDEN)
        b = marker_entries()[1]
        strip = ("index", "anchor", "stop_index")
        assert {k: v for k, v in a.items() if k not in strip} == {k: v for k, v in b.items() if k not in strip}

    def test_marker_false_with_key_is_refused(self, out):
        with pytest.raises(ValueError, match="marker=False"):
            with st_slide(marker=False, key="k"):
                pass

    @pytest.mark.parametrize("mode", [SlideBreakMode.HIDDEN, SlideBreakMode.RULE_ONLY,
                                      SlideBreakMode.SPACER_ONLY, SlideBreakMode.MARKER_ONLY])
    def test_explicit_marker_in_every_mode(self, out, mode):
        with st_slide(cut=True, marker="M", config=SlideBreakConfig(mode=mode)):
            pass
        assert [e["label"] for e in marker_entries()] == ["M"]

    def test_explicit_marker_with_breaks_switched_off(self, out):
        from streamtex.slide import _BREAK_ENABLED_KEY
        with patch("streamlit.session_state", {_BREAK_ENABLED_KEY: False}):
            with st_slide(cut=True, marker="M"):
                pass
        assert [e["label"] for e in marker_entries()] == ["M"]

    def test_default_keeps_the_mode_rule(self, out):
        with st_slide(cut=True, config=SlideBreakConfig(mode=SlideBreakMode.HIDDEN)):
            pass
        assert marker_entries() == []


class TestBreakSettings:
    def test_defaults_call_the_break_with_no_argument(self):
        calls = []
        with patch("streamtex.slide.st_slide_break", lambda *a, **k: calls.append((a, k))), \
             patch("streamtex.container.st_block", contextlib.nullcontext):
            with st_slide(cut=True):
                pass
        assert calls == [((), {})]

    def test_zoom_reaches_the_break(self, out):
        from streamtex.spacing import get_section_zoom
        with st_slide(cut=True, zoom=150):
            assert get_section_zoom() == 150

    def test_config_reaches_the_break(self, out):
        with st_slide(cut=True, config=SlideBreakConfig(space="9vh")):
            pass
        assert any("height: 9vh" in h for k, h in out if k == "html")

    @pytest.mark.parametrize("kw", [dict(zoom=150), dict(spacing=Spacing(top="1em")),
                                    dict(config=SlideBreakConfig())])
    def test_settings_without_cut_raise(self, out, kw):
        with pytest.raises(ValueError, match="need cut=True"):
            with st_slide(**kw):
                pass


class TestBox:
    def test_box_false_is_no_box(self, out):
        with st_slide(cut=True, marker="Long read", box=False):
            out.append(("content", ""))
        assert _kinds(out) == ["rule", "spacer", "marker", "content"]

    def test_box_false_with_style_raises(self, out):
        with pytest.raises(ValueError, match="box=False"):
            with st_slide(box=False, style=Style("color: red;", "r")):
                pass

    def test_style_is_added_to_the_box(self, out):
        with st_slide(style=Style("margin-top: 3vh;", "top")):
            pass
        assert "margin-top: 3vh;" in out[-1][1] and str(stx.SLIDE_CONTAINER) in out[-1][1]


# ---------------------------------------------------------------------------
# Per-session box and break settings
# ---------------------------------------------------------------------------

SCRIPT = textwrap.dedent("""
    import streamlit as st
    import streamtex as stx
    from streamtex.styles import Style
    which = st.query_params.get("w", "a")
    if not st.session_state.get("_set"):
        stx.set_slide_container(Style("min-height: 1vh;" if which == "a" else "min-height: 2vh;", which))
        stx.set_slide_break_config(stx.SlideBreakConfig(space="1vh" if which == "a" else "2vh"))
        st.session_state["_set"] = True
    st.text(str(stx.get_slide_container()) + " | " + stx.get_slide_break_config().space)
""")


def test_two_sessions_keep_their_own_box_and_break_settings():
    from streamlit.testing.v1 import AppTest
    a = AppTest.from_string(SCRIPT)
    a.query_params["w"] = "a"
    a.run()
    b = AppTest.from_string(SCRIPT)
    b.query_params["w"] = "b"
    b.run()
    a.run()                                   # a reruns after b set its own values
    assert "min-height: 1vh;" in a.text[0].value and a.text[0].value.endswith("| 1vh")
    assert "min-height: 2vh;" in b.text[0].value and b.text[0].value.endswith("| 2vh")
    assert stx.get_slide_container() is stx.SLIDE_CONTAINER   # the process-wide value is untouched


def test_outside_a_session_the_fallback_is_used():
    mine = Style("min-height: 70vh;", "mine")
    try:
        stx.set_slide_container(mine)
        assert stx.get_slide_container() is mine
    finally:
        stx.set_slide_container(None)


def test_same_html_as_the_hand_written_form(out):
    with st_slide(cut=True, marker="X"):
        pass
    by_slide = (list(out), [dict(e) for e in marker_entries()])
    out.clear()
    reset_marker_registry(MarkerConfig())
    mk._registry.reset()
    st_slide_break(marker_label="X", marker=MarkerRoles.NAMED)
    from streamtex.container import st_block
    with st_block(stx.get_slide_container()):
        pass
    by_hand = (list(out), [dict(e) for e in marker_entries()])
    assert by_slide == by_hand
