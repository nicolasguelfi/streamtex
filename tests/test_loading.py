"""Unit tests for streamtex.loading — loading overlay with progress indicator."""

from unittest.mock import patch

import pytest

from streamtex import loading
from streamtex.loading import (
    inject_loading_overlay,
    remove_loading_overlay,
    update_loading_progress,
)


@pytest.fixture(autouse=True)
def _reset_progress_throttle():
    """Clear the inter-test progress-emit throttle so each test sees a fresh slate."""
    loading._last_progress_emit = 0.0
    yield
    loading._last_progress_emit = 0.0

# ---------------------------------------------------------------------------
# inject_loading_overlay
# ---------------------------------------------------------------------------

class TestInjectLoadingOverlay:
    """Tests for inject_loading_overlay() — creates the full-screen overlay."""

    @patch("streamtex.loading.components")
    def test_calls_components_html_once(self, mock_components):
        """components.html() is called exactly once."""
        inject_loading_overlay()
        mock_components.html.assert_called_once()

    @patch("streamtex.loading.components")
    def test_height_zero(self, mock_components):
        """The injected component uses height=0 (invisible iframe)."""
        inject_loading_overlay()
        assert mock_components.html.call_args[1]["height"] == 0

    @patch("streamtex.loading.components")
    def test_contains_overlay_id(self, mock_components):
        """The HTML contains the overlay element id."""
        inject_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "stx-loading-overlay" in html_arg

    @patch("streamtex.loading.components")
    def test_contains_percent_element(self, mock_components):
        """The HTML contains the percent display element."""
        inject_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "stx-loading-percent" in html_arg

    @patch("streamtex.loading.components")
    def test_contains_bar_fill_element(self, mock_components):
        """The HTML contains the progress bar fill element."""
        inject_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "stx-loading-bar-fill" in html_arg

    @patch("streamtex.loading.components")
    def test_contains_initializing_status(self, mock_components):
        """The HTML contains the 'Initializing' status text."""
        inject_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "Initializing" in html_arg

    @patch("streamtex.loading.components")
    def test_contains_heartbeat_element(self, mock_components):
        """The HTML contains the heartbeat animation element."""
        inject_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "stx-loading-heartbeat" in html_arg

    @patch("streamtex.loading.components")
    def test_contains_module_name_element(self, mock_components):
        """The HTML contains the module name display element."""
        inject_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "stx-loading-module" in html_arg


# ---------------------------------------------------------------------------
# update_loading_progress
# ---------------------------------------------------------------------------

class TestUpdateLoadingProgress:
    """Tests for update_loading_progress() — updates percentage and counter."""

    @patch("streamtex.loading.components")
    def test_partial_progress_percentage(self, mock_components):
        """5/12 yields 41% in the injected JS."""
        update_loading_progress(5, 12)
        html_arg = mock_components.html.call_args[0][0]
        assert "41" in html_arg

    @patch("streamtex.loading.components")
    def test_partial_progress_module_count(self, mock_components):
        """5/12 injects the current and total module counts."""
        update_loading_progress(5, 12)
        html_arg = mock_components.html.call_args[0][0]
        # The JS template uses __CURRENT__ and __TOTAL__ placeholders
        assert "5" in html_arg
        assert "12" in html_arg

    @patch("streamtex.loading.components")
    def test_zero_total_no_error(self, mock_components):
        """0/0 does not raise and produces pct=0."""
        update_loading_progress(0, 0)
        html_arg = mock_components.html.call_args[0][0]
        # pct should be 0 — check the JS sets var pct = 0
        assert "var pct = 0;" in html_arg

    @patch("streamtex.loading.components")
    def test_complete_progress(self, mock_components):
        """12/12 yields 100%."""
        update_loading_progress(12, 12)
        html_arg = mock_components.html.call_args[0][0]
        assert "var pct = 100;" in html_arg

    @patch("streamtex.loading.components")
    def test_height_zero(self, mock_components):
        """The update component uses height=0."""
        update_loading_progress(3, 10)
        assert mock_components.html.call_args[1]["height"] == 0

    @patch("streamtex.loading.components")
    def test_module_name_in_js(self, mock_components):
        """Module name is injected into the JS when provided."""
        update_loading_progress(3, 10, "bck_intro")
        html_arg = mock_components.html.call_args[0][0]
        assert "bck_intro" in html_arg

    @patch("streamtex.loading.components")
    def test_module_name_default_empty(self, mock_components):
        """Module name defaults to empty string when not provided."""
        update_loading_progress(3, 10)
        html_arg = mock_components.html.call_args[0][0]
        assert "var modName = '';" in html_arg

    @patch("streamtex.loading.components")
    def test_heartbeat_shown(self, mock_components):
        """The update JS shows the heartbeat element."""
        update_loading_progress(3, 10)
        html_arg = mock_components.html.call_args[0][0]
        assert "stx-loading-heartbeat" in html_arg


# ---------------------------------------------------------------------------
# Progress throttle (Chrome iframe-storm guard)
# ---------------------------------------------------------------------------

class TestProgressThrottle:
    """Tests for the time-based throttle on progress iframe injection."""

    @patch("streamtex.loading.components")
    def test_intermediate_calls_within_window_are_throttled(self, mock_components):
        """Two intermediate updates within the throttle window emit one iframe."""
        update_loading_progress(3, 100)
        update_loading_progress(4, 100)
        assert mock_components.html.call_count == 1

    @patch("streamtex.loading.components")
    def test_initial_call_always_emits(self, mock_components):
        """current=0 (transition to progress mode) bypasses the throttle."""
        update_loading_progress(5, 100)  # primes _last_progress_emit
        update_loading_progress(0, 100)  # initial signal — must emit
        assert mock_components.html.call_count == 2

    @patch("streamtex.loading.components")
    def test_final_call_always_emits(self, mock_components):
        """The terminal current==total call bypasses the throttle (so 100% is shown)."""
        update_loading_progress(99, 100)  # primes _last_progress_emit
        update_loading_progress(100, 100)  # final — must emit
        assert mock_components.html.call_count == 2

    @patch("streamtex.loading.components")
    def test_inject_resets_throttle(self, mock_components):
        """A new overlay injection resets the throttle so the next progress call emits."""
        update_loading_progress(5, 100)
        # Without reset the next intermediate call would be throttled.
        inject_loading_overlay()
        update_loading_progress(6, 100)
        # 1 update + 1 inject + 1 update = 3 iframes
        assert mock_components.html.call_count == 3


# ---------------------------------------------------------------------------
# remove_loading_overlay
# ---------------------------------------------------------------------------

class TestRemoveLoadingOverlay:
    """Tests for remove_loading_overlay() — fades out and removes overlay."""

    @patch("streamtex.loading.components")
    def test_calls_components_html_once(self, mock_components):
        """components.html() is called exactly once."""
        remove_loading_overlay()
        mock_components.html.assert_called_once()

    @patch("streamtex.loading.components")
    def test_height_zero(self, mock_components):
        """The remove component uses height=0."""
        remove_loading_overlay()
        assert mock_components.html.call_args[1]["height"] == 0

    @patch("streamtex.loading.components")
    def test_contains_fade_out_opacity(self, mock_components):
        """The remove JS sets opacity for fade-out effect."""
        remove_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "opacity" in html_arg

    @patch("streamtex.loading.components")
    def test_contains_remove_call(self, mock_components):
        """The remove JS calls .remove() to detach the overlay from DOM."""
        remove_loading_overlay()
        html_arg = mock_components.html.call_args[0][0]
        assert "remove()" in html_arg
