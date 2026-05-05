"""Tests for streamtex.ai.providers — provider registry and base class."""

import pytest

from streamtex.ai.providers import (
    SizeValidation,
    get_provider,
    list_providers,
    validate_size,
)
from streamtex.ai.providers.base import AIImageProvider, AIImageResult, ModelCapabilities

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


# ===================================================================
# Size validation
# ===================================================================

class TestModelCapabilitiesSupportsCustom:
    """The supports_custom flag drives the editor's "Custom..." entry."""

    def test_default_false(self):
        caps = ModelCapabilities(sizes=["1024x1024"], qualities=["standard"])
        assert caps.supports_custom is False

    def test_openai_does_not_support_custom(self):
        from streamtex.ai.providers.openai import OpenAIProvider
        for model in ["gpt-image-1", "dall-e-3", None]:
            assert OpenAIProvider.model_capabilities(model).supports_custom is False

    def test_google_does_not_support_custom(self):
        from streamtex.ai.providers.google import GoogleProvider
        assert GoogleProvider.model_capabilities().supports_custom is False

    def test_fal_supports_custom(self):
        from streamtex.ai.providers.fal import FalProvider
        assert FalProvider.model_capabilities().supports_custom is True


class TestDefaultValidateSize:
    """The base class validate_size enforces a strict whitelist."""

    def test_whitelisted_size_passes(self):
        from streamtex.ai.providers.openai import OpenAIProvider
        result = OpenAIProvider.validate_size("1024x1024", "gpt-image-1")
        assert result.valid is True
        assert result.normalized == "1024x1024"
        assert result.warning is None
        assert result.error is None

    def test_unknown_size_rejected_for_openai(self):
        from streamtex.ai.providers.openai import OpenAIProvider
        result = OpenAIProvider.validate_size("1280x256", "gpt-image-1")
        assert result.valid is False
        assert result.error is not None
        assert "openai" in result.error
        assert "Allowed:" in result.error

    def test_unknown_size_rejected_for_google(self):
        from streamtex.ai.providers.google import GoogleProvider
        result = GoogleProvider.validate_size("1280x256")
        assert result.valid is False
        assert result.error is not None


class TestFalValidateSize:
    """fal.ai accepts arbitrary multiples of 64 within bounds."""

    def test_whitelisted_size_passes_without_warning(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("1024x1024")
        assert result.valid is True
        assert result.normalized == "1024x1024"
        assert result.warning is None

    def test_clean_banner_accepted(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("1280x256")
        assert result.valid is True
        assert result.normalized == "1280x256"
        # 1280/256 = 5.0 → triggers ratio warning
        assert result.warning is not None
        assert "Aspect ratio" in result.warning

    def test_moderate_ratio_no_warning(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("1280x768")
        assert result.valid is True
        assert result.normalized == "1280x768"
        assert result.warning is None

    def test_rounds_to_multiple_of_64(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("1280x257")
        assert result.valid is True
        assert result.normalized == "1280x256"
        assert result.warning is not None
        assert "multiples of 64" in result.warning.lower()

    def test_below_min_side_rejected(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("100x100")
        assert result.valid is False
        assert result.error is not None
        assert "between 256 and 2048" in result.error

    def test_above_max_side_rejected(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("4000x4000")
        assert result.valid is False
        assert result.error is not None

    def test_total_pixels_exceeded(self):
        from streamtex.ai.providers.fal import FalProvider
        # 2048*2048 = 4 194 304 px > 2 097 152 px budget
        result = FalProvider.validate_size("2048x2048")
        assert result.valid is False
        assert result.error is not None
        assert "exceeds" in result.error

    def test_extreme_ratio_warns_but_accepts(self):
        from streamtex.ai.providers.fal import FalProvider
        # 2048x256 = 524 288 px (under budget), ratio 8:1
        result = FalProvider.validate_size("2048x256")
        assert result.valid is True
        assert result.warning is not None
        assert "ratio" in result.warning.lower()

    def test_malformed_size_rejected(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("not-a-size")
        assert result.valid is False
        assert result.error is not None
        assert "WxH" in result.error

    def test_negative_dimensions_rejected(self):
        from streamtex.ai.providers.fal import FalProvider
        result = FalProvider.validate_size("-100x100")
        assert result.valid is False
        assert result.error is not None


class TestRegistryValidateSize:
    """The validate_size() registry helper delegates to the provider."""

    def test_dispatches_to_provider(self):
        result = validate_size("fal", "1280x256")
        assert isinstance(result, SizeValidation)
        assert result.valid is True

    def test_rejects_for_strict_provider(self):
        result = validate_size("openai", "1280x256", "gpt-image-1")
        assert result.valid is False

    def test_unknown_provider_returns_invalid(self):
        result = validate_size("nonexistent", "1024x1024")
        assert result.valid is False
        assert result.error is not None
        assert "Unknown provider" in result.error
