"""Tests for `stx component`."""

from __future__ import annotations

import os
from pathlib import Path

from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.component_cmd import _classify_destination


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


def test_component_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["component", "--help"])
    assert result.exit_code == 0
    for sub in ("list", "show", "validate", "find", "new", "promote"):
        assert sub in result.output


def test_classify_destination_primary_local():
    entry = {"type": "local", "name": "mypack", "primary": True, "path": "./mypack"}
    assert _classify_destination(entry) == "primary_local"


def test_classify_destination_pypi():
    entry = {"type": "pypi", "name": "x", "constraint": ">=0.1"}
    assert _classify_destination(entry) == "pypi"


def test_classify_destination_git():
    entry = {"type": "git", "ref": "github.com/x/y", "rev": "main"}
    assert _classify_destination(entry) == "git_remote"


def test_classify_destination_secondary_local_with_git(tmp_path: Path):
    sec = tmp_path / "sec"
    (sec / ".git").mkdir(parents=True)
    entry = {"type": "local", "name": "sec", "path": str(sec), "primary": False}
    assert _classify_destination(entry) == "secondary_local_with_git"


def test_classify_destination_secondary_local_no_git(tmp_path: Path):
    sec = tmp_path / "sec"
    sec.mkdir()
    entry = {"type": "local", "name": "sec", "path": str(sec), "primary": False}
    # No .git → behaves like primary (copy only, no commit)
    assert _classify_destination(entry) == "primary_local"


def test_promote_to_pypi_refused(tmp_path: Path):
    """PR001 — promotion to a PyPI destination is refused."""
    project = _make_project(tmp_path)
    _run(["pack", "add", "pypi:somepack@>=0.1"], project)
    result = _run(["component", "promote", "any", "--to", "somepack"], project)
    assert result.exit_code != 0
    assert "PR001" in result.output


def test_component_new_requires_primary_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    # No primary local pack declared yet
    result = _run(["component", "new", "callout"], project)
    assert result.exit_code != 0
    assert "primary" in result.output.lower()


def test_component_new_into_primary_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "new", "mypack"], project)
    _run(["pack", "set-primary", "mypack"], project)
    result = _run(["component", "new", "demo_block", "--granularity", "block"], project)
    assert result.exit_code == 0, result.output
    target = project / "mypack" / "mypack" / "components" / "demo_block.py"
    assert target.is_file()
    text = target.read_text()
    assert '"name": "demo_block"' in text
    assert '"granularity": "block"' in text
