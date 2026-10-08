"""Nav widget: section label of hidden markers and popup ranges (#97).

The functions are run with node, extracted from the live widget
(marker.py) and from the HTML export nav (export_enrich.py)."""

import json
import re
import shutil
import subprocess

import pytest

from streamtex import marker as mk

pytestmark = pytest.mark.skipif(not shutil.which("node"), reason="node not available")


def _deck():
    """Visible markers at 1, 4, 9 (global numbers), hidden auto stops between,
    one hidden marker with its own label (7) and hidden stops before the first title."""
    m = []
    def add(label, hidden, auto=False):
        e = {"index": len(m), "label": label, "anchor": f"a{len(m)}", "hidden": hidden}
        if auto:
            e["auto"] = True
        m.append(e)
    add("Intro", False)                    # 1
    add("Marker 2", True, auto=True)       # 2
    add("Marker 3", True, auto=True)       # 3
    add("Section B", False)                # 4
    for n in (5, 6):
        add(f"Marker {n}", True, auto=True)
    add("Named hidden", True)              # 7: hidden, own label
    add("Marker 8", True, auto=True)       # 8
    add("Section C", False)                # 9
    add("Marker 10", True, auto=True)      # 10
    return m


def _functions(js: str, names, visible_var: str) -> str:
    out = []
    for n in names:
        # from "function name(" to the closing brace at the same indentation
        mt = re.search(r"^([ \t]*)function " + n + r"\(.*?\n\1\}\n", js, re.S | re.M)
        assert mt, n
        out.append(mt.group(0))
    return "\n".join(out).replace("\\\\u2013", "\\u2013")


def _run(js_funcs: str, visible_var: str, markers, body: str):
    prog = (f"var markers = {json.dumps(markers)};\n"
            f"var {visible_var} = markers.filter(function(m) {{ return !m.hidden; }});\n"
            f"var currentIdx = 0;\n{js_funcs}\n{body}")
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _source_of_widget():
    import inspect
    src = inspect.getsource(mk)
    start = src.index("var visibleMarkers = markers.filter")
    return src[start:]


@pytest.mark.parametrize("which", ["live", "export"])
def test_labels_and_ranges(which):
    if which == "live":
        js, vis = _source_of_widget(), "visibleMarkers"
    else:
        from streamtex.export_enrich import _MARKER_NAV_JS as js
        vis = "visible"
    funcs = _functions(js, ["sectionVi", "rowRange", "currentLabel"], vis)
    body = (f"var labels = []; for (var i = 0; i < markers.length; i++) "
            f"{{ currentIdx = i; labels.push(currentLabel()); }}\n"
            f"var ranges = []; for (var v = 0; v < {vis}.length; v++) ranges.push(rowRange(v));\n"
            f"var active = []; for (var i = 0; i < markers.length; i++) active.push(sectionVi(i));\n"
            f"console.log(JSON.stringify({{labels: labels, ranges: ranges, active: active}}));")
    out = _run(funcs, vis, _deck(), body)
    assert out["labels"] == ["Intro", "Intro", "Intro", "Section B", "Section B", "Section B",
                             "Named hidden", "Section B", "Section C", "Section C"]
    assert out["ranges"] == ["1–3", "4–8", "9–10"]
    assert out["active"] == [0, 0, 0, 1, 1, 1, 1, 1, 2, 2]


def test_hidden_stops_before_first_title_take_the_first_title():
    from streamtex.export_enrich import _MARKER_NAV_JS as js
    funcs = _functions(js, ["sectionVi", "rowRange", "currentLabel"], "visible")
    deck = [{"index": 0, "label": "Marker 1", "anchor": "a0", "hidden": True, "auto": True},
            {"index": 1, "label": "Only", "anchor": "a1", "hidden": False}]
    out = _run(funcs, "visible", deck,
               "currentIdx = 0; console.log(JSON.stringify([currentLabel(), rowRange(0)]));")
    assert out == ["Only", "1–2"]


def test_registry_flags_generated_labels_only():
    mk.reset_marker_registry(mk.MarkerConfig())
    mk._registry.reset()
    from unittest.mock import patch

    import streamlit  # noqa: F401  (st_marker renders through st.html)
    with patch("streamtex.marker.st"), patch("streamtex.marker._render", create=True):
        mk.st_marker("Named", hidden=True)
        mk.st_marker(hidden=True)
    e = mk.marker_entries()
    assert e[0]["label"] == "Named" and "auto" not in e[0]
    assert e[1]["label"] == "Marker 2" and e[1]["auto"] is True
