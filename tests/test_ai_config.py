"""Tests for streamtex.ai.config — AI image generation configuration."""

from unittest.mock import patch

from streamtex.ai.config import (
    AIImageConfig,
    get_ai_image_config,
    set_ai_image_config,
)

# ===================================================================
# AIImageConfig defaults
# ===================================================================

class TestAIImageConfigDefaults:
    def test_defaults(self):
        cfg = AIImageConfig()
        assert cfg.provider == "openai"
        assert cfg.default_size == "1024x1024"
        assert cfg.output_dir == "static/images/ai"
        assert cfg.auto_generate is False
        assert cfg.api_keys == {}

    def test_custom_values(self):
        cfg = AIImageConfig(provider="google", default_size="512x512", auto_generate=True)
        assert cfg.provider == "google"
        assert cfg.default_size == "512x512"
        assert cfg.auto_generate is True


# ===================================================================
# API key resolution
# ===================================================================

class TestResolveApiKey:
    def test_explicit_dict_takes_priority(self):
        cfg = AIImageConfig(api_keys={"openai": "sk-explicit"})
        assert cfg.resolve_api_key("openai") == "sk-explicit"

    def test_stx_env_var(self):
        cfg = AIImageConfig()
        with patch.dict("os.environ", {"STX_OPENAI_API_KEY": "sk-stx-env"}):
            assert cfg.resolve_api_key("openai") == "sk-stx-env"

    def test_provider_env_var_fallback(self):
        cfg = AIImageConfig()
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-default-env"}, clear=False):
            # Remove STX_ var if present
            import os
            os.environ.pop("STX_OPENAI_API_KEY", None)
            assert cfg.resolve_api_key("openai") == "sk-default-env"

    def test_google_env_vars(self):
        cfg = AIImageConfig()
        with patch.dict("os.environ", {"STX_GOOGLE_AI_KEY": "google-key"}, clear=False):
            assert cfg.resolve_api_key("google") == "google-key"

    def test_fal_env_vars(self):
        cfg = AIImageConfig()
        with patch.dict("os.environ", {"STX_FAL_KEY": "fal-key"}, clear=False):
            assert cfg.resolve_api_key("fal") == "fal-key"

    def test_no_key_returns_none(self):
        cfg = AIImageConfig()
        with patch.dict("os.environ", {}, clear=True):
            assert cfg.resolve_api_key("openai") is None

    def test_uses_default_provider(self):
        cfg = AIImageConfig(provider="google", api_keys={"google": "gk"})
        assert cfg.resolve_api_key() == "gk"

    def test_unknown_provider_returns_none(self):
        cfg = AIImageConfig()
        with patch.dict("os.environ", {}, clear=True):
            assert cfg.resolve_api_key("unknown") is None


# ===================================================================
# DI singleton
# ===================================================================

class TestDISingleton:
    def test_set_and_get(self):
        cfg = AIImageConfig(provider="fal")
        set_ai_image_config(cfg)
        assert get_ai_image_config() is cfg
        # Cleanup
        set_ai_image_config(None)

    def test_default_is_none(self):
        set_ai_image_config(None)
        assert get_ai_image_config() is None
