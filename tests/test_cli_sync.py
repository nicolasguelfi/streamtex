"""Tests for stx sync — project-level deterministic dependency sync."""

import os
from unittest.mock import patch

from click.testing import CliRunner

from streamtex.cli.commands import cli


def _write_pyproject(d, name="proj"):
    (d / "pyproject.toml").write_text(f'[project]\nname = "{name}"\n')


def test_sync_defaults_to_locked(tmp_path):
    """stx sync in a project dir runs uv sync --locked."""
    _write_pyproject(tmp_path, "proj")

    with (
        patch("streamtex.cli.sync_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.sync_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["sync"])

    assert result.exit_code == 0, result.output
    assert mock_run.call_count == 1
    cmd = mock_run.call_args.args[0]
    assert cmd[1] == "sync"
    assert "--locked" in cmd


def test_sync_upgrade_deps_drops_locked(tmp_path):
    """stx sync --upgrade-deps runs plain uv sync."""
    _write_pyproject(tmp_path, "proj")

    with (
        patch("streamtex.cli.sync_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.sync_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["sync", "--upgrade-deps"])

    assert result.exit_code == 0, result.output
    cmd = mock_run.call_args.args[0]
    assert "--locked" not in cmd


def test_sync_walks_up_to_find_pyproject(tmp_path):
    """stx sync from a subdirectory finds the parent pyproject.toml."""
    _write_pyproject(tmp_path, "proj")
    sub = tmp_path / "sub" / "deeper"
    sub.mkdir(parents=True)

    with (
        patch("streamtex.cli.sync_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.sync_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(sub)
        result = runner.invoke(cli, ["sync"])

    assert result.exit_code == 0, result.output
    assert mock_run.call_args.kwargs["cwd"] == str(tmp_path)


def test_sync_fails_when_no_pyproject(tmp_path):
    """stx sync exits with an error when no pyproject.toml is found."""
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(cli, ["sync"])
    assert result.exit_code != 0
    assert "No pyproject.toml" in result.output


def test_sync_hint_on_locked_failure(tmp_path):
    """When uv sync --locked fails with a lock-related error, hint user to --upgrade-deps."""
    _write_pyproject(tmp_path, "proj")

    with (
        patch("streamtex.cli.sync_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.sync_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "error: lock file is out of date"
        runner = CliRunner()
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["sync"])

    assert result.exit_code != 0
    assert "--upgrade-deps" in result.output


def test_sync_accepts_path_argument(tmp_path):
    """stx sync <path> uses the specified directory."""
    project = tmp_path / "myproj"
    project.mkdir()
    _write_pyproject(project, "myproj")

    with (
        patch("streamtex.cli.sync_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.sync_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["sync", str(project)])

    assert result.exit_code == 0, result.output
    assert mock_run.call_args.kwargs["cwd"] == str(project)
