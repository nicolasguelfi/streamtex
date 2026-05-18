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


def test_kit_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["kit", "--help"])
    assert result.exit_code == 0
    for sub in ("list", "show", "validate", "install"):
        assert sub in result.output


def test_kit_show_no_colon_fails(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["kit", "show", "default"], project)
    assert result.exit_code != 0
