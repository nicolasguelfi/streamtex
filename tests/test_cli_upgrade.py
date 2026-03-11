"""Tests for stx project upgrade, migration system, and compatibility checker."""

import textwrap

import pytest
from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.migrations.base import Migration, MigrationResult
from streamtex.cli.migrations.compat import (
    _check_file,
    _find_py_files,
    _get_changes_in_range,
    check_compatibility,
)
from streamtex.cli.migrations.registry import (
    ALL_MIGRATIONS,
    _version_tuple,
    detect_project_version,
    get_pending_migrations,
    write_version_marker,
)

# ---------------------------------------------------------------------------
# Version utilities
# ---------------------------------------------------------------------------

class TestVersionTuple:
    def test_simple(self):
        assert _version_tuple("0.4.0") == (0, 4, 0)

    def test_comparison(self):
        assert _version_tuple("0.3.0") < _version_tuple("0.4.0")
        assert _version_tuple("0.4.6") > _version_tuple("0.4.0")
        assert _version_tuple("1.0.0") > _version_tuple("0.99.99")


# ---------------------------------------------------------------------------
# Version detection
# ---------------------------------------------------------------------------

class TestDetectProjectVersion:
    def test_from_stx_version_marker(self, tmp_path):
        (tmp_path / ".stx-version").write_text("0.4.6\n")
        (tmp_path / "pyproject.toml").write_text('[dependencies]\n"streamtex>=0.3.0"\n')
        # Marker takes precedence over pyproject.toml
        assert detect_project_version(str(tmp_path)) == "0.4.6"

    def test_from_pyproject_toml(self, tmp_path):
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = [
                "streamtex>=0.3.0",
            ]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        assert detect_project_version(str(tmp_path)) == "0.3.0"

    def test_from_pyproject_with_extras(self, tmp_path):
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = [
                "streamtex[pdf,ai]>=0.4.6",
            ]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        assert detect_project_version(str(tmp_path)) == "0.4.6"

    def test_fallback_to_zero(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        assert detect_project_version(str(tmp_path)) == "0.0.0"

    def test_no_pyproject(self, tmp_path):
        assert detect_project_version(str(tmp_path)) == "0.0.0"


class TestWriteVersionMarker:
    def test_writes_marker(self, tmp_path):
        write_version_marker(str(tmp_path), "0.4.6")
        marker = tmp_path / ".stx-version"
        assert marker.exists()
        assert marker.read_text().strip() == "0.4.6"


# ---------------------------------------------------------------------------
# Migration registry
# ---------------------------------------------------------------------------

class TestMigrationRegistry:
    def test_migrations_are_registered(self):
        versions = [m.version for m in ALL_MIGRATIONS]
        assert "0.4.0" in versions
        assert "0.4.6" in versions

    def test_migrations_are_sorted(self):
        versions = [_version_tuple(m.version) for m in ALL_MIGRATIONS]
        assert versions == sorted(versions)

    def test_get_pending_migrations(self):
        pending = get_pending_migrations("0.3.0", "0.4.6")
        versions = [m.version for m in pending]
        assert "0.4.0" in versions
        assert "0.4.6" in versions

    def test_get_pending_exclusive_start(self):
        pending = get_pending_migrations("0.4.0", "0.4.6")
        versions = [m.version for m in pending]
        assert "0.4.0" not in versions
        assert "0.4.6" in versions

    def test_get_pending_none_when_current(self):
        pending = get_pending_migrations("0.4.6", "0.4.6")
        assert len(pending) == 0

    def test_get_pending_none_when_ahead(self):
        pending = get_pending_migrations("1.0.0", "0.4.6")
        assert len(pending) == 0


# ---------------------------------------------------------------------------
# Migration v0.4.0 — ruff + pyright
# ---------------------------------------------------------------------------

class TestMigrationV040:
    def _get_migration(self):
        for m in ALL_MIGRATIONS:
            if m.version == "0.4.0":
                return m
        pytest.skip("v0.4.0 migration not registered")

    def test_check_needs_migration(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            name = "test"
            [tool.uv]
            dev-dependencies = []
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        assert m.check(str(tmp_path)) is True

    def test_check_already_done(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            name = "test"
            [tool.ruff.lint]
            ignore = ["F403"]
            [tool.pyright]
            extraPaths = [".."]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        assert m.check(str(tmp_path)) is False

    def test_apply_adds_ruff_and_pyright(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            name = "test"
            [tool.uv]
            dev-dependencies = []
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        result = m.apply(str(tmp_path))
        assert result.applied is True
        assert any("ruff" in c for c in result.changes)
        assert any("pyright" in c for c in result.changes)

        content = (tmp_path / "pyproject.toml").read_text()
        assert "[tool.ruff.lint]" in content
        assert "[tool.pyright]" in content

    def test_apply_dry_run(self, tmp_path):
        m = self._get_migration()
        pyproject = "[project]\nname = \"test\"\n"
        (tmp_path / "pyproject.toml").write_text(pyproject)
        result = m.apply(str(tmp_path), dry_run=True)
        assert result.applied is True
        # File should NOT have been modified
        content = (tmp_path / "pyproject.toml").read_text()
        assert "[tool.ruff.lint]" not in content

    def test_apply_creates_precommit(self, tmp_path):
        m = self._get_migration()
        (tmp_path / "pyproject.toml").write_text("[project]\nname = \"test\"\n")
        m.apply(str(tmp_path))
        precommit = tmp_path / ".pre-commit-config.yaml"
        assert precommit.exists()
        assert "ruff" in precommit.read_text()


# ---------------------------------------------------------------------------
# Migration v0.4.6 — preset extras
# ---------------------------------------------------------------------------

class TestMigrationV046:
    def _get_migration(self):
        for m in ALL_MIGRATIONS:
            if m.version == "0.4.6":
                return m
        pytest.skip("v0.4.6 migration not registered")

    def test_check_needs_extras(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex>=0.4.0"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        assert m.check(str(tmp_path)) is True

    def test_check_already_has_extras(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex[pdf]>=0.4.0"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        # Depending on workspace preset, may or may not need more extras
        # Without workspace, default is ["pdf"], so this should be False
        result = m.check(str(tmp_path))
        # Default extras is ["pdf"], and we already have [pdf]
        assert result is False

    def test_apply_updates_dep(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex>=0.4.0"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        result = m.apply(str(tmp_path))
        assert result.applied is True

        content = (tmp_path / "pyproject.toml").read_text()
        assert "[pdf]" in content

    def test_apply_creates_images_dir(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex>=0.4.0"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        m.apply(str(tmp_path))
        assert (tmp_path / "static" / "images").is_dir()

    def test_apply_creates_setup_py(self, tmp_path):
        m = self._get_migration()
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex>=0.4.0"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        m.apply(str(tmp_path))
        setup = tmp_path / "setup.py"
        assert setup.exists()

    def test_apply_no_pyproject(self, tmp_path):
        m = self._get_migration()
        result = m.apply(str(tmp_path))
        assert result.applied is False
        assert "not found" in result.skipped_reason


# ---------------------------------------------------------------------------
# Compatibility checker
# ---------------------------------------------------------------------------

class TestCompatChecker:
    def test_no_breaking_changes_returns_empty(self, tmp_path):
        """With empty BREAKING_CHANGES list, no issues reported."""
        (tmp_path / "app.py").write_text("from streamtex import st_write\nst_write('hello')\n")
        issues = check_compatibility(str(tmp_path), "0.3.0", "0.4.6")
        assert issues == []

    def test_find_py_files_skips_venv(self, tmp_path):
        (tmp_path / "app.py").write_text("pass")
        venv = tmp_path / ".venv" / "lib"
        venv.mkdir(parents=True)
        (venv / "foo.py").write_text("pass")
        files = _find_py_files(str(tmp_path))
        assert any("app.py" in f for f in files)
        assert not any(".venv" in f for f in files)

    def test_get_changes_in_range_empty(self):
        # No real breaking changes defined yet
        changes = _get_changes_in_range("0.3.0", "0.4.6")
        assert changes == []

    def test_check_file_with_removed_import(self, tmp_path):
        """Test the AST checker with a synthetic removed function."""
        import ast

        source = "from streamtex import st_old_func\nst_old_func()\n"
        tree = ast.parse(source, "test.py")
        changes = [{"type": "removed", "name": "st_old_func", "version": "0.5.0", "note": "Use st_new_func."}]
        issues = _check_file("test.py", tree, changes)
        assert len(issues) == 1
        assert issues[0].code == "REMOVED"
        assert "st_old_func" in issues[0].message

    def test_check_file_with_renamed_import(self, tmp_path):
        import ast

        source = "from streamtex import st_grid_layout\n"
        tree = ast.parse(source, "test.py")
        changes = [{"type": "renamed", "old": "st_grid_layout", "new": "st_grid", "version": "0.5.0"}]
        issues = _check_file("test.py", tree, changes)
        assert len(issues) == 1
        assert issues[0].code == "RENAMED"
        assert "st_grid" in issues[0].suggestion

    def test_check_file_with_param_removed(self, tmp_path):
        import ast

        source = "from streamtex import st_book\nst_book(show_toc=False)\n"
        tree = ast.parse(source, "test.py")
        changes = [
            {"type": "param_removed", "func": "st_book", "param": "show_toc", "version": "0.5.0", "note": "Use toc_config=None."}
        ]
        issues = _check_file("test.py", tree, changes)
        assert len(issues) == 1
        assert issues[0].code == "PARAM_REMOVED"

    def test_syntax_error_handled(self, tmp_path):
        (tmp_path / "bad.py").write_text("def broken(\n")
        # Inject a fake breaking change to trigger scanning
        from streamtex.cli.migrations.compat import BREAKING_CHANGES

        original = BREAKING_CHANGES.copy()
        BREAKING_CHANGES.append({"type": "removed", "name": "x", "version": "0.5.0"})
        try:
            issues = check_compatibility(str(tmp_path), "0.4.0", "0.5.0")
            assert len(issues) == 1
            assert issues[0].code == "PARSE_ERROR"
        finally:
            BREAKING_CHANGES.clear()
            BREAKING_CHANGES.extend(original)


# ---------------------------------------------------------------------------
# CLI integration: stx project upgrade
# ---------------------------------------------------------------------------

class TestUpgradeCLI:
    def test_upgrade_no_pyproject(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["project", "upgrade", str(tmp_path)])
        assert result.exit_code != 0
        assert "pyproject.toml" in result.output

    def test_upgrade_check_only(self, tmp_path):
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex>=0.1.0"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        runner = CliRunner()
        result = runner.invoke(cli, ["project", "upgrade", "--check", str(tmp_path)])
        assert "Detecting versions" in result.output
        assert "Checking compatibility" in result.output
        # Should not show migration steps
        assert "Applying migrations" not in result.output

    def test_upgrade_dry_run(self, tmp_path):
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex>=0.1.0"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["project", "upgrade", "--dry-run", "--skip-sync", "--skip-claude", str(tmp_path)],
        )
        assert "dry-run" in result.output.lower() or "Dry run" in result.output

    def test_upgrade_already_up_to_date(self, tmp_path):
        """If project version >= installed version, prints up-to-date."""
        pyproject = textwrap.dedent("""\
            [project]
            dependencies = ["streamtex>=99.99.99"]
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        runner = CliRunner()
        result = runner.invoke(cli, ["project", "upgrade", str(tmp_path)])
        assert result.exit_code == 0
        assert "up to date" in result.output.lower()

    def test_upgrade_applies_migrations(self, tmp_path):
        """Full upgrade from 0.1.0 applies v0.4.0 + v0.4.6 migrations."""
        pyproject = textwrap.dedent("""\
            [project]
            name = "test-project"
            dependencies = ["streamtex>=0.1.0"]
            [tool.uv]
            dev-dependencies = []
        """)
        (tmp_path / "pyproject.toml").write_text(pyproject)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["project", "upgrade", "--skip-sync", "--skip-claude", str(tmp_path)],
        )
        assert result.exit_code == 0
        assert "Upgrade complete" in result.output
        # Check marker was written
        assert (tmp_path / ".stx-version").exists()
        # Check structural changes were applied
        content = (tmp_path / "pyproject.toml").read_text()
        assert "[tool.ruff.lint]" in content

    def test_upgrade_command_registered(self):
        """stx project upgrade should be a valid command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["project", "upgrade", "--help"])
        assert result.exit_code == 0
        assert "upgrade" in result.output.lower()
        assert "--check" in result.output
        assert "--dry-run" in result.output


# ---------------------------------------------------------------------------
# MigrationResult / base class
# ---------------------------------------------------------------------------

class TestMigrationBase:
    def test_migration_result_defaults(self):
        r = MigrationResult(version="1.0.0", description="test", applied=True)
        assert r.changes == []
        assert r.skipped_reason == ""

    def test_migration_base_not_implemented(self):
        m = Migration()
        with pytest.raises(NotImplementedError):
            m.check("/tmp")
        with pytest.raises(NotImplementedError):
            m.apply("/tmp")
