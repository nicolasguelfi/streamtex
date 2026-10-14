"""Nav widget: section label of unlisted markers and popup ranges (#97, #116).

The role code shared by the live widget (marker.py) and the HTML export
nav (export_enrich.py) is run with node."""

import json
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


def _run(markers, body: str):
    """Run *body* with node after the shared role code (#116), numbers from Python (#117)."""
    markers = mk.annotate_marker_numbers([dict(m) for m in markers])
    prog = (f"var markers = {json.dumps(markers)};\nvar currentIdx = 0;\n"
            f"{mk._MARKER_ROLES_JS}\n{body}")
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _source(which: str) -> str:
    if which == "export":
        from streamtex.export_enrich import _marker_nav_script
        return _marker_nav_script([{"index": 0, "label": "A", "anchor": "a0"}])
    from unittest.mock import patch
    mk.reset_marker_registry(mk.MarkerConfig())
    mk._registry.reset()
    mk.register_marker("A", "a0")
    with patch("streamtex.marker.st.iframe") as frame:
        mk.inject_marker_navigation()
    return frame.call_args[0][0]


@pytest.mark.parametrize("which", ["live", "export"])
def test_labels_and_ranges(which):
    # both widgets run the one role code
    assert mk._MARKER_ROLES_JS in _source(which)
    body = ("var labels = []; for (var i = 0; i < markers.length; i++) "
            "{ currentIdx = i; labels.push(currentLabel()); }\n"
            "var ranges = []; for (var v = 0; v < listedMarkers.length; v++) ranges.push(rowText(v));\n"
            "var active = []; for (var i = 0; i < markers.length; i++) active.push(sectionVi(i));\n"
            "console.log(JSON.stringify({labels: labels, ranges: ranges, active: active}));")
    out = _run(_deck(), body)
    assert out["labels"] == ["Intro", "Intro", "Intro", "Section B", "Section B", "Section B",
                             "Section B", "Section B", "Section C", "Section C"]
    assert out["ranges"] == ["1–3. Intro", "4–8. Section B", "9–10. Section C"]
    assert out["active"] == [0, 0, 0, 1, 1, 1, 1, 1, 2, 2]


def test_hidden_stops_before_first_title_take_the_first_title():
    """#97 label rule kept; row 0 starts at its own number (#117, author decision)."""
    deck = [{"index": 0, "label": "Marker 1", "anchor": "a0", "hidden": True, "auto": True},
            {"index": 1, "label": "Only", "anchor": "a1", "hidden": False}]
    out = _run(deck, "currentIdx = 0; console.log(JSON.stringify([currentLabel(), rowText(0),"
                     " sectionVi(0)]));")
    assert out == ["Only", "2. Only", 0]


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
