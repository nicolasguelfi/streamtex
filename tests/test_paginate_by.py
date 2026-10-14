"""st_book(paginate_by=…): pages that follow the composition tree (#121)."""

import logging
import sys
import textwrap
import types

import pytest

import streamtex.book as bm
import streamtex.marker as mk
from streamtex import pagewalk
from streamtex.pagewalk import normalize_paginate_by, page_starts

pytestmark = pytest.mark.usefixtures("reset_watch")

#: A tree of the lab's shape: three top-level lists, nesting to depth 3,
#: a section heading in a list, #118 breaks between items.
TREE = textwrap.dedent("""
    import sys, types
    import streamtex as stx
    REC = sys.modules.setdefault("_t121rec", types.ModuleType("_t121rec"))
    REC.calls = []
    def leaf(name):
        m = types.ModuleType(name)
        def build(**k):
            REC.calls.append(name)
            stx.st_marker(name)
            stx.st_write("text-" + name)
        m.build = build
        return m
    def lst(name, items, heading=None, trailer=None, page=None):
        m = types.ModuleType(name)
        def build(**k):
            if heading:
                stx.st_write(heading, toc_lvl="1")
            stx.st_sequence(items, **k)
            if trailer:
                stx.st_write(trailer, toc_lvl="2")
        m.build = build
        return m
    opening = lst("opening", [leaf("a1"), leaf("a2")])
    showcase = lst("showcase", [lst("L1", [leaf(f"s1{i}") for i in range(4)]),
                                lst("L2", [leaf(f"s2{i}") for i in range(3)]),
                                leaf("a3")], heading="Showcase", trailer="After")
    llm = lst("llm", [lst("L3", [leaf(f"l3{i}") for i in range(2)]),
                      lst("L4", [leaf(f"l4{i}") for i in range(3)]),
                      lst("L5", [leaf("l50"), leaf("l51"),
                                 lst("L6", [leaf(f"l6{i}") for i in range(3)])]),
                      leaf("a4")])
    stx.st_book([opening, showcase, llm], toc_config=stx.TOCConfig(),
                marker_config=stx.MarkerConfig(), paginate=PAGINATE, paginate_by=MODE)
""")


def _app(mode, paginate=True):
    from streamlit.testing.v1 import AppTest
    return AppTest.from_string(TREE.replace("MODE", repr(mode)).replace("PAGINATE", str(paginate)),
                               default_timeout=60)


def _rec():
    return sys.modules["_t121rec"].calls


def _cache(at):
    return at.session_state[bm._STX_CACHE_KEY]


@pytest.fixture(autouse=True)
def _reset_mode():
    yield
    pagewalk.set_paginate_by("entry")


class TestValues:
    @pytest.mark.parametrize("value,expected", [("entry", "entry"), (0, "entry"), ("leaf", "leaf"),
                                                (2, 2), ("depth:2", 2), (1, 1)])
    def test_normalize(self, value, expected):
        assert normalize_paginate_by(value) == expected

    @pytest.mark.parametrize("bad", ["atom", -1, "depth:x", True, 2.5, None])
    def test_invalid(self, bad):
        with pytest.raises(ValueError, match="paginate_by must be"):
            normalize_paginate_by(bad)

    def test_st_book_refuses_a_wrong_value(self):
        at = _app("atom").run()
        assert at.exception and "paginate_by must be" in at.exception[0].value

    def test_book_defaults_key(self):
        assert "paginate_by" in bm.BOOK_DEFAULT_KEYS


class TestPageStarts:
    def _nodes(self):
        # root -> [leaf, list(leaf, list(leaf))]
        return {(): {"depth": 0}, (0,): {"depth": 1, "children": 0},
                (1,): {"depth": 1, "children": 2}, (1, 0): {"depth": 2, "children": 0},
                (1, 1): {"depth": 2, "children": 1}, (1, 1, 0): {"depth": 3, "children": 0}}

    def test_leaf_and_depths(self):
        n = self._nodes()
        assert page_starts(n, "leaf") == [(0,), (1, 0), (1, 1, 0)]
        assert page_starts(n, 1) == [(0,), (1,)]
        assert page_starts(n, 2) == [(0,), (1, 0), (1, 1)]

    def test_overrides(self):
        n = self._nodes()
        n[(1,)]["page"] = True
        assert page_starts(n, "leaf") == [(0,), (1,)]
        n[(1,)]["page"] = False
        assert page_starts(n, "leaf") == [(0,)]


class TestPageMap:
    @pytest.mark.parametrize("mode,pages", [("entry", 3), (1, 9), (2, 19), ("leaf", 21), ("depth:2", 19)])
    def test_page_counts(self, mode, pages):
        at = _app(mode).run()
        assert not at.exception
        c = _cache(at)
        assert c["total"] == pages and c["entries"] == 3
        assert c["paginate_by"] == normalize_paginate_by(mode)

    def test_markers_and_toc_identical_for_every_mode(self):
        def strip(c):
            return ([{k: e[k] for k in ("index", "label", "anchor", "stop", "listed", "number")}
                     for e in c["markers"]],
                    [{k: e[k] for k in ("title", "level", "key_anchor")} for e in c["toc"]])
        ref = strip(_cache(_app("entry").run()))
        for mode in (1, 2, "leaf"):
            assert strip(_cache(_app(mode).run())) == ref, mode

    def test_leaf_pages_follow_the_flattened_order(self):
        c = _cache(_app("leaf").run())
        first = {}
        for e in c["markers"]:
            first.setdefault(e["page_idx"], e["label"])
        assert [first[i] for i in range(21)] == (
            ["a1", "a2"] + [f"s1{i}" for i in range(4)] + [f"s2{i}" for i in range(3)] + ["a3"]
            + ["l30", "l31", "l40", "l41", "l42", "l50", "l51", "l60", "l61", "l62", "a4"])

    def test_section_heading_and_trailer_tagging(self):
        c = _cache(_app("leaf").run())
        toc = {t["title"].split(" ", 1)[-1]: t["page_idx"] for t in c["toc"]}
        page_of = {e["label"]: e["page_idx"] for e in c["markers"]}
        assert toc["Showcase"] == page_of["s10"]           # leading region: the first item's page
        assert toc["After"] == page_of["a3"]               # trailing region: the entry's last page

    def test_hash_depends_on_the_mode(self):
        hashes = {_cache(_app(m).run())["hash"] for m in ("entry", "leaf")}
        assert len(hashes) == 2


class TestLivePage:
    def _page_of(self, c, label):
        return next(e["page_idx"] for e in c["markers"] if e["label"] == label)

    def test_only_the_target_leaf_runs(self, mock_streamlit):
        at = _app("leaf").run()
        c = _cache(at)
        k = self._page_of(c, "s21")
        _rec().clear()
        mock_streamlit["html"].reset_mock()
        at.session_state[bm._STX_PAGE_KEY] = k
        at.run()
        assert not at.exception
        assert _rec() == ["s21"]
        html = " ".join(str(call.args[0]) for call in mock_streamlit["html"].call_args_list if call.args)
        assert "text-s21" in html and "text-s20" not in html and "text-s22" not in html
        assert '<hr class="stx-slide-break-rule"' not in html   # no rule at the head of the page (s1)

    def test_live_registry_matches_the_cache(self):
        at = _app("leaf").run()
        c = _cache(at)
        for label in ("a1", "s10", "l62", "a4"):
            at.session_state[bm._STX_PAGE_KEY] = self._page_of(c, label)
            at.run()
            assert not at.exception
            live = [(e["index"], e["label"], e["anchor"]) for e in mk.marker_entries()]
            assert live == [(e["index"], e["label"], e["anchor"]) for e in c["markers"]], label

    def test_entry_mode_still_draws_its_breaks(self, mock_streamlit):
        at = _app("entry").run()
        mock_streamlit["html"].reset_mock()
        at.session_state[bm._STX_PAGE_KEY] = 1
        at.run()
        html = " ".join(str(call.args[0]) for call in mock_streamlit["html"].call_args_list if call.args)
        assert '<hr class="stx-slide-break-rule"' in html and "text-s10" in html and "text-a3" in html

    def test_the_section_heading_shows_on_the_first_item_page(self, mock_streamlit):
        at = _app("leaf").run()
        c = _cache(at)
        mock_streamlit["html"].reset_mock()
        at.session_state[bm._STX_PAGE_KEY] = self._page_of(c, "s10")
        at.run()
        html = " ".join(str(call.args[0]) for call in mock_streamlit["html"].call_args_list if call.args)
        assert "Showcase" in html and "text-s10" in html


class TestTitles:
    def test_continuation_pages_are_named(self):
        titles = ["1 A", "Section 2", "3 C", "Section 4"]
        pages = [{"entry": 0}, {"entry": 0}, {"entry": 1}, {"entry": 2}]
        named = bm._page_named({}, titles, pages, True)
        assert named == [True, True, True, False] and titles[1] == "1 A"

    def test_entry_mode_rule_is_unchanged(self):
        titles = ["1 A", "Section 2"]
        assert bm._page_named({}, titles, [{"entry": 0}, {"entry": 1}], False) == [True, False]


def test_continuous_view_ignores_paginate_by():
    def labels(mode):
        at = _app(mode, paginate=False).run()
        assert not at.exception
        return [(e["label"], e["anchor"]) for e in mk.marker_entries()]
    assert labels("leaf") == labels("entry")


def test_page_deep_link_counts_pages():
    from streamtex.deeplink import resolve_initial_page
    markers = [{"index": 0, "label": "x", "anchor": "a", "page_idx": 4}]
    assert resolve_initial_page({"page": "5"}, markers, 21) == (4, None)
    assert resolve_initial_page({"page": "22"}, markers, 21) == (0, None)


def test_gate_falls_back_to_the_whole_entry(caplog):
    """A page the live render does not meet: the whole entry is shown, with a warning."""
    import streamtex as stx
    entry = types.ModuleType("entry")
    entry.build = lambda **k: stx.st_write("whole")
    with caplog.at_level(logging.WARNING, logger="streamtex.book"):
        from unittest.mock import patch
        with patch.object(bm, "st_include", wraps=bm.st_include) as inc:
            bm._render_page(entry, {"entry": 0, "start": [3]}, [{"entry": 0, "start": [3]}], (), {}, None)
    assert inc.call_count == 2
    assert "not met in the live render" in caplog.text


def test_diagnostic_for_a_page_without_stop(caplog):
    script = textwrap.dedent("""
        import types
        import streamtex as stx
        def leaf(name, **roles):
            m = types.ModuleType(name)
            m.build = lambda **k: stx.st_marker(name, **roles)
            return m
        top = types.ModuleType("top")
        top.build = lambda **k: stx.st_sequence([leaf("a"), leaf("q", stop=False)], **k)
        stx.st_book([top], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
                    paginate=True, paginate_by="leaf")
    """)
    from streamlit.testing.v1 import AppTest
    with caplog.at_level(logging.WARNING, logger="streamtex.book"):
        at = AppTest.from_string(script, default_timeout=60).run()
    assert not at.exception
    assert "Arrows will not stop on page 2" in caplog.text
