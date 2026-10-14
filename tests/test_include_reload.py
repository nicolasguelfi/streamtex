"""The page cache and hot reload follow every block reached through st_include (#120)."""

import importlib
import importlib.util
import os
import runpy
import sys
import textwrap
import time
from pathlib import Path
from unittest.mock import patch

import pytest

import streamtex.book as bm
from streamtex import watch
from streamtex.book import _compute_cache_hash, _resolve_cache_path, set_include_reload, st_include

pytestmark = pytest.mark.usefixtures("reset_watch")


def _bump(path: Path, text: str | None = None) -> None:
    """Rewrite *path* (optional) and move its mtime clearly forward."""
    if text is not None:
        path.write_text(text)
    t = time.time() + 10 + _bump.n
    _bump.n += 10
    os.utime(path, (t, t))


_bump.n = 0


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ATOM = """
RUNS = globals().get("RUNS", 0) + 1
SEEN = []
def build():
    SEEN.append("{v}")
"""


@pytest.fixture
def atom(tmp_path):
    p = tmp_path / "atoms" / "bck_atom.py"
    p.parent.mkdir()
    p.write_text(ATOM.format(v="v1"))
    bm._INCLUDED.clear()
    set_include_reload(True)
    with patch("streamtex.book.st"):
        yield p, _load(p, "atoms_bck_atom")
    bm._INCLUDED.clear()
    set_include_reload(True)


class TestReload:
    def test_included_file_is_watched(self, atom):
        p, mod = atom
        st_include(mod)
        assert os.path.abspath(p) in [os.path.realpath(x) for x in watch.watched_files()]

    def test_edit_invalidates_the_snapshot(self, atom):
        p, mod = atom
        st_include(mod)
        snap = bm._watched_snapshot()
        assert watch.snapshot_is_current(snap)
        _bump(p)
        assert not watch.snapshot_is_current(snap)

    def test_snapshot_records_the_code_that_ran(self, atom):
        p, mod = atom
        st_include(mod)
        ran = os.path.getmtime(p)
        _bump(p)                                   # edited after it ran, before the snapshot
        assert bm._watched_snapshot()[str(p.resolve())] == ran

    def test_changed_file_runs_again_in_place(self, atom):
        p, mod = atom
        st_include(mod)
        before = id(mod)
        _bump(p, ATOM.format(v="v2"))
        st_include(mod)
        assert id(mod) == before and mod.SEEN == ["v2"] and mod.RUNS == 2

    def test_unchanged_file_and_first_sight_never_run_again(self, atom):
        p, mod = atom
        st_include(mod)
        st_include(mod)
        assert mod.RUNS == 1 and mod.SEEN == ["v1", "v1"]

    def test_another_object_for_a_known_file_is_recorded(self, atom):
        p, mod = atom
        st_include(mod)
        _bump(p, ATOM.format(v="v2"))
        fresh = _load(p, "atoms_bck_atom")        # e.g. Streamlit evicted and re-imported it
        st_include(fresh)
        assert fresh.RUNS == 1 and fresh.SEEN == ["v2"]

    def test_failure_reported_once_then_retried(self, atom):
        p, mod = atom
        st_include(mod)
        _bump(p, "def build(:\n")
        with patch("streamtex.book.st") as fake:
            with pytest.raises(SyntaxError):
                st_include(mod)
            reds = [c for c in fake.markdown.call_args_list if ":red-background[" in c.args[0]]
            assert len(reds) == 1
        _bump(p, ATOM.format(v="v3"))
        st_include(mod)
        assert mod.SEEN[-1] == "v3"

    def test_opt_out_setting(self, atom):
        p, mod = atom
        st_include(mod)
        set_include_reload(False)
        _bump(p, ATOM.format(v="v2"))
        st_include(mod)
        assert mod.SEEN == ["v1", "v1"]
        assert str(p.resolve()) in [os.path.realpath(x) for x in watch.watched_files()]

    def test_opt_out_env_wins(self, atom, monkeypatch):
        p, mod = atom
        st_include(mod)
        monkeypatch.setenv("STX_INCLUDE_RELOAD", "0")
        _bump(p, ATOM.format(v="v2"))
        st_include(mod)
        assert mod.SEEN == ["v1", "v1"]

    def test_module_in_sys_modules(self, tmp_path):
        pkg = tmp_path / "pk120"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "a.py").write_text(ATOM.format(v="v1"))
        sys.path.insert(0, str(tmp_path))
        try:
            mod = importlib.import_module("pk120.a")
            with patch("streamtex.book.st"):
                st_include(mod)
                _bump(pkg / "a.py", ATOM.format(v="v2"))
                st_include(mod)
            assert sys.modules["pk120.a"] is mod and mod.SEEN == ["v2"]
        finally:
            sys.path.remove(str(tmp_path))
            for n in [n for n in sys.modules if n.startswith("pk120")]:
                del sys.modules[n]

    def test_load_atomic_block(self, tmp_path):
        from streamtex.blocks import load_atomic_block
        comp = tmp_path / "blocks" / "bck_comp.py"
        (tmp_path / "blocks" / "_atomic").mkdir(parents=True)
        comp.write_text("")
        (tmp_path / "blocks" / "_atomic" / "bck_part.py").write_text(ATOM.format(v="v1"))
        part = load_atomic_block("bck_part", str(comp))
        with patch("streamtex.book.st"):
            st_include(part)
            _bump(tmp_path / "blocks" / "_atomic" / "bck_part.py", ATOM.format(v="v2"))
            st_include(part)
        assert part.SEEN == ["v2"]


# ---------------------------------------------------------------------------
# Part C: the cache belongs to the module's book.py
# ---------------------------------------------------------------------------

def _layout(tmp_path):
    for d in ("lists", "atoms", "modules/m", "modules/n/custom"):
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "lists" / "bck_list.py").write_text("def build(**k): pass\n")
    (tmp_path / "modules" / "m" / "book.py").write_text("")
    (tmp_path / "modules" / "n" / "book.py").write_text("")
    (tmp_path / "modules" / "n" / "custom" / "x.py").write_text("")
    return _load(tmp_path / "lists" / "bck_list.py", "lists_bck_list")


class TestAnchor:
    def test_cache_next_to_the_book(self, tmp_path):
        entry = _layout(tmp_path)
        book = tmp_path / "modules" / "m" / "book.py"
        assert _resolve_cache_path([entry], book_file=str(book)) == \
            str(tmp_path / "modules" / "m" / ".stx_cache" / "page_cache.json")

    def test_two_modules_sharing_an_entry_directory(self, tmp_path):
        entry = _layout(tmp_path)
        m = _resolve_cache_path([entry], (), {"lang": "fr"}, str(tmp_path / "modules/m/book.py"))
        n = _resolve_cache_path([entry], (), {"lang": "fr"}, str(tmp_path / "modules/n/book.py"))
        assert m != n

    def test_book_and_custom_enter_the_hash(self, tmp_path):
        entry = _layout(tmp_path)
        book = tmp_path / "modules" / "n" / "book.py"
        h = _compute_cache_hash([entry], book_file=str(book))
        _bump(book)
        h2 = _compute_cache_hash([entry], book_file=str(book))
        _bump(tmp_path / "modules" / "n" / "custom" / "x.py")
        h3 = _compute_cache_hash([entry], book_file=str(book))
        assert len({h, h2, h3}) == 3

    def test_standard_layout_is_unchanged(self, tmp_path):
        (tmp_path / "blocks").mkdir()
        (tmp_path / "custom").mkdir()
        (tmp_path / "custom" / "styles.py").write_text("")
        (tmp_path / "blocks" / "bck_a.py").write_text("def build(): pass\n")
        (tmp_path / "book.py").write_text("")
        entry = _load(tmp_path / "blocks" / "bck_a.py", "blocks_bck_a")
        book = str(tmp_path / "book.py")
        assert _resolve_cache_path([entry], book_file=book) == _resolve_cache_path([entry])
        assert _compute_cache_hash([entry], book_file=book) == _compute_cache_hash([entry])


def test_book_file_found_through_a_helper(tmp_path):
    (tmp_path / "helper120.py").write_text(textwrap.dedent("""
        from streamtex.book import _find_book_file
        def make():
            return _find_book_file()
    """))
    script = tmp_path / "modules" / "m" / "book.py"
    script.parent.mkdir(parents=True)
    script.write_text("import helper120\nFOUND = helper120.make()\n")
    sys.path.insert(0, str(tmp_path))
    try:
        found = runpy.run_path(str(script), run_name="__main__")["FOUND"]
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("helper120", None)
    assert os.path.realpath(found) == os.path.realpath(script)


def test_no_book_file_under_a_test_runner():
    assert bm._find_book_file() is None


# ---------------------------------------------------------------------------
# End to end (AppTest, same process, no restart)
# ---------------------------------------------------------------------------

def test_edit_an_atom_then_rerun(tmp_path):
    from streamlit.testing.v1 import AppTest
    for d in ("atoms", "lists", "modules/m"):
        (tmp_path / d).mkdir(parents=True)
    for d in ("atoms", "lists"):
        (tmp_path / d / "__init__.py").write_text("")
    atom_a = 'import streamtex as stx\ndef build(**k):\n    stx.st_marker("{t}")\n    stx.st_write("{t}", toc_lvl="1")\n'
    (tmp_path / "atoms" / "bck_a.py").write_text(atom_a.format(t="A-1"))
    (tmp_path / "atoms" / "bck_b.py").write_text(atom_a.format(t="B-1"))
    lst = "import streamtex as stx\nfrom atoms import bck_a, bck_b\nITEMS = [{items}]\ndef build(**k):\n    stx.st_sequence(ITEMS, **k)\n"
    (tmp_path / "lists" / "bck_list.py").write_text(lst.format(items="bck_a, bck_b"))
    book = tmp_path / "modules" / "m" / "book.py"
    book.write_text(textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(tmp_path)!r})
        import streamtex as stx
        from lists import bck_list
        stx.st_book([bck_list], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
                    paginate=True)
    """))
    try:
        at = AppTest.from_file(str(book), default_timeout=30).run()
        assert not at.exception

        def labels():
            return [e["label"] for e in at.session_state[bm._STX_CACHE_KEY]["markers"]]
        assert labels() == ["A-1", "B-1"]
        assert (tmp_path / "modules" / "m" / ".stx_cache").is_dir()   # next to book.py
        _bump(tmp_path / "atoms" / "bck_a.py", atom_a.format(t="A-2"))
        at.run()
        assert labels() == ["A-2", "B-1"]
        assert [t["title"].split(" ", 1)[-1] for t in at.session_state[bm._STX_CACHE_KEY]["toc"]] == ["A-2", "B-1"]
        _bump(tmp_path / "lists" / "bck_list.py", lst.format(items="bck_b, bck_a"))
        at.run()
        assert labels() == ["B-1", "A-2"]
    finally:
        sys.path[:] = [p for p in sys.path if p != str(tmp_path)]
        for n in [n for n in sys.modules if n.split(".")[0] in ("atoms", "lists")]:
            del sys.modules[n]
        bm._INCLUDED.clear()
