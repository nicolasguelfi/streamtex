"""Tests for stx CLI infrastructure: help, version, command groups."""

from click.testing import CliRunner

from streamtex.cli.commands import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "StreamTeX CLI" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.3.0" in result.output


def test_workspace_group_exists():
    runner = CliRunner()
    result = runner.invoke(cli, ["workspace", "--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "status" in result.output


def test_bib_group_exists():
    runner = CliRunner()
    result = runner.invoke(cli, ["bib", "--help"])
    assert result.exit_code == 0
    assert "generate-stubs" in result.output


def test_unknown_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["nonexistent-command"])
    assert result.exit_code != 0
