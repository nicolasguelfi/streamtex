"""Lot E — projects with several documents: [book.defaults] (L7), stx run --set
(L8), themable collection and next deck (L9), run-time flags (L10)."""

import json
import types
from pathlib import Path
from unittest.mock import patch

import click
import pytest

import streamtex.book as book
from streamtex import watch
from streamtex.cli import run_set
from streamtex.collection import CollectionConfig, ProjectMeta, next_project, st_next_deck
from streamtex.runtime_flags import env_flag, is_editable, is_exportable


@pytest.fixture(autouse=True)
def _clean():
    watch._reset_for_tests()
    yield
    watch._reset_for_tests()


# --- L7 -------------------------------------------------------------------

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


def test_doc_version_auto_reads_pyproject(tmp_path):
    mod = _project(tmp_path)
    assert book._project_version(str(mod)) == "2.4.1"


# --- L9 -------------------------------------------------------------------

def _collection():
    c = CollectionConfig(title="T")
    c.projects = {"a": ProjectMeta("A", project_url="http://h:1"), "b": ProjectMeta("B", project_url="http://h:2")}
    return c


def test_next_project_and_wrap():
    c = _collection()
    assert next_project(c, "a")[0] == "b"
    assert next_project(c, "b") is None
    assert next_project(c, "b", wrap=True)[0] == "a"
    with pytest.raises(KeyError):
        next_project(c, "zz")


def test_st_next_deck_carries_the_language():
    out = []
    with patch("streamtex.collection._render", side_effect=lambda h, **k: out.append(h)):
        st_next_deck(_collection(), "a", lang="fr")
        st_next_deck(_collection(), "b")                                   # last: nothing
    assert len(out) == 1 and 'href="http://h:2?lang=fr"' in out[0] and "B" in out[0]


def test_collection_card_colours_are_themable(tmp_path):
    (tmp_path / "collection.toml").write_text(
        '[collection]\ntitle = "C"\ncard_border = "1px solid rgba(255,255,255,0.2)"\n'
        'card_text_color = "#ccc"\n[projects.a]\ntitle = "A"\n')
    c = CollectionConfig.from_toml(str(tmp_path / "collection.toml"))
    assert (c.card_border, c.card_text_color) == ("1px solid rgba(255,255,255,0.2)", "#ccc")
    assert CollectionConfig().card_border == "1px solid #ddd"             # 0.7.x default kept


# --- L10 ------------------------------------------------------------------

def test_runtime_flags(tmp_path, monkeypatch):
    for k in ("STX_EDITABLE", "IS_EDITABLE", "STX_EXPORTABLE", "IS_EXPORTABLE"):
        monkeypatch.delenv(k, raising=False)
    assert is_editable() is False and is_exportable() is False
    env = tmp_path / ".env"
    env.write_text("# deploy\nIS_EXPORTABLE='true'\nexport STX_EDITABLE=0\n")
    assert is_exportable(env) is True and is_editable(env) is False
    monkeypatch.setenv("STX_EDITABLE", "yes")
    assert is_editable(env) is True                                        # environment first
    monkeypatch.setenv("STX_EDITABLE", "maybe")
    with pytest.raises(ValueError):
        env_flag("STX_EDITABLE")


# --- L8 -------------------------------------------------------------------

def _run_project(tmp_path):
    for d in ("a", "b"):
        (tmp_path / d).mkdir()
        (tmp_path / d / "book.py").write_text("")
    (tmp_path / "stx.toml").write_text(
        '[[run.documents]]\nid = "deck-a"\nbook = "a/book.py"\nport = 8801\n'
        '[[run.documents]]\nid = "deck-b"\nbook = "b/book.py"\nport = 8802\n')
    return tmp_path


def test_load_and_select_documents(tmp_path):
    root = _run_project(tmp_path)
    docs = run_set.load_documents(root, offset=100)
    assert [(d.id, d.port, d.env_key) for d in docs] == [("deck-a", 8901, "STX_URL_DECK_A"),
                                                        ("deck-b", 8902, "STX_URL_DECK_B")]
    assert [d.id for d in run_set.select(docs, ("deck-b",))] == ["deck-b"]
    with pytest.raises(click.ClickException):
        run_set.select(docs, ("nope",))
    (root / "stx.toml").write_text('[[run.documents]]\nid = "x"\nbook = "missing.py"\nport = 1\n')
    with pytest.raises(click.ClickException, match="book not found"):
        run_set.load_documents(root)


def test_start_passes_every_document_url_and_records_state(tmp_path, monkeypatch):
    root = _run_project(tmp_path)
    docs = run_set.load_documents(root)
    captured = {}

    class FakeProc:
        pid = 4242

    def fake_popen(cmd, cwd=None, env=None, **kw):
        captured.update(cmd=cmd, cwd=cwd, env=env)
        return FakeProc()

    monkeypatch.setattr(run_set, "_port_busy", lambda port: False)
    monkeypatch.setattr(run_set.subprocess, "Popen", fake_popen)
    assert run_set.start(root, docs, docs[0]) == "started"
    assert captured["env"]["STX_URL_DECK_A"] == "http://localhost:8801"
    assert captured["env"]["STX_URL_DECK_B"] == "http://localhost:8802"
    assert Path(captured["cwd"]) == root / "a" and "8801" in captured["cmd"]
    state = json.loads((root / ".stx_run" / "deck-a.json").read_text())
    assert state["pid"] == 4242 and state["port"] == 8801
    monkeypatch.setattr(run_set, "_port_busy", lambda port: True)
    monkeypatch.setattr(run_set, "running_pid", lambda r, d: None)
    assert "busy" in run_set.start(root, docs, docs[1])


# --- L7 / #19: shared block directories ----------------------------------

def test_registry_falls_back_on_shared_dirs_and_keeps_its_own_iteration(tmp_path):
    from streamtex.blocks import BlockNotFoundError, ProjectBlockRegistry

    local = tmp_path / "m1" / "blocks"
    shared = tmp_path / "shared-blocks" / "blocks"
    (shared / "trainers").mkdir(parents=True)
    local.mkdir(parents=True)
    (local / "bck_intro.py").write_text("WHO = 'local intro'\ndef build(**_): pass\n")
    (local / "bck_glossary.py").write_text("WHO = 'local glossary'\ndef build(**_): pass\n")
    (shared / "bck_glossary.py").write_text("WHO = 'shared glossary'\ndef build(**_): pass\n")
    (shared / "trainers" / "bck_trainer.py").write_text("WHO = 'shared trainer'\ndef build(**_): pass\n")

    reg = ProjectBlockRegistry(local, shared_dirs=[shared])
    assert reg.bck_intro.WHO == "local intro"
    assert reg.bck_glossary.WHO == "local glossary"           # local wins
    assert reg.bck_trainer.WHO == "shared trainer"            # recursive fallback
    assert [m.WHO for m in reg] == ["local glossary", "local intro"]  # iteration: own blocks only
    assert len(reg) == 2 and reg.list_shared_blocks() == ["bck_trainer"]
    with pytest.raises(BlockNotFoundError, match="Shared: bck_trainer"):
        reg.get("bck_nope")
    assert ProjectBlockRegistry(local).list_shared_blocks() == []   # no shared_dirs: as before
