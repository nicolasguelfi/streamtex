"""Tests for stx publish check/pypi commands."""

import os
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.publish_cmd import run_publish_checks

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_publish_project(tmp_path):
    """Create a minimal project structure for publish checks."""
    proj = tmp_path / "streamtex-proj"
    proj.mkdir()

    # pyproject.toml
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "streamtex"\nversion = "0.3.0"\n'
        'dependencies = ["streamlit>=1.54.0"]\n'
    )

    # README.md
    (proj / "README.md").write_text("# StreamTeX\n")

    # LICENSE
    (proj / "LICENSE").write_text("MIT License\n")

    # streamtex/__init__.py with __version__
    stx_dir = proj / "streamtex"
    stx_dir.mkdir()
    (stx_dir / "__init__.py").write_text('__version__ = "0.3.0"\n')

    # dist/ with build artifacts
    dist_dir = proj / "dist"
    dist_dir.mkdir()
    (dist_dir / "streamtex-0.3.0-py3-none-any.whl").write_text("")
    (dist_dir / "streamtex-0.3.0.tar.gz").write_text("")

    return proj


# ---------------------------------------------------------------------------
# PublishCheck / run_publish_checks
# ---------------------------------------------------------------------------


def test_publish_check_valid_project(tmp_path):
    proj = _make_publish_project(tmp_path)

    def fake_run(cmd, **kwargs):
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        r.stderr = ""
        return r

    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        checks = run_publish_checks(str(proj))

    statuses = {c.name: c.status for c in checks}
    assert statuses["pyproject.toml"] == "pass"
    assert statuses["version"] == "pass"
    assert statuses["README.md"] == "pass"
    assert statuses["LICENSE"] == "pass"
    assert statuses["__version__"] == "pass"
    assert statuses["no dev deps"] == "pass"
    assert statuses["tests"] == "pass"
    assert statuses["lint"] == "pass"
    assert statuses["build"] == "pass"
    assert statuses["dist files"] == "pass"


def test_publish_check_missing_pyproject(tmp_path):
    proj = _make_publish_project(tmp_path)
    os.remove(proj / "pyproject.toml")

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "pyproject.toml")
    assert check.status == "fail"
    assert "Missing" in check.message


def test_publish_check_missing_version(tmp_path):
    proj = _make_publish_project(tmp_path)
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "streamtex"\ndependencies = []\n'
    )

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "version")
    assert check.status == "fail"


def test_publish_check_missing_readme(tmp_path):
    proj = _make_publish_project(tmp_path)
    os.remove(proj / "README.md")

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "README.md")
    assert check.status == "fail"


def test_publish_check_missing_license(tmp_path):
    proj = _make_publish_project(tmp_path)
    os.remove(proj / "LICENSE")

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "LICENSE")
    assert check.status == "fail"


def test_publish_check_version_mismatch(tmp_path):
    proj = _make_publish_project(tmp_path)
    (proj / "streamtex" / "__init__.py").write_text('__version__ = "0.2.0"\n')

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "__version__")
    assert check.status == "fail"
    assert "Mismatch" in check.message


def test_publish_check_dynamic_version_passes(tmp_path):
    """__version__ resolved via importlib.metadata (indented or not) passes."""
    proj = _make_publish_project(tmp_path)
    (proj / "streamtex" / "__init__.py").write_text(
        "from importlib.metadata import version as _pkg_version\n"
        "try:\n"
        '    __version__ = _pkg_version("streamtex")\n'
        "except Exception:\n"
        '    __version__ = "0.0.0"\n'
    )

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "__version__")
    assert check.status == "pass"
    assert "Dynamic" in check.message


def test_publish_check_dev_deps_in_dependencies(tmp_path):
    proj = _make_publish_project(tmp_path)
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "streamtex"\nversion = "0.3.0"\n'
        'dependencies = ["streamlit", "pytest"]\n'
    )

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "no dev deps")
    assert check.status == "fail"
    assert "pytest" in check.message


def test_publish_check_skip_tests(tmp_path):
    proj = _make_publish_project(tmp_path)

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=False)

    names = [c.name for c in checks]
    assert "tests" not in names


def test_publish_check_skip_lint(tmp_path):
    proj = _make_publish_project(tmp_path)

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=False, skip_lint=True)

    names = [c.name for c in checks]
    assert "lint" not in names


def test_publish_check_build_success(tmp_path):
    proj = _make_publish_project(tmp_path)

    def fake_run(cmd, **kwargs):
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        r.stderr = ""
        return r

    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "build")
    assert check.status == "pass"


def test_publish_check_build_failure(tmp_path):
    proj = _make_publish_project(tmp_path)

    def fake_run(cmd, **kwargs):
        r = MagicMock()
        r.returncode = 1
        r.stdout = ""
        r.stderr = "error"
        return r

    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        checks = run_publish_checks(str(proj), skip_tests=True, skip_lint=True)

    check = next(c for c in checks if c.name == "build")
    assert check.status == "fail"


def test_publish_check_no_uv(tmp_path):
    proj = _make_publish_project(tmp_path)

    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        checks = run_publish_checks(str(proj), skip_tests=False, skip_lint=False)

    # tests, lint, and build should all be warn
    test_check = next(c for c in checks if c.name == "tests")
    assert test_check.status == "warn"
    lint_check = next(c for c in checks if c.name == "lint")
    assert lint_check.status == "warn"
    build_check = next(c for c in checks if c.name == "build")
    assert build_check.status == "warn"


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------


def test_check_command_valid(tmp_path):
    proj = _make_publish_project(tmp_path)

    def fake_run(cmd, **kwargs):
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        r.stderr = ""
        return r

    runner = CliRunner()
    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        result = runner.invoke(
            cli, ["publish", "check", str(proj), "--skip-tests", "--skip-lint"]
        )

    assert result.exit_code == 0, result.output
    assert "PASSED" in result.output


def test_check_command_invalid(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()

    runner = CliRunner()
    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        result = runner.invoke(
            cli, ["publish", "check", str(empty), "--skip-tests", "--skip-lint"]
        )

    assert result.exit_code == 0
    assert "FAILED" in result.output


def test_pypi_command_success(tmp_path):
    proj = _make_publish_project(tmp_path)

    call_log = []

    def fake_run(cmd, **kwargs):
        call_log.append(cmd)
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        r.stderr = ""
        return r

    runner = CliRunner()
    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        result = runner.invoke(
            cli, ["publish", "pypi", str(proj), "--skip-tests", "--skip-lint"]
        )

    assert result.exit_code == 0, result.output
    assert "Published!" in result.output
    assert "pypi.org" in result.output


def test_pypi_command_test_pypi(tmp_path):
    proj = _make_publish_project(tmp_path)

    call_log = []

    def fake_run(cmd, **kwargs):
        call_log.append(cmd)
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        r.stderr = ""
        return r

    runner = CliRunner()
    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        result = runner.invoke(
            cli,
            ["publish", "pypi", str(proj), "--test", "--skip-tests", "--skip-lint"],
        )

    assert result.exit_code == 0, result.output
    assert "test.pypi.org" in result.output
    # Verify --index testpypi was passed to uv publish
    publish_calls = [c for c in call_log if "publish" in c]
    assert any("testpypi" in str(c) for c in publish_calls)


def test_pypi_command_check_fails(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()

    runner = CliRunner()
    with patch("streamtex.cli.publish_cmd._find_uv", return_value=None):
        result = runner.invoke(
            cli, ["publish", "pypi", str(empty), "--skip-tests", "--skip-lint"]
        )

    assert result.exit_code != 0
    assert "Publish checks failed" in result.output


def test_pypi_command_build_fails(tmp_path):
    proj = _make_publish_project(tmp_path)

    call_count = [0]

    def fake_run(cmd, **kwargs):
        call_count[0] += 1
        r = MagicMock()
        # First call (check build) succeeds, second call (actual build) fails
        if "build" in cmd and call_count[0] > 1:
            r.returncode = 1
            r.stderr = "build error"
        else:
            r.returncode = 0
        r.stdout = ""
        if not hasattr(r, "stderr"):
            r.stderr = ""
        return r

    runner = CliRunner()
    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        result = runner.invoke(
            cli, ["publish", "pypi", str(proj), "--skip-tests", "--skip-lint"]
        )

    assert result.exit_code != 0
    assert "Build failed" in result.output


def test_pypi_command_upload_fails(tmp_path):
    proj = _make_publish_project(tmp_path)

    def fake_run(cmd, **kwargs):
        r = MagicMock()
        r.stdout = ""
        r.stderr = ""
        # uv publish fails
        if "publish" in cmd:
            r.returncode = 1
        else:
            r.returncode = 0
        return r

    runner = CliRunner()
    with (
        patch("streamtex.cli.publish_cmd.subprocess.run", side_effect=fake_run),
        patch("streamtex.cli.publish_cmd._find_uv", return_value="/usr/bin/uv"),
    ):
        result = runner.invoke(
            cli, ["publish", "pypi", str(proj), "--skip-tests", "--skip-lint"]
        )

    assert result.exit_code != 0
    assert "Publish failed" in result.output


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------


def test_publish_check_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["publish", "check", "--help"])
    assert result.exit_code == 0
    assert "--skip-tests" in result.output
    assert "--skip-lint" in result.output


def test_publish_pypi_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["publish", "pypi", "--help"])
    assert result.exit_code == 0
    assert "--test" in result.output
    assert "--skip-tests" in result.output
    assert "--skip-lint" in result.output


def test_publish_group_shows_commands():
    runner = CliRunner()
    result = runner.invoke(cli, ["publish", "--help"])
    assert result.exit_code == 0
    assert "check" in result.output
    assert "pypi" in result.output
