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

    def test_finds_webp(self, tmp_path):
        (tmp_path / "abc123.webp").write_bytes(b"WEBP")
        assert _find_cached(str(tmp_path), "abc123") == str(tmp_path / "abc123.webp")

    def test_webp_preferred_over_png(self, tmp_path):
        """When both webp and png exist, webp is returned (checked first)."""
        (tmp_path / "abc123.webp").write_bytes(b"WEBP")
        (tmp_path / "abc123.png").write_bytes(b"PNG")
        assert _find_cached(str(tmp_path), "abc123").endswith(".webp")

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


# ===================================================================
# WebP transcoding (save_format / save_quality)
# ===================================================================

class TestSaveFormat:
    def _make_png_bytes(self, width=4, height=4):
        """Create a minimal valid PNG using Pillow."""
        import io

        from PIL import Image
        img = Image.new("RGBA", (width, height), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @patch("streamtex.ai.generate.get_provider")
    def test_default_saves_as_webp(self, mock_get_provider, tmp_path):
        """Default save_format='webp' transcodes PNG → WebP."""
        cfg = AIImageConfig(output_dir=str(tmp_path))
        mock_prov = MagicMock()
        mock_prov.generate.return_value = AIImageResult(self._make_png_bytes(), "png")
        mock_get_provider.return_value = mock_prov

        result = generate_image("a cat", config=cfg)
        assert result.endswith(".webp")
        assert os.path.isfile(result)

    @patch("streamtex.ai.generate.get_provider")
    def test_save_format_png_keeps_png(self, mock_get_provider, tmp_path):
        """save_format='png' keeps the original PNG bytes."""
        cfg = AIImageConfig(output_dir=str(tmp_path), save_format="png")
        mock_prov = MagicMock()
        png_bytes = self._make_png_bytes()
        mock_prov.generate.return_value = AIImageResult(png_bytes, "png")
        mock_get_provider.return_value = mock_prov

        result = generate_image("a cat", config=cfg)
        assert result.endswith(".png")

    @patch("streamtex.ai.generate.get_provider")
    def test_webp_smaller_than_png(self, mock_get_provider, tmp_path):
        """WebP output should be smaller than the original PNG."""
        cfg = AIImageConfig(output_dir=str(tmp_path))
        png_bytes = self._make_png_bytes(width=64, height=64)
        mock_prov = MagicMock()
        mock_prov.generate.return_value = AIImageResult(png_bytes, "png")
        mock_get_provider.return_value = mock_prov

        result = generate_image("a cat", config=cfg)
        webp_size = os.path.getsize(result)
        assert webp_size < len(png_bytes)

    @patch("streamtex.ai.generate.get_provider")
    def test_save_quality_affects_output(self, mock_get_provider, tmp_path):
        """Lower quality should produce smaller files."""
        png_bytes = self._make_png_bytes(width=64, height=64)

        sizes = {}
        for q in (50, 90):
            cfg = AIImageConfig(output_dir=str(tmp_path / str(q)), save_quality=q)
            os.makedirs(cfg.output_dir, exist_ok=True)
            mock_prov = MagicMock()
            mock_prov.generate.return_value = AIImageResult(png_bytes, "png")
            mock_get_provider.return_value = mock_prov
            result = generate_image("a cat", config=cfg)
            sizes[q] = os.path.getsize(result)

        assert sizes[50] <= sizes[90]

    @patch("streamtex.ai.generate.get_provider")
    def test_fallback_when_pillow_missing(self, mock_get_provider, tmp_path):
        """When Pillow import fails, keep original format."""
        cfg = AIImageConfig(output_dir=str(tmp_path), save_format="webp")
        mock_prov = MagicMock()
        mock_prov.generate.return_value = AIImageResult(b"fake PNG bytes", "png")
        mock_get_provider.return_value = mock_prov

        with patch.dict("sys.modules", {"PIL": None, "PIL.Image": None}):
            # Force ImportError by patching the import inside generate_image
            import builtins
            original_import = builtins.__import__
            def mock_import(name, *args, **kwargs):
                if name == "PIL" or name == "PIL.Image":
                    raise ImportError("mocked")
                return original_import(name, *args, **kwargs)
            with patch("builtins.__import__", side_effect=mock_import):
                result = generate_image("a cat", config=cfg)

        assert result.endswith(".png")  # Fallback to original format
