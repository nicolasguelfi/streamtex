"""st_include(markers=…): the roles of an included block's markers (#113)."""

import textwrap
import threading
import types
from unittest.mock import patch

import pytest

import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex.book import populate_markers_sidebar, st_include
from streamtex.marker import (
    MarkerConfig,
    annotate_marker_numbers,
    marker_entries,
    reset_marker_registry,
    role_override,
    st_marker,
    stop_count,
)
from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break
from streamtex.toc import TOCConfig, reset_toc_registry, toc_entries
from streamtex.write import st_write


def _start(**cfg):
    toc_mod.toc = None
    mk._registry = None
    reset_toc_registry(TOCConfig())
    reset_marker_registry(MarkerConfig(**cfg))


@pytest.fixture(autouse=True)
def registries():
    _start()
    rendered = []
    rec = rendered.append
    with patch("streamtex.marker._render", side_effect=rec), \
         patch("streamtex.write._render", side_effect=rec), \
         patch("streamtex.slide._render", side_effect=rec), \
         patch("streamtex.write.consume_block_top_injected", return_value=True):
        yield rendered
    mk._registry = None
    toc_mod.toc = None


def block(fn, name="blk"):
    m = types.ModuleType(name)
    m.build = fn
    return m


def _roles(e):
    return (e["stop"], e["listed"], e["toc"])


def _atom():
    st_marker("A")
    st_write("text")
    st_slide_break()
    st_marker("B", hidden=True)


# ---------------------------------------------------------------------------

class TestValues:
    def test_default_is_unchanged(self, registries):
        st_include(block(_atom))
        default = [dict(e) for e in marker_entries()]
        html_default = list(registries)
        _start()
        registries.clear()
        st_include(block(_atom), markers=True)
        assert marker_entries() == default and registries == html_default

    def test_the_113_scenario(self):
        """A host slide with its marker includes a block that opens with its own."""
        st_marker("Host")
        st_include(block(lambda: (st_marker("Atom"), st_write("x"))), markers=False)
        assert stop_count() == 1
        host, atom = marker_entries()
        assert _roles(atom) == (False, False, False)
        assert atom["anchor"].startswith("stx-marker-atom-")   # kept: deep link (author decision)

    def test_false_and_breaks(self, registries):
        def two_breaks():
            st_slide_break()
            st_slide_break()
        st_include(block(two_breaks), markers=False)
        assert sum("stx-slide-break-rule" in h for h in registries) == 2
        assert sum("stx-slide-break-spacer" in h for h in registries) == 2
        assert [_roles(e) for e in marker_entries()] == [(False, False, False)] * 2

    def test_false_and_fullscreen_hidden_path(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.HIDDEN, fullscreen=True)
        st_include(block(lambda: st_slide_break(config=cfg)), markers=False)
        assert stop_count() == 0

    def test_hidden(self):
        with patch("streamtex.book.st") as fake_st:
            st_include(block(lambda: st_marker("X")), markers="hidden")
            (e,) = marker_entries()
            assert _roles(e) == (True, False, False)
            populate_markers_sidebar(fake_st)
        assert not fake_st.method_calls or "X" not in str(fake_st.method_calls)

    def test_mapping_forces_roles_on(self):
        st_include(block(lambda: st_slide_break()), markers={"listed": True})
        assert _roles(marker_entries()[0]) == (True, True, False)

    def test_mapping_stop_off(self):
        st_include(block(lambda: st_marker("P")), markers={"stop": False})
        assert _roles(marker_entries()[0]) == (False, True, False)


class TestHeadings:
    def test_bridged_marker_false_keeps_the_toc_entry(self):
        _start(auto_marker_on_toc=True)
        st_include(block(lambda: st_write("T", toc_lvl="1")), markers=False)
        (t,) = toc_entries()
        assert t["section_number"] == "1 "
        assert _roles(marker_entries()[0]) == (False, False, True)

    def test_bridged_marker_hidden_is_the_authors_example(self):
        _start(auto_marker_on_toc=True)
        st_include(block(lambda: st_write("T", toc_lvl="1")), markers="hidden")
        assert _roles(marker_entries()[0]) == (True, False, True)

    def test_toc_false_drops_the_entries(self, registries):
        def inner():
            st_write("Inner", toc_lvl="1")
            st_marker("Annex", toc_lvl="1")
        st_include(block(inner), markers={"toc": False})
        st_write("Host", toc_lvl="1")
        assert [t["title"] for t in toc_entries()] == ["1 Host"]
        assert any(">Inner<" in h for h in registries)                # still rendered as text
        (annex,) = marker_entries()
        assert not annex["toc"] and annex["stop"] and annex["anchor"].startswith("stx-marker-")

    def test_toc_false_keeps_an_automatic_heading_stop(self, registries):
        _start(auto_marker_on_toc=1)
        st_include(block(lambda: st_write("Inner", toc_lvl="1")), markers={"toc": False})
        (e,) = marker_entries()
        assert _roles(e) == (True, True, False) and toc_entries() == []
        assert any(f"id='{e['anchor']}'" in h for h in registries)    # the heading is the anchor

    def test_toc_false_and_attach(self):
        def inner():
            st_marker("Label", hidden=True)
            st_write("H", toc_lvl="2", marker="attach")
        st_include(block(inner), markers={"toc": False})
        (e,) = marker_entries()
        assert not e["toc"] and toc_entries() == []


class TestNumbersAndNesting:
    def test_host_stops_are_numbered_without_gaps(self):
        st_marker("H1")
        st_include(block(lambda: [st_marker() for _ in range(3)]), markers=False)
        st_marker("H2")
        e = annotate_marker_numbers(marker_entries())
        assert [(x["label"], x["number"]) for x in e if x["stop"]] == [("H1", 1), ("H2", 2)]

    def test_outer_inclusion_wins(self):
        atom = block(lambda: st_marker("A"), "atom")
        lst = block(lambda: st_include(atom), "list")
        st_include(lst, markers=False)
        assert _roles(marker_entries()[0]) == (False, False, False)
        _start()
        lst2 = block(lambda: st_include(atom, markers="hidden"), "list2")
        st_include(lst2, markers={"listed": True})
        assert _roles(marker_entries()[0]) == (True, True, False)

    def test_inner_keys_apply_where_the_outer_is_silent(self):
        atom = block(lambda: st_marker("A"), "atom")
        lst = block(lambda: st_include(atom, markers={"stop": False}), "list")
        st_include(lst, markers="hidden")
        assert _roles(marker_entries()[0]) == (False, False, False)

    def test_host_markers_are_not_affected(self):
        def host():
            st_marker("Before")
            st_include(block(lambda: st_marker("In")), markers=False)
            st_marker("After")
        st_include(block(host))
        assert [e["stop"] for e in marker_entries()] == [True, False, True]

    def test_stack_restored_on_exception(self):
        def boom():
            st_marker("In")
            raise RuntimeError("x")
        with patch("streamtex.book.st"):
            with pytest.raises(RuntimeError):
                st_include(block(boom), markers=False)
        assert role_override() == {}
        st_marker("After")
        assert marker_entries()[-1]["stop"]


class TestCall:
    @pytest.mark.parametrize("bad", ["foo", {"stop": 1}, {"color": False}, {"toc": True}, 3])
    def test_validation_before_build(self, bad):
        called = []
        with pytest.raises(ValueError):
            st_include(block(lambda: called.append(1)), markers=bad)
        assert called == []

    def test_not_forwarded(self):
        got = {}
        st_include(block(lambda **kw: got.update(kw)), markers="hidden", lang="fr")
        assert got == {"lang": "fr"}

    @pytest.mark.parametrize("value", [False, "hidden", {"listed": True}, {"stop": False}])
    def test_layout_never_changes(self, registries, value):
        st_include(block(_atom))
        default = list(registries)
        _start()
        registries.clear()
        st_include(block(_atom), markers=value)
        assert registries == default

    def test_threads_do_not_share_an_override(self):
        seen = {}
        barrier = threading.Barrier(2)

        def run(name, value):
            def b():
                barrier.wait()
                seen[name] = dict(role_override())
            with patch("streamtex.book.st"):
                st_include(block(b), markers=value)
        t1 = threading.Thread(target=run, args=("a", False))
        t2 = threading.Thread(target=run, args=("b", "hidden"))
        for t in (t1, t2):
            t.start()
        for t in (t1, t2):
            t.join()
        assert seen == {"a": {"stop": False, "listed": False}, "b": {"listed": False}}


BOOK = textwrap.dedent("""
    import types
    import streamtex as stx

    def block(fn, name):
        m = types.ModuleType(name)
        m.build = fn
        return m

    atom = block(lambda: (stx.st_marker("Inner"), stx.st_slide_break()), "atom")
    def p0(): stx.st_marker("One")
    def p1():
        stx.st_marker("Two")
        stx.st_include(atom, markers="hidden")
    def p2(): stx.st_marker("Three")

    stx.st_book([block(p0, "p0"), block(p1, "p1"), block(p2, "p2")],
                toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(), paginate=True)
""")


@pytest.mark.usefixtures("reset_watch")
def test_paginated_cache_matches_live():
    from streamlit.testing.v1 import AppTest

    from streamtex.book import _STX_CACHE_KEY, _STX_PAGE_KEY
    at = AppTest.from_string(BOOK, default_timeout=30).run()
    assert not at.exception
    cached = at.session_state[_STX_CACHE_KEY]["markers"]
    assert [(e["label"], _roles(e)) for e in cached] == [
        ("One", (True, True, False)), ("Two", (True, True, False)),
        ("Inner", (True, False, False)), ("Marker 4", (True, False, False)),
        ("Three", (True, True, False))]
    at.session_state[_STX_PAGE_KEY] = 1
    at.run()
    live = [e for e in mk.marker_entries() if e["index"] in (1, 2, 3)]
    keys = ("label", "anchor", "stop", "listed", "toc", "stop_index", "number")
    assert [{k: e[k] for k in keys} for e in live] == \
           [{k: e[k] for k in keys} for e in cached[1:4]]
