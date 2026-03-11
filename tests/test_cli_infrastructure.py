"""Tests for stx CLI infrastructure: help, version, command groups."""

from click.testing import CliRunner

from streamtex.cli.commands import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "StreamTeX CLI" in result.output


def test_cli_version():
    from streamtex import __version__

    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_top_level_commands_exist():
    """stx install, stx update, stx status are top-level commands."""
    runner = CliRunner()

    result = runner.invoke(cli, ["install", "--help"])
    assert result.exit_code == 0
    assert "--preset" in result.output
    assert "--project" in result.output

    result = runner.invoke(cli, ["update", "--help"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["status", "--help"])
    assert result.exit_code == 0


def test_bib_group_exists():
    runner = CliRunner()
    result = runner.invoke(cli, ["bib", "--help"])
    assert result.exit_code == 0
    assert "generate-stubs" in result.output


def test_unknown_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["nonexistent-command"])
    assert result.exit_code != 0
