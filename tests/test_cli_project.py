"""Tests for stx project new/validate commands."""

import os
import tomllib
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.project_cmd import (
    generate_block_hello,
    generate_blocks_init,
    generate_book_py,
    generate_collection_book_py,
    generate_collection_toml,
    generate_gitignore,
    generate_pyproject_toml,
    generate_streamlit_config,
    resolve_project_dir,
    scaffold_project,
    validate_project,
)

# ---------------------------------------------------------------------------
# Template generators
# ---------------------------------------------------------------------------


def test_generate_book_py_contains_name():
    content = generate_book_py("my-app")
    assert "my-app" in content
    assert "st_book" in content
    assert "registry" in content


def test_generate_collection_book_py_contains_name():
    content = generate_collection_book_py("my-hub")
    assert "my-hub" in content
    assert "st_collection" in content
    assert "collection.toml" in content


def test_generate_blocks_init_has_registry():
    content = generate_blocks_init()
    assert "ProjectBlockRegistry" in content
    assert "registry" in content


def test_generate_block_hello_has_build():
    content = generate_block_hello()
    assert "def build():" in content
    assert "st_write" in content


def test_generate_pyproject_toml_valid():
    content = generate_pyproject_toml("demo")
    data = tomllib.loads(content)
    assert data["project"]["name"] == "demo"
    deps = data["project"]["dependencies"]
    assert any("streamtex" in d for d in deps)


def test_generate_pyproject_toml_always_includes_cli():
    """cli extra is always present for dual-mode deployment support."""
    # Without extras
    content = generate_pyproject_toml("demo")
    assert "cli" in content

    # With extras
    content = generate_pyproject_toml("demo", extras=["pdf", "ai"])
    assert "cli" in content
    assert "pdf" in content
    assert "ai" in content


def test_generate_streamlit_config_valid():
    content = generate_streamlit_config()
    data = tomllib.loads(content)
    assert data["server"]["enableStaticServing"] is True


def test_generate_gitignore_has_pycache():
    content = generate_gitignore()
    assert "__pycache__" in content


def test_generate_collection_toml_valid():
    content = generate_collection_toml("hub")
    data = tomllib.loads(content)
    assert data["collection"]["name"] == "hub"


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------


def test_scaffold_creates_all_files(tmp_path):
    target = str(tmp_path / "proj")
    os.makedirs(target)
    files = scaffold_project(target, "test")

    expected = [
        "book.py",
        "blocks/__init__.py",
        "blocks/bck_hello.py",
        "custom/__init__.py",
        "custom/styles.py",
        ".streamlit/config.toml",
        "pyproject.toml",
        "setup.py",
        ".gitignore",
        "Dockerfile",
        "nginx.conf",
        "entrypoint.sh",
    ]
    for f in expected:
        assert os.path.isfile(os.path.join(target, f)), f"Missing: {f}"


def test_scaffold_creates_directories(tmp_path):
    target = str(tmp_path / "proj")
    os.makedirs(target)
    scaffold_project(target, "test")

    assert os.path.isdir(os.path.join(target, "blocks"))
    assert os.path.isdir(os.path.join(target, "custom"))
    assert os.path.isdir(os.path.join(target, ".streamlit"))
    assert os.path.isdir(os.path.join(target, "static", "images"))


def test_scaffold_returns_file_list(tmp_path):
    target = str(tmp_path / "proj")
    os.makedirs(target)
    files = scaffold_project(target, "test")
    assert len(files) > 0
    assert "book.py" in files


def test_scaffold_collection_mode(tmp_path):
    target = str(tmp_path / "proj")
    os.makedirs(target)
    files = scaffold_project(target, "hub", collection=True)

    assert "collection.toml" in files
    book_content = open(os.path.join(target, "book.py")).read()
    assert "st_collection" in book_content


def test_scaffold_standard_mode(tmp_path):
    target = str(tmp_path / "proj")
    os.makedirs(target)
    scaffold_project(target, "app")

    book_content = open(os.path.join(target, "book.py")).read()
    assert "st_book" in book_content
    assert "st_collection" not in book_content
    assert not os.path.isfile(os.path.join(target, "collection.toml"))


# ---------------------------------------------------------------------------
# Workspace detection
# ---------------------------------------------------------------------------


def test_resolve_in_workspace_uses_projects(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text('[workspace]\nname = "test"\n')
    projects = ws / "projects"
    projects.mkdir()

    os.chdir(ws)
    target = resolve_project_dir("demo")
    assert target.endswith(os.path.join("projects", "demo"))


def test_resolve_outside_workspace(tmp_path):
    os.chdir(tmp_path)
    target = resolve_project_dir("demo")
    assert target.endswith("demo")
    assert "projects" not in target


def test_resolve_raises_if_exists(tmp_path):
    os.chdir(tmp_path)
    (tmp_path / "demo").mkdir()

    import click

    with pytest.raises(click.ClickException, match="already exists"):
        resolve_project_dir("demo")


# ---------------------------------------------------------------------------
# stx project new command
# ---------------------------------------------------------------------------


def test_new_creates_project(tmp_path):
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(
        cli,
        ["project", "new", "myproj", "--no-git", "--no-sync", "--no-claude"],
    )
    assert result.exit_code == 0, result.output
    proj = tmp_path / "myproj"
    assert (proj / "book.py").is_file()
    assert (proj / "blocks" / "__init__.py").is_file()
    assert (proj / "pyproject.toml").is_file()


def test_new_runs_git_init(tmp_path):
    calls: list = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""
        return _R()

    os.chdir(tmp_path)
    runner = CliRunner()
    with patch("streamtex.cli.project_cmd.subprocess.run", side_effect=fake_run):
        result = runner.invoke(
            cli,
            ["project", "new", "gitproj", "--no-sync", "--no-claude"],
        )

    assert result.exit_code == 0, result.output
    git_calls = [c for c in calls if c[0] == "git"]
    assert len(git_calls) == 1
    assert git_calls[0][1] == "init"


def test_new_no_git_flag(tmp_path):
    calls: list = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""
        return _R()

    os.chdir(tmp_path)
    runner = CliRunner()
    with patch("streamtex.cli.project_cmd.subprocess.run", side_effect=fake_run):
        result = runner.invoke(
            cli,
            ["project", "new", "nogit", "--no-git", "--no-sync", "--no-claude"],
        )

    assert result.exit_code == 0, result.output
    git_calls = [c for c in calls if c[0] == "git"]
    assert len(git_calls) == 0


def test_new_no_sync_flag(tmp_path):
    calls: list = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""
        return _R()

    os.chdir(tmp_path)
    runner = CliRunner()
    with patch("streamtex.cli.project_cmd.subprocess.run", side_effect=fake_run):
        result = runner.invoke(
            cli,
            ["project", "new", "nosync", "--no-git", "--no-sync", "--no-claude"],
        )

    assert result.exit_code == 0, result.output
    # No uv sync calls should be made
    uv_calls = [c for c in calls if "sync" in str(c)]
    assert len(uv_calls) == 0


def test_new_no_claude_flag(tmp_path):
    os.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "new", "noclaude", "--no-git", "--no-sync", "--no-claude"],
    )
    assert result.exit_code == 0, result.output
    proj = tmp_path / "noclaude"
    # .claude/ should NOT be created when --no-claude
    assert not (proj / ".claude").is_dir()


def test_new_collection_flag(tmp_path):
    os.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "new", "hub", "--collection", "--no-git", "--no-sync", "--no-claude"],
    )
    assert result.exit_code == 0, result.output
    proj = tmp_path / "hub"
    assert (proj / "collection.toml").is_file()
    book_content = (proj / "book.py").read_text()
    assert "st_collection" in book_content


# ---------------------------------------------------------------------------
# --template option
# ---------------------------------------------------------------------------


def _setup_workspace_with_templates(tmp_path):
    """Create a fake workspace with streamtex-docs/templates/ for testing."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text('[workspace]\nname = "test"\n')
    (ws / "projects").mkdir()

    # Create a minimal template_project
    tpl_proj = ws / "streamtex-docs" / "templates" / "template_project"
    tpl_proj.mkdir(parents=True)
    (tpl_proj / "book.py").write_text('"""Template project."""\nimport streamtex\n')
    blocks = tpl_proj / "blocks"
    blocks.mkdir()
    (blocks / "__init__.py").write_text("from streamtex.blocks import ProjectBlockRegistry\nregistry = ProjectBlockRegistry(__file__)\n")
    (blocks / "bck_01_welcome.py").write_text('"""Welcome."""\ndef build():\n    pass\n')
    custom = tpl_proj / "custom"
    custom.mkdir()
    (custom / "__init__.py").write_text("")
    (custom / "styles.py").write_text("from streamtex.styles import StxStyles\nclass Styles(StxStyles):\n    pass\n")
    streamlit = tpl_proj / ".streamlit"
    streamlit.mkdir()
    (streamlit / "config.toml").write_text('[server]\nenableStaticServing = true\n')
    (tpl_proj / "setup.py").write_text('"""Setup."""\n')

    # Create a minimal template_collection
    tpl_col = ws / "streamtex-docs" / "templates" / "template_collection"
    tpl_col.mkdir(parents=True)
    (tpl_col / "book.py").write_text('"""Template collection."""\n')
    (tpl_col / "collection.toml").write_text('[collection]\nname = "hub"\n')
    col_blocks = tpl_col / "blocks"
    col_blocks.mkdir()
    (col_blocks / "__init__.py").write_text("from streamtex.blocks import ProjectBlockRegistry\nregistry = ProjectBlockRegistry(__file__)\n")
    (col_blocks / "bck_home.py").write_text('"""Home."""\ndef build():\n    pass\n')

    return ws


def test_new_with_template_project(tmp_path):
    """stx project new --template project copies the rich template."""
    ws = _setup_workspace_with_templates(tmp_path)
    os.chdir(ws)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "new", "tpltest", "--template", "project", "--no-git", "--no-sync", "--no-claude"],
    )
    assert result.exit_code == 0, result.output
    proj = ws / "projects" / "tpltest"
    assert (proj / "book.py").is_file()
    assert (proj / "blocks" / "bck_01_welcome.py").is_file()
    assert (proj / "custom" / "styles.py").is_file()
    assert (proj / "pyproject.toml").is_file()
    assert "template" in result.output.lower()


def test_new_with_template_collection(tmp_path):
    """stx project new --template collection copies the collection template."""
    ws = _setup_workspace_with_templates(tmp_path)
    os.chdir(ws)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "new", "coltest", "--template", "collection", "--no-git", "--no-sync", "--no-claude"],
    )
    assert result.exit_code == 0, result.output
    proj = ws / "projects" / "coltest"
    assert (proj / "book.py").is_file()
    assert (proj / "collection.toml").is_file()
    assert (proj / "blocks" / "bck_home.py").is_file()


def test_new_template_requires_workspace(tmp_path):
    """--template fails if not in a workspace with streamtex-docs."""
    os.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "new", "fail", "--template", "project", "--no-git", "--no-sync", "--no-claude"],
    )
    assert result.exit_code != 0
    assert "workspace" in result.output.lower() or "template" in result.output.lower()


# ---------------------------------------------------------------------------
# Validation function
# ---------------------------------------------------------------------------


def _make_valid_project(tmp_path):
    """Create a fully valid project structure for testing."""
    proj = tmp_path / "valid-proj"
    proj.mkdir()
    scaffold_project(str(proj), "valid")

    # Add .claude/ and CLAUDE.md (needed for checks 7-8)
    (proj / ".claude").mkdir()
    (proj / "CLAUDE.md").write_text("# Project\n")

    return proj


def test_validate_valid_project(tmp_path):
    proj = _make_valid_project(tmp_path)
    checks = validate_project(str(proj))

    statuses = {c.name: c.status for c in checks}
    for name, status in statuses.items():
        assert status in ("pass", "warn"), f"Check '{name}' failed: {status}"


def test_validate_missing_book_py(tmp_path):
    proj = _make_valid_project(tmp_path)
    os.remove(proj / "book.py")

    checks = validate_project(str(proj))
    book_check = next(c for c in checks if c.name == "book.py")
    assert book_check.status == "fail"


def test_validate_missing_blocks_init(tmp_path):
    proj = _make_valid_project(tmp_path)
    os.remove(proj / "blocks" / "__init__.py")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "blocks/__init__.py")
    assert check.status == "fail"


def test_validate_missing_registry(tmp_path):
    proj = _make_valid_project(tmp_path)
    (proj / "blocks" / "__init__.py").write_text("# no registry\n")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "blocks/__init__.py")
    assert check.status == "fail"
    assert "ProjectBlockRegistry" in check.message


def test_validate_missing_styles(tmp_path):
    proj = _make_valid_project(tmp_path)
    os.remove(proj / "custom" / "styles.py")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "custom/styles.py")
    assert check.status == "fail"


def test_validate_missing_streamlit_config(tmp_path):
    proj = _make_valid_project(tmp_path)
    os.remove(proj / ".streamlit" / "config.toml")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == ".streamlit/config.toml")
    assert check.status == "fail"


def test_validate_no_static_serving(tmp_path):
    proj = _make_valid_project(tmp_path)
    (proj / ".streamlit" / "config.toml").write_text('[server]\nport = 8501\n')

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "enableStaticServing")
    assert check.status == "fail"


def test_validate_missing_pyproject(tmp_path):
    proj = _make_valid_project(tmp_path)
    os.remove(proj / "pyproject.toml")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "pyproject.toml")
    assert check.status == "fail"


def test_validate_no_streamtex_dep(tmp_path):
    proj = _make_valid_project(tmp_path)
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["streamlit"]\n'
    )

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "pyproject.toml")
    assert check.status == "fail"
    assert "No streamtex" in check.message


def test_validate_missing_claude_dir(tmp_path):
    proj = _make_valid_project(tmp_path)
    import shutil

    shutil.rmtree(proj / ".claude")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == ".claude/")
    assert check.status == "fail"


def test_validate_missing_claude_md(tmp_path):
    proj = _make_valid_project(tmp_path)
    os.remove(proj / "CLAUDE.md")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "CLAUDE.md")
    assert check.status == "fail"


def test_validate_missing_static_images(tmp_path):
    proj = _make_valid_project(tmp_path)
    import shutil

    shutil.rmtree(proj / "static")

    checks = validate_project(str(proj))
    check = next(c for c in checks if c.name == "static/images/")
    assert check.status == "warn"


# ---------------------------------------------------------------------------
# stx project validate command
# ---------------------------------------------------------------------------


def test_validate_command_valid(tmp_path):
    proj = _make_valid_project(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "validate", str(proj)])
    assert result.exit_code == 0
    assert "VALID" in result.output


def test_validate_command_invalid(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "validate", str(empty)])
    assert result.exit_code == 0
    assert "INVALID" in result.output


def test_validate_command_default_path(tmp_path):
    proj = _make_valid_project(tmp_path)
    os.chdir(proj)
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "validate"])
    assert result.exit_code == 0
    assert "VALID" in result.output


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------


def test_project_group_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "--help"])
    assert result.exit_code == 0
    assert "new" in result.output
    assert "validate" in result.output


def test_project_new_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "new", "--help"])
    assert result.exit_code == 0
    assert "--profile" in result.output
    assert "--collection" in result.output
    assert "--no-git" in result.output
    assert "--no-sync" in result.output
    assert "--no-claude" in result.output
