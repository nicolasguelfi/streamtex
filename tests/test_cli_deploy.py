"""Tests for stx deploy preflight/docker/render/huggingface/status commands."""

import json
import os
import subprocess
import urllib.error
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.deploy_cmd import (
    DeployStatus,
    HF_LFS_PATTERNS,
    PreflightCheck,
    check_hf_status,
    check_render_status,
    derive_service_name,
    detect_git_remote,
    discover_manuals,
    docker_build,
    find_docker,
    generate_dockerfile,
    generate_hf_frontmatter,
    generate_render_service,
    generate_render_yaml,
    http_probe,
    parse_env_vars,
    parse_hf_remote,
    parse_render_yaml_services,
    render_service_url,
    run_preflight,
    setup_hf_remote,
    setup_lfs_tracking,
    update_readme_frontmatter,
    verify_git_lfs,
    verify_hf_cli,
)
from streamtex.cli.project_cmd import scaffold_project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_deploy_project(tmp_path):
    """Create a project structure suitable for deploy preflight."""
    proj = tmp_path / "my-proj"
    proj.mkdir()
    scaffold_project(str(proj), "my-proj")
    return proj


# ---------------------------------------------------------------------------
# Dockerfile template
# ---------------------------------------------------------------------------


def test_generate_dockerfile_has_streamlit():
    content = generate_dockerfile()
    assert '"streamlit"' in content
    assert '"book.py"' in content


def test_generate_dockerfile_has_healthcheck():
    content = generate_dockerfile()
    assert "HEALTHCHECK" in content


# ---------------------------------------------------------------------------
# Preflight function
# ---------------------------------------------------------------------------


def test_preflight_valid_project(tmp_path):
    proj = _make_deploy_project(tmp_path)
    # Add Dockerfile and git init for all checks to pass
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")
    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "add", "."],
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    statuses = {c.name: c.status for c in checks}
    assert statuses["book.py"] == "pass"
    assert statuses["enableStaticServing"] == "pass"
    assert statuses["pyproject.toml"] == "pass"
    assert statuses["git clean"] == "pass"
    assert statuses["sensitive files"] == "pass"
    assert statuses["Dockerfile"] == "pass"


def test_preflight_missing_book_py(tmp_path):
    proj = _make_deploy_project(tmp_path)
    os.remove(proj / "book.py")

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "book.py")
    assert check.status == "fail"


def test_preflight_missing_config(tmp_path):
    proj = _make_deploy_project(tmp_path)
    os.remove(proj / ".streamlit" / "config.toml")

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "enableStaticServing")
    assert check.status == "fail"
    assert "Config missing" in check.message


def test_preflight_no_static_serving(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / ".streamlit" / "config.toml").write_text("[server]\nport = 8501\n")

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "enableStaticServing")
    assert check.status == "fail"


def test_preflight_missing_pyproject(tmp_path):
    proj = _make_deploy_project(tmp_path)
    os.remove(proj / "pyproject.toml")

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "pyproject.toml")
    assert check.status == "fail"


def test_preflight_no_streamtex_dep(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["streamlit"]\n'
    )

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "pyproject.toml")
    assert check.status == "fail"
    assert "No streamtex" in check.message


def test_preflight_git_dirty(tmp_path):
    proj = _make_deploy_project(tmp_path)

    # Mock git status returning dirty output
    def fake_run(cmd, **kwargs):
        r = MagicMock()
        if "status" in cmd and "--porcelain" in cmd:
            r.returncode = 0
            r.stdout = " M book.py\n"
        else:
            r.returncode = 0
            r.stdout = ""
        return r

    with patch("streamtex.cli.deploy_cmd.subprocess.run", side_effect=fake_run):
        checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "git clean")
    assert check.status == "warn"
    assert "Uncommitted" in check.message


def test_preflight_sensitive_files(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / ".env").write_text("SECRET=abc\n")

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "sensitive files")
    assert check.status == "warn"
    assert ".env" in check.message


def test_preflight_no_static_dir(tmp_path):
    proj = _make_deploy_project(tmp_path)
    import shutil

    shutil.rmtree(proj / "static")

    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "static/")
    assert check.status == "warn"


def test_preflight_no_dockerfile(tmp_path):
    proj = _make_deploy_project(tmp_path)
    # scaffold_project doesn't create Dockerfile, so it should be missing
    checks = run_preflight(str(proj), skip_tests=True, skip_lint=True)
    check = next(c for c in checks if c.name == "Dockerfile")
    assert check.status == "warn"


def test_preflight_skip_tests(tmp_path):
    proj = _make_deploy_project(tmp_path)
    checks = run_preflight(str(proj), skip_tests=True, skip_lint=False)

    names = [c.name for c in checks]
    assert "tests" not in names


def test_preflight_skip_lint(tmp_path):
    proj = _make_deploy_project(tmp_path)
    checks = run_preflight(str(proj), skip_tests=False, skip_lint=True)

    names = [c.name for c in checks]
    assert "lint" not in names


# ---------------------------------------------------------------------------
# Docker helpers
# ---------------------------------------------------------------------------


def test_find_docker_found():
    with patch("streamtex.cli.deploy_cmd.shutil.which", return_value="/usr/bin/docker"):
        result = find_docker()
    assert result == "/usr/bin/docker"


def test_find_docker_missing():
    with patch("streamtex.cli.deploy_cmd.shutil.which", return_value=None):
        with pytest.raises(click.ClickException, match="docker not found"):
            find_docker()


def test_docker_build_success(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 0

    with (
        patch("streamtex.cli.deploy_cmd.find_docker", return_value="/usr/bin/docker"),
        patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result),
    ):
        result = docker_build(str(tmp_path), "test-image")
    assert result is True


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------


def test_preflight_command_valid(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    # Init git so git clean check passes
    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    runner = CliRunner()
    result = runner.invoke(
        cli, ["deploy", "preflight", str(proj), "--skip-tests", "--skip-lint"]
    )
    assert result.exit_code == 0, result.output
    assert "PASSED" in result.output


def test_preflight_command_invalid(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        cli, ["deploy", "preflight", str(empty), "--skip-tests", "--skip-lint"]
    )
    assert result.exit_code == 0
    assert "FAILED" in result.output


def test_preflight_command_skip_tests(tmp_path):
    proj = _make_deploy_project(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli, ["deploy", "preflight", str(proj), "--skip-tests", "--skip-lint"]
    )
    assert result.exit_code == 0
    # "tests" should not appear as a check name in the table
    assert "All tests pass" not in result.output


def test_docker_command_build_only(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    # Init git for preflight
    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    build_called = []
    run_called = []

    def fake_docker_build(project_path, tag):
        build_called.append(tag)
        return True

    def fake_docker_run(tag, port):
        run_called.append((tag, port))

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.docker_build", side_effect=fake_docker_build),
        patch("streamtex.cli.deploy_cmd.docker_run", side_effect=fake_docker_run),
    ):
        result = runner.invoke(
            cli, ["deploy", "docker", str(proj), "--build-only"]
        )

    assert result.exit_code == 0, result.output
    assert len(build_called) == 1
    assert len(run_called) == 0


def test_docker_command_generates_dockerfile(tmp_path):
    proj = _make_deploy_project(tmp_path)
    # No Dockerfile initially

    # Init git for preflight
    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.docker_build", return_value=True),
        patch("streamtex.cli.deploy_cmd.docker_run"),
    ):
        result = runner.invoke(cli, ["deploy", "docker", str(proj)])

    assert result.exit_code == 0, result.output
    assert "Dockerfile generated" in result.output
    assert (proj / "Dockerfile").is_file()


def test_docker_command_custom_port(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    run_calls = []

    def fake_docker_run(tag, port):
        run_calls.append((tag, port))

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.docker_build", return_value=True),
        patch("streamtex.cli.deploy_cmd.docker_run", side_effect=fake_docker_run),
    ):
        result = runner.invoke(
            cli, ["deploy", "docker", str(proj), "--port", "9000"]
        )

    assert result.exit_code == 0, result.output
    assert len(run_calls) == 1
    assert run_calls[0][1] == 9000


def test_docker_command_custom_tag(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    build_calls = []

    def fake_docker_build(project_path, tag):
        build_calls.append(tag)
        return True

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.docker_build", side_effect=fake_docker_build),
        patch("streamtex.cli.deploy_cmd.docker_run"),
    ):
        result = runner.invoke(
            cli, ["deploy", "docker", str(proj), "--tag", "my-tag", "--build-only"]
        )

    assert result.exit_code == 0, result.output
    assert len(build_calls) == 1
    assert build_calls[0] == "my-tag"


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------


def test_deploy_group_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "--help"])
    assert result.exit_code == 0
    assert "preflight" in result.output
    assert "docker" in result.output


def test_deploy_preflight_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "preflight", "--help"])
    assert result.exit_code == 0
    assert "--skip-tests" in result.output
    assert "--skip-lint" in result.output


def test_deploy_docker_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "docker", "--help"])
    assert result.exit_code == 0
    assert "--port" in result.output
    assert "--tag" in result.output
    assert "--build-only" in result.output


# ---------------------------------------------------------------------------
# Render: detect_git_remote
# ---------------------------------------------------------------------------


def test_detect_git_remote_https(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "https://github.com/user/repo\n"

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        url = detect_git_remote(str(tmp_path))
    assert url == "https://github.com/user/repo"


def test_detect_git_remote_ssh_normalized(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "git@github.com:user/repo.git\n"

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        url = detect_git_remote(str(tmp_path))
    assert url == "https://github.com/user/repo"


def test_detect_git_remote_strips_dotgit(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "https://github.com/user/repo.git\n"

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        url = detect_git_remote(str(tmp_path))
    assert url == "https://github.com/user/repo"


def test_detect_git_remote_none_on_failure(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        url = detect_git_remote(str(tmp_path))
    assert url is None


# ---------------------------------------------------------------------------
# Render: discover_manuals
# ---------------------------------------------------------------------------


def test_discover_manuals_finds_all(tmp_path):
    manuals = tmp_path / "manuals"
    manuals.mkdir()
    (manuals / "stx_manual_intro").mkdir()
    (manuals / "stx_manuals_collection").mkdir()

    result = discover_manuals(str(tmp_path))
    assert len(result) == 2
    assert "manuals/stx_manuals_collection" in result
    assert "manuals/stx_manual_intro" in result


def test_discover_manuals_excludes_non_matching(tmp_path):
    manuals = tmp_path / "manuals"
    manuals.mkdir()
    (manuals / "stx_manual_intro").mkdir()
    (manuals / "shared-blocks").mkdir()
    (manuals / "README.md").write_text("hi")

    result = discover_manuals(str(tmp_path))
    assert len(result) == 1
    assert "manuals/stx_manual_intro" in result


def test_discover_manuals_no_dir(tmp_path):
    result = discover_manuals(str(tmp_path))
    assert result == []


def test_discover_manuals_sorted(tmp_path):
    manuals = tmp_path / "manuals"
    manuals.mkdir()
    (manuals / "stx_manual_z").mkdir()
    (manuals / "stx_manual_a").mkdir()
    (manuals / "stx_manuals_m").mkdir()

    result = discover_manuals(str(tmp_path))
    assert result == [
        "manuals/stx_manual_a",
        "manuals/stx_manual_z",
        "manuals/stx_manuals_m",
    ]


# ---------------------------------------------------------------------------
# Render: derive_service_name
# ---------------------------------------------------------------------------


def test_derive_name_manual():
    assert derive_service_name("manuals/stx_manual_intro") == "streamtex-intro"


def test_derive_name_manuals():
    assert derive_service_name("manuals/stx_manuals_collection") == "streamtex-collection"


def test_derive_name_fallback():
    assert derive_service_name("manuals/other") == "other"


# ---------------------------------------------------------------------------
# Render: parse_env_vars
# ---------------------------------------------------------------------------


def test_parse_env_valid():
    result = parse_env_vars(("KEY=val",))
    assert result == [("KEY", "val")]


def test_parse_env_value_with_equals():
    result = parse_env_vars(("KEY=a=b",))
    assert result == [("KEY", "a=b")]


def test_parse_env_invalid():
    with pytest.raises(click.BadParameter, match="Invalid format"):
        parse_env_vars(("NOEQUALS",))


# ---------------------------------------------------------------------------
# Render: generate_render_service
# ---------------------------------------------------------------------------


def test_render_service_basic():
    svc = generate_render_service(
        name="my-svc",
        repo="https://github.com/user/repo",
        branch="main",
        plan="free",
        env_vars=[],
    )
    assert "name: my-svc" in svc
    assert "repo: https://github.com/user/repo" in svc
    assert "branch: main" in svc
    assert "plan: free" in svc
    assert "STX_PASSWORD" in svc
    assert "buildFilter" not in svc


def test_render_service_with_folder():
    svc = generate_render_service(
        name="my-svc",
        repo="https://github.com/user/repo",
        branch="main",
        plan="free",
        env_vars=[],
        folder="manuals/stx_manual_intro",
    )
    assert "key: FOLDER" in svc
    assert "value: manuals/stx_manual_intro" in svc


def test_render_service_build_filter():
    svc = generate_render_service(
        name="my-svc",
        repo="https://github.com/user/repo",
        branch="main",
        plan="free",
        env_vars=[],
        build_filter=True,
    )
    assert "buildFilter:" in svc
    assert "paths:" in svc


def test_render_service_custom_env_overrides_password():
    svc = generate_render_service(
        name="my-svc",
        repo="https://github.com/user/repo",
        branch="main",
        plan="free",
        env_vars=[("STX_PASSWORD", "mysecret")],
    )
    # Should have exactly one STX_PASSWORD
    assert svc.count("STX_PASSWORD") == 1
    assert "mysecret" in svc


# ---------------------------------------------------------------------------
# Render: generate_render_yaml
# ---------------------------------------------------------------------------


def test_render_yaml_structure():
    svc1 = "  - type: web\n    name: svc1"
    svc2 = "  - type: web\n    name: svc2"
    yaml = generate_render_yaml([svc1, svc2])
    assert yaml.startswith("services:\n")
    assert "svc1" in yaml
    assert "svc2" in yaml
    assert yaml.endswith("\n")


# ---------------------------------------------------------------------------
# Render: Click command
# ---------------------------------------------------------------------------


def _make_git_project(tmp_path):
    """Create a project with git remote for render tests."""
    proj = tmp_path / "my-proj"
    proj.mkdir()
    scaffold_project(str(proj), "my-proj")
    return proj


def test_render_command_single(tmp_path):
    proj = _make_git_project(tmp_path)

    runner = CliRunner()
    with patch(
        "streamtex.cli.deploy_cmd.detect_git_remote",
        return_value="https://github.com/user/repo",
    ):
        result = runner.invoke(cli, ["deploy", "render", str(proj)])

    assert result.exit_code == 0, result.output
    assert "render.yaml written" in result.output
    assert (proj / "render.yaml").is_file()

    content = (proj / "render.yaml").read_text()
    assert "services:" in content
    assert "buildFilter:" in content
    assert "STX_PASSWORD" in content


def test_render_command_multi(tmp_path):
    proj = _make_git_project(tmp_path)
    manuals = proj / "manuals"
    manuals.mkdir()
    (manuals / "stx_manual_intro").mkdir()
    (manuals / "stx_manual_advanced").mkdir()

    runner = CliRunner()
    with patch(
        "streamtex.cli.deploy_cmd.detect_git_remote",
        return_value="https://github.com/user/repo",
    ):
        result = runner.invoke(cli, ["deploy", "render", str(proj), "--multi"])

    assert result.exit_code == 0, result.output
    assert "render.yaml written" in result.output

    content = (proj / "render.yaml").read_text()
    assert "streamtex-intro" in content
    assert "streamtex-advanced" in content
    assert "FOLDER" in content


def test_render_command_multi_no_manuals(tmp_path):
    proj = _make_git_project(tmp_path)

    runner = CliRunner()
    with patch(
        "streamtex.cli.deploy_cmd.detect_git_remote",
        return_value="https://github.com/user/repo",
    ):
        result = runner.invoke(cli, ["deploy", "render", str(proj), "--multi"])

    assert result.exit_code != 0
    assert "No manuals/" in result.output


def test_render_command_no_remote(tmp_path):
    proj = _make_git_project(tmp_path)

    runner = CliRunner()
    with patch(
        "streamtex.cli.deploy_cmd.detect_git_remote",
        return_value=None,
    ):
        result = runner.invoke(cli, ["deploy", "render", str(proj)])

    assert result.exit_code != 0
    assert "No git remote" in result.output


def test_render_command_generates_dockerfile(tmp_path):
    proj = _make_git_project(tmp_path)
    # Ensure no Dockerfile
    df = proj / "Dockerfile"
    if df.is_file():
        df.unlink()

    runner = CliRunner()
    with patch(
        "streamtex.cli.deploy_cmd.detect_git_remote",
        return_value="https://github.com/user/repo",
    ):
        result = runner.invoke(cli, ["deploy", "render", str(proj)])

    assert result.exit_code == 0, result.output
    assert "Dockerfile generated" in result.output
    assert (proj / "Dockerfile").is_file()


# ---------------------------------------------------------------------------
# Render: Infrastructure
# ---------------------------------------------------------------------------


def test_render_command_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "render", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output
    assert "--branch" in result.output
    assert "--plan" in result.output
    assert "--env" in result.output
    assert "--multi" in result.output


def test_deploy_group_shows_render():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "--help"])
    assert result.exit_code == 0
    assert "render" in result.output


# ---------------------------------------------------------------------------
# Hugging Face: verify_git_lfs
# ---------------------------------------------------------------------------


def test_verify_git_lfs_found():
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "git-lfs/3.4.0\n"

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        assert verify_git_lfs() is True


def test_verify_git_lfs_missing():
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        assert verify_git_lfs() is False


# ---------------------------------------------------------------------------
# Hugging Face: verify_hf_cli
# ---------------------------------------------------------------------------


def test_verify_hf_cli_authenticated():
    mock_result = MagicMock()
    mock_result.returncode = 0

    with (
        patch("streamtex.cli.deploy_cmd.shutil.which", return_value="/usr/bin/huggingface-cli"),
        patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result),
    ):
        assert verify_hf_cli() is True


def test_verify_hf_cli_not_found():
    with patch("streamtex.cli.deploy_cmd.shutil.which", return_value=None):
        assert verify_hf_cli() is False


# ---------------------------------------------------------------------------
# Hugging Face: generate_hf_frontmatter
# ---------------------------------------------------------------------------


def test_generate_hf_frontmatter_defaults():
    fm = generate_hf_frontmatter("My Project", "\U0001f4ca")
    assert "title: My Project" in fm
    assert "sdk: docker" in fm
    assert "app_port: 8501" in fm
    assert fm.startswith("---\n")
    assert fm.endswith("---\n")


def test_generate_hf_frontmatter_custom():
    fm = generate_hf_frontmatter("Custom Title", "\U0001f680", app_port=9000)
    assert "title: Custom Title" in fm
    assert "emoji: \U0001f680" in fm
    assert "app_port: 9000" in fm


# ---------------------------------------------------------------------------
# Hugging Face: update_readme_frontmatter
# ---------------------------------------------------------------------------


def test_update_readme_no_existing(tmp_path):
    fm = generate_hf_frontmatter("Test", "\U0001f4ca")
    result = update_readme_frontmatter(str(tmp_path), fm)
    assert result is True
    readme = (tmp_path / "README.md").read_text()
    assert readme.startswith("---\n")
    assert "title: Test" in readme


def test_update_readme_existing_no_frontmatter(tmp_path):
    (tmp_path / "README.md").write_text("# Hello World\n")
    fm = generate_hf_frontmatter("Test", "\U0001f4ca")
    result = update_readme_frontmatter(str(tmp_path), fm)
    assert result is True
    readme = (tmp_path / "README.md").read_text()
    assert readme.startswith("---\n")
    assert "# Hello World" in readme


def test_update_readme_existing_with_frontmatter(tmp_path):
    old = "---\ntitle: Old\n---\n# Hello\n"
    (tmp_path / "README.md").write_text(old)
    fm = generate_hf_frontmatter("New", "\U0001f680")
    result = update_readme_frontmatter(str(tmp_path), fm)
    assert result is True
    readme = (tmp_path / "README.md").read_text()
    assert "title: New" in readme
    assert "title: Old" not in readme
    assert "# Hello" in readme


# ---------------------------------------------------------------------------
# Hugging Face: setup_lfs_tracking
# ---------------------------------------------------------------------------


def test_setup_lfs_tracking_new_file(tmp_path):
    result = setup_lfs_tracking(str(tmp_path))
    assert result is True
    ga = (tmp_path / ".gitattributes").read_text()
    assert "*.png filter=lfs" in ga
    assert "*.pdf filter=lfs" in ga


def test_setup_lfs_tracking_existing_file(tmp_path):
    (tmp_path / ".gitattributes").write_text("*.png filter=lfs diff=lfs merge=lfs -text\n")
    result = setup_lfs_tracking(str(tmp_path))
    assert result is True
    ga = (tmp_path / ".gitattributes").read_text()
    # png already exists, should not be duplicated
    assert ga.count("*.png") == 1
    # jpg should be added
    assert "*.jpg filter=lfs" in ga


def test_setup_lfs_tracking_no_change(tmp_path):
    # Write all patterns
    lines = [f"{p} filter=lfs diff=lfs merge=lfs -text" for p in HF_LFS_PATTERNS]
    (tmp_path / ".gitattributes").write_text("\n".join(lines) + "\n")
    result = setup_lfs_tracking(str(tmp_path))
    assert result is False


# ---------------------------------------------------------------------------
# Hugging Face: setup_hf_remote
# ---------------------------------------------------------------------------


def test_setup_hf_remote_add(tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        r = MagicMock()
        if "get-url" in cmd:
            r.returncode = 1  # remote doesn't exist yet
        else:
            r.returncode = 0
        return r

    with patch("streamtex.cli.deploy_cmd.subprocess.run", side_effect=fake_run):
        setup_hf_remote(str(tmp_path), "https://huggingface.co/spaces/user/repo")

    # Should have called get-url then add
    add_call = [c for c in calls if "add" in c]
    assert len(add_call) == 1
    assert "https://huggingface.co/spaces/user/repo.git" in add_call[0]


def test_setup_hf_remote_set_url(tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        r = MagicMock()
        r.returncode = 0  # remote already exists
        return r

    with patch("streamtex.cli.deploy_cmd.subprocess.run", side_effect=fake_run):
        setup_hf_remote(str(tmp_path), "https://huggingface.co/spaces/user/repo")

    set_url_call = [c for c in calls if "set-url" in c]
    assert len(set_url_call) == 1


# ---------------------------------------------------------------------------
# Hugging Face: Click command
# ---------------------------------------------------------------------------


def test_huggingface_command_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "huggingface", "--help"])
    assert result.exit_code == 0
    assert "--space" in result.output
    assert "--title" in result.output
    assert "--emoji" in result.output
    assert "--skip-push" in result.output


def test_deploy_group_shows_huggingface():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "--help"])
    assert result.exit_code == 0
    assert "huggingface" in result.output


def test_huggingface_command_success(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    # Init git
    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.verify_git_lfs", return_value=True),
        patch("streamtex.cli.deploy_cmd.verify_hf_cli", return_value=True),
        patch("streamtex.cli.deploy_cmd.setup_hf_remote"),
        patch("streamtex.cli.deploy_cmd.subprocess.run") as mock_run,
    ):
        # Make subprocess calls succeed (for git add/commit/push)
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = runner.invoke(
            cli, ["deploy", "huggingface", str(proj),
                  "--space", "https://huggingface.co/spaces/user/repo"]
        )

    assert result.exit_code == 0, result.output
    assert "Space URL" in result.output


def test_huggingface_command_skip_push(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    push_called = []

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.verify_git_lfs", return_value=True),
        patch("streamtex.cli.deploy_cmd.verify_hf_cli", return_value=True),
        patch("streamtex.cli.deploy_cmd.setup_hf_remote"),
    ):
        result = runner.invoke(
            cli, ["deploy", "huggingface", str(proj),
                  "--space", "https://huggingface.co/spaces/user/repo",
                  "--skip-push"]
        )

    assert result.exit_code == 0, result.output
    assert "Skip-push mode" in result.output
    assert "Pushed" not in result.output


def test_huggingface_command_generates_dockerfile(tmp_path):
    proj = _make_deploy_project(tmp_path)
    # No Dockerfile

    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.verify_git_lfs", return_value=True),
        patch("streamtex.cli.deploy_cmd.verify_hf_cli", return_value=True),
        patch("streamtex.cli.deploy_cmd.setup_hf_remote"),
    ):
        result = runner.invoke(
            cli, ["deploy", "huggingface", str(proj),
                  "--space", "https://huggingface.co/spaces/user/repo",
                  "--skip-push"]
        )

    assert result.exit_code == 0, result.output
    assert "Dockerfile generated" in result.output
    assert (proj / "Dockerfile").is_file()


def test_huggingface_command_preflight_fails(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        cli, ["deploy", "huggingface", str(empty),
              "--space", "https://huggingface.co/spaces/user/repo",
              "--skip-push"]
    )
    assert result.exit_code != 0
    assert "Preflight failed" in result.output


def test_huggingface_command_generates_frontmatter(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.verify_git_lfs", return_value=True),
        patch("streamtex.cli.deploy_cmd.verify_hf_cli", return_value=True),
        patch("streamtex.cli.deploy_cmd.setup_hf_remote"),
    ):
        result = runner.invoke(
            cli, ["deploy", "huggingface", str(proj),
                  "--space", "https://huggingface.co/spaces/user/repo",
                  "--skip-push"]
        )

    assert result.exit_code == 0, result.output
    readme = (proj / "README.md").read_text()
    assert "sdk: docker" in readme
    assert "app_port: 8501" in readme


def test_huggingface_command_custom_title_emoji(tmp_path):
    proj = _make_deploy_project(tmp_path)
    (proj / "Dockerfile").write_text("FROM python:3.13-slim\n")

    subprocess.run(["git", "init", str(proj)], capture_output=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(proj), "commit", "-m", "init"],
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )

    runner = CliRunner()
    with (
        patch("streamtex.cli.deploy_cmd.verify_git_lfs", return_value=True),
        patch("streamtex.cli.deploy_cmd.verify_hf_cli", return_value=True),
        patch("streamtex.cli.deploy_cmd.setup_hf_remote"),
    ):
        result = runner.invoke(
            cli, ["deploy", "huggingface", str(proj),
                  "--space", "https://huggingface.co/spaces/user/repo",
                  "--title", "My Custom Title",
                  "--emoji", "\U0001f680",
                  "--skip-push"]
        )

    assert result.exit_code == 0, result.output
    readme = (proj / "README.md").read_text()
    assert "title: My Custom Title" in readme
    assert "emoji: \U0001f680" in readme


# ---------------------------------------------------------------------------
# Deploy status: render_service_url
# ---------------------------------------------------------------------------


def test_render_service_url():
    assert render_service_url("my-app") == "https://my-app.onrender.com"


def test_render_service_url_with_dash():
    assert render_service_url("streamtex-intro") == "https://streamtex-intro.onrender.com"


# ---------------------------------------------------------------------------
# Deploy status: parse_render_yaml_services
# ---------------------------------------------------------------------------


def test_parse_render_yaml_finds_services(tmp_path):
    yaml_content = """\
services:
  - type: web
    name: streamtex-intro
    runtime: docker
  - type: web
    name: streamtex-advanced
    runtime: docker
"""
    (tmp_path / "render.yaml").write_text(yaml_content)
    result = parse_render_yaml_services(str(tmp_path))
    assert result == ["streamtex-advanced", "streamtex-intro"]


def test_parse_render_yaml_no_file(tmp_path):
    result = parse_render_yaml_services(str(tmp_path))
    assert result == []


def test_parse_render_yaml_empty_file(tmp_path):
    (tmp_path / "render.yaml").write_text("")
    result = parse_render_yaml_services(str(tmp_path))
    assert result == []


# ---------------------------------------------------------------------------
# Deploy status: http_probe
# ---------------------------------------------------------------------------


def test_http_probe_live():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("streamtex.cli.deploy_cmd.urllib.request.urlopen", return_value=mock_resp):
        status, msg = http_probe("https://example.onrender.com")
    assert status == "live"
    assert "200" in msg


def test_http_probe_sleep_502():
    err = urllib.error.HTTPError(
        "https://example.com", 502, "Bad Gateway", {}, None
    )
    with patch("streamtex.cli.deploy_cmd.urllib.request.urlopen", side_effect=err):
        status, msg = http_probe("https://example.com")
    assert status == "sleep"
    assert "502" in msg


def test_http_probe_down_404():
    err = urllib.error.HTTPError(
        "https://example.com", 404, "Not Found", {}, None
    )
    with patch("streamtex.cli.deploy_cmd.urllib.request.urlopen", side_effect=err):
        status, msg = http_probe("https://example.com")
    assert status == "down"
    assert "404" in msg


def test_http_probe_timeout():
    err = urllib.error.URLError("timed out")
    with patch("streamtex.cli.deploy_cmd.urllib.request.urlopen", side_effect=err):
        status, msg = http_probe("https://example.com")
    assert status == "sleep"
    assert "Timeout" in msg


def test_http_probe_error():
    err = OSError("Connection refused")
    with patch("streamtex.cli.deploy_cmd.urllib.request.urlopen", side_effect=err):
        status, msg = http_probe("https://example.com")
    assert status == "error"
    assert "Connection refused" in msg


# ---------------------------------------------------------------------------
# Deploy status: parse_hf_remote
# ---------------------------------------------------------------------------


def test_parse_hf_remote_found(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "https://huggingface.co/spaces/myuser/myrepo.git\n"

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        result = parse_hf_remote(str(tmp_path))
    assert result == "myuser/myrepo"


def test_parse_hf_remote_not_found(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        result = parse_hf_remote(str(tmp_path))
    assert result is None


# ---------------------------------------------------------------------------
# Deploy status: check_render_status
# ---------------------------------------------------------------------------


def test_check_render_status_single_name():
    with patch(
        "streamtex.cli.deploy_cmd.http_probe",
        return_value=("live", "HTTP 200"),
    ):
        results = check_render_status("/tmp", name="my-app")
    assert len(results) == 1
    assert results[0].name == "my-app"
    assert results[0].status == "live"
    assert "onrender.com" in results[0].url


def test_check_render_status_from_render_yaml(tmp_path):
    yaml_content = """\
services:
  - type: web
    name: streamtex-intro
    runtime: docker
"""
    (tmp_path / "render.yaml").write_text(yaml_content)

    with patch(
        "streamtex.cli.deploy_cmd.http_probe",
        return_value=("sleep", "HTTP 502 — service may be waking up"),
    ):
        results = check_render_status(str(tmp_path))
    assert len(results) == 1
    assert results[0].name == "streamtex-intro"
    assert results[0].status == "sleep"


# ---------------------------------------------------------------------------
# Deploy status: check_hf_status
# ---------------------------------------------------------------------------


def test_check_hf_status_with_name():
    resp_data = json.dumps({"runtime": {"stage": "RUNNING"}}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = resp_data
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("streamtex.cli.deploy_cmd.urllib.request.urlopen", return_value=mock_resp):
        results = check_hf_status("/tmp", name="user/repo")
    assert len(results) == 1
    assert results[0].status == "live"
    assert results[0].name == "user/repo"
    assert "huggingface.co" in results[0].url


def test_check_hf_status_no_remote(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""

    with patch("streamtex.cli.deploy_cmd.subprocess.run", return_value=mock_result):
        results = check_hf_status(str(tmp_path))
    assert len(results) == 1
    assert results[0].status == "error"
    assert "No HF Space found" in results[0].message


# ---------------------------------------------------------------------------
# Deploy status: Click command
# ---------------------------------------------------------------------------


def test_status_command_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "status", "--help"])
    assert result.exit_code == 0
    assert "render" in result.output
    assert "huggingface" in result.output
    assert "--path" in result.output
    assert "--timeout" in result.output


def test_status_command_render():
    runner = CliRunner()
    with patch(
        "streamtex.cli.deploy_cmd.check_render_status",
        return_value=[
            DeployStatus(name="my-app", status="live", url="https://my-app.onrender.com", message="HTTP 200"),
        ],
    ):
        result = runner.invoke(cli, ["deploy", "status", "render", "my-app"])
    assert result.exit_code == 0, result.output
    assert "my-app" in result.output
    assert "Live" in result.output


def test_status_command_no_services():
    runner = CliRunner()
    with patch(
        "streamtex.cli.deploy_cmd.check_render_status",
        return_value=[],
    ):
        result = runner.invoke(cli, ["deploy", "status", "render"])
    assert result.exit_code == 0, result.output
    assert "No services found" in result.output


def test_deploy_group_shows_status():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "--help"])
    assert result.exit_code == 0
    assert "status" in result.output
