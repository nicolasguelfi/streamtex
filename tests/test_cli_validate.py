"""Tests for `stx validate` aggregate command."""

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


def test_validate_runs_on_empty_project(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["validate"], project)
    # Empty project = no packs to validate; should return 0 with friendly output
    assert result.exit_code == 0, result.output


def test_validate_outputs_sections(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["validate"], project)
    assert result.exit_code == 0
    assert "Packs" in result.output
    assert "Components" in result.output
