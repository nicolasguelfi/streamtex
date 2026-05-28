"""Tests for `auto_link_streamtex_if_registered` (called by `stx project new`
when the workspace preset is ``developer`` to align the new project on the
locally-cloned streamtex source rather than the PyPI release).
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from unittest.mock import MagicMock

from streamtex.cli import dev_cmd


def _make_project(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
    )
    return tmp_path


def _read_sources(project: Path) -> dict:
    with (project / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    return data.get("tool", {}).get("uv", {}).get("sources", {})


def _fake_streamtex_clone(tmp_path: Path) -> Path:
    """A directory that looks enough like a streamtex source clone to pass
    `validate_repo_path("streamtex", path)` — needs pyproject.toml with the
    matching name."""
    clone = tmp_path / "streamtex-clone"
    (clone / "streamtex").mkdir(parents=True)
    (clone / "streamtex" / "__init__.py").write_text('__version__ = "0.0.0-dev"\n')
    (clone / "pyproject.toml").write_text(
        '[project]\nname = "streamtex"\nversion = "0.0.0-dev"\n'
    )
    return clone


def test_auto_link_no_op_when_streamtex_not_registered(monkeypatch, tmp_path: Path):
    project = _make_project(tmp_path)
    console = MagicMock()
    # GlobalDevConfig with no streamtex entry
    monkeypatch.setattr(
        dev_cmd.GlobalDevConfig,
        "load",
        classmethod(lambda cls: MagicMock(repos={})),
    )
    assert dev_cmd.auto_link_streamtex_if_registered(project, console) is False
    # No source written.
    assert "streamtex" not in _read_sources(project)


def test_auto_link_writes_uv_source_when_registered(monkeypatch, tmp_path: Path):
    project = _make_project(tmp_path)
    clone = _fake_streamtex_clone(tmp_path)
    console = MagicMock()
    monkeypatch.setattr(
        dev_cmd.GlobalDevConfig,
        "load",
        classmethod(lambda cls: MagicMock(repos={"streamtex": str(clone)})),
    )
    # Don't actually invoke `uv sync` in the test — replace with a no-op.
    monkeypatch.setattr(dev_cmd, "_uv_sync", lambda *a, **kw: None)
    assert dev_cmd.auto_link_streamtex_if_registered(project, console) is True
    sources = _read_sources(project)
    assert sources["streamtex"] == {"path": str(clone), "editable": True}


def test_auto_link_appends_marker_to_gitignore(monkeypatch, tmp_path: Path):
    project = _make_project(tmp_path)
    clone = _fake_streamtex_clone(tmp_path)
    console = MagicMock()
    monkeypatch.setattr(
        dev_cmd.GlobalDevConfig,
        "load",
        classmethod(lambda cls: MagicMock(repos={"streamtex": str(clone)})),
    )
    monkeypatch.setattr(dev_cmd, "_uv_sync", lambda *a, **kw: None)
    dev_cmd.auto_link_streamtex_if_registered(project, console)
    gi_text = (project / ".gitignore").read_text(encoding="utf-8")
    assert ".stx-dev.json" in gi_text


def test_auto_link_warns_when_registered_path_invalid(monkeypatch, tmp_path: Path):
    """A registered path that no longer points at a valid streamtex clone must
    return False and surface the validation error (rather than crashing)."""
    project = _make_project(tmp_path)
    bogus = tmp_path / "not-a-streamtex-clone"
    bogus.mkdir()
    console = MagicMock()
    monkeypatch.setattr(
        dev_cmd.GlobalDevConfig,
        "load",
        classmethod(lambda cls: MagicMock(repos={"streamtex": str(bogus)})),
    )
    monkeypatch.setattr(dev_cmd, "_uv_sync", lambda *a, **kw: None)
    assert dev_cmd.auto_link_streamtex_if_registered(project, console) is False
    assert "streamtex" not in _read_sources(project)
    # The console got a warning print.
    assert console.print.called
