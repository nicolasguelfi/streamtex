"""Tests for streamtex.ai.providers — provider registry and base class."""

import pytest

from streamtex.ai.providers import get_provider, list_providers
from streamtex.ai.providers.base import AIImageProvider, AIImageResult

# ===================================================================
# AIImageResult
# ===================================================================

class TestAIImageResult:
    def test_defaults(self):
        r = AIImageResult(image_bytes=b"data")
        assert r.image_bytes == b"data"
        assert r.format == "png"
        assert r.revised_prompt is None

    def test_custom_values(self):
        r = AIImageResult(image_bytes=b"jpg", format="jpeg", revised_prompt="revised")
        assert r.format == "jpeg"
        assert r.revised_prompt == "revised"


# ===================================================================
# AIImageProvider base
# ===================================================================

class TestAIImageProvider:
    def test_generate_not_implemented(self):
        provider = AIImageProvider()
        with pytest.raises(NotImplementedError):
            provider.generate("a cat")


# ===================================================================
# Provider registry
# ===================================================================

class TestProviderRegistry:
    def test_list_providers(self):
        providers = list_providers()
        assert "openai" in providers
        assert "google" in providers
        assert "fal" in providers

    def test_get_openai_provider(self):
        p = get_provider("openai")
        assert p.name == "openai"

    def test_get_google_provider(self):
        p = get_provider("google")
        assert p.name == "google"

    def test_get_fal_provider(self):
        p = get_provider("fal")
        assert p.name == "fal"

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown AI image provider"):
            get_provider("nonexistent")

    def test_unknown_provider_lists_available(self):
        with pytest.raises(ValueError, match="fal"):
            get_provider("bad_name")


# ===================================================================
# Provider import errors (when SDKs are not installed)
# ===================================================================

class TestProviderImportErrors:
    def test_openai_import_error(self):
        """OpenAI provider raises ImportError with install instructions."""
        from unittest.mock import patch
        p = get_provider("openai")
        with patch.dict("sys.modules", {"openai": None}):
            with pytest.raises(ImportError, match="openai"):
                p.generate("test", api_key="fake")

    def test_google_import_error(self):
        """Google provider raises ImportError with install instructions."""
        from unittest.mock import patch
        p = get_provider("google")
        # Need to mock the nested import path
        with patch.dict("sys.modules", {"google": None, "google.genai": None}):
            with pytest.raises(ImportError, match="google-genai"):
                p.generate("test", api_key="fake")

    def test_fal_import_error(self):
        """fal provider raises ImportError with install instructions."""
        from unittest.mock import patch
        p = get_provider("fal")
        with patch.dict("sys.modules", {"fal_client": None}):
            with pytest.raises(ImportError, match="fal-client"):
                p.generate("test", api_key="fake")


# ===================================================================
# Provider API key validation
# ===================================================================

class TestProviderApiKeyValidation:
    def test_openai_no_key_raises(self):
        from unittest.mock import MagicMock, patch
        p = get_provider("openai")
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}), \
             patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                p.generate("test")

    def test_google_no_key_raises(self):
        from unittest.mock import MagicMock, patch
        mock_google = MagicMock()
        mock_genai = MagicMock()
        p = get_provider("google")
        with patch.dict("sys.modules", {"google": mock_google, "google.genai": mock_genai}), \
             patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                p.generate("test")

    def test_fal_no_key_raises(self):
        from unittest.mock import MagicMock, patch
        mock_fal = MagicMock()
        p = get_provider("fal")
        with patch.dict("sys.modules", {"fal_client": mock_fal}), \
             patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                p.generate("test")
