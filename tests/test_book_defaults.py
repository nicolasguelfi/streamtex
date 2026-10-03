"""[book.defaults] of stx.toml and doc_version="auto" (#90)."""

import types

import pytest

import streamtex.book as book

pytestmark = pytest.mark.usefixtures("reset_watch")


def _project(tmp_path, defaults=""):
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n' + defaults)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "2.4.1"\n')
    mod = tmp_path / "modules" / "m1"
    mod.mkdir(parents=True)
    return mod


def test_book_defaults_fill_only_what_the_book_does_not_say(tmp_path, monkeypatch):
    mod = _project(tmp_path, '[book.defaults]\npaginate = true\nzoom = 90\nbogus = 1\n')
    monkeypatch.setattr(book, "_main_script_dir", lambda: str(mod))
    seen = {}
    monkeypatch.setattr(book, "_st_book_impl", lambda ml, *a, **k: seen.update(args=a, kwargs=k))
    blk = types.ModuleType("b")
    book.st_book([blk])
    assert seen["kwargs"] == {"paginate": True, "zoom": 90}               # 'bogus' ignored
    book.st_book([blk], zoom=120)
    assert seen["kwargs"] == {"paginate": True, "zoom": 120}              # explicit wins
    book.st_book([blk], None, None, None, False)                          # export passed positionally
    assert "export" not in seen["kwargs"]


def test_no_defaults_section_changes_nothing(tmp_path, monkeypatch):
    mod = _project(tmp_path)
    monkeypatch.setattr(book, "_main_script_dir", lambda: str(mod))
    seen = {}
    monkeypatch.setattr(book, "_st_book_impl", lambda ml, *a, **k: seen.update(kwargs=k))
    book.st_book([types.ModuleType("b")], page_width=80)
    assert seen["kwargs"] == {"page_width": 80}


def test_st_book_help_documents_book_defaults_and_its_parameters():
    import inspect

    import streamtex

    doc = streamtex.st_book.__doc__
    assert "[book.defaults]" in doc and 'doc_version="auto"' in doc
    assert ":param separator:" in doc  # the implementation's own docstring follows
    assert "toc_config" in inspect.signature(streamtex.st_book).parameters


def test_doc_version_auto_reads_pyproject(tmp_path):
    mod = _project(tmp_path)
    assert book._project_version(str(mod)) == "2.4.1"
