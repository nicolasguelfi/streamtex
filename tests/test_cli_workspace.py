"""Tests for stx workspace init/update/status/upgrade commands (+ deprecated clone/link/sync/hooks)."""

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
    """Default preset is standard: 2 repos (docs + claude)."""
    content = generate_stx_toml("test-ws", "2026-01-01T00:00:00Z")
    assert "[workspace]" in content
    assert 'name = "test-ws"' in content
    assert 'preset = "standard"' in content
    assert "[repos]" in content
    assert "[deploy]" in content
    assert "[claude]" in content

    data = tomllib.loads(content)
    assert data["workspace"]["name"] == "test-ws"
    assert data["workspace"]["preset"] == "standard"


def test_generate_stx_toml_has_repos():
    """Default (standard) has docs + claude, not library."""
    content = generate_stx_toml("ws", "2026-01-01T00:00:00Z")
    data = tomllib.loads(content)

    repos = data["repos"]
    # standard preset: docs + claude only
    assert "streamtex" not in repos
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
    # Default preset is standard: docs + claude
    assert data["workspace"]["preset"] == "standard"
    assert "streamtex-docs" in data["repos"]
    assert "streamtex-claude" in data["repos"]
    assert "streamtex" not in data["repos"]


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

def _write_stx_toml(ws: os.PathLike, preset: str = "standard") -> None:
    """Write a stx.toml into *ws* with the given preset."""
    content = generate_stx_toml("test-ws", "2026-01-01T00:00:00Z", preset=preset)
    (ws / "stx.toml").write_text(content)  # type: ignore[union-attr]


def test_clone_clones_repos(tmp_path):
    """Default standard preset has 2 repos to clone."""
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
    git_calls = [c for c in calls if c[0] == "git"]
    assert len(git_calls) == 2  # streamtex-docs + streamtex-claude (standard)
    assert "cloned" in result.output


def test_clone_skips_existing(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws)

    # Pre-create one repo directory
    (ws / "streamtex-docs").mkdir()

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
    assert len(git_calls) == 1  # streamtex-docs skipped, only streamtex-claude
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

def _create_workspace_with_repos(tmp_path, preset="developer"):
    """Create a workspace with fake repo directories and pyproject.toml files."""
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset=preset)

    from streamtex.cli.workspace_cmd import ALL_REPOS, PRESET_REPOS

    # Create repo directories for the preset
    for repo_key in PRESET_REPOS[preset]:
        repo = ALL_REPOS[repo_key]
        repo_dir = ws / repo["path"]
        repo_dir.mkdir()
        (repo_dir / "pyproject.toml").write_text(
            f'[project]\nname = "{repo["name"]}"\n'
        )

    return ws


def test_link_runs_uv_sync(tmp_path):
    ws = _create_workspace_with_repos(tmp_path, preset="developer")

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
    ws = _create_workspace_with_repos(tmp_path, preset="developer")

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
    # sync runs in ALL repos (developer = 3)
    assert len(sync_dirs) == 3


def test_sync_outside_workspace(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["workspace", "sync"])
    assert result.exit_code != 0
    assert "stx.toml" in result.output


# ---------------------------------------------------------------------------
# Preset-specific generation tests
# ---------------------------------------------------------------------------

def test_generate_stx_toml_preset_basic():
    content = generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="basic")
    data = tomllib.loads(content)
    assert data["workspace"]["preset"] == "basic"
    assert len(data["repos"]) == 0


def test_generate_stx_toml_preset_user():
    content = generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="user")
    data = tomllib.loads(content)
    assert data["workspace"]["preset"] == "user"
    repos = data["repos"]
    assert "streamtex-claude" in repos
    assert "streamtex" not in repos
    assert "streamtex-docs" not in repos
    assert data["claude"]["source"] == "streamtex-claude"


def test_generate_stx_toml_preset_standard():
    content = generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="standard")
    data = tomllib.loads(content)
    assert data["workspace"]["preset"] == "standard"
    repos = data["repos"]
    assert "streamtex-docs" in repos
    assert "streamtex-claude" in repos
    assert "streamtex" not in repos
    assert data["claude"]["source"] == "streamtex-claude"


def test_generate_stx_toml_preset_developer():
    content = generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="developer")
    data = tomllib.loads(content)
    assert data["workspace"]["preset"] == "developer"
    repos = data["repos"]
    assert "streamtex" in repos
    assert repos["streamtex"]["type"] == "library"
    assert repos["streamtex"]["url"].endswith(".git")
    assert "streamtex-docs" in repos
    assert "streamtex-claude" in repos
    assert data["claude"]["source"] == "streamtex-claude"


def test_init_default_preset_is_standard(tmp_path):
    target = tmp_path / "ws"
    runner = CliRunner()
    result = runner.invoke(cli, ["workspace", "init", str(target)])
    assert result.exit_code == 0

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["preset"] == "standard"
    assert len(data["repos"]) == 2


def test_init_preset_basic(tmp_path):
    target = tmp_path / "ws"
    runner = CliRunner()
    result = runner.invoke(cli, ["workspace", "init", str(target), "--preset", "basic"])
    assert result.exit_code == 0

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["preset"] == "basic"
    assert len(data["repos"]) == 0


def test_clone_user_preset_clones_one_repo(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="user")

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
    assert len(git_calls) == 1  # only streamtex-claude


# ---------------------------------------------------------------------------
# Upgrade tests
# ---------------------------------------------------------------------------

def test_upgrade_basic_to_user(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="basic")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["workspace", "upgrade", "user"])

    assert result.exit_code == 0
    assert "Upgraded" in result.output
    assert "streamtex-claude" in result.output

    with open(ws / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["preset"] == "user"
    assert "streamtex-claude" in data["repos"]


def test_upgrade_user_to_standard(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="user")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["workspace", "upgrade", "standard"])

    assert result.exit_code == 0
    assert "Upgraded" in result.output

    with open(ws / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["preset"] == "standard"
    assert "streamtex-docs" in data["repos"]
    assert "streamtex-claude" in data["repos"]


def test_upgrade_standard_to_developer(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="standard")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["workspace", "upgrade", "developer"])

    assert result.exit_code == 0
    assert "Upgraded" in result.output

    with open(ws / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["preset"] == "developer"
    assert "streamtex" in data["repos"]
    assert "streamtex-docs" in data["repos"]
    assert "streamtex-claude" in data["repos"]


def test_upgrade_refuses_downgrade(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="developer")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["workspace", "upgrade", "user"])

    assert result.exit_code != 0
    assert "Cannot downgrade" in result.output


def test_upgrade_same_preset_noop(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="standard")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["workspace", "upgrade", "standard"])

    assert result.exit_code == 0
    assert "Already at" in result.output


def test_upgrade_output_says_update(tmp_path):
    """Upgrade output should say 'stx workspace update', not 'clone'."""
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="basic")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["workspace", "upgrade", "user"])

    assert result.exit_code == 0
    assert "stx workspace update" in result.output
    assert "stx workspace clone" not in result.output


# ---------------------------------------------------------------------------
# Deprecation warnings
# ---------------------------------------------------------------------------

def test_clone_shows_deprecation_warning(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws)

    with patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "clone"])

    assert "deprecated" in result.output.lower()
    assert "stx workspace update" in result.output


def test_sync_shows_deprecation_warning(tmp_path):
    ws = _create_workspace_with_repos(tmp_path, preset="standard")

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "sync"])

    assert "deprecated" in result.output.lower()
    assert "stx workspace update" in result.output


def test_link_shows_deprecation_warning(tmp_path):
    ws = _create_workspace_with_repos(tmp_path, preset="developer")

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "link"])

    assert "deprecated" in result.output.lower()
    assert "stx workspace update" in result.output


def test_hooks_shows_deprecation_warning(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    _write_stx_toml(ws, preset="standard")

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "hooks"])

    assert "deprecated" in result.output.lower()
    assert "stx workspace update" in result.output


# ---------------------------------------------------------------------------
# update command tests
# ---------------------------------------------------------------------------

def test_update_dry_run(tmp_path):
    """--dry-run shows steps without executing."""
    ws = _create_workspace_with_repos(tmp_path, preset="standard")
    # Create .git dirs so pull step finds them
    for repo_dir in [ws / "streamtex-docs", ws / "streamtex-claude"]:
        (repo_dir / ".git").mkdir()

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "update", "--dry-run"])

    assert result.exit_code == 0
    assert "dry run" in result.output.lower()
    assert "would git pull" in result.output
    # subprocess.run should NOT have been called for git pull
    git_pull_calls = [c for c in mock_run.call_args_list if "pull" in str(c)]
    assert len(git_pull_calls) == 0


def test_update_runs_all_steps(tmp_path):
    """Update runs all steps: pull, clone, sync, global commands, profiles, hooks."""
    ws = _create_workspace_with_repos(tmp_path, preset="standard")
    for repo_dir in [ws / "streamtex-docs", ws / "streamtex-claude"]:
        (repo_dir / ".git").mkdir()

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Already up to date."
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "update"])

    assert result.exit_code == 0
    assert "Workspace update complete" in result.output
    # Should show step numbers
    assert "Step 1/" in result.output
    assert "Step 2/" in result.output


def test_update_skip_sync(tmp_path):
    """--skip-sync skips the uv sync step."""
    ws = _create_workspace_with_repos(tmp_path, preset="standard")
    for repo_dir in [ws / "streamtex-docs", ws / "streamtex-claude"]:
        (repo_dir / ".git").mkdir()

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Already up to date."
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "update", "--skip-sync"])

    assert result.exit_code == 0
    assert "Syncing dependencies" not in result.output


def test_update_repair_finds_missing_init(tmp_path):
    """--repair detects missing custom/__init__.py."""
    ws = _create_workspace_with_repos(tmp_path, preset="standard")
    for repo_dir in [ws / "streamtex-docs", ws / "streamtex-claude"]:
        (repo_dir / ".git").mkdir()
    # Create a custom/ dir without __init__.py in one repo
    custom_dir = ws / "streamtex-docs" / "custom"
    custom_dir.mkdir()

    with (
        patch("streamtex.cli.workspace_cmd.subprocess.run") as mock_run,
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Already up to date."
        mock_run.return_value.stderr = ""
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["workspace", "update", "--repair"])

    assert result.exit_code == 0
    assert "custom/__init__.py" in result.output
    # File should have been created
    assert (custom_dir / "__init__.py").is_file()
