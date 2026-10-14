"""st_include refuses inclusion cycles with IncludeCycleError naming the chain (#119)."""

import importlib.util
import sys
import textwrap
import threading
import types
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

import streamtex.book as bm
import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex.book import IncludeCycleError, st_include, st_sequence
from streamtex.marker import MarkerConfig, marker_entries, reset_marker_registry
from streamtex.toc import TOCConfig, reset_toc_registry


def _write_lists(root: Path) -> None:
    (root / "lists").mkdir(parents=True)
    (root / "lists" / "__init__.py").write_text("")
    (root / "lists" / "a.py").write_text(textwrap.dedent("""
        import streamtex as stx
        def build(*args, **kwargs):
            stx.st_marker("a")
            from lists import b
            stx.st_include(b, *args, **kwargs)
    """))
    (root / "lists" / "b.py").write_text(textwrap.dedent("""
        import streamtex as stx
        def build(*args, **kwargs):
            stx.st_marker("b")
            from lists import a
            stx.st_include(a, *args, break_before=True, **kwargs)
    """))
    (root / "lists" / "self_.py").write_text(textwrap.dedent("""
        import sys, streamtex as stx
        def build():
            stx.st_include(sys.modules[__name__])
    """))
    (root / "lists" / "l0.py").write_text(textwrap.dedent("""
        import streamtex as stx
        def build():
            from lists import a
            stx.st_include(a)
    """))


@pytest.fixture
def project(tmp_path):
    _write_lists(tmp_path)
    sys.path.insert(0, str(tmp_path))
    toc_mod.toc = None
    mk._registry = None
    reset_toc_registry(TOCConfig())
    reset_marker_registry(MarkerConfig())
    out = []
    with patch("streamtex.marker._render", side_effect=out.append), \
         patch("streamtex.slide._render", side_effect=out.append), \
         patch("streamtex.book.st") as fake_st:
        yield types.SimpleNamespace(root=tmp_path, out=out, st=fake_st)
    sys.path.remove(str(tmp_path))
    for name in [n for n in sys.modules if n == "lists" or n.startswith("lists.")]:
        del sys.modules[name]
    mk._registry = None
    toc_mod.toc = None


def _red(fake_st):
    return [c for c in fake_st.markdown.call_args_list if ":red-background[" in c.args[0]]


class TestCycles:
    def test_self_inclusion(self, project):
        from lists import self_
        with pytest.raises(IncludeCycleError) as ei:
            st_include(self_)
        assert ei.value.chain == ("lists.self_", "lists.self_")

    def test_two_step_cycle_from_the_entry(self, project):
        from lists import a
        with pytest.raises(IncludeCycleError) as ei:
            st_include(a)
        assert ei.value.chain == ("lists.a", "lists.b", "lists.a")
        assert str(ei.value).startswith("Include cycle: lists.a → lists.b → lists.a. ")
        assert [e["label"] for e in marker_entries()] == ["a", "b"]   # nothing of the refused one

    def test_cycle_below_the_entry(self, project):
        from lists import l0
        with pytest.raises(IncludeCycleError) as ei:
            st_include(l0)
        assert ei.value.chain == ("lists.a", "lists.b", "lists.a")
        assert ei.value.stack == ("lists.l0", "lists.a", "lists.b")

    def test_refused_inclusion_draws_no_break(self, project):
        from lists import a
        with pytest.raises(IncludeCycleError):
            st_include(a)
        assert not any("stx-slide-break" in h for h in project.out)   # b's break_before

    def test_same_file_under_two_names(self, project):
        spec = importlib.util.spec_from_file_location("other_name", project.root / "lists" / "self_.py")
        clone = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(clone)
        from lists import self_
        clone.build = lambda: st_include(self_)
        with pytest.raises(IncludeCycleError) as ei:
            st_include(clone)
        assert ei.value.chain == ("other_name", "lists.self_")

    def test_one_red_message(self, project):
        from lists import l0
        with pytest.raises(IncludeCycleError):
            st_include(l0)
        (msg,) = _red(project.st)
        assert "Include cycle: lists.a → lists.b → lists.a" in msg.args[0]


class TestStack:
    def test_siblings_are_not_a_cycle(self, project):
        x = types.ModuleType("x")
        x.build = lambda: None
        st_include(x)
        st_include(x)
        st_sequence([x, x])
        assert bm._INCLUDE_STACK.get() == ()

    def test_restored_after_a_cycle_and_after_an_error(self, project):
        from lists import a
        with pytest.raises(IncludeCycleError):
            st_include(a)
        assert bm._INCLUDE_STACK.get() == ()
        boom = types.ModuleType("boom")
        boom.build = lambda: 1 / 0
        with pytest.raises(ZeroDivisionError):
            st_include(boom)
        assert bm._INCLUDE_STACK.get() == ()

    def test_one_red_message_for_an_ordinary_error_at_depth_3(self, project):
        err = ValueError("bad")
        c = types.ModuleType("c")
        c.build = lambda: (_ for _ in ()).throw(err)
        b2 = types.ModuleType("b2")
        b2.build = lambda: st_include(c)
        a2 = types.ModuleType("a2")
        a2.build = lambda: st_include(b2)
        with pytest.raises(ValueError) as ei:
            st_include(a2)
        assert ei.value is err
        (msg,) = _red(project.st)
        assert "Error in block 'c'" in msg.args[0]

    def test_depth_bound(self, project):
        depths = []
        leaf = types.ModuleType("leaf")
        leaf.build = lambda: depths.append(len(bm._INCLUDE_STACK.get()))
        def chain(n):
            m = types.ModuleType(f"lvl{n}")
            m.build = (lambda: st_sequence([leaf] * 20)) if n == 0 else (lambda: st_include(chain(n - 1)))
            return m
        st_include(chain(9))
        assert len(depths) == 20 and max(depths) == 11

    def test_threads_share_no_stack(self, project):
        errors = []
        barrier = threading.Barrier(2)
        blk = types.ModuleType("shared")
        blk.build = lambda: barrier.wait()
        def run():
            try:
                st_include(blk)
            except Exception as e:      # noqa: BLE001
                errors.append(e)
        ts = [threading.Thread(target=run) for _ in range(2)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        assert errors == []

    def test_exported(self):
        import streamtex
        assert streamtex.IncludeCycleError is IncludeCycleError


# ---------------------------------------------------------------------------
# Book, warmup, CLI
# ---------------------------------------------------------------------------

BOOK = textwrap.dedent("""
    import sys, types
    sys.path.insert(0, ROOT)
    import streamtex as stx
    from lists import a
    ok = types.ModuleType("ok")
    ok.build = lambda: stx.st_marker("ok")
    stx.st_book([ok, a], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
                paginate=True)
""")


@pytest.fixture
def lists_root(tmp_path):
    _write_lists(tmp_path)
    yield tmp_path
    for name in [n for n in sys.modules if n == "lists" or n.startswith("lists.")]:
        del sys.modules[name]


@pytest.mark.usefixtures("reset_watch")
def test_paginated_cache_build_shows_the_error(lists_root):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_string(BOOK.replace("ROOT", repr(str(lists_root))), default_timeout=30).run()
    assert any("Include cycle: lists.a → lists.b → lists.a" in e.value for e in at.error)
    assert not (lists_root / ".stx_cache").exists()


@pytest.mark.usefixtures("reset_watch")
def test_warmup_never_skips_a_cycle(lists_root):
    from streamlit.testing.v1 import AppTest
    with patch.object(bm, "_warmup_mode", True):
        at = AppTest.from_string(BOOK.replace("ROOT", repr(str(lists_root))), default_timeout=30).run()
    assert at.exception and "Include cycle" in at.exception[0].value


@pytest.mark.usefixtures("reset_watch")
def test_warmup_still_skips_an_ordinary_error(lists_root):
    from streamlit.testing.v1 import AppTest
    book = BOOK.replace("from lists import a", "a = types.ModuleType('boom'); a.build = lambda: 1 / 0")
    with patch.object(bm, "_warmup_mode", True):
        at = AppTest.from_string(book.replace("ROOT", repr(str(lists_root))), default_timeout=30).run()
    assert not at.exception


def _cli_project(tmp_path: Path) -> Path:
    p = tmp_path / "proj"
    p.mkdir()
    _write_lists(p)
    (p / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from lists import a
        stx.st_book([a], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(), paginate=True)
    """))
    return p


def test_cli_export_html_exits_1(tmp_path):
    from streamtex.cli.export_cmd import export_html
    p = _cli_project(tmp_path)
    out = tmp_path / "out"
    try:
        r = CliRunner().invoke(export_html, [str(p), "-o", str(out)])
    finally:
        for name in [n for n in sys.modules if n == "lists" or n.startswith("lists.")]:
            del sys.modules[name]
    assert r.exit_code == 1, r.output
    assert "Include cycle: lists.a → lists.b → lists.a" in r.output
    assert not out.exists() or not any(out.iterdir())


def test_validate_build_names_the_chain_from_the_entry(tmp_path):
    from streamtex.cli.build_check import run_book
    p = _cli_project(tmp_path)
    r = run_book(p / "book.py", timeout=120)
    assert [(e[0], e[1]) for e in r.errors] == [("lists.a", "IncludeCycleError")]
    assert "lists.a → lists.b → lists.a" in r.errors[0][2]
