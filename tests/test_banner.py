"""Tests for the Banner configuration system."""

from streamtex.banner import _MODE_DEFAULTS, BannerConfig, BannerMode


class TestBannerMode:
    def test_enum_values(self):
        assert BannerMode.FULL.value == "full"
        assert BannerMode.COMPACT.value == "compact"
        assert BannerMode.HIDDEN.value == "hidden"

    def test_all_modes_in_lookup(self):
        """FULL and COMPACT must have mode defaults; HIDDEN does not."""
        assert BannerMode.FULL in _MODE_DEFAULTS
        assert BannerMode.COMPACT in _MODE_DEFAULTS
        assert BannerMode.HIDDEN not in _MODE_DEFAULTS


class TestBannerConfigDefaults:
    def test_default_values(self):
        cfg = BannerConfig()
        assert cfg.mode == BannerMode.FULL
        assert cfg.color == "rgba(211, 47, 47, 0.8)"
        assert cfg.text_color == "white"
        assert cfg.font_size is None
        assert cfg.font_weight is None
        assert cfg.padding is None
        assert cfg.border_radius is None
        assert cfg.show_title is True
        assert cfg.show_arrows is True
        assert cfg.show_dividers is None


class TestResolve:
    def test_full_mode_defaults(self):
        css = BannerConfig()._resolve()
        assert css is not None
        assert css["font_size"] == "1.3rem"
        assert css["font_weight"] == "bold"
        assert css["padding"] == "18px 24px"
        assert css["border_radius"] == "8px"
        assert css["show_dividers"] is True
        assert css["color"] == "rgba(211, 47, 47, 0.8)"
        assert css["text_color"] == "white"
        assert css["show_title"] is True
        assert css["show_arrows"] is True

    def test_compact_mode_defaults(self):
        css = BannerConfig(mode=BannerMode.COMPACT)._resolve()
        assert css is not None
        assert css["font_size"] == "0.8rem"
        assert css["font_weight"] == "500"
        assert css["padding"] == "5px 16px"
        assert css["border_radius"] == "4px"
        assert css["show_dividers"] is False

    def test_hidden_mode_returns_none(self):
        assert BannerConfig(mode=BannerMode.HIDDEN)._resolve() is None

    def test_explicit_override_font_size(self):
        css = BannerConfig(font_size="2rem")._resolve()
        assert css["font_size"] == "2rem"

    def test_explicit_override_padding(self):
        css = BannerConfig(mode=BannerMode.COMPACT, padding="10px 20px")._resolve()
        assert css["padding"] == "10px 20px"
        # Other compact defaults remain
        assert css["font_size"] == "0.8rem"

    def test_explicit_override_show_dividers(self):
        """Explicit show_dividers overrides mode default."""
        css = BannerConfig(mode=BannerMode.COMPACT, show_dividers=True)._resolve()
        assert css["show_dividers"] is True

    def test_explicit_override_all(self):
        cfg = BannerConfig(
            color="blue",
            text_color="yellow",
            font_size="3rem",
            font_weight="900",
            padding="50px",
            border_radius="0",
            show_title=False,
            show_arrows=False,
            show_dividers=False,
        )
        css = cfg._resolve()
        assert css["color"] == "blue"
        assert css["text_color"] == "yellow"
        assert css["font_size"] == "3rem"
        assert css["font_weight"] == "900"
        assert css["padding"] == "50px"
        assert css["border_radius"] == "0"
        assert css["show_title"] is False
        assert css["show_arrows"] is False
        assert css["show_dividers"] is False


class TestPresets:
    def test_full_preset(self):
        cfg = BannerConfig.full()
        assert cfg.mode == BannerMode.FULL
        assert cfg.color == "rgba(211, 47, 47, 0.8)"

    def test_full_preset_custom_color(self):
        cfg = BannerConfig.full(color="navy")
        assert cfg.mode == BannerMode.FULL
        assert cfg.color == "navy"

    def test_compact_preset(self):
        cfg = BannerConfig.compact()
        assert cfg.mode == BannerMode.COMPACT
        assert cfg.color == "rgba(211, 47, 47, 0.8)"

    def test_compact_preset_custom_color(self):
        cfg = BannerConfig.compact(color="#1a5276")
        assert cfg.mode == BannerMode.COMPACT
        assert cfg.color == "#1a5276"

    def test_compact_gray_preset(self):
        cfg = BannerConfig.compact_gray()
        assert cfg.mode == BannerMode.COMPACT
        assert "128" in cfg.color  # gray colour
        assert cfg.text_color == "white"

    def test_hidden_preset(self):
        cfg = BannerConfig.hidden()
        assert cfg.mode == BannerMode.HIDDEN
        assert cfg._resolve() is None


class TestBannerColorResolution:
    """Verify that the banner_color path in st_book produces correct
    BannerConfig objects (tested at the resolution level)."""

    def test_banner_color_string_becomes_config(self):
        """Simulates: st_book(modules, banner_color='blue') → BannerConfig(color='blue')."""
        cfg = BannerConfig(color="blue")
        css = cfg._resolve()
        assert css["color"] == "blue"
        # Other defaults untouched
        assert cfg.mode == BannerMode.FULL
        assert css["font_size"] == "1.3rem"

    def test_banner_param_overrides_banner_color(self):
        """When banner= is provided, banner_color is ignored."""
        explicit = BannerConfig.compact(color="navy")
        # The resolution logic in st_book uses `banner` first; we just verify the config
        assert explicit.mode == BannerMode.COMPACT
        assert explicit.color == "navy"
