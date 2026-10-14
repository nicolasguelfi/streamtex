"""The three independent roles of a marker — stop, listed, in TOC (#116)."""

import dataclasses
import json
import shutil
import subprocess
import textwrap
import types
import warnings
from unittest.mock import MagicMock, patch

import pytest

import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex.marker import (
    MarkerConfig,
    MarkerRoles,
    listed_entries,
    marker_entries,
    marker_slide_boundary,
    normalize_marker_entries,
    reset_marker_registry,
    st_marker,
    stop_count,
    stop_entries,
    stop_of,
)
from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide, st_slide_break
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
    with patch("streamtex.marker._render"), patch("streamtex.write._render"), \
         patch("streamtex.slide._render"), \
         patch("streamtex.write.consume_block_top_injected", return_value=True):
        yield
    mk._registry = None
    toc_mod.toc = None


def _roles(e):
    return (e["stop"], e["listed"], e["toc"])


# ---------------------------------------------------------------------------
# 1. The value object
# ---------------------------------------------------------------------------

class TestMarkerRolesObject:
    def test_defaults(self):
        r = MarkerRoles()
        assert (r.stop, r.listed, r.toc_lvl) == (True, True, None)

    def test_constants(self):
        assert MarkerRoles.NAMED == MarkerRoles(stop=True, listed=True)
        assert MarkerRoles.HIDDEN == MarkerRoles(stop=True, listed=False)
        assert MarkerRoles.ANCHOR == MarkerRoles(stop=False, listed=False)

    def test_frozen(self):
        with pytest.raises(dataclasses.FrozenInstanceError):
            MarkerRoles().stop = False

    def test_constants_are_not_fields(self):
        assert [f.name for f in dataclasses.fields(MarkerRoles)] == ["stop", "listed", "toc_lvl"]

    def test_exported(self):
        import streamtex
        assert streamtex.MarkerRoles is MarkerRoles


# ---------------------------------------------------------------------------
# 2. The eight combinations through st_marker
# ---------------------------------------------------------------------------

EIGHT = [
    (dict(label="Prompting", toc_lvl="1"), (True, True, True)),
    (dict(label="X"), (True, True, False)),
    (dict(label="X", hidden=True, toc_lvl="2"), (True, False, True)),
    (dict(hidden=True), (True, False, False)),
    (dict(label="Part B", stop=False, toc_lvl="1"), (False, True, True)),
    (dict(label="Part B", stop=False), (False, True, False)),
    (dict(label="Annex", stop=False, listed=False, toc_lvl="1"), (False, False, True)),
    (dict(key="exercise-3", stop=False, listed=False), (False, False, False)),
]


class TestEightCombinations:
    @pytest.mark.parametrize("kwargs,roles", EIGHT)
    def test_registry_fields(self, kwargs, roles):
        st_marker(**kwargs)
        (e,) = marker_entries()
        assert _roles(e) == roles
        stop, listed, toc = roles
        assert e["hidden"] is (stop and not listed)
        assert e["origin"] == "marker"
        assert e["stop_index"] == (0 if stop else None)
        if toc:
            assert e["toc_anchor"] == e["anchor"] == toc_entries()[-1]["key_anchor"]
            assert e["toc_level"] in (1, 2)
        else:
            assert "toc_anchor" not in e
            assert toc_entries() == []

    def test_relative_toc_level(self):
        st_write("Chapter", toc_lvl="1", marker=False)
        st_marker("Part B", stop=False, toc_lvl="+1")
        (e,) = marker_entries()
        assert e["toc_level"] == 2 and not e["stop"] and e["listed"]

    def test_toc_marker_without_registry_still_gets_its_toc_entry(self):
        mk._registry = None
        with patch("streamtex.marker._render") as render:
            st_marker("Annex", stop=False, listed=False, toc_lvl="1")
        anchor = toc_entries()[-1]["key_anchor"]
        assert f'id="{anchor}"' in render.call_args[0][0]

    def test_key_is_kept(self):
        st_marker(key="exercise-3", stop=False, listed=False)
        assert marker_entries()[0]["key"] == "exercise-3"


# ---------------------------------------------------------------------------
# 3. stop_index and stop_of
# ---------------------------------------------------------------------------

class TestStopIndex:
    def test_only_stops_are_ranked(self):
        st_marker("A", stop=False)
        st_marker("B")
        st_marker("C", stop=False)
        st_marker("D", hidden=True)
        e = marker_entries()
        assert [x["stop_index"] for x in e] == [None, 0, None, 1]
        assert [stop_of(x) for x in e] == [0, 0, 0, 1]
        assert stop_count() == 2
        assert [x["label"] for x in stop_entries()] == ["B", "D"]
        assert [x["label"] for x in listed_entries()] == ["A", "B", "C"]

    def test_module_without_stops(self):
        st_marker("A", stop=False)
        assert stop_of(marker_entries()[0]) is None
        assert stop_count() == 0

    def test_helpers_take_a_list(self):
        entries = [{"index": 0, "label": "a", "anchor": "a", "hidden": True},
                   {"index": 1, "label": "b", "anchor": "b", "hidden": False}]
        assert stop_count(entries) == 2
        assert [e["label"] for e in listed_entries(entries)] == ["b"]


# ---------------------------------------------------------------------------
# 4. Shortcuts and errors
# ---------------------------------------------------------------------------

class TestShortcuts:
    @staticmethod
    def _strip(e):
        return {k: v for k, v in e.items() if k not in ("index", "anchor", "stop_index")}

    def test_hidden_equals_roles_hidden(self):
        st_marker("X", hidden=True)
        st_marker("X", roles=MarkerRoles.HIDDEN)
        a, b = marker_entries()
        assert self._strip(a) == self._strip(b)

    def test_default_is_named_and_auto(self):
        st_marker()
        (e,) = marker_entries()
        assert _roles(e) == (True, True, False)
        assert e["auto"] is True and e["label"] == "Marker 1"

    @pytest.mark.parametrize("kwargs", [dict(hidden=True, listed=True),
                                        dict(hidden=True, stop=False),
                                        dict(hidden=False, listed=False)])
    def test_contradictions_raise_value_error(self, kwargs):
        with pytest.raises(ValueError, match="hidden"):
            st_marker("X", **kwargs)

    def test_roles_and_keywords_are_exclusive(self):
        with pytest.raises(TypeError, match="stop"):
            st_marker("X", roles=MarkerRoles.HIDDEN, stop=False)

    def test_toc_lvl_needs_a_label(self):
        with pytest.raises(ValueError, match="label"):
            st_marker(toc_lvl="1")

    def test_visible_is_not_listed(self):
        with patch("streamtex.marker._render") as render:
            st_marker("X", visible=True, listed=False)
        assert not marker_entries()[0]["listed"]
        assert "dashed" in render.call_args[0][0]


# ---------------------------------------------------------------------------
# 5. A TOC heading's marker (st_write)
# ---------------------------------------------------------------------------

class TestHeadingMarker:
    def test_none_without_auto_is_a_toc_entry_only(self):
        st_write("H", toc_lvl="1")
        assert marker_entries() == [] and len(toc_entries()) == 1

    def test_none_with_auto_creates_a_named_toc_marker(self):
        _start(auto_marker_on_toc=1)
        st_write("H", toc_lvl="1")
        (e,) = marker_entries()
        assert _roles(e) == (True, True, True)
        assert e["origin"] == "toc" and e["anchor"] == e["toc_anchor"]

    def test_roles_per_level(self):
        _start(auto_marker_on_toc=True,
               toc_marker_roles={1: MarkerRoles.NAMED, 2: MarkerRoles.HIDDEN})
        st_write("H1", toc_lvl="1")
        st_slide_break(marker=False)
        st_write("H2", toc_lvl="2")
        st_slide_break(marker=False)
        st_write("H3", toc_lvl="3")
        assert [_roles(e) for e in marker_entries()] == [
            (True, True, True), (True, False, True), (True, True, True)]

    def test_true_declares_its_own_stop(self):
        st_write("H", toc_lvl="1", marker=True)
        assert _roles(marker_entries()[0]) == (True, True, True)

    def test_false_is_no_marker(self):
        _start(auto_marker_on_toc=True)
        st_write("H", toc_lvl="1", marker=False)
        assert marker_entries() == []

    def test_the_authors_example_in_one_call(self):
        st_write("H", toc_lvl="2", marker=MarkerRoles.HIDDEN)
        (e,) = marker_entries()
        assert _roles(e) == (True, False, True)
        assert e["toc_anchor"] == toc_entries()[-1]["key_anchor"]

    def test_roles_with_toc_lvl_are_refused(self):
        with pytest.raises(ValueError, match="toc_lvl"):
            st_write("H", toc_lvl="2", marker=MarkerRoles(toc_lvl="1"))

    def test_unknown_string_is_refused(self):
        with pytest.raises(ValueError, match="attach"):
            st_write("H", toc_lvl="2", marker="atach")

    def test_attach_inside_an_atom_hidden(self):
        st_marker("Label", hidden=True)
        st_write("H", toc_lvl="2", marker="attach")
        (e,) = marker_entries()
        assert _roles(e) == (True, False, True)
        assert e["label"] == "Label"
        assert e["toc_anchor"] == toc_entries()[-1]["key_anchor"]

    def test_attach_inside_an_atom_listed(self):
        st_marker("Label")
        st_write("H", toc_lvl="2", marker="attach")
        (e,) = marker_entries()
        assert _roles(e) == (True, True, True)

    def test_attach_keeps_the_markers_roles(self):
        st_marker("P", stop=False, listed=False)
        st_write("H", toc_lvl="2", marker="attach")
        assert _roles(marker_entries()[0]) == (False, False, True)

    def test_attach_without_target_warns_and_creates(self):
        with pytest.warns(UserWarning, match="no marker opens the slide"):
            st_write("H", toc_lvl="2", marker="attach")
        (e,) = marker_entries()
        assert _roles(e) == (True, True, True) and e["origin"] == "toc"

    def test_marker_without_toc_lvl_warns(self):
        with pytest.warns(UserWarning, match="without toc_lvl"):
            st_write("text", marker=True)


# ---------------------------------------------------------------------------
# 6. Breaks
# ---------------------------------------------------------------------------

class TestBreakRoles:
    def test_default_is_a_hidden_stop(self):
        st_slide_break()
        (e,) = marker_entries()
        assert _roles(e) == (True, False, False) and e["origin"] == "break"

    def test_marker_false_is_no_marker(self):
        st_slide_break(marker=False)
        assert marker_entries() == []

    def test_marker_roles_per_call(self):
        st_slide_break(marker_label="S", marker=MarkerRoles.NAMED)
        assert _roles(marker_entries()[0]) == (True, True, False)

    def test_per_call_wins_over_config(self):
        st_slide_break(config=SlideBreakConfig(marker=False), marker=True)
        assert len(marker_entries()) == 1

    def test_marker_hidden_shortcut(self):
        st_slide_break(marker_label="S", marker_hidden=False)
        assert _roles(marker_entries()[0]) == (True, True, False)

    def test_config_roles(self):
        st_slide_break(config=SlideBreakConfig(marker=MarkerRoles(stop=False)))
        assert _roles(marker_entries()[0]) == (False, True, False)

    def test_toc_roles_through_a_break(self):
        st_slide_break(marker_label="Sec", marker=MarkerRoles(listed=False, toc_lvl="1"))
        (e,) = marker_entries()
        assert _roles(e) == (True, False, True) and e["origin"] == "break"

    def test_hidden_mode_fullscreen_follows_marker_hidden(self):
        """0.7.45 forced hidden=True there and ignored marker_hidden."""
        cfg = SlideBreakConfig(mode=SlideBreakMode.HIDDEN, fullscreen=True, marker_hidden=False)
        st_slide_break(marker_label="S", config=cfg)
        assert _roles(marker_entries()[0]) == (True, True, False)

    def test_sidebar_override_copies_marker(self):
        import streamlit as st

        from streamtex.slide import _BREAK_ENABLED_KEY, _effective_config
        with patch.object(st, "session_state", {_BREAK_ENABLED_KEY: True}):
            cfg, _ = _effective_config(SlideBreakConfig(marker=MarkerRoles.ANCHOR))
        assert cfg.marker == MarkerRoles.ANCHOR


# ---------------------------------------------------------------------------
# 7. No guessed attachment; a warning when a book mixes the two models
# ---------------------------------------------------------------------------

def _0745(entries):
    return [{k: e[k] for k in ("index", "label", "anchor", "hidden")} for e in entries]


class TestNoAutomaticAttachment:
    """Automatic heading markers keep the 0.7.45 registry (decision a1, #116)."""

    def test_break_then_heading_is_0745_and_warns(self):
        _start(auto_marker_on_toc=1)
        st_slide_break()
        with pytest.warns(UserWarning, match="second navigation stop"):
            st_write("Heading", toc_lvl="1")
        key = toc_entries()[-1]["key_anchor"]
        assert _0745(marker_entries()) == [
            {"index": 0, "label": "Marker 1", "anchor": "stx-marker-marker-1-0", "hidden": True},
            {"index": 1, "label": "Heading", "anchor": key, "hidden": False}]

    def test_the_warning_says_what_to_write(self):
        _start(auto_marker_on_toc=1)
        st_slide_break(marker_label="Slide 4")
        with pytest.warns(UserWarning) as rec:
            st_write("Heading", toc_lvl="1")
        msg = str(rec[0].message)
        assert "'Heading'" in msg and "'Slide 4'" in msg and 'marker="attach"' in msg

    def test_st_slide_opens_a_deck_slide_too(self):
        _start(auto_marker_on_toc=1)
        with patch("streamtex.container.st_block", MagicMock()):
            with st_slide():
                st_marker("Atom")
                with pytest.warns(UserWarning, match="second navigation stop"):
                    st_write("Heading", toc_lvl="1")

    def test_a_document_page_never_warns(self):
        """The advanced manual case: a waypoint, then a heading, on one page."""
        _start(auto_marker_on_toc=1)
        st_marker("Hidden Waypoint")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            st_write("MarkerConfig Reference", toc_lvl="1")
        assert [e["label"] for e in marker_entries()] == ["Hidden Waypoint", "MarkerConfig Reference"]

    def test_heading_after_heading_does_not_warn(self):
        _start(auto_marker_on_toc=2)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            st_write("H1", toc_lvl="1")
            st_write("H2", toc_lvl="2")
        assert len(marker_entries()) == 2

    def test_slide_without_stop_does_not_warn(self):
        _start(auto_marker_on_toc=1)
        st_slide_break(marker=False)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            st_write("H", toc_lvl="1")
        assert len(marker_entries()) == 1

    def test_unlisted_non_stop_heading_does_not_warn(self):
        _start(auto_marker_on_toc=1, toc_marker_roles=MarkerRoles(stop=False))
        st_slide_break()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            st_write("H", toc_lvl="1")

    def test_declared_stops_do_not_warn(self):
        st_slide_break()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            st_write("H", toc_lvl="1", marker=True)
            st_write("H2", toc_lvl="2", marker=MarkerRoles.HIDDEN)
        assert len(marker_entries()) == 3

    def test_auto_zero_creates_nothing(self):
        st_slide_break()
        st_write("H", toc_lvl="1")
        (e,) = marker_entries()
        assert not e["toc"]

    def test_attach_is_the_clean_spelling_in_a_deck(self):
        _start(auto_marker_on_toc=1)
        st_slide_break()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            st_write("Heading", toc_lvl="1", marker="attach")
        (e,) = marker_entries()
        assert _roles(e) == (True, False, True)
        assert e["label"] == "Heading" and "auto" not in e
        assert e["anchor"].startswith("stx-marker-")      # the break's anchor stays
        from streamtex.book import _toc_dot_anchors
        assert toc_entries()[-1]["key_anchor"] in _toc_dot_anchors(marker_entries())

    def test_attach_does_not_cross_a_slide(self):
        st_marker("A")
        st_slide_break(marker=False)
        with pytest.warns(UserWarning, match="no marker opens the slide"):
            st_write("H", toc_lvl="1", marker="attach")
        assert len(marker_entries()) == 2

    def test_attach_does_not_cross_a_book_entry(self):
        st_marker("A")
        marker_slide_boundary()
        with pytest.warns(UserWarning, match="no marker opens the slide"):
            st_write("H", toc_lvl="1", marker="attach")

    def test_attach_does_not_link_to_another_heading(self):
        st_write("H1", toc_lvl="1", marker=True)
        with pytest.warns(UserWarning, match="no marker opens the slide"):
            st_write("H2", toc_lvl="2", marker="attach")

    def test_spacing_is_0745(self):
        from streamtex.spacing import Spacing
        _start(auto_marker_on_toc=1)
        with patch("streamtex.write.consume_block_top_injected", return_value=False), \
             patch("streamtex.write.resolve_section_spacing", return_value=Spacing(top="3em")), \
             patch("streamtex.space.st_space") as space:
            st_write("Heading", toc_lvl="1")
        space.assert_called_once_with("v", "3em")

    def test_explicit_attach_adds_no_spacing(self):
        st_marker("Label")
        with patch("streamtex.write.consume_block_top_injected", return_value=False), \
             patch("streamtex.space.st_space") as space:
            st_write("H", toc_lvl="2", marker="attach")
        space.assert_not_called()


# ---------------------------------------------------------------------------
# 8. Slide boundaries
# ---------------------------------------------------------------------------

class TestSlideBoundary:
    def test_slide_without_cut_is_a_boundary(self):
        st_marker("A")
        with patch("streamtex.container.st_block", MagicMock()):
            with st_slide():
                with pytest.warns(UserWarning, match="no marker opens the slide"):
                    st_write("H", toc_lvl="1", marker="attach")
        assert len(marker_entries()) == 2

    def test_slide_with_cut_keeps_its_break_marker(self):
        with patch("streamtex.container.st_block", MagicMock()):
            with st_slide(cut=True):
                st_write("H", toc_lvl="1", marker="attach")
        (e,) = marker_entries()
        assert e["origin"] == "break" and e["label"] == "H"

    def test_include_is_not_a_boundary(self):
        from streamtex.book import st_include
        atom = types.ModuleType("atom")
        atom.build = lambda: st_write("H", toc_lvl="1", marker="attach")
        st_marker("List block")
        st_include(atom)
        (e,) = marker_entries()
        assert e["label"] == "List block" and e["toc"]


# ---------------------------------------------------------------------------
# 9. Older page caches
# ---------------------------------------------------------------------------

class TestNormalisation:
    def test_old_entries_get_their_roles(self):
        old = [{"index": 0, "label": "a", "anchor": "a", "hidden": True},
               {"index": 1, "label": "b", "anchor": "b", "hidden": False}]
        normalize_marker_entries(old)
        assert [_roles(e) for e in old] == [(True, False, False), (True, True, False)]
        assert [e["stop_index"] for e in old] == [0, 1]

    def test_new_entries_are_kept(self):
        st_marker("A", stop=False)
        st_marker("B")
        e = [dict(x) for x in marker_entries()]
        assert normalize_marker_entries([dict(x) for x in e]) == e


# ---------------------------------------------------------------------------
# 10. Book surfaces (AppTest): page cache, pre/post-seed, tabs, titles, page map
# ---------------------------------------------------------------------------

BOOK = textwrap.dedent("""
    import types
    import streamtex as stx
    from streamtex import MarkerRoles

    def block(fn, name):
        m = types.ModuleType(name)
        m.build = fn
        return m

    def p0():
        stx.st_marker("Intro", key="intro")
        stx.st_write("Part one", toc_lvl="1", marker="attach")
        stx.st_marker("Sub", stop=False)
        stx.st_slide_break()
    def p1():
        stx.st_marker(hidden=True)
        stx.st_marker("Deep", key="deep", stop=False, listed=False)
        stx.st_slide_break()
    def p2():
        stx.st_marker("Annex", stop=False, listed=False, toc_lvl="1")
        stx.st_write("Side", toc_lvl="2", marker=MarkerRoles.HIDDEN)
    def p3():
        stx.st_write("Footer")

    stx.st_book([block(p0, "p0"), block(p1, "p1"), block(p2, "p2"), block(p3, "p3")],
                toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
                paginate=PAGINATE)
""")


def _book(paginate: bool):
    from streamlit.testing.v1 import AppTest
    return AppTest.from_string(BOOK.replace("PAGINATE", str(paginate)), default_timeout=30)


@pytest.mark.usefixtures("reset_watch")
class TestBookSurfaces:
    def test_paginated_cache_and_seeds(self):
        from streamtex.book import _STX_CACHE_KEY, _STX_PAGE_KEY, _get_page_titles
        at = _book(True).run()
        assert not at.exception
        cache = at.session_state[_STX_CACHE_KEY]
        m = cache["markers"]
        assert [(e["label"], _roles(e)) for e in m] == [
            ("Intro", (True, True, True)),
            ("Sub", (False, True, False)),
            ("Marker 3", (True, False, False)),
            ("Marker 4", (True, False, False)),
            ("Deep", (False, False, False)),
            ("Marker 6", (True, False, False)),
            ("Annex", (False, False, True)),
            ("Side", (True, False, True)),
        ]
        assert [e["stop_index"] for e in m] == [0, None, 1, 2, None, 3, None, 4]
        # page titles: (1) first listed marker; (2) the row covering the
        # first stop of a page without listed markers; footer unnamed
        assert _get_page_titles(cache, 4) == ["1 Intro", "Sub", "Sub", "Section 4"]
        # pre-seed and post-seed copy every field
        at.session_state[_STX_PAGE_KEY] = 1
        at.run()
        live = mk.marker_entries()
        assert len(live) == len(m)
        page_fields = ("page", "page_idx", "block_idx")   # the current page renders live
        for got, want in zip(live, m):
            assert {k: v for k, v in got.items() if k not in page_fields} == \
                   {k: v for k, v in want.items() if k not in page_fields}
            if want["page_idx"] != 1:
                assert got["page"] == want["page_idx"] and got.get("key") == want.get("key")

    def test_continuous_registry_matches_paginated(self):
        from streamtex.book import _STX_CACHE_KEY
        at = _book(True).run()
        paginated = at.session_state[_STX_CACHE_KEY]["markers"]
        at2 = _book(False).run()
        assert not at2.exception
        continuous = mk.marker_entries()
        strip = ("page_idx", "block_idx", "page")
        assert [{k: v for k, v in e.items() if k not in strip} for e in continuous] == \
               [{k: v for k, v in e.items() if k not in strip} for e in paginated]


class TestBookHelpers:
    def _cache(self):
        _start()
        st_marker("Intro")                       # p0
        st_marker("Sub", stop=False)
        mk._registry._entries[-1]["page_idx"] = 0
        mk._registry._entries[0]["page_idx"] = 0
        st_marker("Only anchors", stop=False, listed=False)
        mk._registry._entries[-1]["page_idx"] = 1  # p1: markers, no stop
        st_marker(hidden=True)
        mk._registry._entries[-1]["page_idx"] = 2
        return {"markers": marker_entries(), "toc": []}

    def test_page_map_is_stop_based(self):
        cache = self._cache()
        first, last = {}, {}
        for e in cache["markers"]:
            if not mk.is_stop(e):
                continue
            first.setdefault(e["page_idx"], e["index"])
            last[e["page_idx"]] = e["index"]
        assert first == {0: 0, 2: 3} and 1 not in first

    def test_toc_dot_needs_a_stop(self):
        from streamtex.book import _toc_dot_anchors
        st_marker("A", stop=False, toc_lvl="1")
        st_marker("B", hidden=True, toc_lvl="1")
        a, b = toc_entries()
        dots = _toc_dot_anchors(marker_entries())
        assert a["key_anchor"] not in dots and b["key_anchor"] in dots

    def test_page_titles(self):
        from streamtex.book import _get_page_titles
        assert _get_page_titles(self._cache(), 4) == ["1 Intro", "Section 2", "Sub", "Section 4"]


# ---------------------------------------------------------------------------
# 11. JS: stepping, counter, popup, label (shared role code, live + export)
# ---------------------------------------------------------------------------

node = pytest.mark.skipif(not shutil.which("node"), reason="node not available")

DECK = [
    {"index": 0, "label": "Title", "anchor": "a0", "stop": True, "listed": True},
    {"index": 1, "label": "Part B", "anchor": "a1", "stop": False, "listed": True},
    {"index": 2, "label": "Marker 3", "anchor": "a2", "stop": True, "listed": False, "auto": True},
    {"index": 3, "label": "deep", "anchor": "a3", "stop": False, "listed": False},
    {"index": 4, "label": "Next", "anchor": "a4", "stop": True, "listed": True},
]


def _node(body, markers=DECK):
    prog = (f"var markers = {json.dumps(markers)};\nvar currentIdx = 0;\n"
            f"{mk._MARKER_ROLES_JS}\n{body}")
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@node
class TestRolesJs:
    def test_stepping_visits_stops_only(self):
        out = _node("var p = 0, seen = [0]; while ((p = stepTarget(p, 1)) !== null) seen.push(p);"
                    "var back = [], q = 4; while ((q = stepTarget(q, -1)) !== null) back.push(q);"
                    "console.log(JSON.stringify([seen, back]));")
        assert out == [[0, 2, 4], [2, 0]]

    def test_from_a_non_stop_position(self):
        out = _node("console.log(JSON.stringify([stepTarget(1, 1), stepTarget(1, -1),"
                    " stepTarget(3, 1), stepTarget(3, -1), stepTarget(0, 2), stepTarget(2, 5)]));")
        assert out == [2, 0, 4, 2, 4, 4]

    def test_past_the_last_stop_is_the_boundary(self):
        assert _node("console.log(JSON.stringify([stepTarget(4, 1), stepTarget(0, -1)]));") == [None, None]

    def test_counter_shows_the_stop_of_the_position(self):
        out = _node("var n = []; for (var i = 0; i < markers.length; i++) { currentIdx = i;"
                    " n.push(stopNumber()); } console.log(JSON.stringify([n, stops.length]));")
        assert out == [["1", "1", "2", "2", "3"], 3]

    def test_popup_rows_are_the_listed_markers(self):
        out = _node("var r = []; for (var v = 0; v < listedMarkers.length; v++) r.push(rowText(v));"
                    "console.log(JSON.stringify(r));")
        # "Part B" (listed, not a stop) shares the number of its slide
        assert out == ["1. Title", "1–2. Part B", "3. Next"]

    def test_label_and_active_row(self):
        out = _node("var l = [], a = []; for (var i = 0; i < markers.length; i++) { currentIdx = i;"
                    " l.push(currentLabel()); a.push(sectionVi(i)); }"
                    " console.log(JSON.stringify([l, a]));")
        assert out == [["Title", "Part B", "Part B", "deep", "Next"], [0, 1, 1, 1, 2]]

    def test_no_stop_at_all(self):
        out = _node("console.log(JSON.stringify([stopNumber(), stops.length, rowText(0),"
                    " stepTarget(0, 1)]));",
                    [{"index": 0, "label": "A", "anchor": "a", "stop": False, "listed": True}])
        assert out == ["–", 0, "A", None]

    def test_old_entries_use_hidden(self):
        out = _node("console.log(JSON.stringify([stops.length, listedMarkers.length]));",
                    [{"index": 0, "label": "A", "anchor": "a", "hidden": True},
                     {"index": 1, "label": "B", "anchor": "b", "hidden": False}])
        assert out == [2, 1]


@node
def test_deeplink_to_a_non_stop_sets_the_position():
    """_DEEPLINK_JS + the export bar: the anchor is scrolled, the counter shows its stop."""
    from streamtex.export_enrich import _DEEPLINK_JS, _marker_nav_script
    dom = textwrap.dedent("""
        var scrolled = [];
        function El(id) { this.id = id; this.style = {}; this.classList = {toggle: function(){}};
          this.children = []; }
        El.prototype.appendChild = function(c) { this.children.push(c); return c; };
        El.prototype.scrollIntoView = function() { scrolled.push(this.id); };
        El.prototype.contains = function() { return false; };
        El.prototype.querySelectorAll = function() { return []; };
        El.prototype.getBoundingClientRect = function() { return {top: 0}; };
        var els = {};
        var document = {
          body: new El('body'),
          getElementById: function(id) { return els[id] || (els[id] = new El(id)); },
          createElement: function() { return new El(''); },
          addEventListener: function() {}
        };
        var window = { location: { search: '?marker=deep', hash: '' },
                       addEventListener: function() {} };
        function URLSearchParams(q) { this.q = q; }
        URLSearchParams.prototype.get = function(k) {
          var m = new RegExp('[?&]' + k + '=([^&]*)').exec(this.q); return m ? m[1] : null; };
        function setTimeout() {}
    """)
    markers = [dict(e, key="deep") if e["label"] == "deep" else e for e in DECK]
    bar = _marker_nav_script(markers)
    deeplink = _DEEPLINK_JS.replace("__MARKERS__", json.dumps(markers)).replace("__TOC__", "[]")
    # expose the bar's counter: the last span created is the label; find the counter by class
    prog = (dom + bar.replace("var counter = document.createElement('span');",
                              "var counter = document.createElement('span'); window.__counter = counter;")
            + deeplink + "\nconsole.log(JSON.stringify([scrolled, window.__counter.textContent]));")
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    scrolled, counter = json.loads(r.stdout)
    assert scrolled[-1] == "a3"
    assert counter == "2 / 3"


def test_find_marker_follows_an_attached_heading():
    from streamtex.deeplink import find_marker
    st_marker("Atom")
    st_write("Prompt patterns", toc_lvl="1", marker="attach")
    key = toc_entries()[-1]["key_anchor"]
    assert find_marker(marker_entries(), key)["label"] == "Atom"


# ---------------------------------------------------------------------------
# 12. HTML export
# ---------------------------------------------------------------------------

def test_export_carries_roles_and_toc_entries():
    from streamtex.export_enrich import enrich_export_html
    for kwargs, _ in EIGHT:
        st_marker(**kwargs)
    html = "<html><head><style></style></head><body><p>x</p></body></html>"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out = enrich_export_html(html, toc=toc_entries(), markers=marker_entries())
    assert "var stops = markers.filter(isStop);" in out
    assert '"stop": false' in out and '"listed": false' in out
    for e in toc_entries():
        assert e["key_anchor"] in out                 # incl. the anchor-only TOC marker (#7)
    assert "__ROLES_JS__" not in out and "__MARKERS__" not in out
