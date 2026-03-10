"""Tests for ai/metadata.py — ImageMetadata and JSON sidecar operations."""

import json
import os

from streamtex.ai.metadata import (
    ImageMetadata,
    load_metadata,
    metadata_path_for,
    save_metadata,
)

# ===================================================================
# ImageMetadata dataclass
# ===================================================================

class TestImageMetadata:
    """Tests for the ImageMetadata dataclass."""

    def test_defaults(self):
        meta = ImageMetadata(name="test")
        assert meta.name == "test"
        assert meta.version == 1
        assert meta.source_type == "local"
        assert meta.prompt is None
        assert meta.provider is None
        assert meta.timestamp  # auto-populated

    def test_ai_metadata(self):
        meta = ImageMetadata(
            name="hero",
            version=3,
            source_type="ai_generated",
            prompt="A sunset",
            provider="openai",
            model="gpt-image-1",
            size="1024x1024",
            quality="hd",
        )
        assert meta.source_type == "ai_generated"
        assert meta.prompt == "A sunset"
        assert meta.provider == "openai"

    def test_timestamp_auto_populated(self):
        meta = ImageMetadata(name="test")
        assert "T" in meta.timestamp  # ISO format

    def test_timestamp_preserved(self):
        meta = ImageMetadata(name="test", timestamp="2026-01-01T00:00:00Z")
        assert meta.timestamp == "2026-01-01T00:00:00Z"


# ===================================================================
# save_metadata and load_metadata
# ===================================================================

class TestMetadataIO:
    """Tests for save_metadata and load_metadata."""

    def test_save_and_load(self, tmp_path):
        meta = ImageMetadata(
            name="hero",
            version=2,
            source_type="ai_generated",
            prompt="A forest",
            provider="openai",
        )
        json_path = str(tmp_path / "hero.json")
        save_metadata(meta, json_path)

        loaded = load_metadata(json_path)
        assert loaded is not None
        assert loaded.name == "hero"
        assert loaded.version == 2
        assert loaded.prompt == "A forest"
        assert loaded.provider == "openai"

    def test_load_nonexistent(self):
        assert load_metadata("/nonexistent/path.json") is None

    def test_save_creates_directory(self, tmp_path):
        deep_path = str(tmp_path / "a" / "b" / "c" / "meta.json")
        meta = ImageMetadata(name="test")
        save_metadata(meta, deep_path)
        assert os.path.isfile(deep_path)

    def test_json_content(self, tmp_path):
        meta = ImageMetadata(name="test", prompt="Hello")
        json_path = str(tmp_path / "test.json")
        save_metadata(meta, json_path)

        with open(json_path) as f:
            data = json.load(f)
        assert data["name"] == "test"
        assert data["prompt"] == "Hello"
        assert data["version"] == 1


# ===================================================================
# metadata_path_for helper
# ===================================================================

class TestMetadataPathFor:
    """Tests for metadata_path_for helper."""

    def test_png(self):
        assert metadata_path_for("images/hero.png") == "images/hero.json"

    def test_jpeg(self):
        assert metadata_path_for("images/photo.jpeg") == "images/photo.json"

    def test_no_extension(self):
        assert metadata_path_for("images/file") == "images/file.json"

    def test_nested_path(self):
        assert metadata_path_for("a/b/c/img.png") == "a/b/c/img.json"
