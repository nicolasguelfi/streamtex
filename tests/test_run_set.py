"""stx run --set: [[run.documents]], document selection, state (#91)."""

import json
from pathlib import Path

import click
import pytest

from streamtex.cli import run_set

pytestmark = pytest.mark.usefixtures("reset_watch")


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
