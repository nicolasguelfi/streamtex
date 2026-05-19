"""Tests for `stx ds`."""

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


def test_ds_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["ds", "--help"])
    assert result.exit_code == 0
    for sub in ("list", "show", "switch", "new", "validate"):
        assert sub in result.output


def test_ds_switch(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["ds", "switch", "streamtex_design:modern_dark"], project)
    assert result.exit_code == 0, result.output
    text = (project / "stx.toml").read_text()
    assert "streamtex_design:modern_dark" in text


def test_ds_show_unqualified_ref_fails(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["ds", "show", "default"], project)
    assert result.exit_code != 0
    assert "<pack>:<name>" in result.output


def test_ds_new_into_primary_local(tmp_path: Path):
    project = _make_project_with_primary_pack(tmp_path)
    result = _run(["ds", "new", "mytheme"], project)
    assert result.exit_code == 0, result.output
    init = project / "mypack" / "design_systems" / "mytheme" / "__init__.py"
    assert init.is_file()
    content = init.read_text()
    assert 'name = "mytheme"' in content
    assert "class DesignSystem" in content


def test_ds_new_refuses_when_no_primary(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["ds", "new", "mytheme"], project)
    assert result.exit_code != 0
    assert "primary local pack" in result.output


def test_ds_new_refuses_non_local_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    (project / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "git"\nname = "remote_pack"\nref = "github.com/x/y"\nrev = "v0.1.0"\n'
    )
    result = _run(["ds", "new", "mytheme", "--pack", "remote_pack"], project)
    assert result.exit_code != 0
    assert "type='git'" in result.output or "only supported in local packs" in result.output


def test_ds_new_refuses_existing(tmp_path: Path):
    project = _make_project_with_primary_pack(tmp_path)
    (project / "mypack" / "design_systems" / "mytheme").mkdir(parents=True)
    result = _run(["ds", "new", "mytheme"], project)
    assert result.exit_code != 0
    assert "already exists" in result.output
