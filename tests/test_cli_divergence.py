"""Tests for streamtex.cli._divergence — warning surfaced when the tool venv
and a project venv ship different streamtex versions.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import click
import pytest

from streamtex.cli import _divergence

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


def _scaffold_project(tmp_path: Path, project_streamtex_version: str | None = None) -> Path:
    """Create a tmp project (pyproject + stx.toml + optional fake venv with
    streamtex/__init__.py containing a controlled __version__)."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n')
    (tmp_path / "stx.toml").write_text('[project]\nname = "demo"\n')
    if project_streamtex_version is not None:
        sp = tmp_path / ".venv" / "lib" / "python3.13" / "site-packages" / "streamtex"
        sp.mkdir(parents=True)
        (sp / "__init__.py").write_text(
            f'"""Fake streamtex for divergence tests."""\n'
            f'__version__ = "{project_streamtex_version}"\n'
        )
    return tmp_path


@pytest.fixture
def fake_tool_version(monkeypatch):
    """Pin the tool streamtex version to a known string."""

    def _set(v: str):
        # _tool_version() does `from streamtex import __version__`; setattr
        # ensures the rebinding is visible on the next call.
        import streamtex

        monkeypatch.setattr(streamtex, "__version__", v, raising=True)
        return v

    return _set


def _force_tty(monkeypatch, *, value: bool):
    """Make stdin/stdout report isatty()=value so the confirm path is exercised."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: value)
    monkeypatch.setattr("sys.stdout.isatty", lambda: value)


# --------------------------------------------------------------------------- #
# Version detection                                                           #
# --------------------------------------------------------------------------- #


def test_project_version_reads_init_py(tmp_path: Path):
    project = _scaffold_project(tmp_path, "0.9.99")
    assert _divergence._project_version(project) == "0.9.99"


def test_project_version_returns_none_when_no_venv(tmp_path: Path):
    project = _scaffold_project(tmp_path, project_streamtex_version=None)
    assert _divergence._project_version(project) is None


def test_project_version_returns_none_when_no_version_marker(tmp_path: Path):
    project = _scaffold_project(tmp_path, "ignored")
    sp = project / ".venv" / "lib" / "python3.13" / "site-packages" / "streamtex"
    (sp / "__init__.py").write_text('"""no version marker here"""\n')
    assert _divergence._project_version(project) is None


# --------------------------------------------------------------------------- #
# Silence paths (no warning expected)                                         #
# --------------------------------------------------------------------------- #


def test_silent_when_no_project_root(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    fake_tool_version("0.7.18")
    monkeypatch.chdir(tmp_path)  # no pyproject.toml + stx.toml here
    _divergence.maybe_warn_divergence("pack list")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_silent_when_project_has_no_venv(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path)
    monkeypatch.chdir(project)
    _divergence.maybe_warn_divergence("pack list")
    assert capsys.readouterr().out == ""


def test_silent_when_versions_match(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.18")
    monkeypatch.chdir(project)
    _divergence.maybe_warn_divergence("pack list")
    assert capsys.readouterr().out == ""


def test_silent_when_running_in_project_venv(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    """When the running interpreter IS the project's .venv (e.g. `uv run stx`),
    introspection already targets the project — no divergence to warn about.
    Replaces the old STX_DELEGATED env-var short-circuit."""
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    # Pretend we're being run by the project's venv interpreter.
    fake_exe = project / ".venv" / "bin" / "python"
    fake_exe.parent.mkdir(parents=True, exist_ok=True)
    fake_exe.write_text("")  # presence is enough; we only resolve the path
    monkeypatch.setattr("sys.executable", str(fake_exe))
    _divergence.maybe_warn_divergence("pack list")
    assert capsys.readouterr().out == ""


def test_silent_when_only_local_suffix_differs(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    """`0.7.18` (PyPI) vs `0.7.18+g1a2b3c` (editable build) is the same upstream
    release — must not warn."""
    fake_tool_version("0.7.18+g1a2b3c")
    project = _scaffold_project(tmp_path, "0.7.18")
    monkeypatch.chdir(project)
    _divergence.maybe_warn_divergence("pack list")
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------- #
# Warning paths                                                               #
# --------------------------------------------------------------------------- #


def test_warns_when_versions_differ_non_tty(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    """Non-TTY: emit the warning but do NOT prompt (would deadlock in CI)."""
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=False)
    _divergence.maybe_warn_divergence("pack list")
    out = capsys.readouterr().out
    assert "divergence" in out.lower()
    assert "0.7.18" in out and "0.7.17" in out
    assert "uv run stx pack list" in out
    # Cache should now contain the suppression key.
    cache_path = project / ".stx_cache" / _divergence._CACHE_FILENAME
    assert cache_path.is_file()
    data = json.loads(cache_path.read_text())
    assert any(k.startswith("pack list|") for k in data)


def test_does_not_re_warn_within_ttl(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=False)
    _divergence.maybe_warn_divergence("pack list")
    assert "divergence" in capsys.readouterr().out.lower()
    # Second invocation in the same session must stay silent.
    _divergence.maybe_warn_divergence("pack list")
    assert capsys.readouterr().out == ""


def test_re_warns_after_ttl_expires(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=False)
    _divergence.maybe_warn_divergence("pack list")
    capsys.readouterr()  # drain
    # Backdate the cache to >1h ago.
    cache_path = project / ".stx_cache" / _divergence._CACHE_FILENAME
    data = json.loads(cache_path.read_text())
    expired_ts = time.time() - _divergence._CACHE_TTL_SECONDS - 1
    for k in data:
        data[k] = expired_ts
    cache_path.write_text(json.dumps(data))
    _divergence.maybe_warn_divergence("pack list")
    assert "divergence" in capsys.readouterr().out.lower()


def test_cache_key_separates_command_names(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    """Warning for `pack list` must not suppress the warning for `component list`."""
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=False)
    _divergence.maybe_warn_divergence("pack list")
    capsys.readouterr()
    _divergence.maybe_warn_divergence("component list")
    out = capsys.readouterr().out
    assert "divergence" in out.lower()
    assert "component list" in out


# --------------------------------------------------------------------------- #
# TTY confirmation                                                            #
# --------------------------------------------------------------------------- #


def test_tty_choice_yes_continues(monkeypatch, tmp_path: Path, fake_tool_version):
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=True)
    monkeypatch.setattr(click, "prompt", lambda *a, **kw: "y")
    # Should not raise.
    _divergence.maybe_warn_divergence("pack list")


def test_tty_choice_no_aborts(monkeypatch, tmp_path: Path, fake_tool_version):
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=True)
    monkeypatch.setattr(click, "prompt", lambda *a, **kw: "n")
    with pytest.raises(click.Abort):
        _divergence.maybe_warn_divergence("pack list")


def test_tty_choice_never_persists_dismissal(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    """Choosing 'v' (never) must suppress this exact divergence permanently,
    even across cache TTL expiry — replaces the old opt-out env var."""
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=True)
    monkeypatch.setattr(click, "prompt", lambda *a, **kw: "v")
    _divergence.maybe_warn_divergence("pack list")  # warns once, records "never"
    capsys.readouterr()  # drain

    # A "never:" marker must be in the cache.
    cache_path = project / ".stx_cache" / _divergence._CACHE_FILENAME
    data = json.loads(cache_path.read_text())
    assert any(k.startswith(_divergence._FOREVER_PREFIX) for k in data)

    # Subsequent calls stay silent — even in a fresh "session" (non-TTY) and
    # even after the rate-limit TTL would have expired.
    _force_tty(monkeypatch, value=False)
    _divergence.maybe_warn_divergence("pack list")
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------- #
# Robustness                                                                  #
# --------------------------------------------------------------------------- #


def test_corrupt_cache_is_ignored(monkeypatch, tmp_path: Path, capsys, fake_tool_version):
    """A broken JSON cache must not prevent the warning."""
    fake_tool_version("0.7.18")
    project = _scaffold_project(tmp_path, "0.7.17")
    cache_path = project / ".stx_cache" / _divergence._CACHE_FILENAME
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text("{ this is not json")
    monkeypatch.chdir(project)
    _force_tty(monkeypatch, value=False)
    _divergence.maybe_warn_divergence("pack list")
    assert "divergence" in capsys.readouterr().out.lower()
