"""Unit tests for streamtex.spacing — section spacing configuration."""

import warnings
from unittest.mock import patch

import pytest

from streamtex.presentation_profile import PresentationProfile
from streamtex.spacing import (
    _BUILTIN_BLOCK,
    _BUILTIN_SECTION,
    Spacing,
    SpacingConfig,
    _resolve_field,
    consume_block_top_injected,
    get_active_profile,
    get_block_spacing,
    get_section_horizontal,
    get_spacing,
    mark_block_top_injected,
    reset_block_spacing,
    resolve_block_spacing,
    resolve_section_spacing,
    set_active_profile,
    set_block_spacing,
    set_section_horizontal,
    set_spacing,
)

# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_spacing_state():
    """Reset all spacing module state before each test."""
    set_spacing(SpacingConfig())
    reset_block_spacing()
    set_active_profile(None)
    set_section_horizontal(None)
    # Reset the block_top_injected flag by consuming it if set
    consume_block_top_injected()
    yield
    set_spacing(SpacingConfig())
    reset_block_spacing()
    set_active_profile(None)
    set_section_horizontal(None)
    consume_block_top_injected()


# ── Spacing dataclass ─────────────────────────────────────────────────────

class TestSpacing:
    """Tests for the Spacing value object."""

    def test_defaults_all_none(self):
        s = Spacing()
        assert s.top is None
        assert s.bottom is None
        assert s.left is None
        assert s.right is None
        assert s.width is None

    def test_int_values(self):
        s = Spacing(top=3, bottom=0)
        assert s.top == 3
        assert s.bottom == 0

    def test_str_values(self):
        s = Spacing(top="70px", bottom="5vh")
        assert s.top == "70px"
        assert s.bottom == "5vh"

    def test_mixed_values(self):
        s = Spacing(top=3, bottom="70px", left="5%", right="2em", width=80)
        assert s.top == 3
        assert s.bottom == "70px"
        assert s.left == "5%"
        assert s.right == "2em"
        assert s.width == 80

    def test_horizontal_only(self):
        s = Spacing(left="5%", right="5%", width=60)
        assert s.top is None
        assert s.left == "5%"
        assert s.width == 60


# ── SpacingConfig dataclass ───────────────────────────────────────────────

class TestSpacingConfig:
    """Tests for the SpacingConfig bundle."""

    def test_defaults_both_none(self):
        cfg = SpacingConfig()
        assert cfg.block is None
        assert cfg.section is None

    def test_with_block_only(self):
        cfg = SpacingConfig(block=Spacing(top=3))
        assert cfg.block.top == 3
        assert cfg.section is None

    def test_with_section_only(self):
        cfg = SpacingConfig(section=Spacing(top=2))
        assert cfg.block is None
        assert cfg.section.top == 2

    def test_with_both(self):
        cfg = SpacingConfig(
            block=Spacing(top=3, bottom=0),
            section=Spacing(top=2, left="5%"),
        )
        assert cfg.block.top == 3
        assert cfg.block.bottom == 0
        assert cfg.section.top == 2
        assert cfg.section.left == "5%"


# ── Built-in defaults ─────────────────────────────────────────────────────

class TestBuiltinDefaults:
    """Tests for built-in default values."""

    def test_builtin_block_bottom_70px(self):
        assert _BUILTIN_BLOCK.bottom == "70px"

    def test_builtin_block_top_none(self):
        assert _BUILTIN_BLOCK.top is None

    def test_builtin_section_all_none(self):
        assert _BUILTIN_SECTION.top is None
        assert _BUILTIN_SECTION.bottom is None
        assert _BUILTIN_SECTION.left is None
        assert _BUILTIN_SECTION.right is None
        assert _BUILTIN_SECTION.width is None


# ── DI functions ──────────────────────────────────────────────────────────

class TestDI:
    """Tests for set/get dependency injection functions."""

    def test_set_get_spacing_roundtrip(self):
        cfg = SpacingConfig(block=Spacing(top=5))
        set_spacing(cfg)
        assert get_spacing() is cfg

    def test_default_spacing_is_empty(self):
        cfg = get_spacing()
        assert cfg.block is None
        assert cfg.section is None

    def test_set_get_block_spacing(self):
        s = Spacing(top=0, width=60)
        set_block_spacing(s)
        assert get_block_spacing() is s

    def test_reset_block_spacing(self):
        set_block_spacing(Spacing(top=1))
        reset_block_spacing()
        assert get_block_spacing() is None

    def test_set_get_active_profile(self):
        p = PresentationProfile(name="Test")
        set_active_profile(p)
        assert get_active_profile() is p

    def test_active_profile_default_none(self):
        assert get_active_profile() is None


# ── Double-spacing flag ───────────────────────────────────────────────────

class TestBlockTopFlag:
    """Tests for the block_top_injected flag."""

    def test_consume_without_mark_returns_false(self):
        assert consume_block_top_injected() is False

    def test_mark_then_consume_returns_true(self):
        mark_block_top_injected()
        assert consume_block_top_injected() is True

    def test_consume_resets_flag(self):
        mark_block_top_injected()
        consume_block_top_injected()
        assert consume_block_top_injected() is False

    def test_double_mark_single_consume(self):
        mark_block_top_injected()
        mark_block_top_injected()
        assert consume_block_top_injected() is True
        assert consume_block_top_injected() is False


# ── Section horizontal state ──────────────────────────────────────────────

class TestSectionHorizontal:
    """Tests for section-level horizontal spacing state."""

    def test_default_none(self):
        assert get_section_horizontal() is None

    def test_set_spacing(self):
        s = Spacing(left="15%", right="15%")
        set_section_horizontal(s)
        assert get_section_horizontal() is s

    def test_clear(self):
        set_section_horizontal(Spacing(left="10%"))
        set_section_horizontal(None)
        assert get_section_horizontal() is None


# ── _resolve_field ─────────────────────────────────────────────────────────

class TestResolveField:
    """Tests for the _resolve_field helper."""

    def test_first_non_none(self):
        assert _resolve_field(None, None, 3) == 3

    def test_first_wins(self):
        assert _resolve_field(1, 2, 3) == 1

    def test_all_none(self):
        assert _resolve_field(None, None) is None

    def test_zero_is_not_none(self):
        assert _resolve_field(0, 5) == 0

    def test_empty_string_is_not_none(self):
        assert _resolve_field("", "5px") == ""

    def test_single_value(self):
        assert _resolve_field(42) == 42


# ── resolve_block_spacing ─────────────────────────────────────────────────

class TestResolveBlockSpacing:
    """Tests for block spacing resolution (3 levels)."""

    def test_no_config_returns_builtin(self):
        result = resolve_block_spacing()
        assert result.bottom == "70px"
        assert result.top is None

    def test_global_overrides_builtin(self):
        set_spacing(SpacingConfig(block=Spacing(top=3, bottom="50px")))
        result = resolve_block_spacing()
        assert result.top == 3
        assert result.bottom == "50px"

    def test_global_partial_inherits_builtin(self):
        set_spacing(SpacingConfig(block=Spacing(top=3)))
        result = resolve_block_spacing()
        assert result.top == 3
        assert result.bottom == "70px"  # from builtin

    def test_profile_overrides_global(self):
        set_spacing(SpacingConfig(block=Spacing(top=3, bottom="50px")))
        profile = PresentationProfile(
            name="Test",
            spacing=SpacingConfig(block=Spacing(top=0)),
        )
        result = resolve_block_spacing(profile=profile)
        assert result.top == 0
        assert result.bottom == "50px"  # from global (profile didn't set bottom)

    def test_profile_overrides_all(self):
        set_spacing(SpacingConfig(block=Spacing(top=3, bottom="50px")))
        profile = PresentationProfile(
            name="Test",
            spacing=SpacingConfig(block=Spacing(top=0, bottom="20px")),
        )
        result = resolve_block_spacing(profile=profile)
        assert result.top == 0
        assert result.bottom == "20px"

    def test_profile_without_spacing(self):
        set_spacing(SpacingConfig(block=Spacing(top=3)))
        profile = PresentationProfile(name="Test")
        result = resolve_block_spacing(profile=profile)
        assert result.top == 3

    def test_horizontal_fields(self):
        set_spacing(SpacingConfig(block=Spacing(left="5%", right="5%", width=80)))
        result = resolve_block_spacing()
        assert result.left == "5%"
        assert result.right == "5%"
        assert result.width == 80


# ── resolve_section_spacing ───────────────────────────────────────────────

class TestResolveSectionSpacing:
    """Tests for section spacing resolution (5 levels)."""

    def test_no_config_returns_builtin(self):
        result = resolve_section_spacing()
        assert result.top is None
        assert result.bottom is None

    def test_global_section(self):
        set_spacing(SpacingConfig(section=Spacing(top=2)))
        result = resolve_section_spacing()
        assert result.top == 2

    def test_profile_overrides_global(self):
        set_spacing(SpacingConfig(section=Spacing(top=2)))
        profile = PresentationProfile(
            name="Test",
            spacing=SpacingConfig(section=Spacing(top=1)),
        )
        result = resolve_section_spacing(profile=profile)
        assert result.top == 1

    def test_block_override_overrides_profile(self):
        set_spacing(SpacingConfig(section=Spacing(top=2)))
        profile = PresentationProfile(
            name="Test",
            spacing=SpacingConfig(section=Spacing(top=1)),
        )
        set_active_profile(profile)
        set_block_spacing(Spacing(top=0))
        result = resolve_section_spacing()
        assert result.top == 0

    def test_call_site_overrides_all(self):
        set_spacing(SpacingConfig(section=Spacing(top=2)))
        set_block_spacing(Spacing(top=0))
        result = resolve_section_spacing(call_site=Spacing(top=4))
        assert result.top == 4

    def test_partial_override_inherits(self):
        set_spacing(SpacingConfig(section=Spacing(top=2, bottom=1)))
        result = resolve_section_spacing(call_site=Spacing(top=4))
        assert result.top == 4
        assert result.bottom == 1  # inherited from global

    def test_active_profile_used_when_no_explicit_profile(self):
        profile = PresentationProfile(
            name="Test",
            spacing=SpacingConfig(section=Spacing(top=7)),
        )
        set_active_profile(profile)
        result = resolve_section_spacing()
        assert result.top == 7

    def test_explicit_profile_overrides_active(self):
        active = PresentationProfile(
            name="Active",
            spacing=SpacingConfig(section=Spacing(top=7)),
        )
        explicit = PresentationProfile(
            name="Explicit",
            spacing=SpacingConfig(section=Spacing(top=3)),
        )
        set_active_profile(active)
        result = resolve_section_spacing(profile=explicit)
        assert result.top == 3

    def test_all_five_levels(self):
        """Verify that level 5 > level 4 > level 3 > level 2 > level 1."""
        set_spacing(SpacingConfig(section=Spacing(top=10, bottom=10, left="10%", right="10%", width=10)))
        profile = PresentationProfile(
            name="P",
            spacing=SpacingConfig(section=Spacing(bottom=20, left="20%", right="20%", width=20)),
        )
        set_active_profile(profile)
        set_block_spacing(Spacing(left="30%", right="30%", width=30))
        result = resolve_section_spacing(call_site=Spacing(right="40%", width=40))
        assert result.top == 10       # L2 (global, no override above)
        assert result.bottom == 20    # L3 (profile)
        assert result.left == "30%"   # L4 (block)
        assert result.right == "40%"  # L5 (call_site)
        assert result.width == 40     # L5 (call_site)

    def test_horizontal_section_spacing(self):
        set_spacing(SpacingConfig(section=Spacing(left="5%", width=60)))
        result = resolve_section_spacing()
        assert result.left == "5%"
        assert result.width == 60


# ── SlideBreakConfig spacing field ────────────────────────────────────────

class TestSlideBreakConfigSpacing:
    """Tests for the spacing field on SlideBreakConfig."""

    def test_default_spacing_none(self):
        from streamtex.slide import SlideBreakConfig
        cfg = SlideBreakConfig()
        assert cfg.spacing is None

    def test_custom_spacing(self):
        from streamtex.slide import SlideBreakConfig
        s = Spacing(top=4)
        cfg = SlideBreakConfig(spacing=s)
        assert cfg.spacing is s


# ── st_slide_break spacing integration ────────────────────────────────────

class TestStSlideBreakSpacing:
    """Tests for section spacing injection in st_slide_break."""

    def test_spacing_top_injected_after_break(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        set_spacing(SpacingConfig(section=Spacing(top=3)))
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space") as mock_space:
            st_slide_break(config=SlideBreakConfig(mode=SlideBreakMode.FULL))
            # st_space should be called with section.top
            space_calls = [c for c in mock_space.call_args_list if c[0] == ("v", 3)]
            assert len(space_calls) >= 1

    def test_spacing_top_skipped_when_block_top_injected(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        set_spacing(SpacingConfig(section=Spacing(top=3)))
        mark_block_top_injected()
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space") as mock_space:
            st_slide_break(config=SlideBreakConfig(mode=SlideBreakMode.FULL))
            # section.top should NOT be injected (block.top already done)
            space_calls = [c for c in mock_space.call_args_list if c[0] == ("v", 3)]
            assert len(space_calls) == 0

    def test_spacing_bottom_injected_before_break(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        set_spacing(SpacingConfig(section=Spacing(bottom=1)))
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space") as mock_space:
            st_slide_break(config=SlideBreakConfig(mode=SlideBreakMode.FULL))
            space_calls = [c for c in mock_space.call_args_list if c[0] == ("v", 1)]
            assert len(space_calls) >= 1

    def test_direct_spacing_param_overrides_config(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        set_spacing(SpacingConfig(section=Spacing(top=10)))
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space") as mock_space:
            st_slide_break(
                config=SlideBreakConfig(mode=SlideBreakMode.FULL, spacing=Spacing(top=5)),
                spacing=Spacing(top=99),
            )
            # Direct spacing= should win (top=99)
            space_calls = [c for c in mock_space.call_args_list if c[0] == ("v", 99)]
            assert len(space_calls) >= 1

    def test_no_spacing_no_extra_st_space(self):
        """When no spacing is configured, no extra st_space calls."""
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space") as mock_space:
            st_slide_break(config=SlideBreakConfig(mode=SlideBreakMode.FULL))
            assert mock_space.call_count == 0


# ── st_write spacing integration ──────────────────────────────────────────

class TestStWriteSpacing:
    """Tests for spacing param on st_write."""

    def test_spacing_without_toc_lvl_warns(self):
        from streamtex.styles import StxStyles
        from streamtex.write import st_write

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            st_write(StxStyles.none, "test", spacing=Spacing(top=2))
            assert len(w) == 1
            assert "toc_lvl" in str(w[0].message)

    def test_spacing_with_toc_lvl_no_warning(self):
        from streamtex.styles import StxStyles
        from streamtex.write import st_write

        with patch("streamtex.write._render"), \
             patch("streamtex.write.register_toc_entry", return_value=("anchor", "", 1)), \
             patch("streamtex.write.get_marker_config", return_value=None):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                st_write(StxStyles.none, "test", toc_lvl="1", spacing=Spacing(top=2))
                assert len(w) == 0


# ── PresentationProfile spacing field ─────────────────────────────────────

class TestPresentationProfileSpacing:
    """Tests for the spacing field on PresentationProfile."""

    def test_default_spacing_none(self):
        p = PresentationProfile(name="Test")
        assert p.spacing is None

    def test_custom_spacing(self):
        cfg = SpacingConfig(block=Spacing(top=3), section=Spacing(top=2))
        p = PresentationProfile(name="Test", spacing=cfg)
        assert p.spacing is cfg
        assert p.spacing.block.top == 3
        assert p.spacing.section.top == 2

    def test_profile_presets_no_spacing(self):
        """Existing presets should still work (spacing=None by default)."""
        for p in PresentationProfile.responsive_preset():
            assert p.spacing is None
        for p in PresentationProfile.presentation_preset():
            assert p.spacing is None
        for p in PresentationProfile.desktop_mobile_preset():
            assert p.spacing is None


# ── Regression: 70px default preservation ─────────────────────────────────

class TestRegressionDefaults:
    """Ensure backward compatibility — no config = same as before."""

    def test_default_block_bottom_is_70px(self):
        """Without any SpacingConfig, block.bottom must be '70px'."""
        result = resolve_block_spacing()
        assert result.bottom == "70px"

    def test_default_section_no_spacing(self):
        """Without any SpacingConfig, no section spacing is injected."""
        result = resolve_section_spacing()
        assert result.top is None
        assert result.bottom is None
        assert result.left is None
        assert result.right is None
        assert result.width is None
