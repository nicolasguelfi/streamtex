"""Tests for streamtex/overlay.py — OverlayController and st_overlay."""

import pytest
from contextlib import contextmanager
from unittest.mock import patch, MagicMock, call


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_st_block():
    """Return a context-manager mock that yields nothing (like a real st_block)."""
    @contextmanager
    def _fake_block(style=None, **kwargs):
        yield

    return _fake_block


# ---------------------------------------------------------------------------
# OverlayController.layer — CSS positioning logic
# ---------------------------------------------------------------------------

class TestOverlayControllerLayer:
    """Tests for OverlayController.layer context manager."""

    def _run_layer(self, captured_styles, **layer_kwargs):
        """
        Instantiate OverlayController, call .layer(**layer_kwargs) and capture
        the style string passed to st_block.
        """
        from streamtex.overlay import OverlayController

        def _fake_st_block(style=None, **kwargs):
            captured_styles.append(str(style) if style is not None else "")

            @contextmanager
            def _ctx():
                yield

            return _ctx()

        with patch("streamtex.overlay.st_block", side_effect=_fake_st_block):
            ctrl = OverlayController()
            with ctrl.layer(**layer_kwargs):
                pass

    # --- integer px conversion ---

    def test_integer_top_becomes_px(self):
        styles = []
        self._run_layer(styles, top=20)
        assert "top: 20px" in styles[0]

    def test_integer_left_becomes_px(self):
        styles = []
        self._run_layer(styles, left=10)
        assert "left: 10px" in styles[0]

    def test_integer_right_becomes_px(self):
        styles = []
        self._run_layer(styles, right=5)
        assert "right: 5px" in styles[0]

    def test_integer_bottom_becomes_px(self):
        styles = []
        self._run_layer(styles, bottom=30)
        assert "bottom: 30px" in styles[0]

    def test_zero_integer_becomes_px(self):
        styles = []
        self._run_layer(styles, top=0)
        assert "top: 0px" in styles[0]

    # --- string values passed through as-is ---

    def test_string_top_used_as_is(self):
        styles = []
        self._run_layer(styles, top="50%")
        assert "top: 50%" in styles[0]

    def test_string_left_used_as_is(self):
        styles = []
        self._run_layer(styles, left="2rem")
        assert "left: 2rem" in styles[0]

    def test_string_bottom_used_as_is(self):
        styles = []
        self._run_layer(styles, bottom="auto")
        assert "bottom: auto" in styles[0]

    def test_string_right_used_as_is(self):
        styles = []
        self._run_layer(styles, right="10vw")
        assert "right: 10vw" in styles[0]

    # --- None values omitted ---

    def test_none_top_omitted(self):
        styles = []
        self._run_layer(styles, top=None, left=10)
        assert "top:" not in styles[0]
        assert "left: 10px" in styles[0]

    def test_none_left_omitted(self):
        styles = []
        self._run_layer(styles, top=5, left=None)
        assert "left:" not in styles[0]
        assert "top: 5px" in styles[0]

    def test_none_right_omitted(self):
        styles = []
        self._run_layer(styles, right=None, bottom=8)
        assert "right:" not in styles[0]
        assert "bottom: 8px" in styles[0]

    def test_none_bottom_omitted(self):
        styles = []
        self._run_layer(styles, bottom=None, top=2)
        assert "bottom:" not in styles[0]

    def test_all_none_produces_no_position_properties(self):
        styles = []
        self._run_layer(styles)  # all default to None
        assert "top:" not in styles[0]
        assert "left:" not in styles[0]
        assert "right:" not in styles[0]
        assert "bottom:" not in styles[0]

    # --- absolute positioning always present ---

    def test_absolute_positioning_always_set(self):
        styles = []
        self._run_layer(styles, top=10)
        assert "position: absolute" in styles[0]

    def test_z_index_always_set(self):
        styles = []
        self._run_layer(styles, top=10)
        assert "z-index" in styles[0]

    # --- combined values ---

    def test_multiple_positions_combined(self):
        styles = []
        self._run_layer(styles, top=10, left=20, right="auto", bottom=0)
        css = styles[0]
        assert "top: 10px" in css
        assert "left: 20px" in css
        assert "right: auto" in css
        assert "bottom: 0px" in css

    # --- user style is merged into final style ---

    def test_user_style_merged(self):
        from streamtex.styles import Style
        styles = []
        user_style = Style("color: red;", "red")
        self._run_layer(styles, top=5)
        # The user style is applied via the Style object passed to layer()
        # via the default StreamTeX_Styles.none; override with explicit style
        captured_styles_with_user = []

        def _fake_st_block(style=None, **kwargs):
            captured_styles_with_user.append(str(style) if style is not None else "")

            @contextmanager
            def _ctx():
                yield

            return _ctx()

        from streamtex.overlay import OverlayController
        with patch("streamtex.overlay.st_block", side_effect=_fake_st_block):
            ctrl = OverlayController()
            with ctrl.layer(style=user_style, top=5):
                pass

        combined = captured_styles_with_user[0]
        assert "color: red;" in combined
        assert "top: 5px" in combined


# ---------------------------------------------------------------------------
# st_overlay — relative container creation
# ---------------------------------------------------------------------------

class TestStOverlay:
    """Tests for the st_overlay context manager."""

    def test_yields_overlay_controller(self):
        from streamtex.overlay import st_overlay, OverlayController

        with patch("streamtex.overlay.st_block", side_effect=_make_fake_st_block()):
            with st_overlay() as ctrl:
                assert isinstance(ctrl, OverlayController)

    def test_relative_positioning_in_container_style(self):
        from streamtex.overlay import st_overlay
        captured_styles = []

        def _spy_st_block(style=None, **kwargs):
            captured_styles.append(str(style) if style is not None else "")

            @contextmanager
            def _ctx():
                yield

            return _ctx()

        with patch("streamtex.overlay.st_block", side_effect=_spy_st_block):
            with st_overlay():
                pass

        assert len(captured_styles) >= 1
        assert "position: relative" in captured_styles[0]

    def test_user_style_merged_into_container(self):
        from streamtex.overlay import st_overlay
        from streamtex.styles import Style

        captured_styles = []
        user_style = Style("background: rgba(0,0,0,0.5);", "overlay_bg")

        def _spy_st_block(style=None, **kwargs):
            captured_styles.append(str(style) if style is not None else "")

            @contextmanager
            def _ctx():
                yield

            return _ctx()

        with patch("streamtex.overlay.st_block", side_effect=_spy_st_block):
            with st_overlay(style=user_style):
                pass

        assert "background: rgba(0,0,0,0.5);" in captured_styles[0]
        assert "position: relative" in captured_styles[0]

    def test_body_executes_inside_context(self):
        from streamtex.overlay import st_overlay

        executed = []
        with patch("streamtex.overlay.st_block", side_effect=_make_fake_st_block()):
            with st_overlay():
                executed.append(True)

        assert executed == [True]

    def test_layer_accessible_from_controller(self):
        """Verify the yielded controller's .layer() method is callable."""
        from streamtex.overlay import st_overlay

        with patch("streamtex.overlay.st_block", side_effect=_make_fake_st_block()):
            with st_overlay() as ctrl:
                assert hasattr(ctrl, "layer")
                assert callable(ctrl.layer)
