"""Tests for the Marker Navigation system."""

import pytest
from streamtex.marker import (
    MarkerConfig, MarkerRegistry,
    reset_marker_registry, register_marker,
    marker_entries, marker_count, get_marker_config,
)
import streamtex.marker as marker_mod


class TestMarkerConfig:
    def test_defaults(self):
        cfg = MarkerConfig()
        assert cfg.keyboard_nav is True
        assert cfg.show_nav_ui is True
        assert cfg.auto_marker_on_toc is False
        assert cfg.nav_position == "bottom-right"
        assert cfg.next_keys == ["PageDown"]
        assert cfg.prev_keys == ["PageUp"]

    def test_custom(self):
        cfg = MarkerConfig(keyboard_nav=False, auto_marker_on_toc=2, nav_position="bottom-center")
        assert cfg.keyboard_nav is False
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
