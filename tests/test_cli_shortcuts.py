"""Tests for stx test/lint shortcut commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from streamtex.cli.commands import cli


@patch("streamtex.cli.shortcuts.subprocess.run")
def test_test_runs_pytest(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    runner = CliRunner()
    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 0
    args = mock_run.call_args[0][0]
    assert "-m" in args
    assert "pytest" in args
    assert "tests/" in args


@patch("streamtex.cli.shortcuts.subprocess.run")
def test_test_verbose(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    runner = CliRunner()
    result = runner.invoke(cli, ["test", "-v"])
    assert result.exit_code == 0
    args = mock_run.call_args[0][0]
    assert "-v" in args


@patch("streamtex.cli.shortcuts.subprocess.run")
def test_test_propagates_exit_code(mock_run):
    mock_run.return_value = MagicMock(returncode=1)
    runner = CliRunner()
    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 1


@patch("streamtex.cli.shortcuts.subprocess.run")
def test_lint_runs_ruff(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    runner = CliRunner()
    result = runner.invoke(cli, ["lint"])
    assert result.exit_code == 0
    args = mock_run.call_args[0][0]
    assert "-m" in args
    assert "ruff" in args
    assert "check" in args
    assert "streamtex/" in args
