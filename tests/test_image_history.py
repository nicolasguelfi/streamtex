"""Tests for ai/history.py — versioned image management."""

import os
import struct
import zlib

import pytest

from streamtex.ai.history import (
    get_current,
    get_current_metadata,
    list_versions,
    rename_image,
    rollback,
    save_version,
)
from streamtex.ai.metadata import load_metadata

# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def managed_dir(tmp_path):
    """Provide a temporary managed images directory."""
    d = str(tmp_path / "managed")
    os.makedirs(d)
    return d


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample PNG file (1x1 white pixel)."""
    def _create_png(path):
        sig = b"\x89PNG\r\n\x1a\n"
        ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
        ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)
        raw = b"\x00\xff\xff\xff"
        compressed = zlib.compress(raw)
        idat_crc = zlib.crc32(b"IDAT" + compressed)
        idat = (
            struct.pack(">I", len(compressed))
            + b"IDAT"
            + compressed
            + struct.pack(">I", idat_crc)
        )
        iend_crc = zlib.crc32(b"IEND")
        iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)
        with open(path, "wb") as f:
            f.write(sig + ihdr + idat + iend)
        return path

    return _create_png(str(tmp_path / "sample.png"))


# ===================================================================
# save_version
# ===================================================================

class TestSaveVersion:
    """Tests for save_version."""

    def test_first_version(self, managed_dir, sample_image):
        result = save_version("hero", sample_image, managed_dir=managed_dir)
        assert os.path.isfile(result)
        assert "hero.png" in result

        meta = get_current_metadata("hero", managed_dir=managed_dir)
        assert meta is not None
        assert meta.version == 1
        assert meta.name == "hero"

    def test_second_version_archives_first(self, managed_dir, sample_image):
        save_version("hero", sample_image, managed_dir=managed_dir)
        save_version(
            "hero",
            sample_image,
            managed_dir=managed_dir,
            source_type="ai_generated",
            prompt="New prompt",
        )

        meta = get_current_metadata("hero", managed_dir=managed_dir)
        assert meta.version == 2
        assert meta.prompt == "New prompt"

        # v1 should be archived
        v1_path = os.path.join(managed_dir, "hero_v1.png")
        assert os.path.isfile(v1_path)
        v1_json = os.path.join(managed_dir, "hero_v1.json")
        assert os.path.isfile(v1_json)
        v1_meta = load_metadata(v1_json)
        assert v1_meta.version == 1

    def test_ai_metadata(self, managed_dir, sample_image):
        save_version(
            "hero",
            sample_image,
            managed_dir=managed_dir,
            source_type="ai_generated",
            prompt="A sunset over mountains",
            provider="openai",
            model="gpt-image-1",
            size="1024x1024",
            quality="hd",
        )
        meta = get_current_metadata("hero", managed_dir=managed_dir)
        assert meta.source_type == "ai_generated"
        assert meta.prompt == "A sunset over mountains"
        assert meta.provider == "openai"
        assert meta.model == "gpt-image-1"

    def test_three_versions(self, managed_dir, sample_image):
        for i in range(3):
            save_version(
                "test", sample_image, managed_dir=managed_dir, prompt=f"version {i+1}"
            )
        meta = get_current_metadata("test", managed_dir=managed_dir)
        assert meta.version == 3
        assert meta.prompt == "version 3"


# ===================================================================
# get_current and get_current_metadata
# ===================================================================

class TestGetCurrent:
    """Tests for get_current and get_current_metadata."""

    def test_not_found(self, managed_dir):
        assert get_current("nonexistent", managed_dir=managed_dir) is None

    def test_found(self, managed_dir, sample_image):
        save_version("hero", sample_image, managed_dir=managed_dir)
        path = get_current("hero", managed_dir=managed_dir)
        assert path is not None
        assert os.path.isfile(path)

    def test_metadata_not_found(self, managed_dir):
        assert get_current_metadata("nonexistent", managed_dir=managed_dir) is None


# ===================================================================
# list_versions
# ===================================================================

class TestListVersions:
    """Tests for list_versions."""

    def test_empty(self, managed_dir):
        assert list_versions("nonexistent", managed_dir=managed_dir) == []

    def test_single_version(self, managed_dir, sample_image):
        save_version("hero", sample_image, managed_dir=managed_dir)
        versions = list_versions("hero", managed_dir=managed_dir)
        assert len(versions) == 1
        assert versions[0][0] == 1

    def test_multiple_versions(self, managed_dir, sample_image):
        for _ in range(3):
            save_version("hero", sample_image, managed_dir=managed_dir)
        versions = list_versions("hero", managed_dir=managed_dir)
        assert len(versions) == 3
        assert [v[0] for v in versions] == [1, 2, 3]

    def test_sorted_ascending(self, managed_dir, sample_image):
        for _ in range(5):
            save_version("hero", sample_image, managed_dir=managed_dir)
        versions = list_versions("hero", managed_dir=managed_dir)
        version_nums = [v[0] for v in versions]
        assert version_nums == sorted(version_nums)


# ===================================================================
# rollback
# ===================================================================

class TestRollback:
    """Tests for rollback."""

    def test_rollback_to_v1(self, managed_dir, sample_image):
        save_version("hero", sample_image, managed_dir=managed_dir, prompt="v1")
        save_version("hero", sample_image, managed_dir=managed_dir, prompt="v2")

        result = rollback("hero", 1, managed_dir=managed_dir)
        assert result is not None
        meta = get_current_metadata("hero", managed_dir=managed_dir)
        assert meta.version == 3  # Rollback creates a new version
        assert meta.prompt == "v1"

    def test_rollback_nonexistent_version(self, managed_dir, sample_image):
        save_version("hero", sample_image, managed_dir=managed_dir)
        result = rollback("hero", 99, managed_dir=managed_dir)
        assert result is None

    def test_rollback_nonexistent_name(self, managed_dir):
        result = rollback("nonexistent", 1, managed_dir=managed_dir)
        assert result is None


# ===================================================================
# rename_image
# ===================================================================

class TestRenameImage:
    """Tests for rename_image."""

    def test_rename(self, managed_dir, sample_image):
        save_version("old_name", sample_image, managed_dir=managed_dir)
        result = rename_image("old_name", "new_name", managed_dir=managed_dir)
        assert result is not None
        assert "new_name" in result

        # Old should be gone
        assert get_current("old_name", managed_dir=managed_dir) is None
        # New should exist
        assert get_current("new_name", managed_dir=managed_dir) is not None
        meta = get_current_metadata("new_name", managed_dir=managed_dir)
        assert meta.name == "new_name"

    def test_rename_with_history(self, managed_dir, sample_image):
        save_version("old", sample_image, managed_dir=managed_dir)
        save_version("old", sample_image, managed_dir=managed_dir)
        rename_image("old", "new", managed_dir=managed_dir)

        # Archived versions should be renamed too
        assert os.path.isfile(os.path.join(managed_dir, "new_v1.png"))

    def test_rename_nonexistent(self, managed_dir):
        result = rename_image("nonexistent", "new", managed_dir=managed_dir)
        assert result is None


# ===================================================================
# Provider available_models
# ===================================================================

class TestProviderModels:
    """Tests for available_models on providers."""

    def test_openai_models(self):
        from streamtex.ai.providers.openai import OpenAIProvider

        models = OpenAIProvider.available_models()
        assert "gpt-image-1" in models
        assert "dall-e-3" in models

    def test_google_models(self):
        from streamtex.ai.providers.google import GoogleProvider

        models = GoogleProvider.available_models()
        assert "imagen-4.0-generate-001" in models

    def test_fal_models(self):
        from streamtex.ai.providers.fal import FalProvider

        models = FalProvider.available_models()
        assert "fal-ai/stable-diffusion-v35-large" in models

    def test_base_returns_empty(self):
        from streamtex.ai.providers.base import AIImageProvider

        assert AIImageProvider.available_models() == []

    def test_registry_get_available_models(self):
        from streamtex.ai.providers.registry import get_available_models

        models = get_available_models("openai")
        assert "gpt-image-1" in models

    def test_registry_unknown_provider(self):
        from streamtex.ai.providers.registry import get_available_models

        assert get_available_models("unknown") == []
