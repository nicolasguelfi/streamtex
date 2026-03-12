"""Tests for link_config — LinkConfig dataclass and global get/set."""


from streamtex.link_config import LinkConfig, get_link_config, set_link_config


class TestLinkConfig:
    def test_default_values(self):
        """Default config: external _blank, internal _self."""
        cfg = LinkConfig()
        assert cfg.external_target == "_blank"
        assert cfg.internal_target == "_self"

    def test_custom_values(self):
        """Custom config values are stored correctly."""
        cfg = LinkConfig(external_target="_self", internal_target="_top")
        assert cfg.external_target == "_self"
        assert cfg.internal_target == "_top"

    def test_is_dataclass(self):
        """LinkConfig is a proper dataclass with field access."""
        from dataclasses import fields
        cfg = LinkConfig()
        field_names = {f.name for f in fields(cfg)}
        assert "external_target" in field_names
        assert "internal_target" in field_names


class TestGetSetLinkConfig:
    def setup_method(self):
        """Reset to default config before each test."""
        set_link_config(LinkConfig())

    def test_get_returns_default(self):
        """get_link_config returns default LinkConfig initially."""
        cfg = get_link_config()
        assert isinstance(cfg, LinkConfig)
        assert cfg.external_target == "_blank"

    def test_set_then_get(self):
        """set_link_config stores config that get_link_config retrieves."""
        custom = LinkConfig(external_target="_top", internal_target="_parent")
        set_link_config(custom)
        result = get_link_config()
        assert result is custom
        assert result.external_target == "_top"
        assert result.internal_target == "_parent"

    def test_set_overwrites_previous(self):
        """Setting a new config replaces the previous one."""
        set_link_config(LinkConfig(external_target="_self"))
        set_link_config(LinkConfig(external_target="_top"))
        assert get_link_config().external_target == "_top"
