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


def test_generate_blocks_init_passes_parent_directory_not_file():
    """The generated blocks/__init__.py must pass the parent directory
    to ProjectBlockRegistry, NOT __file__ directly. Passing __file__ produces
    an empty manifest (Path.glob on a file silently returns nothing), which
    causes the loading overlay to hang forever ("Initializing…" loop)."""
    content = generate_blocks_init()
    assert "Path(__file__).parent" in content, (
        "Generated blocks/__init__.py must use Path(__file__).parent — "
        "passing __file__ directly creates an empty registry."
    )
    assert "ProjectBlockRegistry(__file__)" not in content, (
        "Regression: ProjectBlockRegistry(__file__) yields an empty registry."
    )


def test_generated_blocks_init_executes_and_builds_a_working_registry(tmp_path):
    """End-to-end: write the generated blocks/__init__.py to disk alongside
    a real block file, exec the module, and verify the registry has len > 0.
    This catches the v0.6.41 bug at the integration level."""
    import importlib.util
    import sys

    blocks_dir = tmp_path / "blocks"
    blocks_dir.mkdir()
    (blocks_dir / "__init__.py").write_text(generate_blocks_init())
    (blocks_dir / "bck_hello.py").write_text(
        "def build():\n    return 'hello'\n"
    )

    sys.path.insert(0, str(tmp_path))
    try:
        # Force a fresh import so we hit the generated __init__.py
        if "blocks" in sys.modules:
            del sys.modules["blocks"]
        spec = importlib.util.spec_from_file_location(
            "blocks", blocks_dir / "__init__.py",
            submodule_search_locations=[str(blocks_dir)],
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["blocks"] = mod
        spec.loader.exec_module(mod)
        registry = mod.registry
        assert len(registry) == 1, (
            f"Expected 1 block discovered, got {len(registry)}. "
            f"Generator likely passes __file__ instead of its parent."
        )
        assert list(registry)[0].build() == "hello"
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("blocks", None)


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
        ".stx-version",
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
    assert "--kit" in result.output
    assert "--pack-name" in result.output
    assert "--no-mypack" in result.output


# ---------------------------------------------------------------------------
# Reuse architecture generators + scaffolding
# ---------------------------------------------------------------------------


def test_generate_stx_toml_schema():
    from streamtex.cli.project_cmd import generate_stx_toml

    content = generate_stx_toml(
        "demo",
        pack_name="mypack",
        kit_ref="streamtex_design:project-default",
        design_system_ref="default",
    )
    data = tomllib.loads(content)
    assert data["project"]["name"] == "demo"
    packs = data["packs"]
    primary = [p for p in packs if p.get("primary") is True]
    assert len(primary) == 1
    assert primary[0]["type"] == "local"
    assert primary[0]["name"] == "mypack"
    assert data["design_system"]["ref"] == "default"
    assert data["kit"]["ref"] == "streamtex_design:project-default"


def test_generate_stx_toml_no_mypack():
    from streamtex.cli.project_cmd import generate_stx_toml

    content = generate_stx_toml("demo", pack_name=None)
    data = tomllib.loads(content)
    assert "packs" not in data or all(
        p.get("primary") is not True for p in data.get("packs", [])
    )


def test_generate_mypack_pyproject_toml():
    from streamtex.cli.project_cmd import generate_mypack_pyproject_toml

    content = generate_mypack_pyproject_toml("mypack")
    data = tomllib.loads(content)
    assert data["project"]["name"] == "mypack"
    entry_points = data["project"]["entry-points"]["streamtex.packs"]
    assert entry_points["mypack"] == "mypack"


def test_scaffold_creates_mypack(tmp_path):
    from streamtex.cli.project_cmd import scaffold_mypack

    created = scaffold_mypack(str(tmp_path), "mypack")
    assert any(p.endswith("pyproject.toml") for p in created)
    assert (tmp_path / "mypack" / "mypack" / "_pack_manifest.toml").exists()
    assert (tmp_path / "mypack" / "mypack" / "components" / ".gitkeep").exists()
    assert (tmp_path / "mypack" / "mypack" / "design_systems" / ".gitkeep").exists()
    assert (tmp_path / "mypack" / "mypack" / "kits" / ".gitkeep").exists()


def test_new_no_mypack_flag(tmp_path):
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(
        cli,
        [
            "project", "new", "demo",
            "--no-mypack", "--no-claude", "--no-sync", "--no-git",
        ],
    )
    assert result.exit_code == 0, result.output
    target = tmp_path / "demo"
    assert (target / "stx.toml").exists()
    assert not (target / "mypack").exists()


def test_new_pack_name_override(tmp_path):
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(
        cli,
        [
            "project", "new", "demo",
            "--pack-name", "stuff",
            "--no-claude", "--no-sync", "--no-git",
        ],
    )
    assert result.exit_code == 0, result.output
    target = tmp_path / "demo"
    assert (target / "stuff" / "stuff" / "_pack_manifest.toml").exists()
    assert not (target / "mypack").exists()
    stx_data = tomllib.loads((target / "stx.toml").read_text())
    primary = [p for p in stx_data["packs"] if p.get("primary") is True]
    assert primary and primary[0]["name"] == "stuff"


def test_new_kit_records_in_stx_toml(tmp_path):
    """`--kit <ref>` records the kit and (when the pack is importable) the
    design system in stx.toml. Falls back gracefully when the pack is missing
    from the test venv (the CLI prints a warning and continues)."""
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(
        cli,
        [
            "project", "new", "demo",
            "--kit", "streamtex_design:slides-modern-dark",
            "--no-claude", "--no-sync", "--no-git", "--no-mypack",
        ],
    )
    assert result.exit_code == 0, result.output
    stx_data = tomllib.loads((tmp_path / "demo" / "stx.toml").read_text())
    assert stx_data["kit"]["ref"] == "streamtex_design:slides-modern-dark"

    try:
        import streamtex_design  # noqa: F401
        kit_importable = True
    except ModuleNotFoundError:
        kit_importable = False

    if kit_importable:
        assert stx_data["design_system"]["ref"] == "modern_dark"
        styles_py = (tmp_path / "demo" / "custom" / "styles.py").read_text()
        assert "streamtex_design.design_systems.modern_dark" in styles_py


def test_validate_check_stx_toml(tmp_path):
    """Check 11: stx.toml present and parsable."""
    proj = _make_valid_project(tmp_path)
    (proj / "stx.toml").write_text("[project]\nname = \"demo\"\n")
    checks = validate_project(str(proj))
    stx_checks = [c for c in checks if c.name == "stx.toml"]
    assert stx_checks and stx_checks[0].status == "pass"


def test_validate_check_mypack_dir(tmp_path):
    """Check 12: primary pack dir + _pack_manifest.toml."""
    from streamtex.cli.project_cmd import generate_stx_toml, scaffold_mypack

    proj = _make_valid_project(tmp_path)
    (proj / "stx.toml").write_text(
        generate_stx_toml("demo", pack_name="mypack")
    )
    scaffold_mypack(str(proj), "mypack")
    checks = validate_project(str(proj))
    pack_dir = [c for c in checks if c.name == "primary pack dir"]
    assert pack_dir and pack_dir[0].status == "pass"


def test_validate_check_primary_unique_fails_on_duplicates(tmp_path):
    """Check 14: more than one primary local pack must fail."""
    proj = _make_valid_project(tmp_path)
    (proj / "stx.toml").write_text(
        '[project]\nname="demo"\n\n'
        '[[packs]]\ntype="local"\nname="a"\npath="./a"\nprimary=true\n\n'
        '[[packs]]\ntype="local"\nname="b"\npath="./b"\nprimary=true\n'
    )
    checks = validate_project(str(proj))
    unique = [c for c in checks if c.name == "primary pack unique"]
    assert unique and unique[0].status == "fail"
