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


def test_ds_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["ds", "--help"])
    assert result.exit_code == 0
    for sub in ("list", "show", "switch", "validate"):
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
