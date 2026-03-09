"""Tests for streamtex.ai.generate — image generation orchestrator."""

import os
from unittest.mock import MagicMock, patch

import pytest

from streamtex.ai.config import AIImageConfig
from streamtex.ai.generate import (
    AIImageError,
    _find_cached,
    _make_cache_key,
    generate_image,
    is_cached,
)
from streamtex.ai.providers.base import AIImageResult

# ===================================================================
# Cache key generation
# ===================================================================

class TestMakeCacheKey:
    def test_deterministic(self):
        k1 = _make_cache_key("cat", "openai", "1024x1024")
        k2 = _make_cache_key("cat", "openai", "1024x1024")
        assert k1 == k2

    def test_different_prompts_different_keys(self):
        k1 = _make_cache_key("cat", "openai", "1024x1024")
        k2 = _make_cache_key("dog", "openai", "1024x1024")
        assert k1 != k2

    def test_different_providers_different_keys(self):
        k1 = _make_cache_key("cat", "openai", "1024x1024")
        k2 = _make_cache_key("cat", "google", "1024x1024")
        assert k1 != k2

    def test_different_sizes_different_keys(self):
        k1 = _make_cache_key("cat", "openai", "1024x1024")
        k2 = _make_cache_key("cat", "openai", "512x512")
        assert k1 != k2

    def test_seed_affects_key(self):
        k1 = _make_cache_key("cat", "openai", "1024x1024", seed=42)
        k2 = _make_cache_key("cat", "openai", "1024x1024", seed=99)
        assert k1 != k2

    def test_key_length(self):
        k = _make_cache_key("cat", "openai", "1024x1024")
        assert len(k) == 16


# ===================================================================
# Cache lookup
# ===================================================================

class TestFindCached:
    def test_finds_png(self, tmp_path):
        (tmp_path / "abc123.png").write_bytes(b"PNG")
        assert _find_cached(str(tmp_path), "abc123") == str(tmp_path / "abc123.png")

    def test_finds_jpeg(self, tmp_path):
        (tmp_path / "abc123.jpeg").write_bytes(b"JPEG")
        assert _find_cached(str(tmp_path), "abc123") == str(tmp_path / "abc123.jpeg")

    def test_not_found(self, tmp_path):
        assert _find_cached(str(tmp_path), "missing") is None


# ===================================================================
# generate_image
# ===================================================================

class TestGenerateImage:
    def test_returns_cached_file(self, tmp_path):
        """If the image is already cached, no API call is made."""
        cfg = AIImageConfig(output_dir=str(tmp_path))

        # Pre-create cached file
        cache_key = _make_cache_key("cat", "openai", "1024x1024")
        cached_file = tmp_path / f"{cache_key}.png"
        cached_file.write_bytes(b"cached PNG")

        result = generate_image("cat", config=cfg)
        assert result == str(cached_file)

    @patch("streamtex.ai.generate.get_provider")
    def test_generates_and_saves(self, mock_get_provider, tmp_path):
        """When not cached, calls provider and saves the result."""
        cfg = AIImageConfig(output_dir=str(tmp_path), auto_generate=True)
        mock_provider = MagicMock()
        mock_provider.generate.return_value = AIImageResult(
            image_bytes=b"generated PNG data",
            format="png",
        )
        mock_get_provider.return_value = mock_provider

        with patch.dict("os.environ", {"STX_OPENAI_API_KEY": "sk-test"}):
            result = generate_image("a beautiful sunset", config=cfg)

        assert os.path.isfile(result)
        assert result.endswith(".png")
        with open(result, "rb") as f:
            assert f.read() == b"generated PNG data"

    @patch("streamtex.ai.generate.get_provider")
    def test_provider_error_raises_ai_image_error(self, mock_get_provider, tmp_path):
        """Provider failures are wrapped in AIImageError."""
        cfg = AIImageConfig(output_dir=str(tmp_path))
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = RuntimeError("API error")
        mock_get_provider.return_value = mock_provider

        with patch.dict("os.environ", {"STX_OPENAI_API_KEY": "sk-test"}):
            with pytest.raises(AIImageError, match="Image generation failed"):
                generate_image("a cat", config=cfg)

    @patch("streamtex.ai.generate.get_provider")
    def test_saves_jpeg_format(self, mock_get_provider, tmp_path):
        """JPEG format is saved with .jpeg extension."""
        cfg = AIImageConfig(output_dir=str(tmp_path))
        mock_provider = MagicMock()
        mock_provider.generate.return_value = AIImageResult(
            image_bytes=b"JPEG data", format="jpeg",
        )
        mock_get_provider.return_value = mock_provider

        with patch.dict("os.environ", {"STX_OPENAI_API_KEY": "sk-test"}):
            result = generate_image("a cat", config=cfg)

        assert result.endswith(".jpeg")

    def test_creates_output_dir(self, tmp_path):
        """Output directory is created if it doesn't exist."""
        output_dir = str(tmp_path / "nested" / "dir")
        cfg = AIImageConfig(output_dir=output_dir)

        # Pre-create cache to avoid API call
        os.makedirs(output_dir, exist_ok=True)
        cache_key = _make_cache_key("cat", "openai", "1024x1024")
        with open(os.path.join(output_dir, f"{cache_key}.png"), "wb") as f:
            f.write(b"PNG")

        result = generate_image("cat", config=cfg)
        assert os.path.isfile(result)


# ===================================================================
# is_cached
# ===================================================================

class TestIsCached:
    def test_returns_true_when_cached(self, tmp_path):
        cfg = AIImageConfig(output_dir=str(tmp_path))
        cache_key = _make_cache_key("cat", "openai", "1024x1024")
        (tmp_path / f"{cache_key}.png").write_bytes(b"PNG")
        assert is_cached("cat", config=cfg) is True

    def test_returns_false_when_not_cached(self, tmp_path):
        cfg = AIImageConfig(output_dir=str(tmp_path))
        assert is_cached("cat", config=cfg) is False
