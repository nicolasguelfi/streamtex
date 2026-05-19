"""Tests for the `_add_default_design_pack` helper."""

from __future__ import annotations

import tomllib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from streamtex.cli.install_cmd import (
    _DEFAULT_DESIGN_PACK,
    _DESIGN_PACK_PRESETS,
    _add_default_design_pack,
)


def _bootstrap_project(tmp_path: Path, name: str = "demo") -> Path:
    """Create a workspace skeleton with a projects/<name>/stx.toml."""
    ws_root = tmp_path / "ws"
    proj_dir = ws_root / "projects" / name
    proj_dir.mkdir(parents=True)
    (proj_dir / "stx.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
    )
    return ws_root


def test_design_pack_added_for_standard_preset(tmp_path):
    ws_root = _bootstrap_project(tmp_path)
    console = MagicMock()
    _add_default_design_pack(str(ws_root), "demo", "standard", console)

    stx_toml = (ws_root / "projects" / "demo" / "stx.toml").read_text()
    data = tomllib.loads(stx_toml)
    packs = data.get("packs", [])
    assert len(packs) == 1
    entry = packs[0]
    assert entry["name"] == _DEFAULT_DESIGN_PACK["name"]
    assert entry["type"] == "git"
    assert entry["rev"] == _DEFAULT_DESIGN_PACK["rev"]


@pytest.mark.parametrize("preset", sorted(_DESIGN_PACK_PRESETS))
def test_design_pack_added_for_opt_in_presets(tmp_path, preset):
    ws_root = _bootstrap_project(tmp_path, name=f"demo_{preset}")
    console = MagicMock()
    _add_default_design_pack(str(ws_root), f"demo_{preset}", preset, console)

    stx_toml = (ws_root / "projects" / f"demo_{preset}" / "stx.toml").read_text()
    data = tomllib.loads(stx_toml)
    assert any(p["name"] == "streamtex-design" for p in data.get("packs", []))


@pytest.mark.parametrize("preset", ["basic", "user"])
def test_design_pack_skipped_for_minimal_presets(tmp_path, preset):
    ws_root = _bootstrap_project(tmp_path, name=f"demo_{preset}")
    console = MagicMock()
    _add_default_design_pack(str(ws_root), f"demo_{preset}", preset, console)

    stx_toml = (ws_root / "projects" / f"demo_{preset}" / "stx.toml").read_text()
    data = tomllib.loads(stx_toml)
    assert not data.get("packs"), "minimal presets must not auto-add packs"


def test_design_pack_idempotent(tmp_path):
    ws_root = _bootstrap_project(tmp_path)
    console = MagicMock()
    _add_default_design_pack(str(ws_root), "demo", "developer", console)
    _add_default_design_pack(str(ws_root), "demo", "developer", console)

    data = tomllib.loads(
        (ws_root / "projects" / "demo" / "stx.toml").read_text()
    )
    streamtex_design = [p for p in data["packs"] if p["name"] == "streamtex-design"]
    assert len(streamtex_design) == 1


def test_design_pack_skipped_when_stx_toml_missing(tmp_path):
    ws_root = tmp_path / "ws"
    (ws_root / "projects" / "demo").mkdir(parents=True)
    console = MagicMock()
    _add_default_design_pack(str(ws_root), "demo", "standard", console)
    assert not (ws_root / "projects" / "demo" / "stx.toml").exists()
