"""Tests for stx claude install/list commands."""

import os

from click.testing import CliRunner

from streamtex.cli.claude_cmd import find_claude_repo, install_profile, list_profiles
from streamtex.cli.commands import cli


# ---------------------------------------------------------------------------
# Fixtures: build a minimal workspace with a mock streamtex-claude repo
# ---------------------------------------------------------------------------

def _make_workspace(tmp_path):
    """Create a workspace with stx.toml and a mock streamtex-claude repo."""
    ws = tmp_path / "ws"
    ws.mkdir()

    # stx.toml
    toml = """\
[workspace]
name = "test-ws"
created = "2026-01-01T00:00:00Z"

[repos.streamtex-claude]
url = "https://github.com/nicolasguelfi/streamtex-claude.git"
path = "streamtex-claude"
type = "claude"

[claude]
source = "streamtex-claude"
"""
    (ws / "stx.toml").write_text(toml)

    # Mock claude repo structure
    claude = ws / "streamtex-claude"
    claude.mkdir()

    # Profile: project
    project = claude / "profiles" / "project"
    project.mkdir(parents=True)
    (project / "manifest.toml").write_text(
        'description = "Project profile for StreamTeX apps"\n'
    )
    commands_dir = project / "commands" / "developer"
    commands_dir.mkdir(parents=True)
    (commands_dir / "test-run.md").write_text("Run tests\n")
    (project / "CLAUDE.md").write_text("# Project CLAUDE.md\n")

    # Profile: library
    library = claude / "profiles" / "library"
    library.mkdir(parents=True)
    (library / "manifest.toml").write_text(
        'description = "Library profile for streamtex core"\n'
    )

    # Shared references
    shared_refs = claude / "shared" / "references"
    shared_refs.mkdir(parents=True)
    (shared_refs / "coding_standards.md").write_text("# Coding Standards\n")

    return ws


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

def test_find_claude_repo(tmp_path):
    ws = _make_workspace(tmp_path)
    import click
    import pytest

    from streamtex.cli.workspace_cmd import load_stx_toml

    config = load_stx_toml(str(ws))
    repo = find_claude_repo(str(ws), config)
    assert repo.endswith("streamtex-claude")
    assert os.path.isdir(repo)


def test_find_claude_repo_missing(tmp_path):
    import click
    import pytest

    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(
        '[workspace]\nname = "x"\n[repos]\n[claude]\nsource = "streamtex-claude"\n'
    )

    from streamtex.cli.workspace_cmd import load_stx_toml

    config = load_stx_toml(str(ws))
    with pytest.raises(click.ClickException, match="not found"):
        find_claude_repo(str(ws), config)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def test_list_shows_profiles(tmp_path):
    ws = _make_workspace(tmp_path)
    profiles = list_profiles(str(ws / "streamtex-claude"))

    assert len(profiles) == 2
    names = {p["name"] for p in profiles}
    assert names == {"library", "project"}

    project = next(p for p in profiles if p["name"] == "project")
    assert "Project profile" in project["description"]
    assert project["files"] >= 3  # manifest.toml, CLAUDE.md, test-run.md


def test_list_command(tmp_path):
    ws = _make_workspace(tmp_path)
    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "list"])
    assert result.exit_code == 0
    assert "project" in result.output
    assert "library" in result.output


def test_list_no_claude_repo(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(
        '[workspace]\nname = "x"\n[repos]\n[claude]\nsource = "streamtex-claude"\n'
    )

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "list"])
    assert result.exit_code != 0
    assert "not found" in result.output


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

def test_install_copies_files(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    installed = install_profile(
        str(ws / "streamtex-claude"), "project", str(target)
    )

    assert len(installed) > 0
    # Commands dir copied into .claude/
    assert (target / ".claude" / "commands" / "developer" / "test-run.md").is_file()


def test_install_copies_shared_references(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    assert (target / ".claude" / "references" / "coding_standards.md").is_file()


def test_install_writes_stx_profile(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    marker = target / ".claude" / ".stx-profile"
    assert marker.is_file()
    assert marker.read_text().strip() == "project"


def test_install_copies_claude_md(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    claude_md = target / "CLAUDE.md"
    assert claude_md.is_file()
    assert "Project CLAUDE.md" in claude_md.read_text()


def test_install_unknown_profile(tmp_path):
    import click
    import pytest

    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    with pytest.raises(click.ClickException, match="not found"):
        install_profile(
            str(ws / "streamtex-claude"), "nonexistent", str(target)
        )


def test_install_command(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "install", "project", str(target)])
    assert result.exit_code == 0
    assert "installed" in result.output
    assert (target / ".claude" / ".stx-profile").is_file()


def test_install_no_claude_repo(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(
        '[workspace]\nname = "x"\n[repos]\n[claude]\nsource = "streamtex-claude"\n'
    )

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "install", "project", "."])
    assert result.exit_code != 0
    assert "not found" in result.output
