"""Where each slide is written, copied from the browser in one gesture (#157)."""
import json
import os
import re
import subprocess
import sys
import textwrap
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from streamtex import source as src
from streamtex.source import (
    PUBLISHED_FILE,
    SourceConfig,
    annotate_sources,
    begin_book,
    combo_text,
    document_name,
    page_payload,
    parse_combo,
    without_sources,
)


@pytest.fixture(autouse=True)
def _fresh_book(tmp_path):
    begin_book(None, str(tmp_path), environ={})
    yield
    begin_book(None, str(tmp_path), environ={})


# -- settings ------------------------------------------------------------------------------

def test_both_sides_are_off_by_default(tmp_path):
    cfg = begin_book(None, str(tmp_path), environ={})
    assert (cfg.live, cfg.html) == ("off", "off")
    assert page_payload("live") is None and page_payload("html") is None


@pytest.mark.parametrize("live, html", [("on", "on"), ("on", "off"), ("off", "on"), ("off", "off")])
def test_the_two_sides_are_independent(tmp_path, live, html):
    begin_book({"live": live, "html": html}, str(tmp_path), environ={})
    assert (page_payload("live") is not None) == (live == "on")
    assert (page_payload("html") is not None) == (html == "on")


def test_the_environment_overrides_the_book(tmp_path):
    cfg = begin_book({"live": "on", "html": "on", "copy_key": "ctrl+alt+meta+l"}, str(tmp_path),
                     environ={"STX_SOURCE_HTML": "off", "STX_SOURCE_COPY_KEY": "ctrl+shift+k",
                              "STX_SOURCE_EDITOR": "vscode://file/{abs}:{line}"})
    assert (cfg.live, cfg.html, cfg.copy_key, cfg.editor) == ("on", "off", "ctrl+shift+k",
                                                               "vscode://file/{abs}:{line}")


def test_a_source_config_true_and_hidden_are_accepted(tmp_path):
    assert begin_book(SourceConfig(live="on"), str(tmp_path), environ={}).live == "on"
    assert begin_book(True, str(tmp_path), environ={}).html == "on"
    assert begin_book({"live": "hidden", "html": False}, str(tmp_path), environ={}).live == "on"


@pytest.mark.parametrize("bad", [{"live": "maybe"}, {"colour": "red"}, {"copy_key": "ctrl+alt"},
                                 {"copy_click": "x"}, 42])
def test_bad_settings_are_refused(tmp_path, bad):
    with pytest.raises((ValueError, TypeError), match="source"):
        begin_book(bad, str(tmp_path), environ={})


def test_a_published_site_carries_nothing_unless_its_target_says_so(tmp_path):
    (tmp_path / PUBLISHED_FILE).write_text(json.dumps({"release": "abc123", "source": {"live": "off", "html": "off"}}))
    book = tmp_path / "trainings" / "X" / "slides"
    book.mkdir(parents=True)
    assert begin_book({"live": "on", "html": "on"}, str(book), environ={}).live == "off"
    (tmp_path / PUBLISHED_FILE).write_text(json.dumps({"release": "abc123", "source": {"live": "on"}}))
    cfg = begin_book(None, str(book), environ={})
    assert (cfg.live, cfg.html) == ("on", "off")
    assert page_payload("live")["release"] == "abc123"
    assert page_payload("live")["root"] == "" and page_payload("live")["editor"] == ""   # no editor online
    # the environment still wins (stx release publish --html-env STX_SOURCE_HTML=on)
    assert begin_book(None, str(book), environ={"STX_SOURCE_HTML": "on"}).html == "on"


def test_a_record_without_source_turns_both_sides_off(tmp_path):
    (tmp_path / PUBLISHED_FILE).write_text(json.dumps({"release": "r1"}))
    assert begin_book({"live": "on", "html": "on"}, str(tmp_path), environ={}).live == "off"


# -- keys, clicks, names -------------------------------------------------------------------

def test_keys_are_physical_keys():
    assert parse_combo("ctrl+alt+meta+l", key=True) == {"ctrl": True, "alt": True, "meta": True,
                                                         "shift": False, "code": "KeyL"}
    assert parse_combo("Cmd+Option+7", key=True)["code"] == "Digit7"
    assert parse_combo("ctrl+f5", key=True)["code"] == "F5"
    assert parse_combo("", key=True) is None
    assert parse_combo("alt", key=False) == {"ctrl": False, "alt": True, "meta": False, "shift": False}
    assert combo_text(parse_combo("ctrl+alt+meta+l", key=True)) == "⌃⌥⌘L"


@pytest.mark.parametrize("text, key", [("ctrl+alt", True), ("l", False), ("ctrl+hyper+l", True),
                                       ("ctrl+l+m", True)])
def test_bad_combos_are_refused(text, key):
    with pytest.raises(ValueError):
        parse_combo(text, key=key)


def test_the_document_is_the_books_folder(tmp_path):
    assert document_name(str(tmp_path / "trainings" / "GAI4AS21H" / "slides"), str(tmp_path)) == "GAI4AS21H/slides"
    assert document_name(str(tmp_path / "docs" / "deck"), str(tmp_path)) == "docs/deck"
    assert document_name(str(tmp_path), str(tmp_path)) == tmp_path.name
    begin_book({"document": "POSTAIR"}, str(tmp_path), environ={})
    assert src._book.document == "POSTAIR"


def test_the_root_is_the_repository(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "trainings" / "X").mkdir(parents=True)
    (tmp_path / "trainings" / "X" / "stx.toml").write_text("")
    root, published = src._find_root(str(tmp_path / "trainings" / "X"))
    assert root == str(tmp_path) and published is None


def test_ranks_count_the_stops_of_a_file_within_an_entry():
    """As slide_map.py: an atom included by a list block has its own ranks; the host takes its own back.

    A marker's own key= does not change it: the author's notes are filed under <file>#<rank>."""
    def stop(file, entry, key=None):
        e = {"stop": True, "source": {"file": file, "line": 1, "entry": entry}}
        if key:
            e["key"] = key
        return e
    entries = [stop("content/bck_who.py", "bck_list"), stop("content/atoms/bck_a.py", "bck_list"),
               stop("content/atoms/bck_a.py", "bck_list"), stop("content/bck_who.py", "bck_list"),
               {"stop": False, "source": {"file": "content/bck_who.py", "line": 9, "entry": "bck_list"}},
               stop("content/bck_who.py", "bck_next"), stop("content/bck_x.py", "bck_next", key="intro")]
    annotate_sources(entries)
    got = [(e["source"]["rank"], e["source"]["of"], e["source"]["key"]) for e in entries if e["stop"]]
    assert got == [(1, 2, "who#1"), (1, 2, "a#1"), (2, 2, "a#2"), (2, 2, "who#2"), (1, 1, "who#1"),
                   (1, 1, "x#1")]
    assert "rank" not in entries[4]["source"]                       # not a slide


def test_without_sources_leaves_the_entries_as_before():
    entries = [{"index": 0, "label": "A", "source": {"file": "x.py"}}, {"index": 1}]
    assert without_sources(entries) == [{"index": 0, "label": "A"}, {"index": 1}]
    assert entries[0]["source"] == {"file": "x.py"}                # the registry keeps it


def test_the_editor_is_cursor_and_only_live_on_this_computer(tmp_path):
    begin_book({"live": "on", "html": "on"}, str(tmp_path), environ={})
    live, html = page_payload("live"), page_payload("html")
    assert live["editor"] == "cursor://file/{abs}:{line}" and live["root"] == str(tmp_path).replace(os.sep, "/")
    assert html["editor"] == "" and html["root"] == ""
    assert "⌥-click or ⌃⌥⌘L: copy" in live["hint"] and "⌘-click or ⌃⌥⌘O: open it in the editor" in live["hint"]
    assert "editor" not in html["hint"]


def test_the_release_is_the_commit_plus_a_mark_when_modified(tmp_path):
    for cmd in (["init", "-q"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"]):
        subprocess.run(["git", "-C", str(tmp_path), *cmd], check=True)
    (tmp_path / "f.py").write_text("a")
    subprocess.run(["git", "-C", str(tmp_path), "add", "f.py"], check=True)
    begin_book(None, str(tmp_path), environ={})
    src._release_cache.clear()
    sha = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "--short=8", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    assert src.release_name() == sha + "+"                         # f.py staged, not committed


# -- a real book ---------------------------------------------------------------------------

ATOM = '''
import streamtex as stx
def build(**k):
    with stx.st_slide(marker="A"):                      # @A
        stx.st_write("A")
'''
LOOP = '''
import streamtex as stx
def build(**k):
    for i in range(3):
        with stx.st_slide(cut=i > 0, marker=f"L{i}"):   # @L
            stx.st_write("L")
'''
INTRO = '''
import streamtex as stx
def build(**k):
    with stx.st_slide(marker="Intro", key="intro"):     # @I1
        stx.st_write("Intro")
    with stx.st_slide(                                  # @I2 (a call on four lines: its first)
        cut=True,
        marker="Two",
    ):
        stx.st_write("Two")
    stx.st_slide_break()                                # @I3
    stx.st_marker("Three")                              # @I4
'''
LIST = '''
import streamtex as stx
from blocks import bck_atom
def build(**k):
    with stx.st_slide(marker="Head"):                   # @H
        stx.st_write("Head")
    stx.st_sequence([bck_atom, bck_atom])
'''


@pytest.fixture
def deck(tmp_path):
    p = tmp_path / "proj" / "docs" / "deck"
    (p / "blocks").mkdir(parents=True)
    (tmp_path / "proj" / ".git").mkdir()
    (p / "blocks" / "__init__.py").write_text("")
    for name, text in (("bck_intro", INTRO), ("bck_loop", LOOP), ("bck_list", LIST), ("bck_atom", ATOM)):
        (p / "blocks" / f"{name}.py").write_text(textwrap.dedent(text))
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def _write_book(deck, source=None, paginate=False):
    (deck / "book.py").write_text(textwrap.dedent(f"""
        import streamtex as stx
        from blocks import bck_intro, bck_loop, bck_list
        stx.st_book([bck_intro, bck_loop, bck_list], toc_config=stx.TOCConfig(),
                    marker_config=stx.MarkerConfig(), paginate={paginate}, source={source!r})
    """))


def _line(deck, block, tag):
    lines = (deck / "blocks" / f"{block}.py").read_text().splitlines()
    return next(i for i, line in enumerate(lines, 1) if f"# {tag}" in line)


def _export(deck, tmp_path, *args):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / ("out" + "".join(a.strip("-") for a in args))
    r = CliRunner().invoke(export_html, [str(deck), "-o", str(out), *args])
    assert r.exit_code == 0, r.output
    return next(out.rglob("deck.html")).read_text(encoding="utf-8")


def _markers_of(html):
    return json.loads(re.search(r"var markers = (\[.*?\]);\n", html).group(1))


def test_each_stop_records_where_it_is_written(deck, tmp_path):
    _write_book(deck, {"html": "on"})
    html = _export(deck, tmp_path)
    stops = [m for m in _markers_of(html) if m.get("stop", True)]
    got = [(m["label"], m["source"]["file"], m["source"]["line"], m["source"]["entry"],
            f'{m["source"]["rank"]}/{m["source"]["of"]}', m["source"]["key"]) for m in stops]
    f = "docs/deck/blocks/"
    intro, loop, lst, atom = (f + n + ".py" for n in ("bck_intro", "bck_loop", "bck_list", "bck_atom"))
    want = [
        ("Intro", intro, _line(deck, "bck_intro", "@I1"), "bck_intro", "1/4", "intro#1"),    # key= or not
        ("Two", intro, _line(deck, "bck_intro", "@I2"), "bck_intro", "2/4", "intro#2"),      # the with line
        ("Marker 3", intro, _line(deck, "bck_intro", "@I3"), "bck_intro", "3/4", "intro#3"),
        ("Three", intro, _line(deck, "bck_intro", "@I4"), "bck_intro", "4/4", "intro#4"),
        ("L0", loop, _line(deck, "bck_loop", "@L"), "bck_loop", "1/3", "loop#1"),            # a loop:
        ("L1", loop, _line(deck, "bck_loop", "@L"), "bck_loop", "2/3", "loop#2"),            # one line,
        ("L2", loop, _line(deck, "bck_loop", "@L"), "bck_loop", "3/3", "loop#3"),            # three ranks
        ("Head", lst, _line(deck, "bck_list", "@H"), "bck_list", "1/1", "list#1"),
        ("A", atom, _line(deck, "bck_atom", "@A"), "bck_list", "1/2", "atom#1"),             # the atom,
        ("A", atom, _line(deck, "bck_atom", "@A"), "bck_list", "2/2", "atom#2"),             # not the list
    ]
    assert got == want, got


def test_off_leaves_the_export_as_before(deck, tmp_path):
    """The default (off): not one byte changes, the source recorded or not."""
    _write_book(deck)
    today = _export(deck, tmp_path)
    with patch("streamtex.source.capture", return_value=None):
        before = _export(deck, tmp_path, "--suffix", "")
    assert today == before
    assert '"source"' not in today and "#157" not in today and "stx-src" not in today


def test_html_on_puts_the_source_and_the_gesture_in_the_export(deck, tmp_path):
    _write_book(deck, {"html": "on"})
    html = _export(deck, tmp_path)
    assert '"source"' in html and "copy where this slide is written" in html
    assert '"doc": "docs/deck"' in html
    assert '"root": ""' in html                       # no absolute path in an export


def test_the_export_option_overrides_the_book(deck, tmp_path):
    _write_book(deck, {"html": "on"})
    assert '"source"' not in _export(deck, tmp_path, "--source", "off")
    assert os.environ.get("STX_SOURCE_HTML") is None   # put back after the export
    _write_book(deck)
    assert '"source"' in _export(deck, tmp_path, "--source", "on")


def _live_widget(entries_cfg, source):
    """The live marker widget script for a few markers, with *source* settings."""
    import streamtex.marker as mk
    from streamtex.marker import MarkerConfig, reset_marker_registry, st_marker
    reset_marker_registry(MarkerConfig())
    for label in entries_cfg:
        st_marker(label)
    begin_book(source, os.getcwd(), environ={})
    shown = []
    with patch("streamlit.iframe", side_effect=lambda html, **k: shown.append(html)), \
         patch("streamtex.marker._render"):
        mk.inject_marker_navigation()
    return shown[0]


def test_live_off_leaves_the_widget_as_before():
    today = _live_widget(["A", "B"], None)
    with patch("streamtex.source.capture", return_value=None):
        before = _live_widget(["A", "B"], None)
    assert today == before and '"source"' not in today and "#157" not in today


def test_live_on_gives_the_widget_the_gesture():
    js = _live_widget(["A", "B"], {"live": "on"})
    assert '"source"' in js and "#157" in js and "srcDoc = hostDoc" in js
    assert js.index("#157") < js.index("scheduleInit(INIT_MIN_MS);\n})();")
    assert '"footHint"' in js and "cursor://file/{abs}:{line}" in js


def test_a_paginated_book_records_the_same_sources(deck, tmp_path):
    _write_book(deck, {"html": "on"})
    cont = [m.get("source") for m in _markers_of(_export(deck, tmp_path))]
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]
    _write_book(deck, {"html": "on"}, paginate=True)
    pag = [m.get("source") for m in _markers_of(_export(deck, tmp_path))]
    assert cont == pag


# -- stx release ---------------------------------------------------------------------------

def _project(tmp_path, defaults=""):
    root = tmp_path / "rel"
    (root / "docs" / "deck").mkdir(parents=True)
    (root / "docs" / "deck" / "book.py").write_text("")
    (root / "stx.toml").write_text(textwrap.dedent("""
        [release]
        project = "demo"
        [[release.sites]]
        site = "deck"
        book = "docs/deck/book.py"
    """) + defaults)
    for cmd in (["init", "-q"], ["add", "."], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True)
    return root


def test_a_table_of_book_defaults_reaches_the_published_site(tmp_path):
    """[book.defaults.source] was written as {"live": ...}: not TOML, every default lost."""
    import tomllib

    from streamtex.release import build
    root = _project(tmp_path, '[book.defaults]\nstage = false\n[book.defaults.source]\nlive = "on"\nskip = ["a.b"]\n')
    text = build.book_defaults_toml(root)
    assert tomllib.loads(text)["book"]["defaults"] == {"stage": False, "source": {"live": "on", "skip": ["a.b"]}}


def test_the_snapshot_records_the_release_and_the_targets_setting(tmp_path):
    from streamtex.release import build
    from streamtex.release.config import load_config
    root = _project(tmp_path)
    cfg = load_config(root)
    for n, (release, source) in enumerate([(None, None), ("r1", {"live": "on"})]):
        work = tmp_path / f"w{n}"
        work.mkdir()
        code = build.snapshot(cfg, cfg.site("deck"), work, release=release, source=source)
        record = json.loads((code / PUBLISHED_FILE).read_text())
        sha = subprocess.run(["git", "-C", str(root), "rev-parse", "--short=12", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        assert record["release"] == (release or sha) and record["site"] == "deck"
        assert record["source"] == {"live": "on" if source else "off", "html": "off"}


def test_the_shells_source_setting_never_reaches_a_publication(tmp_path, monkeypatch):
    from streamtex.release import ReleaseError, build
    from streamtex.release.config import load_config
    root = _project(tmp_path)
    cfg = load_config(root)
    code = tmp_path / "code"
    (code / "docs" / "deck").mkdir(parents=True)
    seen = []
    monkeypatch.setenv("STX_SOURCE_HTML", "on")
    monkeypatch.setattr(build.subprocess, "run",
                        lambda argv, **k: seen.append(k["env"]) or subprocess.CompletedProcess(argv, 1, "", "no"))
    with pytest.raises(ReleaseError):
        build.export(cfg, cfg.site("deck"), code, tmp_path / "w", "r1")
    assert "STX_SOURCE_HTML" not in seen[0]
    seen.clear()
    with pytest.raises(ReleaseError):
        build.export(cfg, cfg.site("deck"), code, tmp_path / "w", "r1", html_env={"STX_SOURCE_HTML": "on"})
    assert seen[0]["STX_SOURCE_HTML"] == "on"                     # --html-env still can


def test_a_project_helper_can_be_skipped(tmp_path, monkeypatch):
    """A project wrapper around st_slide: with skip=, the source is the block that called it."""
    (tmp_path / "myhelpers.py").write_text(textwrap.dedent('''
        from contextlib import contextmanager
        import streamtex as stx
        @contextmanager
        def slide(**k):
            with stx.st_slide(**k):                     # @helper
                yield
        def plain(**k):
            return stx.st_slide(**k)                    # an alias: transparent, no skip needed
    '''))
    (tmp_path / "bck_user.py").write_text(textwrap.dedent('''
        import myhelpers
        def build():
            with myhelpers.slide(marker="X"):           # @user
                pass
            with myhelpers.plain(marker="Y"):           # @plain
                pass
    '''))
    monkeypatch.syspath_prepend(str(tmp_path))
    import bck_user

    from streamtex.marker import MarkerConfig, marker_entries, reset_marker_registry
    lines = {tag: next(i for i, s in enumerate((tmp_path / f).read_text().splitlines(), 1) if tag in s)
             for f, tag in (("myhelpers.py", "@helper"), ("bck_user.py", "@user"), ("bck_user.py", "@plain"))}
    for skip, want in (((), ("myhelpers.py", lines["@helper"])), (("myhelpers",), ("bck_user.py", lines["@user"]))):
        begin_book({"skip": skip}, str(tmp_path), environ={})
        reset_marker_registry(MarkerConfig())
        with patch("streamtex.marker._render"), patch("streamtex.container.st_block"):
            bck_user.build()
        got, plain = (e["source"] for e in marker_entries()[-2:])
        assert (got["file"], got["line"]) == want
        assert (plain["file"], plain["line"]) == ("bck_user.py", lines["@plain"])
    for name in ("bck_user", "myhelpers"):
        sys.modules.pop(name, None)
