"""Tests for `stx pack`."""

from __future__ import annotations

import os
from pathlib import Path

from click.testing import CliRunner

from streamtex.cli.commands import cli


def _make_project(tmp_path: Path) -> Path:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "0.1.0"\n')
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


def test_pack_help_lists_subcommands():
    runner = CliRunner()
    result = runner.invoke(cli, ["pack", "--help"])
    assert result.exit_code == 0
    for sub in ("add", "remove", "list", "sync", "info", "validate", "new", "set-primary"):
        assert sub in result.output


def test_pack_add_git_ref(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "git:github.com/x/y@v0.1.0"], project)
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'type = "git"' in stx_toml
    assert "github.com/x/y" in stx_toml


def test_pack_add_pypi_ref(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "pypi:streamtex-pack-x@>=0.1,<0.2"], project)
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'type = "pypi"' in stx_toml


def test_pack_new_creates_local_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "new", "mypack"], project)
    assert result.exit_code == 0, result.output
    pkg_root = project / "mypack" / "mypack"
    assert (pkg_root / "_pack_manifest.toml").is_file()
    assert (pkg_root / "components").is_dir()
    assert (pkg_root / "design_systems").is_dir()
    # Declared in stx.toml
    stx_toml = (project / "stx.toml").read_text()
    assert 'name = "mypack"' in stx_toml


def test_pack_set_primary_round_trip(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "new", "a"], project)
    _run(["pack", "new", "b"], project)
    r1 = _run(["pack", "set-primary", "b"], project)
    assert r1.exit_code == 0, r1.output
    stx_toml = (project / "stx.toml").read_text()
    # b should be primary
    assert "primary = true" in stx_toml


def test_pack_remove(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "add", "git:github.com/x/y@v0.1.0"], project)
    result = _run(["pack", "remove", "y"], project)
    assert result.exit_code == 0, result.output
    assert "github.com/x/y" not in (project / "stx.toml").read_text()


def test_pack_add_unsupported_ref(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "not-a-ref"], project)
    assert result.exit_code != 0
    assert "Unsupported" in result.output or "git:" in result.output


def test_pack_add_dev_local_with_manifest(tmp_path: Path):
    project = _make_project(tmp_path)
    # First create a valid local pack
    _run(["pack", "new", "auxpack"], project)
    # Drop a stub component so the pack satisfies PV009
    (project / "auxpack" / "auxpack" / "components" / "stub.py").write_text("# stub\n")
    # Remove its [[packs]] entry so we can re-add via --dev
    _run(["pack", "remove", "auxpack"], project)
    result = _run(["pack", "add", "--dev", str(project / "auxpack" / "auxpack")], project)
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'name = "auxpack"' in stx_toml
    assert "editable = true" in stx_toml


def test_pack_add_dev_missing_path_fails(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "--dev", "/does/not/exist"], project)
    assert result.exit_code != 0
    assert "does not exist" in result.output
