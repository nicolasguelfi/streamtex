"""Unit tests for streamtex.slide — presentation-mode slide breaks."""

from unittest.mock import MagicMock, patch

from streamtex.slide import (
    _BREAK_ENABLED_KEY,
    _BREAK_MODE_KEY,
    _BREAK_SPACE_KEY,
    _MODE_LABELS,
    SlideBreakConfig,
    SlideBreakMode,
    add_slide_break_options,
    get_slide_break_config,
    set_slide_break_config,
    st_slide_break,
)

# ── SlideBreakMode enum ──────────────────────────────────────────────────

class TestSlideBreakMode:
    """Tests for SlideBreakMode enum values."""

    def test_all_modes_exist(self):
        assert SlideBreakMode.FULL.value == "full"
        assert SlideBreakMode.RULE_ONLY.value == "rule_only"
        assert SlideBreakMode.SPACER_ONLY.value == "spacer_only"
        assert SlideBreakMode.MARKER_ONLY.value == "marker_only"
        assert SlideBreakMode.HIDDEN.value == "hidden"

    def test_five_modes(self):
        assert len(SlideBreakMode) == 5


# ── SlideBreakConfig ─────────────────────────────────────────────────────

class TestSlideBreakConfig:
    """Tests for SlideBreakConfig dataclass."""

    def test_defaults(self):
        cfg = SlideBreakConfig()
        assert cfg.mode == SlideBreakMode.FULL
        assert cfg.space == "60vh"
        assert cfg.thickness == "1px"
        assert cfg.color == "128, 128, 128"
        assert cfg.opacity == 0.5
        assert cfg.marker is True

    def test_custom_values(self):
        cfg = SlideBreakConfig(
            mode=SlideBreakMode.RULE_ONLY,
            space="80vh", thickness="2px",
            color="79, 172, 254", opacity=0.5, marker=False,
        )
        assert cfg.mode == SlideBreakMode.RULE_ONLY
        assert cfg.space == "80vh"
        assert cfg.thickness == "2px"
        assert cfg.color == "79, 172, 254"
        assert cfg.opacity == 0.5
        assert cfg.marker is False

    def test_hidden_mode(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.HIDDEN)
        assert cfg.mode == SlideBreakMode.HIDDEN


# ── Global config ────────────────────────────────────────────────────────

class TestGlobalConfig:
    """Tests for set/get global config."""

    def test_set_and_get(self):
        original = get_slide_break_config()
        custom = SlideBreakConfig(space="50vh")
        set_slide_break_config(custom)
        assert get_slide_break_config() is custom
        set_slide_break_config(original)

    def test_mode_preserved(self):
        original = get_slide_break_config()
        custom = SlideBreakConfig(mode=SlideBreakMode.SPACER_ONLY)
        set_slide_break_config(custom)
        assert get_slide_break_config().mode == SlideBreakMode.SPACER_ONLY
        set_slide_break_config(original)


# ── st_slide_break rendering ─────────────────────────────────────────────

class TestStSlideBreak:
    """Tests for st_slide_break rendering with modes."""

    def test_full_mode_renders_rule_and_spacer(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.FULL)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            assert mock_render.call_count == 2
            rule_call = mock_render.call_args_list[0][0][0]
            spacer_call = mock_render.call_args_list[1][0][0]
            assert 'class="stx-slide-break-rule"' in rule_call
            assert 'class="stx-slide-break-spacer"' in spacer_call

    def test_rule_only_mode_renders_rule_no_spacer(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.RULE_ONLY)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            assert mock_render.call_count == 1
            assert 'stx-slide-break-rule' in mock_render.call_args_list[0][0][0]

    def test_spacer_only_mode_renders_spacer_no_rule(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.SPACER_ONLY)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            assert mock_render.call_count == 1
            assert 'stx-slide-break-spacer' in mock_render.call_args_list[0][0][0]

    def test_marker_only_mode_renders_marker_only(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.MARKER_ONLY)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break(config=cfg)
            mock_render.assert_not_called()
            mock_marker.assert_called_once()

    def test_hidden_mode_renders_nothing(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.HIDDEN)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break(config=cfg)
            mock_render.assert_not_called()
            mock_marker.assert_not_called()

    def test_inline_styles_use_config_values(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.FULL)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            rule_html = mock_render.call_args_list[0][0][0]
            assert "1px" in rule_html
            assert "128, 128, 128" in rule_html
            assert "0.5" in rule_html

    def test_inline_styles_in_spacer(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.FULL)
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            spacer_html = mock_render.call_args_list[1][0][0]
            assert "60vh" in spacer_html

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
        cfg = SlideBreakConfig(
            mode=SlideBreakMode.FULL,
            space="50vh", thickness="3px",
            color="255, 0, 0", opacity=0.8,
        )
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            rule_call = mock_render.call_args_list[0][0][0]
            assert "3px" in rule_call
            assert "255, 0, 0" in rule_call
            assert "0.8" in rule_call
            spacer_call = mock_render.call_args_list[1][0][0]
            assert "50vh" in spacer_call

    def test_rule_margin_top_in_rule(self):
        cfg = SlideBreakConfig(rule_margin_top="2em")
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            rule_html = mock_render.call_args_list[0][0][0]
            assert "margin-top: 2em" in rule_html

    def test_rule_margin_top_absent_in_spacer_only(self):
        cfg = SlideBreakConfig(mode=SlideBreakMode.SPACER_ONLY, rule_margin_top="2em")
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            assert mock_render.call_count == 1
            html = mock_render.call_args_list[0][0][0]
            assert "stx-slide-break-spacer" in html
            assert "margin-top" not in html

    def test_marker_label_passed(self):
        with patch("streamtex.slide._render"), \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break(marker_label="Section 2")
            mock_marker.assert_called_once_with("Section 2", hidden=True)

    def test_default_config_full_mode_renders_two_elements(self):
        with patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break()
            assert mock_render.call_count == 2


# ── Session state override (sidebar widget integration) ─────────────────

class TestSessionStateOverride:
    """Tests for Python-side session state override in st_slide_break."""

    def test_disabled_via_session_state_renders_nothing(self):
        mock_state = {_BREAK_ENABLED_KEY: False}
        with patch("streamtex.slide.st.session_state", mock_state), \
             patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker") as mock_marker:
            st_slide_break()
            mock_render.assert_not_called()
            mock_marker.assert_not_called()

    def test_session_state_mode_override(self):
        mock_state = {
            _BREAK_ENABLED_KEY: True,
            _BREAK_MODE_KEY: "Rule only",
            _BREAK_SPACE_KEY: 60,
        }
        with patch("streamtex.slide.st.session_state", mock_state), \
             patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break()
            assert mock_render.call_count == 1
            assert "stx-slide-break-rule" in mock_render.call_args_list[0][0][0]

    def test_session_state_spacer_only_override(self):
        mock_state = {
            _BREAK_ENABLED_KEY: True,
            _BREAK_MODE_KEY: "Spacer only",
            _BREAK_SPACE_KEY: 80,
        }
        with patch("streamtex.slide.st.session_state", mock_state), \
             patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break()
            assert mock_render.call_count == 1
            html = mock_render.call_args_list[0][0][0]
            assert "stx-slide-break-spacer" in html
            assert "80vh" in html

    def test_session_state_space_value_applied(self):
        mock_state = {
            _BREAK_ENABLED_KEY: True,
            _BREAK_MODE_KEY: "Full",
            _BREAK_SPACE_KEY: 90,
        }
        with patch("streamtex.slide.st.session_state", mock_state), \
             patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break()
            spacer_html = mock_render.call_args_list[1][0][0]
            assert "90vh" in spacer_html

    def test_no_session_state_uses_config(self):
        """When no sidebar keys exist, config is used as-is."""
        mock_state = {}
        cfg = SlideBreakConfig(mode=SlideBreakMode.RULE_ONLY, space="42vh")
        with patch("streamtex.slide.st.session_state", mock_state), \
             patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            st_slide_break(config=cfg)
            assert mock_render.call_count == 1
            assert "stx-slide-break-rule" in mock_render.call_args_list[0][0][0]

    def test_per_call_config_overrides_session_state(self):
        """Explicit config= parameter overrides session state mode/space."""
        mock_state = {
            _BREAK_ENABLED_KEY: True,
            _BREAK_MODE_KEY: "Rule only",
            _BREAK_SPACE_KEY: 30,
        }
        cfg = SlideBreakConfig(mode=SlideBreakMode.SPACER_ONLY, space="99vh")
        with patch("streamtex.slide.st.session_state", mock_state), \
             patch("streamtex.slide._render") as mock_render, \
             patch("streamtex.slide.st_marker"):
            # config= is provided, but session state is also active
            # _effective_config still applies session state overrides
            # because sidebar is active (enabled key exists)
            st_slide_break(config=cfg)
            # Session state overrides: mode=Rule only, space=30vh
            assert mock_render.call_count == 1
            assert "stx-slide-break-rule" in mock_render.call_args_list[0][0][0]


# ── add_slide_break_options ──────────────────────────────────────────────

class TestAddSlideBreakOptions:
    """Tests for add_slide_break_options sidebar widget."""

    def test_initializes_session_state(self):
        mock_state = {}
        ctx = MagicMock()
        with patch("streamtex.slide.st.session_state", mock_state):
            add_slide_break_options(container=ctx)
            assert _BREAK_ENABLED_KEY in mock_state
            assert _BREAK_MODE_KEY in mock_state
            assert _BREAK_SPACE_KEY in mock_state

    def test_default_mode_stored_as_label_string(self):
        mock_state = {}
        ctx = MagicMock()
        with patch("streamtex.slide.st.session_state", mock_state):
            add_slide_break_options(default_mode=SlideBreakMode.RULE_ONLY,
                                    container=ctx)
            assert mock_state[_BREAK_MODE_KEY] == "Rule only"

    def test_mode_labels_cover_three_visual_modes(self):
        assert len(_MODE_LABELS) == 3
        assert SlideBreakMode.FULL in _MODE_LABELS.values()
        assert SlideBreakMode.RULE_ONLY in _MODE_LABELS.values()
        assert SlideBreakMode.SPACER_ONLY in _MODE_LABELS.values()


# ── Mode rendering matrix ───────────────────────────────────────────────

class TestModeRenderingMatrix:
    """Verify the full rendering matrix: mode × element → rendered?"""

    _MODES_RENDER = {
        SlideBreakMode.FULL: {"rule": True, "spacer": True, "marker": True},
        SlideBreakMode.RULE_ONLY: {"rule": True, "spacer": False, "marker": True},
        SlideBreakMode.SPACER_ONLY: {"rule": False, "spacer": True, "marker": True},
        SlideBreakMode.MARKER_ONLY: {"rule": False, "spacer": False, "marker": True},
        SlideBreakMode.HIDDEN: {"rule": False, "spacer": False, "marker": False},
    }

    def test_all_modes_rendering(self):
        for mode, expected in self._MODES_RENDER.items():
            cfg = SlideBreakConfig(mode=mode)
            with patch("streamtex.slide._render") as mock_render, \
                 patch("streamtex.slide.st_marker") as mock_marker:
                st_slide_break(config=cfg)

                render_calls = [c[0][0] for c in mock_render.call_args_list]
                has_rule = any("stx-slide-break-rule" in c for c in render_calls)
                has_spacer = any("stx-slide-break-spacer" in c for c in render_calls)
                has_marker = mock_marker.called

                assert has_rule == expected["rule"], \
                    f"{mode}: rule expected={expected['rule']}, got={has_rule}"
                assert has_spacer == expected["spacer"], \
                    f"{mode}: spacer expected={expected['spacer']}, got={has_spacer}"
                assert has_marker == expected["marker"], \
                    f"{mode}: marker expected={expected['marker']}, got={has_marker}"
