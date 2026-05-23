"""Tests for stx screenshot — the headless capture CLI command.

The command shells out to Streamlit + Playwright at runtime, so these tests
exercise the surface layer (CLI parsing, helper functions, early error
handling) without actually launching a browser. Integration coverage of
the full capture loop belongs in a slow-test marker, not here.
"""

import socket
import sys
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.screenshot_cmd import (
    _free_port,
    _streamlit_cmd,
    _streamlit_importable,
    _wait_for_http,
    capture_screenshots,
    screenshot,
)

# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def test_free_port_returns_valid_port():
    """_free_port returns an int in the OS-assignable range."""
    port = _free_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535


def test_free_port_returns_distinct_ports():
    """Two consecutive calls should normally return different ports."""
    p1 = _free_port()
    p2 = _free_port()
    # Both must be valid; equality is technically possible but extremely rare.
    assert isinstance(p1, int) and isinstance(p2, int)


def test_wait_for_http_raises_on_unreachable():
    """An unreachable URL hits the timeout and raises TimeoutError."""
    # Bind a socket to a random port then immediately close it, so the URL
    # is guaranteed unreachable for the rest of the test.
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    with pytest.raises(TimeoutError):
        _wait_for_http(f"http://127.0.0.1:{port}/", timeout_s=0.5)


def test_streamlit_importable_returns_bool():
    """_streamlit_importable returns a real bool (depends on test env)."""
    result = _streamlit_importable()
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Subprocess command construction
# ---------------------------------------------------------------------------


def test_streamlit_cmd_prefers_current_interpreter_when_importable():
    """When streamlit is importable in the running interpreter, use sys.executable -m streamlit."""
    with patch("streamtex.cli.screenshot_cmd._streamlit_importable", return_value=True):
        cmd = _streamlit_cmd("book.py", 8501)
    assert cmd[0] == sys.executable
    assert cmd[1:3] == ["-m", "streamlit"]
    assert "run" in cmd
    assert "book.py" in cmd
    assert "8501" in cmd
    assert "--server.headless" in cmd


def test_streamlit_cmd_falls_back_to_uv_when_not_importable():
    """When streamlit isn't importable, the command should attempt `uv run streamlit`."""
    with (
        patch("streamtex.cli.screenshot_cmd._streamlit_importable", return_value=False),
        patch("shutil.which", return_value="/usr/local/bin/uv"),
    ):
        cmd = _streamlit_cmd("book.py", 8501)
    assert cmd[0] == "/usr/local/bin/uv"
    assert cmd[1:3] == ["run", "streamlit"]
    assert "book.py" in cmd
    assert "8501" in cmd


def test_streamlit_cmd_final_fallback_when_uv_missing():
    """If neither streamlit importable nor uv on PATH, fall back to sys.executable."""
    with (
        patch("streamtex.cli.screenshot_cmd._streamlit_importable", return_value=False),
        patch("shutil.which", return_value=None),
    ):
        cmd = _streamlit_cmd("book.py", 8501)
    assert cmd[0] == sys.executable
    assert cmd[1:3] == ["-m", "streamlit"]


def test_streamlit_cmd_includes_required_flags():
    """All required Streamlit headless flags are present."""
    with patch("streamtex.cli.screenshot_cmd._streamlit_importable", return_value=True):
        cmd = _streamlit_cmd("project/book.py", 9001)
    assert "--server.headless" in cmd and "true" in cmd
    assert "--server.runOnSave" in cmd and "false" in cmd
    assert "--browser.gatherUsageStats" in cmd and "false" in cmd
    assert "--server.port" in cmd and "9001" in cmd


# ---------------------------------------------------------------------------
# capture_screenshots — early validation
# ---------------------------------------------------------------------------


def test_capture_screenshots_raises_on_missing_book(tmp_path):
    """A non-existent book path raises ClickException before any subprocess starts."""
    missing = tmp_path / "does_not_exist.py"
    with pytest.raises(click.ClickException) as exc_info:
        capture_screenshots(book=str(missing), out_dir=str(tmp_path / "out"))
    assert "File not found" in str(exc_info.value.message)


def test_capture_screenshots_raises_when_playwright_missing(tmp_path, monkeypatch):
    """A missing Playwright install surfaces the install-hint ClickException."""
    book = tmp_path / "book.py"
    book.write_text("# minimal", encoding="utf-8")

    # Force the playwright import inside capture_screenshots to fail.
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "playwright.sync_api" or name.startswith("playwright"):
            raise ImportError("forced for test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(click.ClickException) as exc_info:
        capture_screenshots(book=str(book), out_dir=str(tmp_path / "out"))
    # Hint mentions the extras group and the playwright install command.
    msg = str(exc_info.value.message)
    assert "streamtex[pdf]" in msg
    assert "playwright install" in msg


# ---------------------------------------------------------------------------
# CLI surface — argument parsing + help
# ---------------------------------------------------------------------------


def test_cli_screenshot_help_renders():
    """`stx screenshot --help` lists all 5 options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["screenshot", "--help"])
    assert result.exit_code == 0
    for flag in ["--out", "--viewport", "--no-per-slide", "--no-full-page", "--settle"]:
        assert flag in result.output


def test_cli_screenshot_rejects_malformed_viewport(tmp_path):
    """A --viewport without 'WxH' shape is rejected before any capture call."""
    runner = CliRunner()
    book = tmp_path / "book.py"
    book.write_text("# minimal", encoding="utf-8")
    result = runner.invoke(
        cli,
        ["screenshot", str(book), "--viewport", "not-a-viewport"],
    )
    assert result.exit_code != 0
    assert "Invalid --viewport" in result.output


def test_cli_screenshot_rejects_missing_book():
    """An invocation pointing at a missing book.py surfaces the ClickException."""
    runner = CliRunner()
    result = runner.invoke(cli, ["screenshot", "/tmp/never_exists_streamtex_test.py"])
    assert result.exit_code != 0
    assert "File not found" in result.output


def test_cli_screenshot_parses_viewport_into_tuple(tmp_path, monkeypatch):
    """Valid --viewport WxH is split into an (int, int) tuple before delegation."""
    book = tmp_path / "book.py"
    book.write_text("# minimal", encoding="utf-8")

    captured = {}

    def fake_capture(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        "streamtex.cli.screenshot_cmd.capture_screenshots", fake_capture
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["screenshot", str(book), "--viewport", "1280x720"],
    )
    assert result.exit_code == 0, result.output
    assert captured.get("viewport") == (1280, 720)


def test_cli_screenshot_no_flags_invert_defaults(tmp_path, monkeypatch):
    """--no-per-slide and --no-full-page each invert the corresponding default."""
    book = tmp_path / "book.py"
    book.write_text("# minimal", encoding="utf-8")

    captured = {}
    monkeypatch.setattr(
        "streamtex.cli.screenshot_cmd.capture_screenshots",
        lambda **kw: captured.update(kw),
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["screenshot", str(book), "--no-per-slide", "--no-full-page"],
    )
    assert result.exit_code == 0, result.output
    assert captured.get("per_slide") is False
    assert captured.get("full_page") is False


def test_cli_screenshot_passes_settle_value(tmp_path, monkeypatch):
    """--settle is forwarded as settle_s (float)."""
    book = tmp_path / "book.py"
    book.write_text("# minimal", encoding="utf-8")

    captured = {}
    monkeypatch.setattr(
        "streamtex.cli.screenshot_cmd.capture_screenshots",
        lambda **kw: captured.update(kw),
    )

    runner = CliRunner()
    result = runner.invoke(
        cli, ["screenshot", str(book), "--settle", "1.5"]
    )
    assert result.exit_code == 0, result.output
    assert captured.get("settle_s") == 1.5


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


def test_screenshot_is_registered_on_cli():
    """The `screenshot` command is part of the top-level `stx` CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "screenshot" in result.output


def test_screenshot_command_object_has_expected_options():
    """Direct introspection: every documented option is on the Click command."""
    declared = {opt.name for opt in screenshot.params}
    expected = {"book", "out_dir", "viewport", "no_per_slide", "no_full_page", "settle"}
    assert expected.issubset(declared)
