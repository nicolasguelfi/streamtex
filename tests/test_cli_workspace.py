"""Tests for stx install / update / status commands and workspace helpers."""

import os
import tomllib
from unittest.mock import patch

from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.workspace_cmd import generate_stx_toml, load_stx_toml

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


# ---------------------------------------------------------------------------
# stx install — workspace creation
# ---------------------------------------------------------------------------

def _mock_subprocess_and_uv():
    """Return context managers that mock subprocess.run and shutil.which for uv."""
    return (
        patch("streamtex.cli.install_cmd.subprocess.run", _fake_run),
        patch("streamtex.cli.workspace_cmd.subprocess.run", _fake_run),
        patch("streamtex.cli.workspace_cmd.shutil.which", return_value="/usr/bin/uv"),
        patch("streamtex.cli.install_cmd.shutil.which", return_value="/usr/bin/uv"),
    )


def _fake_run(cmd, **_kwargs):
    class _R:
        returncode = 0
        stdout = "Already up to date."
        stderr = ""
    return _R()


def test_install_creates_workspace(tmp_path):
    """stx install --preset standard creates stx.toml and projects/."""
    target = tmp_path / "my-workspace"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        result = runner.invoke(cli, ["install", "--preset", "standard"])

    assert result.exit_code == 0, result.output
    assert (target / "stx.toml").is_file()
    assert (target / "projects").is_dir()


def test_install_toml_valid(tmp_path):
    target = tmp_path / "ws"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        runner.invoke(cli, ["install", "--preset", "standard"])

    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert "workspace" in data
    assert "repos" in data
    assert "deploy" in data
    assert "claude" in data
    assert data["workspace"]["preset"] == "standard"
    assert "streamtex-docs" in data["repos"]
    assert "streamtex-claude" in data["repos"]
    assert "streamtex" not in data["repos"]


def test_install_preset_basic(tmp_path):
    target = tmp_path / "ws"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        result = runner.invoke(cli, ["install", "--preset", "basic"])

    assert result.exit_code == 0, result.output
    with open(target / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["preset"] == "basic"
    assert len(data["repos"]) == 0


def test_install_preset_power_requires_project(tmp_path):
    """--preset power without --project should fail."""
    target = tmp_path / "ws"
    target.mkdir()

    runner = CliRunner()
    os.chdir(target)
    result = runner.invoke(cli, ["install", "--preset", "power"])

    assert result.exit_code != 0
    assert "--project" in result.output


def test_install_with_project(tmp_path):
    """stx install --preset standard --project hello creates the project."""
    target = tmp_path / "ws"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        result = runner.invoke(cli, ["install", "--preset", "standard", "--project", "hello"])

    assert result.exit_code == 0, result.output
    assert (target / "projects" / "hello" / "book.py").is_file()
    assert (target / "projects" / "hello" / "pyproject.toml").is_file()

    # Check extras are in pyproject.toml (standard = pdf, ai)
    with open(target / "projects" / "hello" / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    deps = data["project"]["dependencies"]
    stx_dep = [d for d in deps if "streamtex" in d][0]
    assert "pdf" in stx_dep
    assert "ai" in stx_dep


def test_install_power_with_project(tmp_path):
    """stx install --preset power --project demo includes inspector extra."""
    target = tmp_path / "ws"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        result = runner.invoke(cli, ["install", "--preset", "power", "--project", "demo"])

    assert result.exit_code == 0, result.output
    assert (target / "projects" / "demo" / "book.py").is_file()

    with open(target / "projects" / "demo" / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    deps = data["project"]["dependencies"]
    stx_dep = [d for d in deps if "streamtex" in d][0]
    assert "pdf" in stx_dep
    assert "ai" in stx_dep
    assert "inspector" in stx_dep


def test_install_basic_project_has_pdf_only(tmp_path):
    """Basic preset project should only include pdf extra."""
    target = tmp_path / "ws"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        result = runner.invoke(cli, ["install", "--preset", "basic", "--project", "hello"])

    assert result.exit_code == 0, result.output
    with open(target / "projects" / "hello" / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    deps = data["project"]["dependencies"]
    stx_dep = [d for d in deps if "streamtex" in d][0]
    assert "pdf" in stx_dep
    assert "ai" not in stx_dep
    assert "inspector" not in stx_dep


def test_install_shows_playwright_hint(tmp_path):
    """Install with project should show playwright installation hint."""
    target = tmp_path / "ws"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        result = runner.invoke(cli, ["install", "--preset", "basic", "--project", "hello"])

    assert "playwright install chromium" in result.output


def test_install_project_only_in_existing_workspace(tmp_path):
    """stx install --project myapp in existing workspace creates project only."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="standard"))
    (ws / "projects").mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["install", "--project", "newapp"])

    assert result.exit_code == 0, result.output
    assert (ws / "projects" / "newapp" / "book.py").is_file()


def test_install_existing_workspace_no_args_gives_hint(tmp_path):
    """stx install with no args in existing workspace suggests options."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(generate_stx_toml("ws", "2026-01-01T00:00:00Z"))

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["install"])

    assert result.exit_code != 0
    assert "--project" in result.output


def test_install_skips_existing_project(tmp_path):
    """Re-running install with same project name skips project creation."""
    ws = tmp_path / "ws"
    ws.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(ws)
        # First install
        result1 = runner.invoke(cli, ["install", "--preset", "basic", "--project", "hello"])
        assert result1.exit_code == 0

        # Clear state file so we can re-run
        state_file = ws / ".stx-install.json"
        if state_file.exists():
            state_file.unlink()

        # Second install (project already exists)
        result2 = runner.invoke(cli, ["install", "--project", "hello"])
        assert result2.exit_code == 0
        assert "already exists" in result2.output


def test_install_state_file_resume(tmp_path):
    """Install creates a state file that allows resuming."""
    ws = tmp_path / "ws"
    ws.mkdir()

    import json

    # Write a state file simulating a partial install
    state = {
        "started": "2026-01-01T00:00:00Z",
        "preset": "basic",
        "project": None,
        "template": None,
        "steps": {"init": "done", "clone": "done"},
    }
    (ws / "stx.toml").write_text(generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="basic"))
    (ws / "projects").mkdir()
    (ws / ".stx-install.json").write_text(json.dumps(state))

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["install", "--preset", "basic"])

    assert result.exit_code == 0, result.output
    assert "Resuming" in result.output
    # State file should be cleaned up
    assert not (ws / ".stx-install.json").exists()


# ---------------------------------------------------------------------------
# stx install — preset upgrade
# ---------------------------------------------------------------------------

def test_install_upgrade_preset(tmp_path):
    """stx install --preset developer in a standard workspace upgrades."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="standard"))
    (ws / "projects").mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["install", "--preset", "developer"])

    assert result.exit_code == 0, result.output
    assert "Upgraded" in result.output

    with open(ws / "stx.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["workspace"]["preset"] == "developer"
    assert "streamtex" in data["repos"]


def test_install_refuses_downgrade(tmp_path):
    """stx install --preset basic in developer workspace fails."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="developer"))

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["install", "--preset", "basic"])

    assert result.exit_code != 0
    assert "Cannot downgrade" in result.output


def test_install_same_preset_with_project(tmp_path):
    """stx install --preset standard --project x in standard workspace creates the project."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="standard"))
    (ws / "projects").mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(ws)
        result = runner.invoke(cli, ["install", "--preset", "standard", "--project", "x"])

    assert result.exit_code == 0, result.output
    assert (ws / "projects" / "x" / "book.py").is_file()


# ---------------------------------------------------------------------------
# stx status (top-level)
# ---------------------------------------------------------------------------

def test_status_outside_workspace(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["status"])
    assert result.exit_code != 0
    assert "stx.toml" in result.output


# ---------------------------------------------------------------------------
# stx update (top-level)
# ---------------------------------------------------------------------------

def _write_stx_toml(ws, preset="standard"):
    """Write a stx.toml into *ws* with the given preset."""
    content = generate_stx_toml("test-ws", "2026-01-01T00:00:00Z", preset=preset)
    (ws / "stx.toml").write_text(content)


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


def test_update_dry_run(tmp_path):
    """--dry-run shows steps without executing."""
    ws = _create_workspace_with_repos(tmp_path, preset="standard")
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
        result = runner.invoke(cli, ["update", "--dry-run"])

    assert result.exit_code == 0
    assert "dry run" in result.output.lower()
    assert "would git pull" in result.output


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
        result = runner.invoke(cli, ["update"])

    assert result.exit_code == 0
    assert "Workspace update complete" in result.output
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
        result = runner.invoke(cli, ["update", "--skip-sync"])

    assert result.exit_code == 0
    assert "Syncing dependencies" not in result.output


def test_update_repair_finds_missing_init(tmp_path):
    """--repair detects missing custom/__init__.py."""
    ws = _create_workspace_with_repos(tmp_path, preset="standard")
    for repo_dir in [ws / "streamtex-docs", ws / "streamtex-claude"]:
        (repo_dir / ".git").mkdir()
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
        result = runner.invoke(cli, ["update", "--repair"])

    assert result.exit_code == 0
    assert "custom/__init__.py" in result.output
    assert (custom_dir / "__init__.py").is_file()


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


def test_generate_stx_toml_preset_power():
    """Power preset has docs + claude (same repos as standard)."""
    content = generate_stx_toml("ws", "2026-01-01T00:00:00Z", preset="power")
    data = tomllib.loads(content)
    assert data["workspace"]["preset"] == "power"
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


# ---------------------------------------------------------------------------
# Extras in pyproject.toml
# ---------------------------------------------------------------------------

def test_generate_pyproject_toml_no_extras():
    from streamtex.cli.project_cmd import generate_pyproject_toml
    content = generate_pyproject_toml("test-proj")
    assert '"streamtex>=0.3.0"' in content
    assert "[" not in content.split("streamtex")[1].split(">=")[0]  # no extras brackets


def test_generate_pyproject_toml_with_extras():
    from streamtex.cli.project_cmd import generate_pyproject_toml
    content = generate_pyproject_toml("test-proj", extras=["pdf", "ai", "inspector"])
    assert '"streamtex[pdf,ai,inspector]>=0.3.0"' in content


def test_scaffold_project_with_extras(tmp_path):
    from streamtex.cli.project_cmd import scaffold_project
    target = tmp_path / "proj"
    target.mkdir()
    scaffold_project(str(target), "proj", extras=["pdf", "ai"])

    with open(target / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    deps = data["project"]["dependencies"]
    stx_dep = [d for d in deps if "streamtex" in d][0]
    assert "pdf" in stx_dep
    assert "ai" in stx_dep


# ---------------------------------------------------------------------------
# PRESET_EXTRAS mapping
# ---------------------------------------------------------------------------

def test_preset_extras_mapping():
    from streamtex.cli.workspace_cmd import PRESET_EXTRAS
    assert PRESET_EXTRAS["basic"] == ["pdf"]
    assert PRESET_EXTRAS["user"] == ["pdf"]
    assert PRESET_EXTRAS["standard"] == ["pdf", "ai"]
    assert PRESET_EXTRAS["power"] == ["pdf", "ai", "inspector"]
    assert PRESET_EXTRAS["developer"] == ["pdf", "ai", "inspector"]


# ---------------------------------------------------------------------------
# Template availability
# ---------------------------------------------------------------------------

def test_available_templates():
    from streamtex.cli.install_cmd import AVAILABLE_TEMPLATES
    assert "project" in AVAILABLE_TEMPLATES
    assert "collection" in AVAILABLE_TEMPLATES
    assert "slides" in AVAILABLE_TEMPLATES


def test_install_unavailable_template_prompts_fallback(tmp_path):
    """Unavailable template should prompt to use 'project' instead."""
    target = tmp_path / "ws"
    target.mkdir()

    patches = _mock_subprocess_and_uv()
    with patches[0], patches[1], patches[2], patches[3]:
        runner = CliRunner()
        os.chdir(target)
        # Simulate user saying "yes" to fallback template, then "no" to cloning docs
        result = runner.invoke(
            cli,
            ["install", "--preset", "basic", "--project", "hello", "--template", "presentation"],
            input="y\nn\n",
        )

    assert result.exit_code == 0, result.output
    assert "not yet available" in result.output
    assert "expanding our template catalog" in result.output
