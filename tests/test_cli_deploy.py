"""Tests for stx deploy preflight/docker commands."""

import os
import subprocess
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.deploy_cmd import (
    PreflightCheck,
    docker_build,
    find_docker,
    generate_dockerfile,
    run_preflight,
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
