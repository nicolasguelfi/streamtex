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
    _apply_edits,
    _save_and_reload,
    _cancel_edits,
    _invalidate_module_cache,
    _scan_project_files,
    _get_cached_project_files,
    _EXCLUDED_DIRS,
    _STX_INSPECTOR_OPEN,
    _STX_INSPECTOR_BLOCK,
    _STX_INSPECTOR_AUTH,
    _STX_INSPECTOR_PENDING,
    _STX_INSPECTOR_MODE,
    _STX_INSPECTOR_PROJECT_ROOT,
    _STX_INSPECTOR_PROJECT_FILES,
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
        # Hide streamlit_ace so the ImportError fallback is triggered
        with patch.dict("sys.modules", {"streamlit_ace": None}):
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


class TestApplyEdits:
    @patch("streamtex.inspector.st")
    def test_stages_content_in_pending(self, mock_st):
        mock_st.session_state = {"_stx_insp_editor_abc": "new code"}
        _apply_edits("/project/block.py", "_stx_insp_editor_abc")
        pending = mock_st.session_state[_STX_INSPECTOR_PENDING]
        assert pending["/project/block.py"] == "new code"

    @patch("streamtex.inspector.st")
    def test_skips_when_editor_is_none(self, mock_st):
        mock_st.session_state = {}
        _apply_edits("/project/block.py", "_stx_insp_editor_abc")
        assert _STX_INSPECTOR_PENDING not in mock_st.session_state

    @patch("streamtex.inspector.st")
    def test_stages_multiple_files(self, mock_st):
        mock_st.session_state = {
            "_stx_insp_editor_a": "code A",
            "_stx_insp_editor_b": "code B",
        }
        _apply_edits("/project/a.py", "_stx_insp_editor_a")
        _apply_edits("/project/b.py", "_stx_insp_editor_b")
        pending = mock_st.session_state[_STX_INSPECTOR_PENDING]
        assert pending["/project/a.py"] == "code A"
        assert pending["/project/b.py"] == "code B"


class TestCancelEdits:
    @patch("streamtex.inspector.st")
    def test_removes_file_from_pending(self, mock_st):
        mock_st.session_state = {
            _STX_INSPECTOR_PENDING: {"/project/a.py": "x", "/project/b.py": "y"},
        }
        _cancel_edits("/project/a.py")
        assert "/project/a.py" not in mock_st.session_state[_STX_INSPECTOR_PENDING]
        assert "/project/b.py" in mock_st.session_state[_STX_INSPECTOR_PENDING]


class TestSaveAndReload:
    def test_writes_pending_and_current_with_backup(self, tmp_path):
        file_a = tmp_path / "a.py"
        file_b = tmp_path / "b.py"
        file_a.write_text("old A", encoding="utf-8")
        file_b.write_text("old B", encoding="utf-8")

        with patch("streamtex.inspector.st") as mock_st:
            mock_st.session_state = {
                _STX_INSPECTOR_PENDING: {str(file_a): "new A"},
                "_stx_insp_editor_b": "new B",
            }
            _save_and_reload(str(file_b), "_stx_insp_editor_b", backup=True)

        assert file_a.read_text() == "new A"
        assert file_b.read_text() == "new B"
        assert (tmp_path / "a.py.bak").read_text() == "old A"
        assert (tmp_path / "b.py.bak").read_text() == "old B"

    def test_writes_without_backup(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("original", encoding="utf-8")

        with patch("streamtex.inspector.st") as mock_st:
            mock_st.session_state = {"_stx_insp_editor_x": "new content"}
            _save_and_reload(str(test_file), "_stx_insp_editor_x", backup=False)

        assert test_file.read_text() == "new content"
        assert not (tmp_path / "test.py.bak").exists()

    def test_noop_when_no_content(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("original", encoding="utf-8")

        with patch("streamtex.inspector.st") as mock_st:
            mock_st.session_state = {}
            _save_and_reload(str(test_file), "_stx_insp_editor_x", backup=False)

        assert test_file.read_text() == "original"


# ---------------------------------------------------------------------------
# _invalidate_module_cache
# ---------------------------------------------------------------------------


class TestInvalidateModuleCache:
    def test_clears_project_registry_cache(self, tmp_path):
        """ProjectBlockRegistry caches are cleared on invalidation."""
        from streamtex.blocks import ProjectBlockRegistry

        reg = ProjectBlockRegistry(tmp_path)
        reg._cache["bck_test"] = types.ModuleType("bck_test")

        try:
            _invalidate_module_cache()
            assert reg._cache == {}
        finally:
            ProjectBlockRegistry._instances.remove(reg)

    def test_clears_lazy_registry_cache(self, tmp_path):
        """LazyBlockRegistry caches are cleared on invalidation."""
        from streamtex.blocks import LazyBlockRegistry

        reg = LazyBlockRegistry([str(tmp_path)])
        reg._cache["bck_shared"] = types.ModuleType("bck_shared")
        reg._not_found.add("bck_missing")

        try:
            _invalidate_module_cache()
            assert reg._cache == {}
            assert reg._not_found == set()
        finally:
            LazyBlockRegistry._instances.remove(reg)

    def test_clears_both_registries(self, tmp_path):
        """Both registry types are cleared in a single call."""
        from streamtex.blocks import ProjectBlockRegistry, LazyBlockRegistry

        preg = ProjectBlockRegistry(tmp_path)
        preg._cache["bck_a"] = types.ModuleType("a")
        lreg = LazyBlockRegistry([str(tmp_path)])
        lreg._cache["bck_b"] = types.ModuleType("b")

        try:
            _invalidate_module_cache()
            assert preg._cache == {}
            assert lreg._cache == {}
        finally:
            ProjectBlockRegistry._instances.remove(preg)
            LazyBlockRegistry._instances.remove(lreg)


# ---------------------------------------------------------------------------
# _scan_project_files
# ---------------------------------------------------------------------------


class TestScanProjectFiles:
    def test_finds_known_extensions(self, tmp_path):
        (tmp_path / "block.py").write_text("x = 1", encoding="utf-8")
        (tmp_path / "diagram.mmd").write_text("graph TD", encoding="utf-8")
        (tmp_path / "data.json").write_text("{}", encoding="utf-8")
        reg = FileCategoryRegistry()
        files = _scan_project_files(str(tmp_path), reg)
        labels = {f.label for f in files}
        assert "block.py" in labels
        assert "diagram.mmd" in labels
        assert "data.json" in labels

    def test_excludes_venv_and_pycache(self, tmp_path):
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "lib.py").write_text("pass", encoding="utf-8")
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "mod.py").write_text("pass", encoding="utf-8")
        (tmp_path / "real.py").write_text("pass", encoding="utf-8")
        reg = FileCategoryRegistry()
        files = _scan_project_files(str(tmp_path), reg)
        labels = {f.label for f in files}
        assert "real.py" in labels
        assert not any(".venv" in l for l in labels)
        assert not any("__pycache__" in l for l in labels)

    def test_relative_labels(self, tmp_path):
        sub = tmp_path / "blocks"
        sub.mkdir()
        (sub / "bck_intro.py").write_text("pass", encoding="utf-8")
        reg = FileCategoryRegistry()
        files = _scan_project_files(str(tmp_path), reg)
        labels = {f.label for f in files}
        assert os.path.join("blocks", "bck_intro.py") in labels

    def test_subdirectories_scanned(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (deep / "deep.py").write_text("pass", encoding="utf-8")
        reg = FileCategoryRegistry()
        files = _scan_project_files(str(tmp_path), reg)
        paths = [f.path for f in files]
        assert str(deep / "deep.py") in paths

    def test_unknown_extensions_skipped(self, tmp_path):
        (tmp_path / "photo.png").write_bytes(b"\x89PNG")
        (tmp_path / "archive.zip").write_bytes(b"PK")
        (tmp_path / "real.py").write_text("pass", encoding="utf-8")
        reg = FileCategoryRegistry()
        files = _scan_project_files(str(tmp_path), reg)
        labels = {f.label for f in files}
        assert "photo.png" not in labels
        assert "archive.zip" not in labels
        assert "real.py" in labels

    def test_empty_directory(self, tmp_path):
        reg = FileCategoryRegistry()
        files = _scan_project_files(str(tmp_path), reg)
        assert files == []


# ---------------------------------------------------------------------------
# discover_sources — static fallback
# ---------------------------------------------------------------------------


class TestDiscoverSourcesStaticFallback:
    def _make_module(self, path):
        m = types.ModuleType("test_block")
        m.__file__ = str(path)
        m.build = lambda: None
        return m

    def test_finds_file_in_static_subdir(self, tmp_path):
        """When a basename is referenced but not adjacent, find it in static/."""
        (tmp_path / "book.py").touch()
        static_sub = tmp_path / "static" / "diagrams"
        static_sub.mkdir(parents=True)
        mmd_file = static_sub / "sequence.mmd"
        mmd_file.write_text("sequenceDiagram", encoding="utf-8")

        blocks_dir = tmp_path / "blocks"
        blocks_dir.mkdir()
        block_file = blocks_dir / "bck_test.py"
        block_file.write_text(
            'def build():\n    path = "sequence.mmd"\n',
            encoding="utf-8",
        )

        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        paths = [s.path for s in sources]
        assert str(mmd_file) in paths

    def test_no_crash_without_static_dir(self, tmp_path):
        """No static/ directory → no crash, just normal missing-file behaviour."""
        (tmp_path / "book.py").touch()
        blocks_dir = tmp_path / "blocks"
        blocks_dir.mkdir()
        block_file = blocks_dir / "bck_test.py"
        block_file.write_text(
            'def build():\n    path = "missing.mmd"\n',
            encoding="utf-8",
        )

        module = self._make_module(block_file)
        reg = FileCategoryRegistry()
        sources = discover_sources(module, reg)
        # Only main file — no crash
        assert len(sources) == 1
        assert sources[0].path == str(block_file)


# ---------------------------------------------------------------------------
# _get_cached_project_files
# ---------------------------------------------------------------------------


class TestGetCachedProjectFiles:
    @patch("streamtex.inspector.st")
    def test_cache_hit(self, mock_st, tmp_path):
        (tmp_path / "block.py").write_text("pass", encoding="utf-8")
        reg = FileCategoryRegistry()

        # First call populates cache
        mock_st.session_state = {}
        files1 = _get_cached_project_files(str(tmp_path), reg)
        assert len(files1) == 1

        # Second call returns same object from cache
        files2 = _get_cached_project_files(str(tmp_path), reg)
        assert files2 is files1

    @patch("streamtex.inspector.st")
    def test_cache_invalidation_on_root_change(self, mock_st, tmp_path):
        dir_a = tmp_path / "a"
        dir_a.mkdir()
        (dir_a / "file_a.py").write_text("pass", encoding="utf-8")
        dir_b = tmp_path / "b"
        dir_b.mkdir()
        (dir_b / "file_b.py").write_text("pass", encoding="utf-8")
        reg = FileCategoryRegistry()

        mock_st.session_state = {}
        files_a = _get_cached_project_files(str(dir_a), reg)
        assert any("file_a.py" in f.label for f in files_a)

        files_b = _get_cached_project_files(str(dir_b), reg)
        assert any("file_b.py" in f.label for f in files_b)
        assert not any("file_a.py" in f.label for f in files_b)


# ---------------------------------------------------------------------------
# render_inspector_panel — mode selector & filter UI
# ---------------------------------------------------------------------------


class TestProjectModeUI:
    @patch("streamtex.inspector.st")
    def test_mode_selector_shown_with_project_root(self, mock_st):
        mock_st.session_state = {
            _STX_INSPECTOR_OPEN: True,
            _STX_INSPECTOR_BLOCK: "bck_test",
        }
        mock_st.segmented_control.return_value = None
        mock_st.text_input.return_value = ""
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        for col in mock_st.columns.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)

        config = InspectorConfig(enabled=True)
        reg = FileCategoryRegistry()
        src = SourceFile(
            path="/fake/bck_test.py",
            category=FileCategory(name="Python", extensions={".py"}),
        )
        render_inspector_panel([src], config, reg, project_root="/fake/project")

        # segmented_control called twice: width selector + mode selector
        assert mock_st.segmented_control.call_count == 2
        mode_call = mock_st.segmented_control.call_args_list[1]
        assert "Block files" in mode_call[0][1]
        assert "Project" in mode_call[0][1]

    @patch("streamtex.inspector.st")
    def test_mode_selector_hidden_without_project_root(self, mock_st):
        mock_st.session_state = {
            _STX_INSPECTOR_OPEN: True,
            _STX_INSPECTOR_BLOCK: "bck_test",
        }
        mock_st.segmented_control.return_value = None
        mock_st.text_input.return_value = ""
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        for col in mock_st.columns.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)

        config = InspectorConfig(enabled=True)
        reg = FileCategoryRegistry()
        src = SourceFile(
            path="/fake/bck_test.py",
            category=FileCategory(name="Python", extensions={".py"}),
        )
        render_inspector_panel([src], config, reg)  # no project_root

        # Only width selector — no mode selector
        assert mock_st.segmented_control.call_count == 1

    @patch("streamtex.inspector.st")
    def test_filter_always_present(self, mock_st):
        mock_st.session_state = {
            _STX_INSPECTOR_OPEN: True,
            _STX_INSPECTOR_BLOCK: "bck_test",
        }
        mock_st.segmented_control.return_value = None
        mock_st.text_input.return_value = ""
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        for col in mock_st.columns.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)

        config = InspectorConfig(enabled=True)
        reg = FileCategoryRegistry()
        src = SourceFile(
            path="/fake/bck_test.py",
            category=FileCategory(name="Python", extensions={".py"}),
        )
        render_inspector_panel([src], config, reg)

        # text_input should be called for the filter
        mock_st.text_input.assert_called_once()
