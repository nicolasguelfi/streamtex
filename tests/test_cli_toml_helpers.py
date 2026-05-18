"""Unit tests for the shared _toml_helpers (rebaselinage 2026-05-18 §29.4 step 0)."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from streamtex.cli._toml_helpers import (
    get_uv_sources,
    remove_uv_source,
    set_uv_source,
)


def _write_pyproject(tmp: Path, body: str) -> None:
    (tmp / "pyproject.toml").write_text(body)


def test_set_uv_source_creates_section(tmp_path: Path):
    _write_pyproject(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n',
    )
    set_uv_source(tmp_path, "mypack", "./mypack", editable=True)
    with (tmp_path / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    assert data["tool"]["uv"]["sources"]["mypack"] == {"path": "./mypack", "editable": True}


def test_set_uv_source_preserves_other_entries(tmp_path: Path):
    _write_pyproject(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
        '\n[tool.uv.sources]\n'
        'streamtex = { path = "../streamtex", editable = true }\n',
    )
    set_uv_source(tmp_path, "mypack", "./mypack")
    sources = get_uv_sources(tmp_path)
    assert "streamtex" in sources
    assert "mypack" in sources


def test_set_uv_source_updates_existing(tmp_path: Path):
    _write_pyproject(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n',
    )
    set_uv_source(tmp_path, "mypack", "./old")
    set_uv_source(tmp_path, "mypack", "./new")
    sources = get_uv_sources(tmp_path)
    assert sources["mypack"]["path"] == "./new"


def test_remove_uv_source(tmp_path: Path):
    _write_pyproject(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n',
    )
    set_uv_source(tmp_path, "mypack", "./mypack")
    assert remove_uv_source(tmp_path, "mypack") is True
    sources = get_uv_sources(tmp_path)
    assert "mypack" not in sources
    # Removing again is a no-op
    assert remove_uv_source(tmp_path, "mypack") is False


def test_set_uv_source_no_pyproject_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        set_uv_source(tmp_path, "x", "./x")


def test_round_trip_preserves_other_keys(tmp_path: Path):
    _write_pyproject(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
        '\n[tool.uv]\nmanaged = true\n',
    )
    set_uv_source(tmp_path, "mypack", "./mypack")
    text = (tmp_path / "pyproject.toml").read_text()
    assert "managed = true" in text
    assert 'name = "demo"' in text
