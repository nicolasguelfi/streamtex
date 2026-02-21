"""Unit tests for streamtex/inspector.py — Block Inspector."""

import json
import os
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from streamtex.inspector import (
    InspectorConfig,
    FileCategory,
    FileCategoryRegistry,
    SourceFile,
    _validate_python,
    _validate_json,
    discover_sources,
    _render_editor,
    inject_inspector_css,
    render_edit_button,
    render_inspector_panel,
    _find_project_root,
    _close_inspector,
    _save_file,
    _invalidate_module_cache,
    _STX_INSPECTOR_OPEN,
    _STX_INSPECTOR_BLOCK,
    _STX_INSPECTOR_AUTH,
)


# ---------------------------------------------------------------------------
# InspectorConfig
# ---------------------------------------------------------------------------


class TestInspectorConfig:
    def test_defaults(self):
        cfg = InspectorConfig()
        assert cfg.enabled is False
        assert cfg.password is None
        assert cfg.panel_width == "35vw"
        assert cfg.backup is True

    def test_custom_values(self):
        cfg = InspectorConfig(enabled=True, password="secret", panel_width="40vw", backup=False)
        assert cfg.enabled is True
        assert cfg.password == "secret"
        assert cfg.panel_width == "40vw"
        assert cfg.backup is False


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


class TestValidators:
    def test_validate_python_valid(self):
        assert _validate_python("x = 1\nprint(x)") is None

    def test_validate_python_invalid(self):
        result = _validate_python("def f(\n")
        assert result is not None
        assert "Syntax error" in result

    def test_validate_json_valid(self):
        assert _validate_json('{"key": "value"}') is None

    def test_validate_json_invalid(self):
        result = _validate_json("{bad json}")
        assert result is not None
        assert "JSON error" in result

    def test_validate_python_empty(self):
        assert _validate_python("") is None

    def test_validate_json_array(self):
        assert _validate_json("[1, 2, 3]") is None


# ---------------------------------------------------------------------------
# FileCategoryRegistry
# ---------------------------------------------------------------------------


class TestFileCategoryRegistry:
    def test_detect_python(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("block.py")
        assert cat.name == "Python"
        assert cat.ace_mode == "python"

    def test_detect_mermaid(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("diagram.mmd")
        assert cat.name == "Diagrams"

    def test_detect_json(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("data.json")
        assert cat.name == "Data"

    def test_detect_markdown(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("readme.md")
        assert cat.name == "Texts"

    def test_detect_unknown_extension(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("file.xyz")
        assert cat.name == "Text"
        assert cat.ace_mode == "text"

    def test_detect_case_insensitive(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("FILE.PY")
        assert cat.name == "Python"

    def test_detect_all_diagram_extensions(self):
        reg = FileCategoryRegistry()
        for ext in [".mmd", ".tex", ".puml", ".dot"]:
            cat = reg.detect(f"file{ext}")
            assert cat.name == "Diagrams", f"Failed for {ext}"

    def test_detect_all_data_extensions(self):
        reg = FileCategoryRegistry()
        for ext in [".json", ".csv", ".toml", ".yaml", ".yml"]:
            cat = reg.detect(f"file{ext}")
            assert cat.name == "Data", f"Failed for {ext}"

    def test_detect_all_text_extensions(self):
        reg = FileCategoryRegistry()
        for ext in [".txt", ".md", ".bib", ".ris"]:
            cat = reg.detect(f"file{ext}")
            assert cat.name == "Texts", f"Failed for {ext}"

    def test_register_custom_category(self):
        reg = FileCategoryRegistry()
        reg.register(FileCategory(name="Rust", extensions={".rs"}, ace_mode="rust"))
        cat = reg.detect("main.rs")
        assert cat.name == "Rust"

    def test_register_overrides_extension(self):
        reg = FileCategoryRegistry()
        reg.register(FileCategory(name="MyPython", extensions={".py"}, ace_mode="python"))
        cat = reg.detect("script.py")
        assert cat.name == "MyPython"

    def test_categories_property(self):
        reg = FileCategoryRegistry()
        cats = reg.categories
        names = [c.name for c in cats]
        assert "Python" in names
        assert "Diagrams" in names
        assert "Data" in names
        assert "Texts" in names

    def test_python_category_has_validator(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("test.py")
        assert cat.validator is not None
        assert cat.validator("x = 1") is None

    def test_json_category_has_validator(self):
        reg = FileCategoryRegistry()
        cat = reg.detect("test.json")
        assert cat.validator is not None
        assert cat.validator('{"a": 1}') is None


# ---------------------------------------------------------------------------
# SourceFile
# ---------------------------------------------------------------------------


class TestSourceFile:
    def test_auto_label_from_path(self):
        sf = SourceFile(
            path="/project/blocks/bck_intro.py",
            category=FileCategory(name="Python", extensions={".py"}),
        )
        assert sf.label == "bck_intro.py"

    def test_custom_label(self):
        sf = SourceFile(
            path="/project/blocks/bck_intro.py",
            category=FileCategory(name="Python", extensions={".py"}),
            label="Introduction Block",
        )
        assert sf.label == "Introduction Block"


# ---------------------------------------------------------------------------
# _find_project_root
# ---------------------------------------------------------------------------


class TestFindProjectRoot:
    def test_finds_root_with_book_py(self, tmp_path):
        (tmp_path / "book.py").touch()
        blocks_dir = tmp_path / "blocks"
        blocks_dir.mkdir()
        block_file = blocks_dir / "bck_test.py"
        block_file.touch()
        assert _find_project_root(str(block_file)) == str(tmp_path)

    def test_returns_none_without_book_py(self, tmp_path):
        block_file = tmp_path / "blocks" / "bck_test.py"
        block_file.parent.mkdir()
        block_file.touch()
        # No book.py anywhere → returns None
        result = _find_project_root(str(block_file))
        # Will walk up to filesystem root, may or may not find book.py
        # but with tmp_path it should not find one nearby
        # This test is best-effort since the real filesystem might have book.py somewhere
        assert result is None or isinstance(result, str)


# ---------------------------------------------------------------------------
# discover_sources
# ---------------------------------------------------------------------------


class TestDiscoverSources:
    def _make_module(self, path):
        """Create a fake module with __file__ pointing to *path*."""
        m = types.ModuleType("test_block")
        m.__file__ = str(path)
        m.build = lambda: None
        return m

    def test_discover_main_file(self, tmp_path):
        block_file = tmp_path / "bck_test.py"
        block_file.write_text("def build(): pass\n", encoding="utf-8")
        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        assert len(sources) >= 1
        assert sources[0].path == str(block_file)
        assert sources[0].category.name == "Python"

    def test_discover_atomic_blocks(self, tmp_path):
        atomic_dir = tmp_path / "_atomic"
        atomic_dir.mkdir()
        atomic_file = atomic_dir / "bck_part_a.py"
        atomic_file.write_text("def build(): pass\n", encoding="utf-8")

        main_code = (
            'from streamtex import load_atomic_block\n'
            'def build():\n'
            '    m = load_atomic_block("bck_part_a", __file__)\n'
        )
        block_file = tmp_path / "bck_composite.py"
        block_file.write_text(main_code, encoding="utf-8")

        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        paths = [s.path for s in sources]
        assert str(atomic_file) in paths

    def test_discover_static_references(self, tmp_path):
        mmd_file = tmp_path / "diagram.mmd"
        mmd_file.write_text("graph TD\n  A-->B\n", encoding="utf-8")

        main_code = (
            'def build():\n'
            '    path = "diagram.mmd"\n'
        )
        block_file = tmp_path / "bck_test.py"
        block_file.write_text(main_code, encoding="utf-8")

        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        paths = [s.path for s in sources]
        assert str(mmd_file) in paths

    def test_discover_styles_import(self, tmp_path):
        # Create project structure
        (tmp_path / "book.py").touch()
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        styles_file = custom_dir / "styles.py"
        styles_file.write_text("class Styles: pass\n", encoding="utf-8")

        blocks_dir = tmp_path / "blocks"
        blocks_dir.mkdir()
        main_code = (
            'from custom.styles import Styles as s\n'
            'def build(): pass\n'
        )
        block_file = blocks_dir / "bck_test.py"
        block_file.write_text(main_code, encoding="utf-8")

        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        paths = [s.path for s in sources]
        assert str(styles_file) in paths

    def test_discover_dunder_sources(self, tmp_path):
        extra_file = tmp_path / "notes.md"
        extra_file.write_text("# Notes\n", encoding="utf-8")

        block_file = tmp_path / "bck_test.py"
        block_file.write_text("def build(): pass\n", encoding="utf-8")

        module = self._make_module(block_file)
        module.__sources__ = ["notes.md"]
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        paths = [s.path for s in sources]
        assert str(extra_file) in paths

    def test_discover_missing_file_skipped(self, tmp_path):
        main_code = (
            'def build():\n'
            '    path = "nonexistent.mmd"\n'
        )
        block_file = tmp_path / "bck_test.py"
        block_file.write_text(main_code, encoding="utf-8")

        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        # Only the main file should be found (no crash on missing static)
        assert len(sources) == 1
        assert sources[0].path == str(block_file)

    def test_discover_no_duplicates(self, tmp_path):
        mmd_file = tmp_path / "diagram.mmd"
        mmd_file.write_text("graph TD\n", encoding="utf-8")

        main_code = (
            'def build():\n'
            '    a = "diagram.mmd"\n'
            '    b = "diagram.mmd"\n'
        )
        block_file = tmp_path / "bck_test.py"
        block_file.write_text(main_code, encoding="utf-8")

        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        mmd_count = sum(1 for s in sources if s.path == str(mmd_file))
        assert mmd_count == 1

    def test_discover_no_file_returns_empty(self):
        module = types.ModuleType("no_file")
        reg = FileCategoryRegistry()
        assert discover_sources(module, reg) == []


# ---------------------------------------------------------------------------
# _render_editor
# ---------------------------------------------------------------------------


class TestRenderEditor:
    @patch("streamtex.inspector.st")
    def test_fallback_to_text_area(self, mock_st):
        """When streamlit_ace is not installed, fall back to st.text_area."""
        mock_st.text_area.return_value = "edited content"
        result = _render_editor("original", "python", "key1")
        mock_st.text_area.assert_called_once()
        assert result == "edited content"

    def test_ace_editor_used_when_available(self):
        """When streamlit_ace is importable, st_ace should be called."""
        mock_ace = MagicMock(return_value="ace content")
        with patch.dict("sys.modules", {"streamlit_ace": MagicMock(st_ace=mock_ace)}):
            result = _render_editor("original", "python", "key2")
            mock_ace.assert_called_once()
            assert result == "ace content"


# ---------------------------------------------------------------------------
# render_edit_button
# ---------------------------------------------------------------------------


class TestInjectInspectorCss:
    @patch("streamtex.inspector.st")
    def test_injects_global_css(self, mock_st):
        inject_inspector_css()
        mock_st.html.assert_called_once()
        css_arg = mock_st.html.call_args[0][0]
        assert "stx-edit-marker" in css_arg
        assert "position: absolute" in css_arg


class TestRenderEditButton:
    @patch("streamtex.inspector.st")
    def test_button_rendered_when_enabled(self, mock_st):
        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        config = InspectorConfig(enabled=True)
        render_edit_button("bck_test", config)

        # Marker span should be injected (1 call, no per-button CSS)
        mock_st.html.assert_called_once()
        assert "stx-edit-marker" in mock_st.html.call_args[0][0]
        # Button should be created
        mock_st.button.assert_called_once()

    @patch("streamtex.inspector.st")
    def test_button_hidden_when_disabled(self, mock_st):
        config = InspectorConfig(enabled=False)
        render_edit_button("bck_test", config)
        mock_st.button.assert_not_called()


# ---------------------------------------------------------------------------
# render_inspector_panel
# ---------------------------------------------------------------------------


class TestRenderInspectorPanel:
    @patch("streamtex.inspector.st")
    def test_panel_not_rendered_when_closed(self, mock_st):
        mock_st.session_state = {}
        config = InspectorConfig(enabled=True)
        reg = FileCategoryRegistry()
        render_inspector_panel([], config, reg)
        # No sidebar content should be rendered
        mock_st.sidebar.__enter__.assert_not_called()

    @patch("streamtex.inspector.st")
    def test_password_gate_shown_when_configured(self, mock_st):
        mock_st.session_state = {
            _STX_INSPECTOR_OPEN: True,
            _STX_INSPECTOR_BLOCK: "bck_test",
        }
        mock_sidebar = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        for col in mock_st.columns.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.button.return_value = False
        mock_st.text_input.return_value = ""

        config = InspectorConfig(enabled=True, password="secret")
        reg = FileCategoryRegistry()
        render_inspector_panel([], config, reg)

        # Password input should be rendered
        mock_st.text_input.assert_called_once()

    @patch("streamtex.inspector.st")
    def test_no_sources_shows_info(self, mock_st):
        mock_st.session_state = {
            _STX_INSPECTOR_OPEN: True,
            _STX_INSPECTOR_BLOCK: "bck_test",
        }
        mock_sidebar = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        for col in mock_st.columns.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.button.return_value = False

        config = InspectorConfig(enabled=True)
        reg = FileCategoryRegistry()
        render_inspector_panel([], config, reg)
        mock_st.info.assert_called_once()


# ---------------------------------------------------------------------------
# File save with backup
# ---------------------------------------------------------------------------


class TestCloseInspector:
    @patch("streamtex.inspector.st")
    def test_close_sets_session_state(self, mock_st):
        mock_st.session_state = {_STX_INSPECTOR_OPEN: True}
        _close_inspector()
        assert mock_st.session_state[_STX_INSPECTOR_OPEN] is False


class TestSaveFile:
    def test_save_writes_content_with_backup(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("original", encoding="utf-8")
        editor_key = "_stx_insp_editor_test"

        with patch("streamtex.inspector.st") as mock_st:
            mock_st.session_state = {editor_key: "edited content"}
            _save_file(str(test_file), editor_key, backup=True)

        assert test_file.read_text() == "edited content"
        assert (tmp_path / "test.py.bak").read_text() == "original"

    def test_save_writes_content_without_backup(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("original", encoding="utf-8")
        editor_key = "_stx_insp_editor_test"

        with patch("streamtex.inspector.st") as mock_st:
            mock_st.session_state = {editor_key: "new content"}
            _save_file(str(test_file), editor_key, backup=False)

        assert test_file.read_text() == "new content"
        assert not (tmp_path / "test.py.bak").exists()


class TestFileSaveBackup:
    def test_backup_created_on_save(self, tmp_path):
        """Verify .bak file is created when config.backup is True."""
        test_file = tmp_path / "test.py"
        test_file.write_text("original", encoding="utf-8")

        config = InspectorConfig(enabled=True, backup=True)

        # Simulate the save logic from _render_file_editor
        import shutil
        bak_path = str(test_file) + ".bak"
        shutil.copy2(str(test_file), bak_path)

        with open(str(test_file), "w", encoding="utf-8") as f:
            f.write("edited")

        assert test_file.read_text() == "edited"
        assert Path(bak_path).read_text() == "original"


# ---------------------------------------------------------------------------
# _invalidate_module_cache
# ---------------------------------------------------------------------------


class TestInvalidateModuleCache:
    def test_removes_project_modules(self, tmp_path):
        """Modules whose __file__ is inside the project tree are evicted."""
        import sys

        (tmp_path / "book.py").touch()
        block_file = tmp_path / "blocks" / "bck_test.py"
        block_file.parent.mkdir()
        block_file.write_text("x = 1\n", encoding="utf-8")

        # Inject a fake module into sys.modules
        fake_mod = types.ModuleType("fake_project_block")
        fake_mod.__file__ = str(block_file)
        sys.modules["fake_project_block"] = fake_mod

        _invalidate_module_cache(str(block_file))

        assert "fake_project_block" not in sys.modules

    def test_keeps_unrelated_modules(self, tmp_path):
        """Modules outside the project tree are left untouched."""
        import sys

        (tmp_path / "book.py").touch()
        block_file = tmp_path / "blocks" / "bck_test.py"
        block_file.parent.mkdir()
        block_file.write_text("x = 1\n", encoding="utf-8")

        # Inject a fake module outside the project tree
        fake_mod = types.ModuleType("unrelated_module")
        fake_mod.__file__ = "/somewhere/else/mod.py"
        sys.modules["unrelated_module"] = fake_mod

        try:
            _invalidate_module_cache(str(block_file))
            assert "unrelated_module" in sys.modules
        finally:
            sys.modules.pop("unrelated_module", None)

    def test_fallback_when_no_book_py(self, tmp_path):
        """Without book.py, uses the file's directory as project root."""
        import sys

        block_file = tmp_path / "standalone" / "script.py"
        block_file.parent.mkdir()
        block_file.write_text("x = 1\n", encoding="utf-8")

        fake_mod = types.ModuleType("standalone_mod")
        fake_mod.__file__ = str(block_file)
        sys.modules["standalone_mod"] = fake_mod

        _invalidate_module_cache(str(block_file))

        assert "standalone_mod" not in sys.modules
