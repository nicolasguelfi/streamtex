"""Tests for stx workspace init/clone/link/status/sync commands."""

import os
from unittest.mock import patch

from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.workspace_cmd import generate_stx_toml, load_stx_toml


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


# ---------------------------------------------------------------------------
# stx.toml generation
# ---------------------------------------------------------------------------

def test_generate_stx_toml():
    content = generate_stx_toml("test-ws", "2026-01-01T00:00:00Z")
    assert "[workspace]" in content
    assert 'name = "test-ws"' in content
    assert "[repos]" in content
    assert "[deploy]" in content
    assert "[claude]" in content

    data = tomllib.loads(content)
    assert data["workspace"]["name"] == "test-ws"


def test_generate_stx_toml_has_repos():
    content = generate_stx_toml("ws", "2026-01-01T00:00:00Z")
    data = tomllib.loads(content)

    repos = data["repos"]
    assert "streamtex" in repos
    assert repos["streamtex"]["type"] == "library"
    assert repos["streamtex"]["url"].endswith(".git")
    assert repos["streamtex"]["path"] == "streamtex"

    assert "streamtex-docs" in repos
    assert repos["streamtex-docs"]["type"] == "docs"

    assert "streamtex-claude" in repos
    assert repos["streamtex-claude"]["type"] == "claude"

    # claude section references the source
    assert data["claude"]["source"] == "streamtex-claude"


# ---------------------------------------------------------------------------
# load / init
# ---------------------------------------------------------------------------

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

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert "workspace" in data
    assert "repos" in data
    assert "deploy" in data
    assert "claude" in data
    # New: verify repos have proper structure
    assert "streamtex" in data["repos"]
    assert data["repos"]["streamtex"]["type"] == "library"


def test_init_custom_name(tmp_path):
    target = tmp_path / "ws"
    runner = CliRunner()
    runner.invoke(cli, ["workspace", "init", str(target), "--name", "custom-name"])

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["name"] == "custom-name"


def test_init_default_name(tmp_path):
    target = tmp_path / "my-project"
    runner = CliRunner()
    runner.invoke(cli, ["workspace", "init", str(target)])

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


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def test_status_outside_workspace(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["workspace", "status"])
    assert result.exit_code != 0
    assert "stx.toml" in result.output


# ---------------------------------------------------------------------------
# clone
# ---------------------------------------------------------------------------

def _write_stx_toml(ws: os.PathLike) -> None:
    """Write a minimal stx.toml into *ws*."""
    content = generate_stx_toml("test-ws", "2026-01-01T00:00:00Z")
    (ws / "stx.toml").write_text(content)  # type: ignore[union-attr]


def test_clone_clones_repos(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws)

    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""
        return _R()

    with patch("streamtex.cli.workspace_cmd.subprocess.run", side_effect=fake_run):
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=ws):
            os.chdir(ws)
            result = runner.invoke(cli, ["workspace", "clone"])

    assert result.exit_code == 0
    # Should have called git clone for each repo
    git_calls = [c for c in calls if c[0] == "git"]
    assert len(git_calls) == 3  # streamtex, streamtex-docs, streamtex-claude
    assert "cloned" in result.output


def test_clone_skips_existing(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws)

    # Pre-create one repo directory
    (ws / "streamtex").mkdir()

    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""
        return _R()

    with patch("streamtex.cli.workspace_cmd.subprocess.run", side_effect=fake_run):
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=ws):
            os.chdir(ws)
            result = runner.invoke(cli, ["workspace", "clone"])

    assert result.exit_code == 0
    git_calls = [c for c in calls if c[0] == "git"]
    assert len(git_calls) == 2  # streamtex skipped
    assert "already exists" in result.output


def test_clone_outside_workspace(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["workspace", "clone"])
    assert result.exit_code != 0
    assert "stx.toml" in result.output


# ---------------------------------------------------------------------------
# link / sync
# ---------------------------------------------------------------------------

def _create_workspace_with_repos(tmp_path):
    """Create a workspace with fake repo directories and pyproject.toml files."""
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws)

    # Create repo directories with pyproject.toml
    for name in ("streamtex", "streamtex-docs", "streamtex-claude"):
        repo = ws / name
        repo.mkdir()
        (repo / "pyproject.toml").write_text(f'[project]\nname = "{name}"\n')

    return ws


def test_link_runs_uv_sync(tmp_path):
    ws = _create_workspace_with_repos(tmp_path)

    sync_dirs: list[str] = []

    def fake_run(cmd, **kwargs):
        if cmd[-1] == "sync":
            sync_dirs.append(kwargs.get("cwd", ""))

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""
        return _R()

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "link"])

    assert result.exit_code == 0
    # link only syncs docs and project repos (not library or claude)
    assert len(sync_dirs) == 1  # only streamtex-docs (type=docs)
    assert sync_dirs[0].endswith("streamtex-docs")


def test_sync_runs_all_repos(tmp_path):
    ws = _create_workspace_with_repos(tmp_path)

    sync_dirs: list[str] = []

    def fake_run(cmd, **kwargs):
        if cmd[-1] == "sync":
            sync_dirs.append(kwargs.get("cwd", ""))

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""
        return _R()

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "sync"])

    assert result.exit_code == 0
    # sync runs in ALL repos
    assert len(sync_dirs) == 3


def test_sync_outside_workspace(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["workspace", "sync"])
    assert result.exit_code != 0
    assert "stx.toml" in result.output
