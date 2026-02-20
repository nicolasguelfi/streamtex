"""Tests for the Marker Navigation system."""

import pytest
from unittest.mock import patch, MagicMock
from streamtex.marker import (
    MarkerConfig, MarkerRegistry,
    reset_marker_registry, register_marker,
    marker_entries, marker_count, get_marker_config,
    st_marker,
)
import streamtex.marker as marker_mod


class TestMarkerConfig:
    def test_defaults(self):
        cfg = MarkerConfig()
        assert cfg.show_nav_ui is True
        assert cfg.auto_marker_on_toc is False
        assert cfg.nav_position == "bottom-right"
        assert cfg.nav_label_chars == 40
        assert cfg.popup_open is False
        assert cfg.next_keys == ["PageDown"]
        assert cfg.prev_keys == ["PageUp"]

    def test_custom(self):
        cfg = MarkerConfig(auto_marker_on_toc=2, nav_position="bottom-center")
        assert cfg.auto_marker_on_toc == 2
        assert cfg.nav_position == "bottom-center"

    def test_auto_marker_bool_true(self):
        cfg = MarkerConfig(auto_marker_on_toc=True)
        assert cfg.auto_marker_on_toc is True

    def test_custom_keys(self):
        cfg = MarkerConfig(
            next_keys=["PageDown", "ArrowRight", "Ctrl+ArrowRight"],
            prev_keys=["PageUp", "ArrowLeft"],
        )
        assert "Ctrl+ArrowRight" in cfg.next_keys
        assert len(cfg.prev_keys) == 2

    def test_key_lists_are_independent(self):
        cfg1 = MarkerConfig()
        cfg2 = MarkerConfig()
        cfg1.next_keys.append("Space")
        assert "Space" not in cfg2.next_keys


class TestMarkerRegistry:
    def test_empty_registry(self):
        reg = MarkerRegistry(MarkerConfig())
        assert reg.get_entries() == []
        assert reg.count() == 0

    def test_register_single(self):
        reg = MarkerRegistry(MarkerConfig())
        idx = reg.register("Intro", "anchor-1")
        assert idx == 0
        entries = reg.get_entries()
        assert len(entries) == 1
        assert entries[0] == {"index": 0, "label": "Intro", "anchor": "anchor-1"}

    def test_register_multiple(self):
        reg = MarkerRegistry(MarkerConfig())
        reg.register("A", "a-1")
        reg.register("B", "b-2")
        reg.register("C", "c-3")
        assert reg.count() == 3
        entries = reg.get_entries()
        assert entries[0]["label"] == "A"
        assert entries[2]["index"] == 2

    def test_reset(self):
        reg = MarkerRegistry(MarkerConfig())
        reg.register("X", "x-1")
        reg.reset()
        assert reg.get_entries() == []
        assert reg.count() == 0

    def test_get_entries_returns_copy(self):
        reg = MarkerRegistry(MarkerConfig())
        reg.register("A", "a-1")
        copy = reg.get_entries()
        copy.append({"index": 99, "label": "fake", "anchor": "fake"})
        assert reg.count() == 1


class TestGlobalFunctions:
    def setup_method(self):
        """Reset global state before each test."""
        marker_mod._registry = None

    def test_init_and_reset(self):
        reset_marker_registry(MarkerConfig())
        assert get_marker_config() is not None
        idx = register_marker("Test", "t-1")
        assert idx == 0
        assert marker_count() == 1

    def test_register_without_init_raises(self):
        with pytest.raises(AssertionError):
            register_marker("Bad", "b-1")

    def test_marker_entries_without_init_graceful(self):
        assert marker_entries() == []

    def test_marker_count_without_init_graceful(self):
        assert marker_count() == 0

    def test_get_config_without_init(self):
        assert get_marker_config() is None

    def test_reset_preserves_registry_object(self):
        reset_marker_registry(MarkerConfig())
        register_marker("A", "a-1")
        reset_marker_registry()  # reset without new config
        assert marker_count() == 0
        assert get_marker_config() is not None


class TestStMarker:
    """Test the st_marker() public API — HTML rendering for visible/invisible markers."""

    def setup_method(self):
        marker_mod._registry = None

    def test_noop_without_registry(self):
        """st_marker() should be a no-op if registry is not initialized."""
        st_marker("test")  # should not raise
        assert marker_count() == 0

    @patch("streamtex.marker._render")
    def test_visible_marker_html(self, mock_render):
        reset_marker_registry(MarkerConfig())
        st_marker("Section A", visible=True)
        assert marker_count() == 1
        html = mock_render.call_args[0][0]
        assert 'class="streamtex-marker"' in html
        assert 'data-marker-index="0"' in html
        assert "Section A" in html
        assert "border-top: 1px dashed" in html

    @patch("streamtex.marker._render")
    def test_invisible_marker_html(self, mock_render):
        reset_marker_registry(MarkerConfig())
        st_marker("Hidden")
        assert marker_count() == 1
        html = mock_render.call_args[0][0]
        assert 'class="streamtex-marker"' in html
        assert "height: 0" in html
        # Invisible markers should NOT contain the label text in the HTML
        assert ">Hidden<" not in html

    @patch("streamtex.marker._render")
    def test_auto_label(self, mock_render):
        reset_marker_registry(MarkerConfig())
        st_marker()  # no label provided
        entries = marker_entries()
        assert entries[0]["label"] == "Marker 1"

    @patch("streamtex.marker._render")
    def test_multiple_markers_indexed(self, mock_render):
        reset_marker_registry(MarkerConfig())
        st_marker("A")
        st_marker("B")
        st_marker("C")
        assert marker_count() == 3
        entries = marker_entries()
        assert entries[0]["index"] == 0
        assert entries[1]["index"] == 1
        assert entries[2]["index"] == 2


class TestAutoMarkerOnToc:
    """Test the TOC → Marker bridge in write.py._handle_toc()."""

    def setup_method(self):
        marker_mod._registry = None

    @patch("streamtex.write.register_toc_entry")
    def test_auto_true_registers_marker(self, mock_toc):
        """auto_marker_on_toc=True should register a marker for any TOC heading."""
        mock_toc.return_value = ("anchor-1", "", 1)
        reset_marker_registry(MarkerConfig(auto_marker_on_toc=True))
        from streamtex.write import _handle_toc
        _handle_toc("Heading", toc_lvl="1")
        assert marker_count() == 1
        assert marker_entries()[0]["label"] == "Heading"

    @patch("streamtex.write.register_toc_entry")
    def test_auto_int_filters_by_level(self, mock_toc):
        """auto_marker_on_toc=1 should only register level 1 headings."""
        reset_marker_registry(MarkerConfig(auto_marker_on_toc=1))
        from streamtex.write import _handle_toc
        # Level 1 — should register
        mock_toc.return_value = ("anchor-1", "", 1)
        _handle_toc("Level 1", toc_lvl="1")
        # Level 2 — should NOT register
        mock_toc.return_value = ("anchor-2", "", 2)
        _handle_toc("Level 2", toc_lvl="2")
        assert marker_count() == 1
        assert marker_entries()[0]["label"] == "Level 1"

    @patch("streamtex.write.register_toc_entry")
    def test_auto_false_no_markers(self, mock_toc):
        """auto_marker_on_toc=False should not register any markers."""
        mock_toc.return_value = ("anchor-1", "", 1)
        reset_marker_registry(MarkerConfig(auto_marker_on_toc=False))
        from streamtex.write import _handle_toc
        _handle_toc("Heading", toc_lvl="1")
        assert marker_count() == 0

    @patch("streamtex.write.register_toc_entry")
    def test_marker_false_excludes(self, mock_toc):
        """marker=False should exclude the heading even when auto is True."""
        mock_toc.return_value = ("anchor-1", "", 1)
        reset_marker_registry(MarkerConfig(auto_marker_on_toc=True))
        from streamtex.write import _handle_toc
        _handle_toc("Excluded", toc_lvl="1", marker=False)
        assert marker_count() == 0

    @patch("streamtex.write.register_toc_entry")
    def test_marker_true_forces_include(self, mock_toc):
        """marker=True should force-include even when auto is False."""
        mock_toc.return_value = ("anchor-1", "", 1)
        reset_marker_registry(MarkerConfig(auto_marker_on_toc=False))
        from streamtex.write import _handle_toc
        _handle_toc("Forced", toc_lvl="1", marker=True)
        assert marker_count() == 1
        assert marker_entries()[0]["label"] == "Forced"
