"""The standard break between included items, st_include(break_before=), st_sequence (#118)."""

import dataclasses
import textwrap
import types
from unittest.mock import patch

import pytest

import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex import slide as slide_mod
from streamtex.book import st_include, st_sequence
from streamtex.marker import MarkerConfig, marker_entries, reset_marker_registry, st_marker
from streamtex.slide import (
    _BREAK_ENABLED_KEY,
    _BREAK_MODE_KEY,
    SlideBreakConfig,
    get_slide_break_config,
    set_slide_break_config,
    st_slide_break,
)
from streamtex.toc import TOCConfig, reset_toc_registry


@pytest.fixture(autouse=True)
def env():
    toc_mod.toc = None
    mk._registry = None
    reset_toc_registry(TOCConfig())
    reset_marker_registry(MarkerConfig())
    saved = get_slide_break_config()
    out = []
    with patch("streamtex.slide._render", side_effect=out.append), \
         patch("streamtex.marker._render", side_effect=out.append), \
         patch("streamlit.session_state", {}):
        yield out
    set_slide_break_config(saved)
    mk._registry = None
    toc_mod.toc = None


def blk(name, out=None, fn=None):
    m = types.ModuleType(name)
    m.build = fn or (lambda *a, **k: out.append(f"<{name}>"))
    return m


def lab_cut():
    """The lab's project-side break (lists/_include.py), the reference."""
    st_slide_break(config=dataclasses.replace(get_slide_break_config(), marker=False))


def _breaks(out):
    return [h for h in out if "stx-slide-break-rule" in h]


class TestStandardBreak:
    def test_same_html_as_the_lab_cut(self, env):
        set_slide_break_config(SlideBreakConfig(space="2vh", rule_margin_top="1em",
                                                rule_margin_bottom="1em"))
        lab_cut()
        lab = list(env)
        env.clear()
        slide_mod._standard_break()
        assert env == lab and marker_entries() == []

    def test_reads_the_config_at_call_time(self, env):
        set_slide_break_config(SlideBreakConfig(space="2vh", rule_margin_top="1em"))
        slide_mod._standard_break()
        assert "margin-top: 1em" in env[0] and "height: 2vh" in env[1]

    def test_sidebar_toggle_off_draws_nothing(self, env):
        with patch("streamlit.session_state", {_BREAK_ENABLED_KEY: False}):
            slide_mod._standard_break()
        assert env == [] and marker_entries() == []

    def test_sidebar_rule_only(self, env):
        with patch("streamlit.session_state", {_BREAK_ENABLED_KEY: True, _BREAK_MODE_KEY: "Rule only"}):
            slide_mod._standard_break()
        assert len(env) == 1 and "stx-slide-break-rule" in env[0]

    def test_sidebar_marker_only_places_no_marker(self, env):
        with patch("streamlit.session_state", {_BREAK_ENABLED_KEY: True, _BREAK_MODE_KEY: "Marker only"}):
            slide_mod._standard_break()
        assert env == [] and marker_entries() == []

    def test_is_a_slide_boundary(self):
        st_marker("A")
        slide_mod._standard_break()
        assert mk.marker_attach_target() is None


class TestBreakBefore:
    def test_false_is_nothing(self, env):
        st_include(blk("a", env))
        st_include(blk("b", env), break_before=False)
        assert env == ["<a>", "<b>"]

    def test_true_is_the_standard_break_before_the_block(self, env):
        st_include(blk("b", env), break_before=True)
        assert len(env) == 3 and env[-1] == "<b>" and "stx-slide-break-rule" in env[0]
        assert marker_entries() == []

    def test_a_config_is_used_as_given(self, env):
        st_include(blk("b", env), break_before=SlideBreakConfig(marker=True, marker_hidden=True))
        (e,) = marker_entries()
        assert e["stop"] and not e["listed"]

    def test_wrong_type(self, env):
        built = []
        with pytest.raises(TypeError):
            st_include(blk("b", fn=lambda: built.append(1)), break_before="yes")
        assert env == [] and built == []

    def test_markers_do_not_apply_to_the_hosts_break(self):
        st_include(blk("b", fn=lambda: None),
                   break_before=SlideBreakConfig(marker=True, marker_hidden=False), markers=False)
        assert marker_entries()[0]["stop"]

    def test_none_block_draws_no_break(self, env):
        with patch("streamtex.book.st"):
            st_include(None, break_before=True)
        assert env == []


class TestStSequence:
    def test_breaks_between_items_only(self, env):
        st_sequence([blk("a", env), blk("b", env), blk("c", env)])
        tags = ["|" if "stx-slide-break-rule" in h else h for h in env if "spacer" not in h]
        assert tags == ["<a>", "|", "<b>", "|", "<c>"]

    def test_one_and_zero_items(self, env):
        st_sequence([blk("a", env)])
        assert env == ["<a>"]
        env.clear()
        st_sequence([])
        assert env == []

    def test_nested_lists_never_break_at_their_head(self, env):
        inner = blk("L", fn=lambda *a, **k: st_sequence([blk("b", env), blk("c", env)], *a, **k))
        st_sequence([blk("a", env), inner])
        tags = ["|" if "stx-slide-break-rule" in h else h for h in env if "spacer" not in h]
        assert tags == ["<a>", "|", "<b>", "|", "<c>"]

    def test_separator_none(self, env):
        st_sequence([blk("a", env), blk("b", env)], separator=None)
        assert env == ["<a>", "<b>"]

    def test_separator_block_gets_the_same_args(self, env):
        got = []
        sep = blk("sep", fn=lambda *a, **k: got.append((a, k)))
        st_sequence([blk("a", env), blk("b", env), blk("c", env)], "x", separator=sep, lang="fr")
        assert got == [(("x",), {"lang": "fr"})] * 2 and _breaks(env) == []

    def test_separator_config(self, env):
        st_sequence([blk("a", env), blk("b", env)], separator=SlideBreakConfig(marker=False, space="9vh"))
        assert any("height: 9vh" in h for h in env)

    def test_separator_wrong_type_before_any_item(self, env):
        with pytest.raises(TypeError):
            st_sequence([blk("a", env)], separator=42)
        assert env == []

    def test_args_and_kwargs_reach_every_item(self):
        got = []
        items = [blk(n, fn=lambda *a, **k: got.append((a, k))) for n in "abc"]
        st_sequence(items, "x", lang="fr", rev="7")
        assert got == [(("x",), {"lang": "fr", "rev": "7"})] * 3

    def test_markers_reach_every_item(self):
        items = [blk(n, fn=lambda: st_marker("Atom")) for n in "ab"]
        st_sequence(items, markers=False)
        assert [e["stop"] for e in marker_entries()] == [False, False]
        assert mk.stop_count() == 0

    def test_one_stop_per_slide_with_atoms(self):
        items = [blk(n, fn=lambda: st_marker("Atom")) for n in "abc"]
        st_sequence(items)
        assert mk.stop_count() == 3

    def test_exported(self):
        import streamtex
        assert streamtex.st_sequence is st_sequence


def test_pdf_page_break_per_standard_break():
    from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
    from streamtex.pdf_export import PdfMode, inject_print_css
    reset_export_buffer(ExportConfig(enabled=True))
    with patch("streamtex.slide._render", wraps=None) as r:
        r.side_effect = __import__("streamtex.export", fromlist=["_render"])._render
        st_sequence([blk(n, fn=lambda: None) for n in "abc"])
    html = generate_export_html()
    reset_export_buffer(ExportConfig(enabled=False))
    assert html.count('class="stx-slide-break-spacer"') == 2
    printed = inject_print_css(html, PdfMode.PAGINATED)
    assert "page-break-after: always" in printed or "break-after: page" in printed


BOOK = textwrap.dedent("""
    import types
    import streamtex as stx
    def block(name):
        m = types.ModuleType(name)
        m.build = lambda: stx.st_marker(name)
        return m
    stx.st_book([block("a"), block("b"), block("c")], toc_config=stx.TOCConfig(),
                marker_config=stx.MarkerConfig(), paginate=True)
""")


@pytest.mark.usefixtures("reset_watch")
def test_export_break_between_entries_is_the_standard_break():
    """The cache build captures the export with the module's break between entries."""
    from streamlit.testing.v1 import AppTest

    calls = []
    real = slide_mod._standard_break
    with patch("streamtex.slide._standard_break", side_effect=lambda: (calls.append(1), real())):
        at = AppTest.from_string(BOOK, default_timeout=30).run()
    assert not at.exception
    assert len(calls) == 2                                            # between 3 entries
    assert len(mk.marker_entries()) == 3      # no marker added (the fixture patches session_state)
