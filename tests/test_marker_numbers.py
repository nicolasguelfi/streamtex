"""One number per marker — its slide number — on every surface (#117)."""

import json
import shutil
import subprocess
import textwrap

import pytest

import streamtex.marker as mk
from streamtex.deeplink import find_slide, page_url, resolve_initial_page
from streamtex.marker import annotate_marker_numbers, marker_row_text

node = pytest.mark.skipif(not shutil.which("node"), reason="node not available")


def _m(i, label, stop=True, listed=True, page=0):
    return {"index": i, "label": label, "anchor": f"a{i}", "stop": stop,
            "listed": listed, "hidden": stop and not listed, "page_idx": page}


def _0745():
    """10 stops; listed at 1, 4, 9 (the fixture of test_marker_sections)."""
    listed = {0, 3, 8}
    return [_m(i, f"L{i + 1}" if i in listed else f"Marker {i + 1}", listed=i in listed)
            for i in range(10)]


def _example_45():
    """#117 §4.5: 10 stops, listed at 1, 4, 9 and a listed non-stop inside slide 6."""
    out = []
    for n in range(1, 11):
        out.append(_m(len(out), {1: "Intro", 4: "Section B", 9: "Section C"}.get(n, f"Marker {n}"),
                      listed=n in (1, 4, 9)))
        if n == 6:
            out.append(_m(len(out), "Part B2", stop=False))
    return out


def _rows(entries):
    return [marker_row_text(e) for e in entries if e["listed"]]


# ---------------------------------------------------------------------------
# annotate_marker_numbers
# ---------------------------------------------------------------------------

class TestAnnotate:
    def test_0745_example(self):
        e = annotate_marker_numbers(_0745())
        assert [x["number"] for x in e] == list(range(1, 11))
        assert _rows(e) == ["1–3. L1", "4–8. L4", "9–10. L9"]

    def test_row_zero_starts_at_its_own_number(self):
        e = annotate_marker_numbers([_m(0, "Marker 1", listed=False), _m(1, "Only")])
        assert e[1]["row_text"] == "2"

    def test_example_45(self):
        e = annotate_marker_numbers(_example_45())
        assert [(x["label"], x["number"]) for x in e if x["listed"]] == [
            ("Intro", 1), ("Section B", 4), ("Part B2", 6), ("Section C", 9)]
        assert _rows(e) == ["1–3. Intro", "4–6. Section B", "6–8. Part B2", "9–10. Section C"]
        assert [x["row_end"] for x in e if x["listed"]] == [3, 6, 8, 10]

    def test_non_stop_before_first_stop_is_one(self):
        e = annotate_marker_numbers([_m(0, "Pre", stop=False), _m(1, "First")])
        assert [x["number"] for x in e] == [1, 1]

    def test_module_without_stops(self):
        e = annotate_marker_numbers([_m(0, "A", stop=False), _m(1, "B", stop=False)])
        assert [x["number"] for x in e] == [None, None]
        assert _rows(e) == ["A", "B"]

    def test_two_listed_markers_in_one_slide(self):
        e = [_m(i, f"Marker {i + 1}", listed=False) for i in range(4)]
        e.append(_m(4, "Five"))                       # stop 5
        e.append(_m(5, "Five bis", stop=False))       # inside slide 5
        e += [_m(6, "Marker 6", listed=False), _m(7, "Marker 7", listed=False), _m(8, "Eight")]
        annotate_marker_numbers(e)
        assert [x["row_text"] for x in e if x["listed"]] == ["5", "5–7", "8"]

    def test_old_cache_entries(self):
        old = [{"index": 0, "label": "a", "anchor": "a", "hidden": True},
               {"index": 1, "label": "b", "anchor": "b", "hidden": False}]
        annotate_marker_numbers(mk.normalize_marker_entries(old))
        assert [x["number"] for x in old] == [1, 2] and old[1]["row_text"] == "2"

    def test_idempotent(self):
        e = annotate_marker_numbers(_example_45())
        before = json.dumps(e)
        assert json.dumps(annotate_marker_numbers(e)) == before


# ---------------------------------------------------------------------------
# Page titles and footer first paint
# ---------------------------------------------------------------------------

class TestBookNumbers:
    def test_page_titles(self):
        from streamtex.book import _get_page_titles
        e = _example_45()
        for x in e:                       # pages: slides 1-3, 4-5, 6-8 (+ Part B2), 9-10
            n = x["index"]
            x["page_idx"] = 0 if n < 3 else 1 if n < 5 else 2 if n < 9 else 3
        e[5]["listed"] = False           # page 2 opens on an unlisted stop (slide 6)
        annotate_marker_numbers(e)
        titles = _get_page_titles({"markers": e}, 5)
        assert titles[:4] == ["1 Intro", "4 Section B", "6 Part B2", "9 Section C"]
        e[6]["listed"] = False           # no listed marker on page 2 any more
        annotate_marker_numbers(e)
        assert _get_page_titles({"markers": e}, 5)[2] == "Section B"   # rule 2: no number
        assert _get_page_titles({"markers": e}, 5)[4] == "Section 5"   # footer page: unnamed

    def test_footer_first_slide(self):
        from streamtex.book import _footer_first_slide
        e = _example_45()
        for x in e:
            x["page_idx"] = 0 if x["index"] < 3 else 2
        annotate_marker_numbers(e)
        assert _footer_first_slide(e, 0, None) == 1
        assert _footer_first_slide(e, 2, None) == 4          # the page's first stop
        assert _footer_first_slide(e, 1, None) == 3          # no marker: the last stop before
        assert _footer_first_slide(e, 2, 6) == 6             # deep link to "Part B2" (index 6)
        assert _footer_first_slide([], 3, None) == 1


# ---------------------------------------------------------------------------
# Deep link by slide number
# ---------------------------------------------------------------------------

class TestSlideDeepLink:
    def _markers(self):
        e = _example_45()
        for x in e:
            x["page_idx"] = x["index"] // 4
        return e

    def test_find_slide_skips_non_stops(self):
        e = self._markers()
        assert find_slide(e, 7)["index"] == 7            # Part B2 (index 6) is not a stop
        assert find_slide(e, 0) is None and find_slide(e, 11) is None

    def test_resolve(self):
        e = self._markers()
        assert resolve_initial_page({"slide": "4"}, e, 3) == (0, 3)
        assert resolve_initial_page({"slide": "9"}, e, 3) == (2, 9)

    def test_precedence_marker_slide_page(self):
        e = self._markers()
        e[1]["key"] = "two"
        assert resolve_initial_page({"marker": "two", "slide": "9", "page": "3"}, e, 3) == (0, 1)
        assert resolve_initial_page({"slide": "9", "page": "1"}, e, 3) == (2, 9)

    @pytest.mark.parametrize("bad", ["0", "11", "abc", "-1", "2.5"])
    def test_invalid_values_fall_through(self, bad):
        assert resolve_initial_page({"slide": bad, "page": "2"}, self._markers(), 3) == (1, None)

    def test_page_url(self):
        assert page_url("https://x/w?lang=fr", slide=4) == "https://x/w?lang=fr&slide=4"
        assert page_url("https://x/w?slide=2", page=3) == "https://x/w?page=3"
        assert page_url("https://x/w", marker="m", slide=4) == "https://x/w?marker=m"
        assert page_url("https://x/w", slide=4, page=2) == "https://x/w?slide=4"
        with pytest.raises(ValueError):
            page_url("https://x/w", slide=0)


# ---------------------------------------------------------------------------
# JS: counter, input, popup rows, footer sync; export deep link
# ---------------------------------------------------------------------------

def _node(markers, body):
    prog = (f"var markers = {json.dumps(markers)};\nvar currentIdx = 0;\n"
            f"{mk._MARKER_ROLES_JS}\n{body}")
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@node
class TestJs:
    def test_counter_for_every_position(self):
        e = annotate_marker_numbers(_example_45())
        out = _node(e, "var c = []; for (var i = 0; i < markers.length; i++) { currentIdx = i;"
                       " c.push(stopNumber() + ' / ' + stops.length); } console.log(JSON.stringify(c));")
        assert out[6] == "6 / 10"                 # the non-stop "Part B2"
        assert out == [f"{n} / 10" for n in (1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10)]

    def test_popup_rows_read_python(self):
        e = annotate_marker_numbers(_example_45())
        out = _node(e, "var r = []; for (var v = 0; v < listedMarkers.length; v++) r.push(rowText(v));"
                       " console.log(JSON.stringify(r));")
        assert out == _rows(e)

    def test_no_range_code_left_in_js(self):
        from streamtex.export_enrich import _MARKER_NAV_JS
        assert "rowRange" not in mk._MARKER_ROLES_JS and "rowRange" not in _MARKER_NAV_JS

    def test_live_widget_input_and_footer(self):
        from unittest.mock import patch
        mk.reset_marker_registry(mk.MarkerConfig())
        mk._registry.reset()
        mk.register_marker("A", "a0")
        with patch("streamtex.marker.st.iframe") as frame:
            mk.inject_marker_navigation()
        js = frame.call_args[0][0]
        assert "counterInput.max = String(stops.length);" in js
        assert "navigateTo(stops[n - 1].index);" in js
        assert "'Slide ' + stopNumber() + ' / ' + stops.length" in js
        assert '"number": 1' in js and '"row_text": "1"' in js
        mk._registry = None


@node
def test_export_deeplink_by_slide():
    from streamtex.export_enrich import _DEEPLINK_JS
    e = annotate_marker_numbers(_example_45())
    dom = textwrap.dedent("""
        var scrolled = [];
        var document = { addEventListener: function() {}, getElementById: function(id) {
          return { scrollIntoView: function() { scrolled.push(id); },
                   getBoundingClientRect: function() { return { top: 0 }; } }; } };
        var window = { location: { search: '?slide=7', hash: '' }, addEventListener: function() {},
                       __stxMarkerNavigateTo: function(i) { scrolled.push('idx' + i); } };
        function URLSearchParams(q) { this.q = q; }
        URLSearchParams.prototype.get = function(k) {
          var m = new RegExp('[?&]' + k + '=([^&]*)').exec(this.q); return m ? m[1] : null; };
    """)
    js = dom + _DEEPLINK_JS.replace("__MARKERS__", json.dumps(e)).replace("__TOC__", "[]").replace("__PAGE_NAV__", "null") \
        + "\nconsole.log(JSON.stringify(scrolled));"
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)[:2] == ["a7", "idx7"]       # slide 7 = index 7 (Part B2 skipped)


def test_export_carries_numbers():
    from streamtex.export_enrich import enrich_export_html
    e = annotate_marker_numbers(_example_45())
    out = enrich_export_html("<html><head><style></style></head><body></body></html>", markers=e)
    assert '"row_text": "6–8"' in out and '"number": 6' in out
    assert "__" + "MARKERS__" not in out


# ---------------------------------------------------------------------------
# The same numbers in paginated and continuous mode (AppTest)
# ---------------------------------------------------------------------------

BOOK = textwrap.dedent("""
    import types
    import streamtex as stx

    def block(fn, name):
        m = types.ModuleType(name)
        m.build = fn
        return m

    def p0():
        stx.st_marker(hidden=True)
        stx.st_marker("Intro")
        stx.st_slide_break()
    def p1():
        stx.st_marker("Part", stop=False)
        stx.st_marker("Body")
        stx.st_slide_break()

    stx.st_book([block(p0, "p0"), block(p1, "p1")], toc_config=stx.TOCConfig(),
                marker_config=stx.MarkerConfig(), paginate=PAGINATE)
""")


@pytest.mark.usefixtures("reset_watch")
def test_same_numbers_in_both_modes():
    from streamlit.testing.v1 import AppTest

    from streamtex.book import _STX_CACHE_KEY
    at = AppTest.from_string(BOOK.replace("PAGINATE", "True"), default_timeout=30).run()
    assert not at.exception
    paginated = _rows(at.session_state[_STX_CACHE_KEY]["markers"])
    at2 = AppTest.from_string(BOOK.replace("PAGINATE", "False"), default_timeout=30).run()
    assert not at2.exception
    continuous = _rows(mk.marker_entries())
    assert paginated == continuous == ["2–3. Intro", "3. Part", "4–5. Body"]
