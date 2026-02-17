"""Tests for the Table of Contents system."""

import pytest
from streamtex.toc import TOCConfig, TOCRegistry


class TestTOCConfig:
    def test_defaults(self):
        config = TOCConfig()
        assert config.numerate_titles is True
        assert config.toc_position == -1

    def test_custom_position(self):
        config = TOCConfig(toc_position=3)
        assert config.toc_position == 3


class TestTOCRegistry:
    def test_empty_registry(self):
        reg = TOCRegistry()
        assert reg.get_entries() == []

    def test_register_entry(self):
        reg = TOCRegistry()
        key_anchor, section_number = reg.register_entry("Introduction", "1")
        entries = reg.get_entries()
        assert len(entries) == 1
        assert entries[0]["title"] == "1 Introduction"
        assert entries[0]["level"] == 1

    def test_register_multiple_entries(self):
        reg = TOCRegistry()
        reg.register_entry("Chapter 1", "1")
        reg.register_entry("Chapter 2", "1")
        entries = reg.get_entries()
        assert len(entries) == 2
        assert entries[0]["title"] == "1 Chapter 1"
        assert entries[1]["title"] == "2 Chapter 2"

    def test_hierarchical_numbering(self):
        reg = TOCRegistry()
        reg.register_entry("Chapter", "1")
        reg.register_entry("Section", "2")
        entries = reg.get_entries()
        assert entries[0]["title"] == "1 Chapter"
        assert entries[1]["title"] == "1.1 Section"

    def test_relative_level_positive(self):
        reg = TOCRegistry()
        reg.register_entry("Root", "1")
        reg.register_entry("Sub", "+1")
        entries = reg.get_entries()
        assert entries[1]["level"] == 2

    def test_relative_level_negative(self):
        reg = TOCRegistry()
        reg.register_entry("Level 1", "1")
        reg.register_entry("Level 2", "2")
        reg.register_entry("Back to 1", "-1")
        entries = reg.get_entries()
        assert entries[2]["level"] == 1

    def test_no_numeration(self):
        config = TOCConfig(numerate_titles=False)
        reg = TOCRegistry(config)
        reg.register_entry("Title", "1")
        entries = reg.get_entries()
        assert entries[0]["title"] == "Title"

    def test_reset(self):
        reg = TOCRegistry()
        reg.register_entry("Something", "1")
        reg.reset()
        assert reg.get_entries() == []
        assert reg.current_level == 1

    def test_key_anchor_format(self):
        anchor = TOCRegistry.get_key_anchor("1.2 My Title")
        assert anchor == "1-2-my-title"

    def test_level_minimum_is_1(self):
        reg = TOCRegistry()
        reg.register_entry("Title", "-5")
        entries = reg.get_entries()
        assert entries[0]["level"] == 1
