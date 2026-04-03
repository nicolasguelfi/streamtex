"""Unit tests for per-block / per-section zoom feature."""

from unittest.mock import patch

import pytest

from streamtex.presentation_profile import PresentationProfile
from streamtex.spacing import (
    Spacing,
    SpacingConfig,
    consume_block_top_injected,
    get_section_horizontal,
    get_section_zoom,
    reset_block_spacing,
    resolve_block_spacing,
    resolve_section_spacing,
    set_active_profile,
    set_block_spacing,
    set_section_horizontal,
    set_section_zoom,
    set_spacing,
)

# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_state():
    """Reset all spacing module state before each test."""
    set_spacing(SpacingConfig())
    reset_block_spacing()
    set_active_profile(None)
    set_section_horizontal(None)
    set_section_zoom(None)
    consume_block_top_injected()
    yield
    set_spacing(SpacingConfig())
    reset_block_spacing()
    set_active_profile(None)
    set_section_horizontal(None)
    set_section_zoom(None)
    consume_block_top_injected()


# ── Spacing.zoom dataclass field ─────────────────────────────────────────


class TestSpacingZoomField:
    """Tests for the zoom field on Spacing."""

    def test_default_none(self):
        s = Spacing()
        assert s.zoom is None

    def test_explicit_value(self):
        s = Spacing(zoom=75)
        assert s.zoom == 75

    def test_mixed_with_other_fields(self):
        s = Spacing(top=3, left="5%", zoom=120)
        assert s.top == 3
        assert s.left == "5%"
        assert s.zoom == 120


# ── Section zoom DI ──────────────────────────────────────────────────────


class TestSectionZoomDI:
    """Tests for set/get section zoom state."""

    def test_default_none(self):
        assert get_section_zoom() is None

    def test_set_zoom(self):
        set_section_zoom(80)
        assert get_section_zoom() == 80

    def test_clear_zoom(self):
        set_section_zoom(120)
        set_section_zoom(None)
        assert get_section_zoom() is None


# ── resolve_block_spacing with zoom ──────────────────────────────────────


class TestResolveBlockSpacingZoom:
    """Tests for zoom in block spacing resolution."""

    def test_no_config_zoom_none(self):
        result = resolve_block_spacing()
        assert result.zoom is None

    def test_global_zoom(self):
        set_spacing(SpacingConfig(block=Spacing(zoom=80)))
        result = resolve_block_spacing()
        assert result.zoom == 80

    def test_profile_overrides_global_zoom(self):
        set_spacing(SpacingConfig(block=Spacing(zoom=80)))
        profile = PresentationProfile(
            name="Test",
            spacing=SpacingConfig(block=Spacing(zoom=60)),
        )
        result = resolve_block_spacing(profile=profile)
        assert result.zoom == 60

    def test_profile_without_zoom_inherits_global(self):
        set_spacing(SpacingConfig(block=Spacing(zoom=80)))
        profile = PresentationProfile(name="Test")
        result = resolve_block_spacing(profile=profile)
        assert result.zoom == 80


# ── resolve_section_spacing with zoom ────────────────────────────────────


class TestResolveSectionSpacingZoom:
    """Tests for zoom in section spacing resolution (5 levels)."""

    def test_no_config_zoom_none(self):
        result = resolve_section_spacing()
        assert result.zoom is None

    def test_global_section_zoom(self):
        set_spacing(SpacingConfig(section=Spacing(zoom=75)))
        result = resolve_section_spacing()
        assert result.zoom == 75

    def test_call_site_overrides_all(self):
        set_spacing(SpacingConfig(section=Spacing(zoom=75)))
        result = resolve_section_spacing(call_site=Spacing(zoom=150))
        assert result.zoom == 150

    def test_block_override_zoom(self):
        set_spacing(SpacingConfig(section=Spacing(zoom=75)))
        set_block_spacing(Spacing(zoom=90))
        result = resolve_section_spacing()
        assert result.zoom == 90

    def test_five_level_zoom_hierarchy(self):
        set_spacing(SpacingConfig(section=Spacing(zoom=50)))
        profile = PresentationProfile(
            name="P",
            spacing=SpacingConfig(section=Spacing(zoom=60)),
        )
        set_active_profile(profile)
        set_block_spacing(Spacing(zoom=70))
        result = resolve_section_spacing(call_site=Spacing(zoom=80))
        assert result.zoom == 80  # call-site wins


# ── _inject_block_horizontal_css with zoom ───────────────────────────────


class TestInjectBlockZoomCSS:
    """Tests for zoom in block-level CSS injection."""

    def test_zoom_injected_in_css(self):
        from streamtex.book import _inject_block_horizontal_css

        with patch("streamtex.book.st") as mock_st:
            _inject_block_horizontal_css(Spacing(zoom=75))
            css = mock_st.html.call_args[0][0]
            assert "zoom: 0.75" in css

    def test_no_zoom_no_css(self):
        from streamtex.book import _inject_block_horizontal_css

        with patch("streamtex.book.st") as mock_st:
            _inject_block_horizontal_css(Spacing())
            mock_st.html.assert_not_called()

    def test_zoom_200_percent(self):
        from streamtex.book import _inject_block_horizontal_css

        with patch("streamtex.book.st") as mock_st:
            _inject_block_horizontal_css(Spacing(zoom=200))
            css = mock_st.html.call_args[0][0]
            assert "zoom: 2.0" in css

    def test_zoom_combined_with_width(self):
        from streamtex.book import _inject_block_horizontal_css

        with patch("streamtex.book.st") as mock_st:
            _inject_block_horizontal_css(Spacing(width=80, zoom=75))
            css = mock_st.html.call_args[0][0]
            assert "width: 80%" in css
            assert "zoom: 0.75" in css


# ── st_html section zoom wrapping ────────────────────────────────────────


class TestRenderZoomWrapping:
    """Tests for zoom wrapping in st_html/_render."""

    def test_no_zoom_no_wrap(self):
        from streamtex.export import st_html

        with patch("streamtex.export.st.html") as mock_st_html:
            st_html("<p>test</p>")
            html = mock_st_html.call_args[0][0]
            assert "zoom" not in html

    def test_section_zoom_wraps(self):
        from streamtex.export import st_html

        set_section_zoom(80)
        with patch("streamtex.export.st.html") as mock_st_html:
            st_html("<p>test</p>")
            html = mock_st_html.call_args[0][0]
            assert "zoom: 0.8" in html
            assert "<p>test</p>" in html

    def test_section_zoom_with_horizontal(self):
        from streamtex.export import st_html

        set_section_horizontal(Spacing(left="10%"))
        set_section_zoom(120)
        with patch("streamtex.export.st.html") as mock_st_html:
            st_html("<p>test</p>")
            html = mock_st_html.call_args[0][0]
            assert "margin-left: 10%" in html
            assert "zoom: 1.2" in html


# ── st_slide_break zoom parameter ───────────────────────────────────────


class TestSlideBreakZoomParam:
    """Tests for the zoom= shortcut on st_slide_break."""

    def test_zoom_activates_section_zoom(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space"):
            st_slide_break(
                config=SlideBreakConfig(mode=SlideBreakMode.FULL),
                zoom=75,
            )

        assert get_section_zoom() == 75

    def test_zoom_overrides_spacing_zoom(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space"):
            st_slide_break(
                config=SlideBreakConfig(mode=SlideBreakMode.FULL),
                spacing=Spacing(zoom=50),
                zoom=75,
            )

        # zoom= param wins over spacing.zoom
        assert get_section_zoom() == 75

    def test_slide_break_clears_previous_zoom(self):
        set_section_zoom(120)
        assert get_section_zoom() == 120

        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space"):
            st_slide_break(config=SlideBreakConfig(mode=SlideBreakMode.FULL))

        # No zoom on this break, so section zoom should be cleared
        assert get_section_zoom() is None

    def test_zoom_preserves_spacing_fields(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break

        set_spacing(SpacingConfig(section=Spacing(left="10%")))
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker"), \
             patch("streamtex.space.st_space"):
            st_slide_break(
                config=SlideBreakConfig(mode=SlideBreakMode.FULL),
                zoom=80,
            )

        # Horizontal from global section spacing should still be active
        sh = get_section_horizontal()
        assert sh is not None
        assert sh.left == "10%"
        # And zoom should be active
        assert get_section_zoom() == 80


# ── st_zoom context manager ──────────────────────────────────────────────


class TestStZoomContextManager:
    """Tests for the st_zoom() context manager."""

    def test_injects_zoom_css(self):
        from streamtex.zoom import st_zoom

        with patch("streamtex.zoom.st.container") as mock_ct, \
             patch("streamtex.zoom.st.html") as mock_html:
            mock_ct.return_value.__enter__ = lambda s: None
            mock_ct.return_value.__exit__ = lambda s, *a: False
            with st_zoom(75):
                pass
            css = mock_html.call_args[0][0]
            assert "zoom: 0.75" in css

    def test_default_100_no_visible_change(self):
        from streamtex.zoom import st_zoom

        with patch("streamtex.zoom.st.container") as mock_ct, \
             patch("streamtex.zoom.st.html") as mock_html:
            mock_ct.return_value.__enter__ = lambda s: None
            mock_ct.return_value.__exit__ = lambda s, *a: False
            with st_zoom(100):
                pass
            css = mock_html.call_args[0][0]
            assert "zoom: 1.0" in css

    def test_zoom_200(self):
        from streamtex.zoom import st_zoom

        with patch("streamtex.zoom.st.container") as mock_ct, \
             patch("streamtex.zoom.st.html") as mock_html:
            mock_ct.return_value.__enter__ = lambda s: None
            mock_ct.return_value.__exit__ = lambda s, *a: False
            with st_zoom(200):
                pass
            css = mock_html.call_args[0][0]
            assert "zoom: 2.0" in css

    def test_export_wrapper(self):
        from streamtex.zoom import st_zoom

        with patch("streamtex.zoom.st.container") as mock_ct, \
             patch("streamtex.zoom.st.html"), \
             patch("streamtex.zoom.is_export_active", return_value=True), \
             patch("streamtex.zoom.export_push_wrapper") as mock_push, \
             patch("streamtex.zoom.export_pop_wrapper") as mock_pop:
            mock_ct.return_value.__enter__ = lambda s: None
            mock_ct.return_value.__exit__ = lambda s, *a: False
            with st_zoom(50):
                pass
            mock_push.assert_called_once()
            assert "zoom: 0.5" in mock_push.call_args[0][0]
            mock_pop.assert_called_once_with("</div>")

    def test_no_export_wrapper_when_inactive(self):
        from streamtex.zoom import st_zoom

        with patch("streamtex.zoom.st.container") as mock_ct, \
             patch("streamtex.zoom.st.html"), \
             patch("streamtex.zoom.is_export_active", return_value=False), \
             patch("streamtex.zoom.export_push_wrapper") as mock_push, \
             patch("streamtex.zoom.export_pop_wrapper") as mock_pop:
            mock_ct.return_value.__enter__ = lambda s: None
            mock_ct.return_value.__exit__ = lambda s, *a: False
            with st_zoom(50):
                pass
            mock_push.assert_not_called()
            mock_pop.assert_not_called()
