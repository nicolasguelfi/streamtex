"""Tests for `dev_cmd._add_uv_source` / `_remove_uv_source` delegating to D17 helpers.

These tests verify the multi-pack correctness fix: editing the streamtex source
must NOT wipe sibling entries in `[tool.uv.sources]` (e.g. `mypack`,
`streamtex-design`).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from streamtex.cli.dev_cmd import _add_uv_source, _remove_uv_source


def _write(tmp: Path, body: str) -> None:
    (tmp / "pyproject.toml").write_text(body)


def _read(tmp: Path) -> dict:
    with (tmp / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)


def test_add_uv_source_preserves_sibling_entries(tmp_path: Path):
    _write(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
        '\n[tool.uv.sources]\n'
        'mypack = { path = "./mypack", editable = true }\n'
        'streamtex-design = { path = "../streamtex-design", editable = true }\n',
    )
    _add_uv_source(tmp_path, "/some/path/streamtex")
    data = _read(tmp_path)
    sources = data["tool"]["uv"]["sources"]
    assert sources["streamtex"] == {"path": "/some/path/streamtex", "editable": True}
    assert sources["mypack"] == {"path": "./mypack", "editable": True}
    assert sources["streamtex-design"] == {"path": "../streamtex-design", "editable": True}


def test_add_uv_source_creates_section_when_missing(tmp_path: Path):
    _write(tmp_path, '[project]\nname = "demo"\nversion = "0.1.0"\n')
    _add_uv_source(tmp_path, "/abs/path")
    data = _read(tmp_path)
    assert data["tool"]["uv"]["sources"]["streamtex"] == {
        "path": "/abs/path",
        "editable": True,
    }


def test_add_uv_source_updates_existing_streamtex_entry(tmp_path: Path):
    _write(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
        '\n[tool.uv.sources]\n'
        'streamtex = { path = "/old/path", editable = true }\n',
    )
    _add_uv_source(tmp_path, "/new/path")
    data = _read(tmp_path)
    assert data["tool"]["uv"]["sources"]["streamtex"]["path"] == "/new/path"


def test_remove_uv_source_targets_streamtex_only(tmp_path: Path):
    _write(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
        '\n[tool.uv.sources]\n'
        'streamtex = { path = "/some/path", editable = true }\n'
        'mypack = { path = "./mypack", editable = true }\n',
    )
    _remove_uv_source(tmp_path)
    data = _read(tmp_path)
    sources = data["tool"]["uv"]["sources"]
    assert "streamtex" not in sources
    assert sources["mypack"] == {"path": "./mypack", "editable": True}


def test_remove_uv_source_drops_empty_section(tmp_path: Path):
    _write(
        tmp_path,
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
        '\n[tool.uv.sources]\n'
        'streamtex = { path = "/some/path", editable = true }\n',
    )
    _remove_uv_source(tmp_path)
    data = _read(tmp_path)
    # Section should be removed when empty
    assert data.get("tool", {}).get("uv", {}).get("sources", {}) == {}


def test_remove_uv_source_when_absent_is_noop(tmp_path: Path):
    _write(tmp_path, '[project]\nname = "demo"\nversion = "0.1.0"\n')
    _remove_uv_source(tmp_path)  # must not raise
    data = _read(tmp_path)
    assert data["project"]["name"] == "demo"
