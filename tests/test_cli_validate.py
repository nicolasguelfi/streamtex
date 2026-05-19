"""Tests for `stx validate` aggregate command."""

from __future__ import annotations

import os
from pathlib import Path

from click.testing import CliRunner

from streamtex.cli.commands import cli


def _make_project(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n')
    (tmp_path / "stx.toml").write_text('[project]\nname = "demo"\n')
    return tmp_path


def _run(cmd: list[str], cwd: Path):
    runner = CliRunner()
    prev = os.getcwd()
    try:
        os.chdir(cwd)
        return runner.invoke(cli, cmd)
    finally:
        os.chdir(prev)


def test_validate_runs_on_empty_project(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["validate"], project)
    # Empty project = no packs to validate; should return 0 with friendly output
    assert result.exit_code == 0, result.output


def test_validate_outputs_sections(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["validate"], project)
    assert result.exit_code == 0
    assert "Packs" in result.output
    assert "Components" in result.output
    assert "Design systems" in result.output
    assert "Kits" in result.output


def test_validate_includes_ds_pass_for_installed_pack(tmp_path: Path, monkeypatch):
    """If streamtex_design is reachable, the DS pass surfaces its DS."""
    project = _make_project(tmp_path)
    try:
        import streamtex_design  # noqa: F401
    except ImportError:
        import pytest

        pytest.skip("streamtex_design not installed in this venv")

    from streamtex.core import discovery

    class _Pack:
        name = "streamtex_design"
        entry_point_module = "streamtex_design"
        state = "nominal"

    monkeypatch.setattr(discovery, "discover_packs", lambda _p=None: [_Pack()])

    result = _run(["validate"], project)
    assert "Design systems" in result.output
    # The default DS shipped with streamtex_design should be listed
    assert "streamtex_design:default" in result.output


def test_validate_kit_failure_propagates_to_exit_code(tmp_path: Path, monkeypatch):
    """A failing kit makes the aggregate validate exit 2."""
    project = _make_project(tmp_path)
    from streamtex.core import discovery, validation

    class _Pack:
        name = "fake"
        entry_point_module = "streamtex"  # any importable module with __file__
        state = "nominal"

    class _KitErr:
        severity = "error"
        code = "KV001"
        message = "synthetic kit failure"

    # Make the pack's filesystem layout look like it has a kits/ dir with one TOML
    import streamtex as _stx

    pack_root = Path(_stx.__file__).resolve().parent
    kits_dir = pack_root / "kits"
    fake_kit = kits_dir / "fake_kit.toml"
    created_dir = not kits_dir.exists()
    if created_dir:
        kits_dir.mkdir(parents=True)
    fake_kit.write_text("name = 'fake_kit'\n")
    try:
        monkeypatch.setattr(discovery, "discover_packs", lambda _p=None: [_Pack()])
        monkeypatch.setattr(validation, "validate_kit", lambda _p: [_KitErr()])
        # Stub the other validators to no-op so only the kit failure is seen
        monkeypatch.setattr(validation, "validate_pack", lambda _p: [])
        monkeypatch.setattr(discovery, "discover_components", lambda _packs: [])

        result = _run(["validate"], project)
        assert result.exit_code == 2, result.output
        assert "KV001" in result.output
    finally:
        fake_kit.unlink(missing_ok=True)
        if created_dir and kits_dir.exists() and not any(kits_dir.iterdir()):
            kits_dir.rmdir()


def test_validate_has_strict_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--help"])
    assert result.exit_code == 0
    assert "--strict" in result.output


def test_validate_strict_clean_project_exits_zero(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["validate", "--strict"], project)
    assert result.exit_code == 0, result.output


def test_validate_exit_code_2_on_errors(tmp_path: Path, monkeypatch):
    """A simulated 'error' validation issue → exit code 2."""
    from streamtex.core import validation

    project = _make_project(tmp_path)

    class _FakeIssue:
        severity = "error"
        code = "TEST001"
        message = "synthetic error"

    monkeypatch.setattr(validation, "validate_pack", lambda _path: [_FakeIssue()])

    # Need at least one discovered pack — patch discover_packs to inject one
    from streamtex.core import discovery

    class _FakePack:
        name = "fake"
        entry_point_module = "streamtex"  # any importable module
        state = "nominal"

    monkeypatch.setattr(discovery, "discover_packs", lambda _p=None: [_FakePack()])

    result = _run(["validate"], project)
    assert result.exit_code == 2, result.output
    assert "TEST001" in result.output


def test_validate_exit_code_1_on_warnings_only(tmp_path: Path, monkeypatch):
    """Warnings only without --strict → exit code 1."""
    from streamtex.core import discovery, validation

    project = _make_project(tmp_path)

    class _FakeWarning:
        severity = "warning"
        code = "TESTW01"
        message = "synthetic warning"

    class _FakePack:
        name = "fake"
        entry_point_module = "streamtex"
        state = "nominal"

    monkeypatch.setattr(validation, "validate_pack", lambda _path: [_FakeWarning()])
    monkeypatch.setattr(discovery, "discover_packs", lambda _p=None: [_FakePack()])

    result = _run(["validate"], project)
    assert result.exit_code == 1, result.output
    assert "TESTW01" in result.output
    assert "warning" in result.output.lower()


def test_validate_strict_promotes_warnings_to_errors(tmp_path: Path, monkeypatch):
    """Warnings only with --strict → exit code 2."""
    from streamtex.core import discovery, validation

    project = _make_project(tmp_path)

    class _FakeWarning:
        severity = "warning"
        code = "TESTW02"
        message = "synthetic warning"

    class _FakePack:
        name = "fake"
        entry_point_module = "streamtex"
        state = "nominal"

    monkeypatch.setattr(validation, "validate_pack", lambda _path: [_FakeWarning()])
    monkeypatch.setattr(discovery, "discover_packs", lambda _p=None: [_FakePack()])

    result = _run(["validate", "--strict"], project)
    assert result.exit_code == 2, result.output
    assert "TESTW02" in result.output
    assert "promoted to errors" in result.output
