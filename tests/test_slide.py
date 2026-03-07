"""Unit tests for streamtex.slide — presentation-mode slide breaks."""

from unittest.mock import patch

from streamtex.slide import (
    SlideBreakConfig,
    get_slide_break_config,
    set_slide_break_config,
    st_slide_break,
)


class TestSlideBreakConfig:
    """Tests for SlideBreakConfig dataclass."""

    def test_defaults(self):
        cfg = SlideBreakConfig()
        assert cfg.space == "60vh"
        assert cfg.thickness == "1px"
        assert cfg.color == "128, 128, 128"
        assert cfg.opacity == 0.3
        assert cfg.marker is True

    def test_custom_values(self):
        cfg = SlideBreakConfig(space="80vh", thickness="2px", color="79, 172, 254", opacity=0.5, marker=False)
        assert cfg.space == "80vh"
        assert cfg.thickness == "2px"
        assert cfg.color == "79, 172, 254"
        assert cfg.opacity == 0.5
        assert cfg.marker is False


class TestGlobalConfig:
    """Tests for set/get global config."""

    def test_set_and_get(self):
        original = get_slide_break_config()
        custom = SlideBreakConfig(space="50vh")
        set_slide_break_config(custom)
        assert get_slide_break_config() is custom
        # Restore
        set_slide_break_config(original)


class TestStSlideBreak:
    """Tests for st_slide_break rendering."""

    def test_renders_rule_with_css_class(self):
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break()
            rule_call = mock_render.call_args_list[0][0][0]
            assert 'class="stx-slide-break-rule"' in rule_call
            assert "<hr" in rule_call

    def test_renders_spacer_with_css_class(self):
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break()
            spacer_call = mock_render.call_args_list[1][0][0]
            assert 'class="stx-slide-break-spacer"' in spacer_call
            assert "60vh" in spacer_call

    def test_renders_hidden_marker_by_default(self):
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break()
            mock_marker.assert_called_once()
            _, kwargs = mock_marker.call_args
            assert kwargs.get("hidden") is True

    def test_no_marker_when_disabled(self):
        cfg = SlideBreakConfig(marker=False)
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break(config=cfg)
            mock_marker.assert_not_called()

    def test_custom_config_applies(self):
        cfg = SlideBreakConfig(space="50vh", thickness="3px", color="255, 0, 0", opacity=0.8)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            rule_call = mock_render.call_args_list[0][0][0]
            assert "3px" in rule_call
            assert "255, 0, 0" in rule_call
            assert "0.8" in rule_call
            spacer_call = mock_render.call_args_list[1][0][0]
            assert "50vh" in spacer_call

    def test_render_called_twice(self):
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break()
            assert mock_render.call_count == 2

    def test_marker_label_passed(self):
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break(marker_label="Section 2")
            mock_marker.assert_called_once_with("Section 2", hidden=True)
