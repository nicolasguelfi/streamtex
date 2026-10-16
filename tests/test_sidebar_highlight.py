"""The sidebar entry in cyan follows the floating bar's slide (#130).

The live check (a real browser presses the arrows) is
``tests/e2e/test_nav_sidebar_highlight.py``.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest

import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex.book import _toc_nav_table
from streamtex.marker import MarkerConfig, marker_entries, reset_marker_registry, st_marker
from streamtex.toc import TOCConfig, reset_toc_registry, toc_entries
from streamtex.write import st_write

from .test_sidebar_targets import _deck, _on_page, _sidebar_html


@pytest.fixture(autouse=True)
def registries():
    toc_mod.toc = None
    mk._registry = None
    reset_toc_registry(TOCConfig())
    reset_marker_registry(MarkerConfig())
    with patch("streamtex.marker._render"), patch("streamtex.write._render"), \
         patch("streamtex.write.consume_block_top_injected", return_value=True):
        yield
    mk._registry = None
    toc_mod.toc = None


def _titles(cache, table):
    """Stop index -> heading title, without its number (« 2.1 Detail » -> « Detail »)."""
    return {stop: cache["toc"][pos]["title"].split(" ", 1)[-1] for stop, pos in table.items()}


# ---------------------------------------------------------------------------
# The Contents table
# ---------------------------------------------------------------------------

def test_each_slide_names_the_heading_in_force():
    cache = _deck()     # page 0: s1 « Intro » | page 1: « Top » s2 s3 s4 « Detail » s5
    table = _toc_nav_table(cache["toc"], cache["markers"], 2)
    assert _titles(cache, table) == {0: "Intro", 1: "Top", 2: "Top", 3: "Detail", 4: "Detail"}


def test_the_first_heading_of_a_slide_wins():
    st_marker("s1")
    st_write("Title", toc_lvl="1")
    st_write("Sub", toc_lvl="2")
    st_marker("s2")
    _on_page(0, 2, 2)
    table = _toc_nav_table(toc_entries(), marker_entries(), 2)
    assert _titles({"toc": toc_entries()}, table) == {0: "Title", 1: "Title"}


def test_a_heading_above_the_sidebar_level_is_skipped():
    cache = _deck()
    table = _toc_nav_table(cache["toc"], cache["markers"], 1)          # « Detail » is level 2
    assert _titles(cache, table) == {0: "Intro", 1: "Top", 2: "Top", 3: "Top", 4: "Top"}


def test_slides_before_any_heading_have_no_entry():
    st_marker("s1")
    st_marker("s2")
    st_write("Late", toc_lvl="1")
    _on_page(0, 2, 1)
    table = _toc_nav_table(toc_entries(), marker_entries(), 2)
    assert table == {1: 0}


def test_a_non_stop_marker_belongs_to_its_slide():
    st_marker("s1")
    st_marker("aside", stop=False)
    st_write("Aside", toc_lvl="1")
    st_marker("s2")
    _on_page(0, 3, 1)
    table = _toc_nav_table(toc_entries(), marker_entries(), 2)
    assert table == {0: 0, 2: 0}          # « Aside » sits in slide s1


# ---------------------------------------------------------------------------
# The sidebar: one data-stx-nav per entry, no colour from the server
# ---------------------------------------------------------------------------

def test_sidebar_entries_carry_their_nav_key():
    html = _sidebar_html(_deck(), 1)
    assert re.findall(r'data-stx-nav="(mk\d+|toc\d+)"', html) == [
        "toc0", "toc1", "toc2", "mk0", "mk1", "mk2", "mk3", "mk4"]


def test_the_server_no_longer_colours_the_first_entry_of_the_page():
    assert "stx-link-active-color" not in _sidebar_html(_deck(), 1)


# ---------------------------------------------------------------------------
# The bar: one style rule per move
# ---------------------------------------------------------------------------

def _bar_js(nav_toc):
    mk._registry.reset()
    for i, label in enumerate(("s1", "s2", "s3")):
        mk.register_marker(label, f"a{i}")
    with patch("streamtex.marker.st.iframe") as frame:
        mk.inject_marker_navigation(nav_toc=nav_toc)
    return frame.call_args[0][0]


def test_the_bar_receives_the_table():
    js = _bar_js({0: 0, 1: 0, 2: 3})
    assert 'var navToc = {"0": 0, "1": 0, "2": 3};' in js
    assert "syncSidebar();" in js


def test_continuous_books_send_no_table():
    assert "var navToc = null;" in _bar_js(None)


node = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")


@node
def test_the_rule_names_the_rows_of_each_position():
    js = _bar_js({0: 0, 1: 0, 2: 3})
    sync = re.search(r"function syncSidebar\(\) \{.*?\n    \}\n", js, re.S).group(0)
    entries = json.loads(re.search(r"var markers = (\[.*?\]);\n", js).group(1))
    prog = f"""
var markers = {json.dumps(entries)};
var currentIdx = 0;
{mk._MARKER_ROLES_JS}
var navToc = {{"0": 0, "1": 0, "2": 3}};
var styles = {{}};
var hostDoc = {{
  head: {{ appendChild: function (el) {{ styles[el.id] = el; }} }},
  getElementById: function (id) {{ return styles[id] || null; }},
  createElement: function () {{ return {{}}; }}
}};
{sync}
var out = [];
for (var i = 0; i < markers.length; i++) {{ currentIdx = i; syncSidebar(); out.push(styles['stx-sidebar-active-style'].textContent); }}
console.log(JSON.stringify(out));
"""
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rule = ' {{ color: var(--stx-link-active-color) !important; }}'
    assert json.loads(r.stdout) == [
        '[data-stx-nav="mk0"] a, [data-stx-nav="toc0"] a' + rule.format(),
        '[data-stx-nav="mk1"] a, [data-stx-nav="toc0"] a' + rule.format(),
        '[data-stx-nav="mk2"] a, [data-stx-nav="toc3"] a' + rule.format(),
    ]
