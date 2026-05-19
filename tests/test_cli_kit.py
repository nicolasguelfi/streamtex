"""Tests for `stx kit`."""

from __future__ import annotations

import os
from pathlib import Path

from click.testing import CliRunner

from streamtex.cli.commands import cli


def _make_project(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n')
    (tmp_path / "stx.toml").write_text('[project]\nname = "demo"\n')
    return tmp_path


def _run(cmd: list[str], cwd: Path):
    runner = CliRunner()
    prev = os.getcwd()
    try:
        os.chdir(cwd)
        return runner.invoke(cli, cmd)
    finally:
        os.chdir(prev)


def _make_project_with_primary_pack(tmp_path: Path, pack_name: str = "mypack") -> Path:
    project = _make_project(tmp_path)
    (project / pack_name).mkdir()
    (project / pack_name / "__init__.py").write_text("")
    (project / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        f'[[packs]]\ntype = "local"\nname = "{pack_name}"\npath = "{pack_name}"\nprimary = true\n'
    )
    return project


def test_kit_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["kit", "--help"])
    assert result.exit_code == 0
    for sub in ("list", "show", "validate", "install", "new"):
        assert sub in result.output


def test_kit_show_no_colon_fails(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["kit", "show", "default"], project)
    assert result.exit_code != 0


def test_kit_new_into_primary_local(tmp_path: Path):
    project = _make_project_with_primary_pack(tmp_path)
    result = _run(["kit", "new", "mykit"], project)
    assert result.exit_code == 0, result.output
    kit_file = project / "mypack" / "kits" / "mykit.toml"
    assert kit_file.is_file()
    text = kit_file.read_text()
    assert 'name = "mykit"' in text
    assert 'ref = "default"' in text


def test_kit_new_custom_design_system(tmp_path: Path):
    project = _make_project_with_primary_pack(tmp_path)
    result = _run(["kit", "new", "mykit", "--design-system", "modern_dark"], project)
    assert result.exit_code == 0, result.output
    text = (project / "mypack" / "kits" / "mykit.toml").read_text()
    assert 'ref = "modern_dark"' in text


def test_kit_new_refuses_when_no_primary(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["kit", "new", "mykit"], project)
    assert result.exit_code != 0
    assert "primary local pack" in result.output


def test_kit_new_refuses_non_local_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    (project / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "git"\nname = "remote_pack"\nref = "github.com/x/y"\nrev = "v0.1.0"\n'
    )
    result = _run(["kit", "new", "mykit", "--pack", "remote_pack"], project)
    assert result.exit_code != 0
    assert "type='git'" in result.output or "only supported in local packs" in result.output


def test_kit_new_refuses_existing(tmp_path: Path):
    project = _make_project_with_primary_pack(tmp_path)
    (project / "mypack" / "kits").mkdir(parents=True)
    (project / "mypack" / "kits" / "mykit.toml").write_text("")
    result = _run(["kit", "new", "mykit"], project)
    assert result.exit_code != 0
    assert "already exists" in result.output
