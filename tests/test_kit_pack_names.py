"""A kit reference accepts either name of its pack (#31).

A pack has an entry-point name (``streamtex-pack-fake``) and a module
(``stx_fake_pack``). ``stx kit`` matched only the first, ``stx project new
--kit`` imported only the second.
"""

from __future__ import annotations

import os
import sys
import tomllib
from importlib import metadata
from pathlib import Path

import pytest
from click.testing import CliRunner

from streamtex.cli._shared import _resolve_pack_token
from streamtex.cli.commands import cli

PACK = "streamtex-pack-fake"
MODULE = "stx_fake_pack"


@pytest.fixture
def fake_pack(tmp_path, monkeypatch):
    """Install a pack with one kit, visible through the streamtex.packs entry point."""
    root = tmp_path / "site"
    pkg = root / MODULE
    (pkg / "kits").mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "_pack_manifest.toml").write_text(f'name = "{PACK}"\nversion = "0.1.0"\n')
    (pkg / "kits" / "demo.toml").write_text('name = "demo"\n\n[design_system]\nref = "dark"\n')
    monkeypatch.syspath_prepend(str(root))
    ep = metadata.EntryPoint(name=PACK, value=MODULE, group="streamtex.packs")
    real = metadata.entry_points

    def entry_points(**kw):
        if kw.get("group") == "streamtex.packs":
            return metadata.EntryPoints([ep])
        return real(**kw)

    monkeypatch.setattr(metadata, "entry_points", entry_points)
    yield
    sys.modules.pop(MODULE, None)


def _run(args, cwd: Path):
    prev = os.getcwd()
    os.chdir(cwd)
    try:
        return CliRunner().invoke(cli, args)
    finally:
        os.chdir(prev)


def _project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n')
    (proj / "stx.toml").write_text('[project]\nname = "demo"\n')
    return proj


def test_resolver_accepts_both_names(fake_pack):
    assert _resolve_pack_token(PACK) == (PACK, MODULE)
    assert _resolve_pack_token(MODULE) == (PACK, MODULE)
    assert _resolve_pack_token("unknown") == ("unknown", "unknown")


@pytest.mark.parametrize("token", [PACK, MODULE])
def test_kit_show_and_install_accept_both_names(fake_pack, tmp_path, token):
    proj = _project(tmp_path)
    shown = _run(["kit", "show", f"{token}:demo"], proj)
    assert shown.exit_code == 0, shown.output
    installed = _run(["kit", "install", f"{token}:demo"], proj)
    assert installed.exit_code == 0, installed.output
    data = tomllib.loads((proj / "stx.toml").read_text())
    assert data["kit"]["use"] == f"{PACK}:demo"
    assert data["design_system"]["use"] == f"{PACK}:dark"


@pytest.mark.parametrize("token", [PACK, MODULE])
def test_project_new_kit_accepts_both_names(fake_pack, tmp_path, token):
    result = _run(
        ["project", "new", "demo", "--kit", f"{token}:demo",
         "--no-claude", "--no-sync", "--no-git", "--no-mypack"],
        tmp_path,
    )
    assert result.exit_code == 0, result.output
    assert "not installed" not in result.output
    data = tomllib.loads((tmp_path / "demo" / "stx.toml").read_text())
    pack = next(p for p in data["packs"] if p["type"] == "git")
    assert pack["name"] == PACK
    assert pack["ref"] == "github.com/nicolasguelfi/streamtex-packs"
    assert pack["subdirectory"] == PACK
    assert data["kit"]["ref"] == f"{PACK}:demo"
    assert data["design_system"]["ref"] == "dark"
    styles = (tmp_path / "demo" / "custom" / "styles.py").read_text()
    assert f"from {MODULE}.design_systems.dark import" in styles
