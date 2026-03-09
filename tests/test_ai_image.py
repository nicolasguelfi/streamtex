"""Tests for streamtex.ai_image — st_ai_image() and st_ai_image_widget()."""

from unittest.mock import MagicMock, patch

from streamtex.ai.config import AIImageConfig, set_ai_image_config
from streamtex.ai.generate import _make_cache_key
from streamtex.ai_image import st_ai_image

# ===================================================================
# st_ai_image — cached image
# ===================================================================

class TestStAiImageCached:
    def test_displays_cached_image(self, tmp_path):
        """When the image is already cached, it is displayed directly."""
        cfg = AIImageConfig(output_dir=str(tmp_path))

        cache_key = _make_cache_key("a cat", "openai", "1024x1024")
        cached_file = tmp_path / f"{cache_key}.png"
        cached_file.write_bytes(b"cached PNG")

        with patch("streamtex.ai_image.st_image") as mock_st_image:
            result = st_ai_image("a cat", config=cfg)

        assert result == str(cached_file)
        mock_st_image.assert_called_once()
        call_kwargs = mock_st_image.call_args
        assert call_kwargs.kwargs["uri"] == str(cached_file)


# ===================================================================
# st_ai_image — auto_generate mode
# ===================================================================

class TestStAiImageAutoGenerate:
    @patch("streamtex.ai_image.generate_image")
    @patch("streamtex.ai_image.is_cached", return_value=False)
    @patch("streamtex.ai_image.st_image")
    def test_auto_generate_calls_api(self, mock_st_image, mock_is_cached, mock_generate, tmp_path):
        cfg = AIImageConfig(output_dir=str(tmp_path), auto_generate=True)
        fake_path = str(tmp_path / "generated.png")
        mock_generate.return_value = fake_path

        result = st_ai_image("a sunset", config=cfg)

        mock_generate.assert_called_once()
        mock_st_image.assert_called_once()
        assert result == fake_path

    @patch("streamtex.ai_image.generate_image")
    @patch("streamtex.ai_image.is_cached", return_value=False)
    def test_auto_generate_error_shows_st_error(self, mock_is_cached, mock_generate, tmp_path):
        from streamtex.ai.generate import AIImageError
        cfg = AIImageConfig(output_dir=str(tmp_path), auto_generate=True)
        mock_generate.side_effect = AIImageError("API down")

        mock_st = MagicMock()
        with patch("streamtex.ai_image.st", mock_st):
            result = st_ai_image("a sunset", config=cfg)

        assert result is None
        mock_st.error.assert_called_once()


# ===================================================================
# st_ai_image — manual mode (placeholder)
# ===================================================================

class TestStAiImageManualMode:
    @patch("streamtex.ai_image.is_cached", return_value=False)
    def test_manual_mode_shows_placeholder(self, mock_is_cached, tmp_path):
        cfg = AIImageConfig(output_dir=str(tmp_path), auto_generate=False)

        mock_st = MagicMock()
        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.button.return_value = False  # User hasn't clicked yet

        with patch("streamtex.ai_image.st", mock_st):
            result = st_ai_image("a cat", config=cfg)

        assert result is None
        mock_st.container.assert_called_once()
        mock_st.caption.assert_called_once()
        mock_st.button.assert_called_once()


# ===================================================================
# st_ai_image — provider and size overrides
# ===================================================================

class TestStAiImageOverrides:
    def test_provider_override(self, tmp_path):
        """Provider parameter overrides config default."""
        cfg = AIImageConfig(output_dir=str(tmp_path), provider="openai")

        # Create cache for google provider
        cache_key = _make_cache_key("test", "google", "1024x1024")
        (tmp_path / f"{cache_key}.png").write_bytes(b"PNG")

        with patch("streamtex.ai_image.st_image"):
            result = st_ai_image("test", provider="google", config=cfg)

        assert result is not None

    def test_size_override(self, tmp_path):
        """Size parameter overrides config default."""
        cfg = AIImageConfig(output_dir=str(tmp_path))

        cache_key = _make_cache_key("test", "openai", "512x512")
        (tmp_path / f"{cache_key}.png").write_bytes(b"PNG")

        with patch("streamtex.ai_image.st_image"):
            result = st_ai_image("test", size="512x512", config=cfg)

        assert result is not None


# ===================================================================
# DI config integration
# ===================================================================

class TestDIConfigIntegration:
    def test_uses_global_config(self, tmp_path):
        """st_ai_image uses the global config if none is passed."""
        cfg = AIImageConfig(output_dir=str(tmp_path), provider="fal")
        set_ai_image_config(cfg)

        cache_key = _make_cache_key("test", "fal", "1024x1024")
        (tmp_path / f"{cache_key}.png").write_bytes(b"PNG")

        try:
            with patch("streamtex.ai_image.st_image"):
                result = st_ai_image("test")
            assert result is not None
        finally:
            set_ai_image_config(None)
