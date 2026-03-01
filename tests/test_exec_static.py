"""Tests for streamtex.utils.exec_static()."""

import pytest
from unittest.mock import patch


class TestExecStatic:
    """Tests for exec_static() function."""

    def test_executes_python_code(self, tmp_path):
        """exec_static runs the file and populates the context."""
        code_file = tmp_path / "example.py"
        code_file.write_text("result = 1 + 2\n")

        ctx: dict = {}
        with patch("streamtex.blocks.resolve_static", return_value=str(code_file)):
            from streamtex.utils import exec_static
            exec_static("example.py", context=ctx)

        assert ctx["result"] == 3

    def test_start_line(self, tmp_path):
        """start_line skips initial lines."""
        code_file = tmp_path / "multi.py"
        code_file.write_text("a = 1\nb = 2\nc = 3\n")

        ctx: dict = {}
        with patch("streamtex.blocks.resolve_static", return_value=str(code_file)):
            from streamtex.utils import exec_static
            exec_static("multi.py", context=ctx, start_line=2)

        assert "a" not in ctx
        assert ctx["b"] == 2
        assert ctx["c"] == 3

    def test_end_line(self, tmp_path):
        """end_line stops after the given line."""
        code_file = tmp_path / "multi.py"
        code_file.write_text("a = 1\nb = 2\nc = 3\n")

        ctx: dict = {}
        with patch("streamtex.blocks.resolve_static", return_value=str(code_file)):
            from streamtex.utils import exec_static
            exec_static("multi.py", context=ctx, end_line=2)

        assert ctx["a"] == 1
        assert ctx["b"] == 2
        assert "c" not in ctx

    def test_start_and_end_line(self, tmp_path):
        """Combined start_line + end_line extracts a range."""
        code_file = tmp_path / "multi.py"
        code_file.write_text("a = 1\nb = 2\nc = 3\nd = 4\n")

        ctx: dict = {}
        with patch("streamtex.blocks.resolve_static", return_value=str(code_file)):
            from streamtex.utils import exec_static
            exec_static("multi.py", context=ctx, start_line=2, end_line=3)

        assert "a" not in ctx
        assert ctx["b"] == 2
        assert ctx["c"] == 3
        assert "d" not in ctx

    def test_uses_caller_context_when_none(self, tmp_path):
        """When context=None, exec_static uses the caller's namespace."""
        code_file = tmp_path / "use_caller.py"
        code_file.write_text("result = x + 10\n")

        x = 5  # noqa: F841 — accessed by exec'd code
        with patch("streamtex.blocks.resolve_static", return_value=str(code_file)):
            from streamtex.utils import exec_static
            # context=None → caller's globals + locals
            exec_static("use_caller.py")

    def test_file_not_found(self):
        """exec_static raises FileNotFoundError for missing files."""
        with patch("streamtex.blocks.resolve_static", return_value="/nonexistent/file.py"):
            from streamtex.utils import exec_static
            with pytest.raises(FileNotFoundError):
                exec_static("missing.py", context={})
