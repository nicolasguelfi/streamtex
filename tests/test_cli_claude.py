"""Tests for stx claude install/list/update/diff commands."""

import os

from click.testing import CliRunner

from streamtex.cli.claude_cmd import (
    _render_claude_md,
    collect_source_files,
    compare_profile,
    find_claude_repo,
    find_profile_targets,
    install_profile,
    list_profiles,
    read_installed_profile,
)
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
        '[profile]\nname = "project"\ndescription = "Project profile for StreamTeX apps"\n'
    )
    commands_dir = project / "commands" / "developer"
    commands_dir.mkdir(parents=True)
    (commands_dir / "test-run.md").write_text("Run tests\n")
    (project / "CLAUDE.md").write_text("# Project CLAUDE.md\n")

    # Profile: library
    library = claude / "profiles" / "library"
    library.mkdir(parents=True)
    (library / "manifest.toml").write_text(
        '[profile]\nname = "library"\ndescription = "Library profile for streamtex core"\n'
    )

    # Shared references
    shared_refs = claude / "shared" / "references"
    shared_refs.mkdir(parents=True)
    (shared_refs / "coding_standards.md").write_text("# Coding Standards\n")

    # Shared commands
    shared_cmds = claude / "shared" / "commands"
    shared_cmds.mkdir(parents=True)
    (shared_cmds / "stx-guide.md").write_text("# STX Guide\n")

    return ws


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

def test_find_claude_repo(tmp_path):
    ws = _make_workspace(tmp_path)

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


def test_install_copies_shared_commands(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    cmd_file = target / ".claude" / "commands" / "stx-guide.md"
    assert cmd_file.is_file()
    # Shared commands are read-only
    import stat
    mode = cmd_file.stat().st_mode
    assert not (mode & stat.S_IWUSR)


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


# ---------------------------------------------------------------------------
# read_installed_profile
# ---------------------------------------------------------------------------

def test_read_installed_profile(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / ".stx-profile").write_text("project\n")
    assert read_installed_profile(str(tmp_path)) == "project"


def test_read_installed_profile_missing(tmp_path):
    assert read_installed_profile(str(tmp_path)) is None


def test_read_installed_profile_empty(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / ".stx-profile").write_text("")
    assert read_installed_profile(str(tmp_path)) is None


# ---------------------------------------------------------------------------
# collect_source_files
# ---------------------------------------------------------------------------

def test_collect_source_files(tmp_path):
    ws = _make_workspace(tmp_path)
    files = collect_source_files(str(ws / "streamtex-claude"), "project")

    assert "CLAUDE.md" in files
    assert ".claude/commands/developer/test-run.md" in files
    # shared references
    assert ".claude/references/coding_standards.md" in files
    # manifest.toml should be excluded
    assert all("manifest.toml" not in v for v in files)


def test_collect_source_files_unknown_profile(tmp_path):
    ws = _make_workspace(tmp_path)
    files = collect_source_files(str(ws / "streamtex-claude"), "nonexistent")
    assert files == {}


# ---------------------------------------------------------------------------
# compare_profile
# ---------------------------------------------------------------------------

def test_compare_profile_all_identical(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    # Install then compare — should be identical
    install_profile(str(ws / "streamtex-claude"), "project", str(target))
    diffs = compare_profile(str(ws / "streamtex-claude"), "project", str(target))

    statuses = {d.path: d.status for d in diffs}
    assert statuses["CLAUDE.md"] == "identical"
    assert statuses[".claude/commands/developer/test-run.md"] == "identical"
    assert statuses[".claude/references/coding_standards.md"] == "identical"


def test_compare_profile_modified(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # Modify CLAUDE.md locally
    (target / "CLAUDE.md").write_text("# Custom CLAUDE.md\n")

    diffs = compare_profile(str(ws / "streamtex-claude"), "project", str(target))
    statuses = {d.path: d.status for d in diffs}
    assert statuses["CLAUDE.md"] == "modified"


def test_compare_profile_missing(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # Delete a file
    os.remove(target / ".claude" / "commands" / "developer" / "test-run.md")

    diffs = compare_profile(str(ws / "streamtex-claude"), "project", str(target))
    statuses = {d.path: d.status for d in diffs}
    assert statuses[".claude/commands/developer/test-run.md"] == "missing"


def test_compare_profile_extra(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # Add an extra file
    (target / ".claude" / "custom-notes.md").write_text("My notes\n")

    diffs = compare_profile(str(ws / "streamtex-claude"), "project", str(target))
    extras = [d for d in diffs if d.status == "extra"]
    assert len(extras) == 1
    assert extras[0].path == ".claude/custom-notes.md"


# ---------------------------------------------------------------------------
# diff command
# ---------------------------------------------------------------------------

def test_diff_command_up_to_date(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "diff", str(target)])
    assert result.exit_code == 0, result.output
    assert "up to date" in result.output


def test_diff_command_has_differences(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))
    (target / "CLAUDE.md").write_text("# Custom\n")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "diff", str(target)])
    assert result.exit_code == 0, result.output
    assert "differences" in result.output
    assert "Modified" in result.output


def test_diff_command_no_profile(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "diff", str(target)])
    assert result.exit_code != 0
    assert "No Claude profile" in result.output


def test_diff_command_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["claude", "diff", "--help"])
    assert result.exit_code == 0
    assert "Compare" in result.output


# ---------------------------------------------------------------------------
# update command
# ---------------------------------------------------------------------------

def test_update_command_already_up_to_date(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", str(target)])
    assert result.exit_code == 0, result.output
    assert "up to date" in result.output


def test_update_command_skips_modified_without_force(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # Modify source file in claude repo
    src = ws / "streamtex-claude" / "profiles" / "project" / "commands" / "developer" / "test-run.md"
    src.write_text("Run tests v2\n")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", str(target)])
    assert result.exit_code == 0, result.output
    # Modified files are skipped without --force
    assert "Skipped" in result.output
    assert "test-run.md" in result.output

    # Verify the file was NOT updated (old content preserved)
    content = (target / ".claude" / "commands" / "developer" / "test-run.md").read_text()
    assert "v2" not in content


def test_update_command_updates_modified_with_force(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # Modify source file in claude repo
    src = ws / "streamtex-claude" / "profiles" / "project" / "commands" / "developer" / "test-run.md"
    src.write_text("Run tests v2\n")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", "--force", str(target)])
    assert result.exit_code == 0, result.output
    assert "Updated" in result.output
    assert "test-run.md" in result.output

    # Verify the file was updated
    updated = (target / ".claude" / "commands" / "developer" / "test-run.md").read_text()
    assert "v2" in updated


def test_update_command_creates_backup_on_force(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # Modify source file in claude repo
    src = ws / "streamtex-claude" / "profiles" / "project" / "commands" / "developer" / "test-run.md"
    src.write_text("Run tests v2\n")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", "--force", str(target)])
    assert result.exit_code == 0, result.output
    assert "Backup saved to" in result.output

    # Verify backup directory was created
    backup_root = target / ".claude" / ".backup"
    assert backup_root.is_dir()
    # Should contain a timestamped subdirectory
    backups = [*backup_root.iterdir()]
    assert len(backups) == 1
    assert backups[0].is_dir()


def test_update_command_preserves_claude_md(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # User customizes CLAUDE.md
    (target / "CLAUDE.md").write_text("# My Custom CLAUDE.md\n")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", str(target)])
    assert result.exit_code == 0, result.output
    assert "Skipped" in result.output
    assert "CLAUDE.md" in result.output

    # CLAUDE.md preserved
    assert "My Custom" in (target / "CLAUDE.md").read_text()


def test_update_command_force_overwrites_claude_md(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # User customizes CLAUDE.md
    (target / "CLAUDE.md").write_text("# My Custom CLAUDE.md\n")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", str(target), "--force"])
    assert result.exit_code == 0, result.output
    assert "Updated" in result.output

    # CLAUDE.md overwritten with repo version
    assert "Project CLAUDE.md" in (target / "CLAUDE.md").read_text()


def test_update_command_restores_missing(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    install_profile(str(ws / "streamtex-claude"), "project", str(target))

    # Delete a file
    os.remove(target / ".claude" / "commands" / "developer" / "test-run.md")

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", str(target)])
    assert result.exit_code == 0, result.output
    assert "Updated" in result.output

    # File restored
    assert (target / ".claude" / "commands" / "developer" / "test-run.md").is_file()


def test_update_command_no_profile(tmp_path):
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", str(target)])
    assert result.exit_code != 0
    assert "No Claude profile" in result.output


def test_update_command_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["claude", "update", "--help"])
    assert result.exit_code == 0
    assert "--force" in result.output


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------

def test_claude_group_shows_update_and_diff():
    runner = CliRunner()
    result = runner.invoke(cli, ["claude", "--help"])
    assert result.exit_code == 0
    assert "update" in result.output
    assert "diff" in result.output


# ---------------------------------------------------------------------------
# Workspace with inherited profile
# ---------------------------------------------------------------------------

def _make_workspace_with_child(tmp_path):
    """Create a workspace with a ``child`` profile that extends ``project``."""
    ws = _make_workspace(tmp_path)
    claude = ws / "streamtex-claude"

    # Profile: child (extends project)
    child = claude / "profiles" / "child"
    child.mkdir(parents=True)
    (child / "manifest.toml").write_text(
        '[profile]\nname = "child"\ndescription = "Child profile"\nextends = "project"\n'
    )

    overlay = child / "overlay"
    overlay.mkdir()

    # Add a new file via overlay
    overlay_cmds = overlay / "commands" / "designer"
    overlay_cmds.mkdir(parents=True)
    (overlay_cmds / "child-cmd.md").write_text("Child command\n")

    # Override an existing parent file via overlay
    parent_cmds = overlay / "commands" / "developer"
    parent_cmds.mkdir(parents=True)
    (parent_cmds / "test-run.md").write_text("Run tests (child override)\n")

    return ws


# ---------------------------------------------------------------------------
# collect_source_files — inheritance
# ---------------------------------------------------------------------------

def test_collect_source_files_inherited(tmp_path):
    ws = _make_workspace_with_child(tmp_path)
    files = collect_source_files(str(ws / "streamtex-claude"), "child")

    # Parent file inherited
    assert "CLAUDE.md" in files

    # Child overlay file present
    assert ".claude/commands/designer/child-cmd.md" in files

    # Parent's shared references inherited
    assert ".claude/references/coding_standards.md" in files


def test_collect_source_files_overlay_overrides_parent(tmp_path):
    ws = _make_workspace_with_child(tmp_path)
    files = collect_source_files(str(ws / "streamtex-claude"), "child")

    # The overlay version of test-run.md should replace the parent version
    src = files[".claude/commands/developer/test-run.md"]
    with open(src) as f:
        content = f.read()
    assert "child override" in content


# ---------------------------------------------------------------------------
# find_profile_targets
# ---------------------------------------------------------------------------

def test_find_profile_targets(tmp_path):
    ws = _make_workspace(tmp_path)
    claude_repo = str(ws / "streamtex-claude")

    # Install profiles in two top-level dirs
    proj_a = ws / "proj-a"
    proj_a.mkdir()
    install_profile(claude_repo, "project", str(proj_a))

    proj_b = ws / "proj-b"
    proj_b.mkdir()
    install_profile(claude_repo, "library", str(proj_b))

    # Install in a projects/ subdir
    projects = ws / "projects"
    projects.mkdir()
    proj_c = projects / "proj-c"
    proj_c.mkdir()
    install_profile(claude_repo, "project", str(proj_c))

    targets = find_profile_targets(str(ws))
    paths = {t[0] for t in targets}
    profiles = {t[0]: t[1] for t in targets}

    assert str(proj_a) in paths
    assert str(proj_b) in paths
    assert str(proj_c) in paths
    assert profiles[str(proj_a)] == "project"
    assert profiles[str(proj_b)] == "library"
    assert profiles[str(proj_c)] == "project"


# ---------------------------------------------------------------------------
# update --all
# ---------------------------------------------------------------------------

def test_update_all_flag(tmp_path):
    ws = _make_workspace(tmp_path)
    claude_repo = str(ws / "streamtex-claude")

    # Install in two projects
    proj_a = ws / "proj-a"
    proj_a.mkdir()
    install_profile(claude_repo, "project", str(proj_a))

    proj_b = ws / "proj-b"
    proj_b.mkdir()
    install_profile(claude_repo, "project", str(proj_b))

    # Modify source so both projects are out of date
    src = ws / "streamtex-claude" / "profiles" / "project" / "commands" / "developer" / "test-run.md"
    src.write_text("Run tests v3\n")

    runner = CliRunner()
    os.chdir(ws)
    # --force required to overwrite modified files
    result = runner.invoke(cli, ["claude", "update", "--all", "--force"])
    assert result.exit_code == 0, result.output
    assert "Updated" in result.output

    # Both projects should be updated
    for proj in [proj_a, proj_b]:
        content = (proj / ".claude" / "commands" / "developer" / "test-run.md").read_text()
        assert "v3" in content


# ---------------------------------------------------------------------------
# check command
# ---------------------------------------------------------------------------

def test_check_command(tmp_path):
    ws = _make_workspace(tmp_path)
    claude_repo = str(ws / "streamtex-claude")

    proj_a = ws / "proj-a"
    proj_a.mkdir()
    install_profile(claude_repo, "project", str(proj_a))

    runner = CliRunner()
    os.chdir(ws)

    # All up to date
    result = runner.invoke(cli, ["claude", "check"])
    assert result.exit_code == 0, result.output
    assert "up to date" in result.output

    # Make source diverge
    src = ws / "streamtex-claude" / "profiles" / "project" / "commands" / "developer" / "test-run.md"
    src.write_text("Run tests v4\n")

    result = runner.invoke(cli, ["claude", "check"])
    assert result.exit_code == 1
    assert "out of sync" in result.output


# ---------------------------------------------------------------------------
# CLAUDE.md.j2 template rendering
# ---------------------------------------------------------------------------

def test_render_claude_md_substitutes_variables():
    """{{ project_name }} and {{ profile }} are replaced."""
    import tempfile

    template = "# {{ project_name }} Rules\nProfile: {{ profile }}\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".j2", delete=False) as f:
        f.write(template)
        f.flush()
        result = _render_claude_md(f.name, "my-project", "documentation")
    os.unlink(f.name)

    assert "# my-project Rules" in result
    assert "Profile: documentation" in result
    assert "{{" not in result


def test_render_claude_md_conditional_blocks():
    """{% if profile == 'X' %} blocks are included/excluded correctly."""
    import tempfile

    template = (
        "Before\n"
        '{% if profile == "presentation" %}\n'
        "Presentation content\n"
        "{% endif %}\n"
        "After\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".j2", delete=False) as f:
        f.write(template)
        path = f.name

    # Profile matches — block included
    result = _render_claude_md(path, "proj", "presentation")
    assert "Presentation content" in result

    # Profile doesn't match — block excluded
    result = _render_claude_md(path, "proj", "documentation")
    assert "Presentation content" not in result
    assert "Before" in result
    assert "After" in result

    os.unlink(path)


def test_install_renders_claude_md_from_j2(tmp_path):
    """install_profile renders CLAUDE.md from .j2 template."""
    ws = _make_workspace(tmp_path)
    claude_repo = str(ws / "streamtex-claude")

    # Replace project profile's CLAUDE.md with a .j2 template
    profile_dir = ws / "streamtex-claude" / "profiles" / "project"
    (profile_dir / "CLAUDE.md").unlink()
    (profile_dir / "CLAUDE.md.j2").write_text(
        "# {{ project_name }} — Rules\nProfile: {{ profile }}\n"
    )

    target = ws / "my-app"
    target.mkdir()
    installed = install_profile(claude_repo, "project", str(target))

    # Template should be copied to .claude/
    assert (target / ".claude" / "CLAUDE.md.j2").exists()

    # Rendered CLAUDE.md should exist at project root
    assert (target / "CLAUDE.md").exists()
    content = (target / "CLAUDE.md").read_text()
    assert "# my-app — Rules" in content
    assert "Profile: project" in content
    assert "CLAUDE.md" in installed


def test_update_rerenders_claude_md(tmp_path):
    """update re-renders CLAUDE.md when the .j2 template changes."""
    ws = _make_workspace(tmp_path)
    claude_repo = str(ws / "streamtex-claude")

    # Use .j2 template
    profile_dir = ws / "streamtex-claude" / "profiles" / "project"
    (profile_dir / "CLAUDE.md").unlink()
    (profile_dir / "CLAUDE.md.j2").write_text(
        "# {{ project_name }} v1\n"
    )

    target = ws / "my-app"
    target.mkdir()
    install_profile(claude_repo, "project", str(target))
    assert "v1" in (target / "CLAUDE.md").read_text()

    # Update template source
    (profile_dir / "CLAUDE.md.j2").write_text(
        "# {{ project_name }} v2\n"
    )

    runner = CliRunner()
    os.chdir(ws)
    result = runner.invoke(cli, ["claude", "update", "--force", str(target)])
    assert result.exit_code == 0, result.output

    # CLAUDE.md should be re-rendered with new content
    content = (target / "CLAUDE.md").read_text()
    assert "# my-app v2" in content
