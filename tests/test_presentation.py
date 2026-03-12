"""Unit tests for streamtex.presentation — fullscreen 16/9 presentation mode."""

from unittest.mock import MagicMock, patch

from streamtex.presentation import (
    _PRES_FOOTER_KEY,
    _PRES_FULLSCREEN_KEY,
    _PRESENTATION_CONFIG_KEY,
    PresentationConfig,
    _inject_presentation_css,
    add_presentation_options,
    get_presentation_config,
    set_presentation_config,
    st_presentation_footer,
)

# ── PresentationConfig dataclass ──────────────────────────────────────────


class TestPresentationConfig:
    """Tests for PresentationConfig defaults and custom values."""

    def test_defaults(self):
        cfg = PresentationConfig()
        assert cfg.title == ""
        assert cfg.subtitle == ""
        assert cfg.aspect_ratio == "16/9"
        assert cfg.enforce_ratio is True
        assert cfg.footer is True
        assert cfg.footer_height == "48px"
        assert cfg.footer_bg is None
        assert cfg.footer_text_color is None
        assert cfg.footer_font_size == "18px"
        assert cfg.center_content is True
        assert cfg.content_padding == "48px 64px"
        assert cfg.hide_streamlit_header is True
        assert cfg.hide_streamlit_footer is True
        assert cfg.hide_deploy_button is True
        assert cfg.sidebar_default == "collapsed"
        assert cfg.slide_transition == "none"
        assert cfg.transition_duration == "0.3s"

    def test_custom_title(self):
        cfg = PresentationConfig(title="My Talk")
        assert cfg.title == "My Talk"

    def test_custom_aspect_ratio(self):
        cfg = PresentationConfig(aspect_ratio="4/3")
        assert cfg.aspect_ratio == "4/3"

    def test_custom_footer_disabled(self):
        cfg = PresentationConfig(footer=False)
        assert cfg.footer is False

    def test_custom_footer_styling(self):
        cfg = PresentationConfig(
            footer_bg="#111", footer_text_color="#eee", footer_font_size="14px"
        )
        assert cfg.footer_bg == "#111"
        assert cfg.footer_text_color == "#eee"
        assert cfg.footer_font_size == "14px"

    def test_no_centering(self):
        cfg = PresentationConfig(center_content=False)
        assert cfg.center_content is False

    def test_no_ratio_enforcement(self):
        cfg = PresentationConfig(enforce_ratio=False)
        assert cfg.enforce_ratio is False

    def test_custom_padding(self):
        cfg = PresentationConfig(content_padding="24px 32px")
        assert cfg.content_padding == "24px 32px"

    def test_streamlit_ui_flags(self):
        cfg = PresentationConfig(
            hide_streamlit_header=False,
            hide_streamlit_footer=False,
            hide_deploy_button=False,
        )
        assert cfg.hide_streamlit_header is False
        assert cfg.hide_streamlit_footer is False
        assert cfg.hide_deploy_button is False

    def test_transition_fade(self):
        cfg = PresentationConfig(slide_transition="fade", transition_duration="0.5s")
        assert cfg.slide_transition == "fade"
        assert cfg.transition_duration == "0.5s"

    def test_sidebar_default_expanded(self):
        cfg = PresentationConfig(sidebar_default="expanded")
        assert cfg.sidebar_default == "expanded"

    def test_subtitle(self):
        cfg = PresentationConfig(subtitle="A deep dive")
        assert cfg.subtitle == "A deep dive"

    def test_footer_height_custom(self):
        cfg = PresentationConfig(footer_height="60px")
        assert cfg.footer_height == "60px"

    def test_16_10_ratio(self):
        cfg = PresentationConfig(aspect_ratio="16/10")
        assert cfg.aspect_ratio == "16/10"


# ── DI pattern (set/get) ─────────────────────────────────────────────────


class TestDIPattern:
    """Tests for set/get_presentation_config DI."""

    @patch("streamtex.presentation.st")
    def test_set_stores_in_session_state(self, mock_st):
        mock_st.session_state = {}
        mock_st.html = MagicMock()
        cfg = PresentationConfig(title="Test")
        set_presentation_config(cfg)
        assert mock_st.session_state[_PRESENTATION_CONFIG_KEY] is cfg

    @patch("streamtex.presentation.st")
    def test_get_returns_none_when_not_set(self, mock_st):
        mock_st.session_state = {}
        assert get_presentation_config() is None

    @patch("streamtex.presentation.st")
    def test_get_returns_config_when_set(self, mock_st):
        cfg = PresentationConfig(title="Get Test")
        mock_st.session_state = {_PRESENTATION_CONFIG_KEY: cfg}
        assert get_presentation_config() is cfg

    @patch("streamtex.presentation.st")
    def test_set_calls_inject_css(self, mock_st):
        mock_st.session_state = {}
        mock_st.html = MagicMock()
        cfg = PresentationConfig()
        set_presentation_config(cfg)
        mock_st.html.assert_called_once()

    @patch("streamtex.presentation.st")
    def test_set_overwrites_previous(self, mock_st):
        mock_st.session_state = {}
        mock_st.html = MagicMock()
        cfg1 = PresentationConfig(title="First")
        cfg2 = PresentationConfig(title="Second")
        set_presentation_config(cfg1)
        set_presentation_config(cfg2)
        assert mock_st.session_state[_PRESENTATION_CONFIG_KEY] is cfg2


# ── CSS injection ────────────────────────────────────────────────────────


class TestCSSInjection:
    """Tests for _inject_presentation_css."""

    @patch("streamtex.presentation.st")
    def test_hides_header(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(hide_streamlit_header=True))
        css = mock_st.html.call_args[0][0]
        assert "stHeader" in css
        assert "display: none" in css

    @patch("streamtex.presentation.st")
    def test_does_not_hide_header_when_disabled(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(
            hide_streamlit_header=False,
            hide_streamlit_footer=False,
            hide_deploy_button=False,
        ))
        css = mock_st.html.call_args[0][0]
        assert "stHeader" not in css

    @patch("streamtex.presentation.st")
    def test_hides_footer(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(hide_streamlit_footer=True))
        css = mock_st.html.call_args[0][0]
        assert "footer { display: none" in css

    @patch("streamtex.presentation.st")
    def test_hides_deploy_button(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(hide_deploy_button=True))
        css = mock_st.html.call_args[0][0]
        assert "stDeployButton" in css

    @patch("streamtex.presentation.st")
    def test_aspect_ratio_enforced(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(enforce_ratio=True))
        css = mock_st.html.call_args[0][0]
        assert "100vw" in css
        assert "100vh" in css
        assert "overflow: hidden" in css

    @patch("streamtex.presentation.st")
    def test_no_aspect_ratio_when_disabled(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(
            enforce_ratio=False,
            hide_streamlit_header=False,
            hide_streamlit_footer=False,
            hide_deploy_button=False,
        ))
        css = mock_st.html.call_args[0][0]
        assert "overflow: hidden" not in css

    @patch("streamtex.presentation.st")
    def test_centering_css(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(center_content=True))
        css = mock_st.html.call_args[0][0]
        assert "justify-content: center" in css

    @patch("streamtex.presentation.st")
    def test_no_centering_when_disabled(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(
            center_content=False,
            hide_streamlit_header=False,
            hide_streamlit_footer=False,
            hide_deploy_button=False,
            enforce_ratio=False,
            footer=False,
        ))
        if mock_st.html.called:
            css = mock_st.html.call_args[0][0]
            assert "justify-content" not in css
        # If not called at all, centering CSS is definitely not present

    @patch("streamtex.presentation.st")
    def test_footer_css_generated(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(footer=True))
        css = mock_st.html.call_args[0][0]
        assert "stx-presentation-footer" in css
        assert "position: fixed" in css
        assert "z-index: 999" in css

    @patch("streamtex.presentation.st")
    def test_footer_custom_bg(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(footer=True, footer_bg="#222"))
        css = mock_st.html.call_args[0][0]
        assert "#222" in css

    @patch("streamtex.presentation.st")
    def test_footer_custom_text_color(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(
            PresentationConfig(footer=True, footer_text_color="#ccc")
        )
        css = mock_st.html.call_args[0][0]
        assert "#ccc" in css

    @patch("streamtex.presentation.st")
    def test_footer_font_size(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(
            PresentationConfig(footer=True, footer_font_size="20px")
        )
        css = mock_st.html.call_args[0][0]
        assert "20px" in css

    @patch("streamtex.presentation.st")
    def test_footer_height_in_css(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(
            PresentationConfig(footer=True, footer_height="60px")
        )
        css = mock_st.html.call_args[0][0]
        assert "60px" in css

    @patch("streamtex.presentation.st")
    def test_content_padding(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(
            PresentationConfig(enforce_ratio=True, content_padding="24px 32px")
        )
        css = mock_st.html.call_args[0][0]
        assert "24px 32px" in css

    @patch("streamtex.presentation.st")
    def test_padding_bottom_when_footer(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(footer=True))
        css = mock_st.html.call_args[0][0]
        assert "padding-bottom" in css

    @patch("streamtex.presentation.st")
    def test_no_footer_css_when_disabled(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(
            footer=False,
            hide_streamlit_header=False,
            hide_streamlit_footer=False,
            hide_deploy_button=False,
            enforce_ratio=False,
            center_content=False,
        ))
        # Should have no CSS to inject, or minimal
        if mock_st.html.called:
            css = mock_st.html.call_args[0][0]
            assert "stx-presentation-footer" not in css

    @patch("streamtex.presentation.st")
    def test_transition_css_when_enabled(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(
            PresentationConfig(slide_transition="fade", transition_duration="0.5s")
        )
        css = mock_st.html.call_args[0][0]
        assert "0.5s" in css
        assert "ease-in-out" in css

    @patch("streamtex.presentation.st")
    def test_no_transition_css_when_none(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(
            slide_transition="none",
            hide_streamlit_header=False,
            hide_streamlit_footer=False,
            hide_deploy_button=False,
            enforce_ratio=False,
            center_content=False,
            footer=False,
        ))
        if mock_st.html.called:
            css = mock_st.html.call_args[0][0]
            assert "transition" not in css

    @patch("streamtex.presentation.st")
    def test_default_footer_uses_css_vars(self, mock_st):
        mock_st.html = MagicMock()
        _inject_presentation_css(PresentationConfig(footer=True))
        css = mock_st.html.call_args[0][0]
        assert "var(--background-color" in css
        assert "var(--text-color" in css


# ── st_presentation_footer ───────────────────────────────────────────────


class TestFooterRendering:
    """Tests for st_presentation_footer."""

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_renders_counter(self, mock_get, mock_render):
        mock_get.return_value = PresentationConfig(footer=True)
        st_presentation_footer(current_slide=3, total_slides=10)
        html = mock_render.call_args[0][0]
        assert "Slide 3 / 10" in html

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_renders_title(self, mock_get, mock_render):
        mock_get.return_value = PresentationConfig(title="Docker Talk", footer=True)
        st_presentation_footer(current_slide=1, total_slides=5)
        html = mock_render.call_args[0][0]
        assert "Docker Talk" in html
        assert "stx-pf-title" in html

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_no_title_when_empty(self, mock_get, mock_render):
        mock_get.return_value = PresentationConfig(title="", footer=True)
        st_presentation_footer(current_slide=1, total_slides=5)
        html = mock_render.call_args[0][0]
        assert "stx-pf-title" not in html

    @patch("streamtex.presentation._render")
    def test_explicit_title_overrides_config(self, mock_render):
        cfg = PresentationConfig(title="Config Title", footer=True)
        st_presentation_footer(
            current_slide=1, total_slides=5, title="Override", config=cfg
        )
        html = mock_render.call_args[0][0]
        assert "Override" in html

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_no_render_when_footer_disabled(self, mock_get, mock_render):
        mock_get.return_value = PresentationConfig(footer=False)
        st_presentation_footer(current_slide=1, total_slides=5)
        mock_render.assert_not_called()

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_no_render_when_no_config(self, mock_get, mock_render):
        mock_get.return_value = None
        st_presentation_footer(current_slide=1, total_slides=5)
        mock_render.assert_not_called()

    @patch("streamtex.presentation._render")
    def test_explicit_config(self, mock_render):
        cfg = PresentationConfig(title="Explicit", footer=True)
        st_presentation_footer(current_slide=2, total_slides=8, config=cfg)
        html = mock_render.call_args[0][0]
        assert "Slide 2 / 8" in html
        assert "Explicit" in html

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_footer_css_class(self, mock_get, mock_render):
        mock_get.return_value = PresentationConfig(footer=True)
        st_presentation_footer(current_slide=1, total_slides=1)
        html = mock_render.call_args[0][0]
        assert "stx-presentation-footer" in html

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_counter_css_class(self, mock_get, mock_render):
        mock_get.return_value = PresentationConfig(footer=True)
        st_presentation_footer(current_slide=1, total_slides=1)
        html = mock_render.call_args[0][0]
        assert "stx-pf-counter" in html

    @patch("streamtex.presentation._render")
    @patch("streamtex.presentation.get_presentation_config")
    def test_single_slide(self, mock_get, mock_render):
        mock_get.return_value = PresentationConfig(footer=True)
        st_presentation_footer(current_slide=1, total_slides=1)
        html = mock_render.call_args[0][0]
        assert "Slide 1 / 1" in html


# ── add_presentation_options ─────────────────────────────────────────────


class TestPresentationOptions:
    """Tests for add_presentation_options sidebar widget."""

    @patch("streamtex.presentation.st")
    def test_no_render_when_no_config(self, mock_st):
        mock_st.session_state = {}
        mock_st.sidebar = MagicMock()
        add_presentation_options()
        mock_st.sidebar.toggle.assert_not_called()

    @patch("streamtex.presentation.st")
    def test_renders_toggles_when_config_set(self, mock_st):
        cfg = PresentationConfig(footer=True)
        mock_st.session_state = {_PRESENTATION_CONFIG_KEY: cfg}
        mock_st.sidebar = MagicMock()
        add_presentation_options()
        assert mock_st.sidebar.toggle.call_count == 2

    @patch("streamtex.presentation.st")
    def test_initializes_session_state(self, mock_st):
        cfg = PresentationConfig(footer=True)
        mock_st.session_state = {_PRESENTATION_CONFIG_KEY: cfg}
        mock_st.sidebar = MagicMock()
        add_presentation_options()
        assert mock_st.session_state[_PRES_FOOTER_KEY] is True
        assert mock_st.session_state[_PRES_FULLSCREEN_KEY] is True

    @patch("streamtex.presentation.st")
    def test_custom_container(self, mock_st):
        cfg = PresentationConfig(footer=True)
        mock_st.session_state = {_PRESENTATION_CONFIG_KEY: cfg}
        custom_ctx = MagicMock()
        add_presentation_options(container=custom_ctx)
        assert custom_ctx.toggle.call_count == 2
        mock_st.sidebar.toggle.assert_not_called()

    @patch("streamtex.presentation.st")
    def test_preserves_existing_session_state(self, mock_st):
        cfg = PresentationConfig(footer=True)
        mock_st.session_state = {
            _PRESENTATION_CONFIG_KEY: cfg,
            _PRES_FOOTER_KEY: False,
            _PRES_FULLSCREEN_KEY: False,
        }
        mock_st.sidebar = MagicMock()
        add_presentation_options()
        # Should not overwrite existing values
        assert mock_st.session_state[_PRES_FOOTER_KEY] is False
        assert mock_st.session_state[_PRES_FULLSCREEN_KEY] is False


# ── SlideBreakConfig.fullscreen integration ──────────────────────────────


class TestSlideBreakFullscreen:
    """Tests for SlideBreakConfig.fullscreen in slide.py."""

    def test_fullscreen_default_false(self):
        from streamtex.slide import SlideBreakConfig
        cfg = SlideBreakConfig()
        assert cfg.fullscreen is False

    def test_fullscreen_true(self):
        from streamtex.slide import SlideBreakConfig
        cfg = SlideBreakConfig(fullscreen=True)
        assert cfg.fullscreen is True

    def test_fullscreen_forces_100vh(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break
        cfg = SlideBreakConfig(
            mode=SlideBreakMode.FULL,
            space="5vh",
            fullscreen=True,
        )
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            spacer_html = mock_render.call_args_list[1][0][0]
            assert "100vh" in spacer_html
            assert "5vh" not in spacer_html

    def test_non_fullscreen_uses_configured_space(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break
        cfg = SlideBreakConfig(
            mode=SlideBreakMode.FULL,
            space="50vh",
            fullscreen=False,
        )
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            spacer_html = mock_render.call_args_list[1][0][0]
            assert "50vh" in spacer_html

    def test_fullscreen_hidden_mode_still_renders_marker(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break
        cfg = SlideBreakConfig(
            mode=SlideBreakMode.HIDDEN,
            fullscreen=True,
            marker=True,
        )
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break(config=cfg)
            mock_render.assert_not_called()
            mock_marker.assert_called_once()

    def test_fullscreen_hidden_no_marker_when_disabled(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break
        cfg = SlideBreakConfig(
            mode=SlideBreakMode.HIDDEN,
            fullscreen=True,
            marker=False,
        )
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break(config=cfg)
            mock_render.assert_not_called()
            mock_marker.assert_not_called()

    def test_fullscreen_spacer_only(self):
        from streamtex.slide import SlideBreakConfig, SlideBreakMode, st_slide_break
        cfg = SlideBreakConfig(
            mode=SlideBreakMode.SPACER_ONLY,
            fullscreen=True,
        )
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            spacer_html = mock_render.call_args_list[0][0][0]
            assert "100vh" in spacer_html

    def test_fullscreen_preserved_in_effective_config(self):
        from streamtex.slide import _BREAK_ENABLED_KEY, SlideBreakConfig, _effective_config
        cfg = SlideBreakConfig(fullscreen=True)
        with patch("streamtex.slide.st") as mock_st:
            mock_st.session_state = {_BREAK_ENABLED_KEY: True}
            effective, enabled = _effective_config(cfg)
            assert effective.fullscreen is True
            assert enabled is True
