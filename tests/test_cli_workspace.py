"""Tests for stx workspace init/status commands."""

import os

from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.workspace_cmd import generate_stx_toml, load_stx_toml


def test_generate_stx_toml():
    content = generate_stx_toml("test-ws", "2026-01-01T00:00:00Z")
    assert "[workspace]" in content
    assert 'name = "test-ws"' in content
    assert "[repos]" in content
    assert "[deploy]" in content
    assert "[claude]" in content

    # Verify it parses as valid TOML
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]
    data = tomllib.loads(content)
    assert data["workspace"]["name"] == "test-ws"


def test_load_stx_toml(tmp_path):
    toml_content = generate_stx_toml("loaded-ws", "2026-01-01T00:00:00Z")
    toml_file = tmp_path / "stx.toml"
    toml_file.write_text(toml_content)

    data = load_stx_toml(str(tmp_path))
    assert data["workspace"]["name"] == "loaded-ws"


def test_load_stx_toml_missing(tmp_path):
    import click
    import pytest

    with pytest.raises(click.ClickException, match="stx.toml not found"):
        load_stx_toml(str(tmp_path))


def test_init_creates_stx_toml(tmp_path):
    target = tmp_path / "my-workspace"
    runner = CliRunner()
    result = runner.invoke(cli, ["workspace", "init", str(target)])
    assert result.exit_code == 0
    assert (target / "stx.toml").is_file()
    assert (target / "projects").is_dir()


def test_init_toml_valid(tmp_path):
    target = tmp_path / "ws"
    runner = CliRunner()
    runner.invoke(cli, ["workspace", "init", str(target)])

    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert "workspace" in data
    assert "repos" in data
    assert "deploy" in data
    assert "claude" in data


def test_init_custom_name(tmp_path):
    target = tmp_path / "ws"
    runner = CliRunner()
    runner.invoke(cli, ["workspace", "init", str(target), "--name", "custom-name"])

    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["name"] == "custom-name"


def test_init_default_name(tmp_path):
    target = tmp_path / "my-project"
    runner = CliRunner()
    runner.invoke(cli, ["workspace", "init", str(target)])

    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["name"] == "my-project"


def test_init_creates_directory(tmp_path):
    target = tmp_path / "new" / "nested" / "ws"
    runner = CliRunner()
    result = runner.invoke(cli, ["workspace", "init", str(target)])
    assert result.exit_code == 0
    assert target.is_dir()


def test_init_refuses_existing(tmp_path):
    target = tmp_path / "ws"
    target.mkdir()
    (target / "stx.toml").write_text("[workspace]\nname = 'old'\n")

    runner = CliRunner()
    result = runner.invoke(cli, ["workspace", "init", str(target)])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_status_outside_workspace(tmp_path):
    runner = CliRunner()
    # Run from a temp dir that has no stx.toml
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["workspace", "status"])
    assert result.exit_code != 0
    assert "stx.toml" in result.output
