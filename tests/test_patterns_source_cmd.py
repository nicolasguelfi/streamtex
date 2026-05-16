"""Tests for `stx patterns source` subgroup + structured trace_source()."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from streamtex.cli.patterns_cmd import patterns
from streamtex.patterns import SourceNotFoundError
from streamtex.patterns.project_toml import write_project_source
from streamtex.patterns.resolver import (
    SourceLevel,
    TraceStatus,
    resolve_source,
    trace_source,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_MANIFEST = """\
[repo]
name = "streamtex-patterns"
version = "0.1.0"
description = "fixture"
spec_version = "A2"
since = "2026-05-10"

[scopes]
core = "Universal"

[presets]
core = "core.toml"
"""


@pytest.fixture()
def valid_source(tmp_path: Path) -> Path:
    """A minimal directory that passes `_is_valid_source`."""
    src = tmp_path / "src-patterns"
    src.mkdir()
    (src / "manifest.toml").write_text(_MANIFEST, encoding="utf-8")
    (src / "core").mkdir()
    (src / "presets").mkdir()
    return src


@pytest.fixture()
def invalid_source(tmp_path: Path) -> Path:
    """A directory missing manifest.toml."""
    src = tmp_path / "bogus"
    src.mkdir()
    return src


# ---------------------------------------------------------------------------
# trace_source()
# ---------------------------------------------------------------------------

def test_trace_all_skipped_when_nothing_configured(tmp_path: Path) -> None:
    entries, resolved = trace_source(tmp_path)
    assert resolved is None
    # 4 levels in trace
    assert {e.level for e in entries} == set(SourceLevel)
    # L1 / L2 / L3 / L4 all skipped (no override, no toml, no workspace_root)
    for e in entries:
        assert e.status == TraceStatus.SKIPPED


def test_trace_cli_override_matched(tmp_path: Path, valid_source: Path) -> None:
    entries, resolved = trace_source(tmp_path, cli_override=str(valid_source))
    assert resolved is not None
    assert resolved.level == SourceLevel.CLI_OVERRIDE
    assert entries[0].status == TraceStatus.MATCHED
    # All other levels reported as unreached
    for e in entries[1:]:
        assert e.status in (TraceStatus.UNREACHED, TraceStatus.SKIPPED)


def test_trace_cli_override_invalid(tmp_path: Path, invalid_source: Path) -> None:
    entries, resolved = trace_source(tmp_path, cli_override=str(invalid_source))
    assert resolved is None
    assert entries[0].status == TraceStatus.INVALID
    assert "manifest.toml" in (entries[0].detail or "")


def test_trace_cli_override_git_plus_marked_invalid(tmp_path: Path) -> None:
    entries, resolved = trace_source(tmp_path, cli_override="git+https://x/y.git")
    assert resolved is None
    assert entries[0].status == TraceStatus.INVALID
    assert "git+" in (entries[0].detail or "")


def test_trace_project_toml_matched(tmp_path: Path, valid_source: Path) -> None:
    (tmp_path / "stx.toml").write_text(
        f"[patterns]\nsource = \"{valid_source}\"\n", encoding="utf-8",
    )
    entries, resolved = trace_source(tmp_path)
    assert resolved is not None
    assert resolved.level == SourceLevel.PROJECT_TOML
    matched = next(e for e in entries if e.status == TraceStatus.MATCHED)
    assert matched.level == SourceLevel.PROJECT_TOML


def test_trace_workspace_toml_matched(tmp_path: Path, valid_source: Path) -> None:
    workspace = tmp_path / "ws"
    project = workspace / "projects" / "p1"
    project.mkdir(parents=True)
    (workspace / "stx.toml").write_text(
        f"[patterns]\nsource = \"{valid_source}\"\n", encoding="utf-8",
    )
    entries, resolved = trace_source(project, workspace_root=workspace)
    assert resolved is not None
    assert resolved.level == SourceLevel.WORKSPACE_TOML


def test_trace_auto_sibling_matched(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    project = workspace / "projects" / "p1"
    project.mkdir(parents=True)
    sibling = workspace / "streamtex-patterns"
    sibling.mkdir()
    (sibling / "manifest.toml").write_text(_MANIFEST, encoding="utf-8")
    entries, resolved = trace_source(project, workspace_root=workspace)
    assert resolved is not None
    assert resolved.level == SourceLevel.AUTO_SIBLING


def test_resolve_raises_with_hint_on_failure(tmp_path: Path) -> None:
    with pytest.raises(SourceNotFoundError) as excinfo:
        resolve_source(tmp_path)
    msg = str(excinfo.value)
    assert "L1" in msg and "L4" in msg
    assert "stx patterns source clone" in msg
    assert "stx patterns source set" in msg


# ---------------------------------------------------------------------------
# write_project_source() round-trip
# ---------------------------------------------------------------------------

def test_write_project_source_creates_stx_toml(tmp_path: Path) -> None:
    written = write_project_source(tmp_path, "../shared/patterns")
    assert written.name == "stx.toml"
    text = written.read_text(encoding="utf-8")
    assert "[patterns]" in text
    assert 'source = "../shared/patterns"' in text


def test_write_project_source_preserves_selection(tmp_path: Path) -> None:
    (tmp_path / "stx.toml").write_text(
        "[workspace]\nname = \"x\"\n\n[patterns]\n\n[patterns.selection]\n"
        "mode = \"individual\"\nitems = [\"ptn_a\"]\n",
        encoding="utf-8",
    )
    write_project_source(tmp_path, "./streamtex-patterns")
    text = (tmp_path / "stx.toml").read_text(encoding="utf-8")
    assert "[patterns.selection]" in text
    assert 'mode = "individual"' in text
    assert 'source = "./streamtex-patterns"' in text
    # workspace block preserved
    assert 'name = "x"' in text


# ---------------------------------------------------------------------------
# stx patterns source show
# ---------------------------------------------------------------------------

def test_source_show_resolves(tmp_path: Path, valid_source: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "stx.toml").write_text(
        f"[patterns]\nsource = \"{valid_source}\"\n", encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "show"])
    assert result.exit_code == 0
    # Don't assert on coloured Rich output; assert on substrings that
    # survive the table renderer with reasonable terminal width.
    assert "Resolved" in result.output
    assert "project_toml" in result.output


def test_source_show_unresolved_prints_next_steps(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "show"])
    assert result.exit_code == 0
    assert "No source resolved" in result.output
    assert "source clone" in result.output


# ---------------------------------------------------------------------------
# stx patterns source set
# ---------------------------------------------------------------------------

def test_source_set_writes_and_validates(
    tmp_path: Path, valid_source: Path, monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "set", str(valid_source)])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "stx.toml").read_text(encoding="utf-8")
    assert f'source = "{valid_source}"' in text


def test_source_set_refuses_invalid_without_allow_missing(
    tmp_path: Path, invalid_source: Path, monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "set", str(invalid_source)])
    assert result.exit_code != 0
    assert "manifest.toml" in result.output


def test_source_set_records_with_allow_missing(
    tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        ["source", "set", "/does/not/exist/yet", "--allow-missing"],
    )
    assert result.exit_code == 0, result.output
    text = (tmp_path / "stx.toml").read_text(encoding="utf-8")
    assert "/does/not/exist/yet" in text


# ---------------------------------------------------------------------------
# stx patterns source link
# ---------------------------------------------------------------------------

@pytest.mark.skipif(sys.platform == "win32",
                    reason="symlinks require admin on Windows")
def test_source_link_creates_symlink(
    tmp_path: Path, valid_source: Path, monkeypatch,
) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "stx.toml").write_text(
        "[workspace]\nname = \"demo\"\n", encoding="utf-8",
    )
    monkeypatch.chdir(workspace)
    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "link", str(valid_source)])
    assert result.exit_code == 0, result.output
    dst = workspace / "streamtex-patterns"
    assert dst.is_symlink()
    assert dst.resolve() == valid_source.resolve()


def test_source_link_refuses_without_workspace(
    tmp_path: Path, valid_source: Path, monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)  # no stx.toml here → no workspace
    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "link", str(valid_source)])
    assert result.exit_code != 0
    assert "workspace" in result.output.lower()


def test_source_link_refuses_invalid_target(
    tmp_path: Path, invalid_source: Path, monkeypatch,
) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "stx.toml").write_text(
        "[workspace]\nname = \"demo\"\n", encoding="utf-8",
    )
    monkeypatch.chdir(workspace)
    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "link", str(invalid_source)])
    assert result.exit_code != 0
    assert "manifest.toml" in result.output


# ---------------------------------------------------------------------------
# stx patterns source clone (subprocess mocked)
# ---------------------------------------------------------------------------

def test_source_clone_uses_default_url_and_target(
    tmp_path: Path, valid_source: Path, monkeypatch,
) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "stx.toml").write_text(
        "[workspace]\nname = \"demo\"\n", encoding="utf-8",
    )
    monkeypatch.chdir(workspace)

    expected_target = workspace / "streamtex-patterns"

    def fake_run(cmd, capture_output=False, text=False, timeout=None):
        # Simulate a successful git clone: copy valid_source into expected_target
        import shutil

        assert cmd[0].endswith("git")
        assert cmd[1] == "clone"
        assert cmd[-1] == str(expected_target)
        shutil.copytree(valid_source, expected_target)

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    runner = CliRunner()
    with patch("subprocess.run", side_effect=fake_run):
        result = runner.invoke(patterns, ["source", "clone"])
    assert result.exit_code == 0, result.output
    assert (expected_target / "manifest.toml").is_file()


def test_source_clone_refuses_when_target_non_empty(
    tmp_path: Path, monkeypatch,
) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "stx.toml").write_text(
        "[workspace]\nname = \"demo\"\n", encoding="utf-8",
    )
    existing = workspace / "streamtex-patterns"
    existing.mkdir()
    (existing / "leftover.txt").write_text("old", encoding="utf-8")
    monkeypatch.chdir(workspace)

    runner = CliRunner()
    result = runner.invoke(patterns, ["source", "clone"])
    assert result.exit_code != 0
    assert "non-empty" in result.output or "--force" in result.output
