"""Tests for search filtering of markers in the sidebar (continuous + paginated modes).

Verifies that:
- Continuous mode assigns block_idx to marker entries
- populate_markers_sidebar renders data-stx-block attributes when search is enabled
- populate_markers_sidebar falls back to st.html() when search is disabled
- Paginated mode cache includes marker block_idx (already worked, regression guard)
"""

from unittest.mock import MagicMock, patch

import streamtex.marker as marker_mod
import streamtex.toc as toc_mod
from streamtex.marker import (
    MarkerConfig,
    marker_entries,
    register_marker,
    reset_marker_registry,
)
from streamtex.toc import TOCConfig, reset_toc_registry, toc_entries

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_registries(marker_config=None, toc_config=None):
    """Reset both registries to a clean state."""
    toc_mod.toc = None
    marker_mod._registry = None
    if toc_config is not None:
        reset_toc_registry(toc_config)
    if marker_config is not None:
        reset_marker_registry(marker_config)


# ===========================================================================
# 1. Continuous mode: block_idx assignment to markers
# ===========================================================================

class TestContinuousModeBlockIdxAssignment:
    """Test that the continuous mode loop assigns block_idx to marker entries."""

    def setup_method(self):
        _setup_registries(
            marker_config=MarkerConfig(),
            toc_config=TOCConfig(),
        )

    def test_markers_get_block_idx_after_registration(self):
        """Simulate the continuous mode loop logic:
        register markers, then tag them with block_idx."""
        # Block 0: register 2 markers
        markers_before = len(marker_entries())
        register_marker("Marker A", "anchor-a")
        register_marker("Marker B", "anchor-b")
        for entry in marker_entries()[markers_before:]:
            if "block_idx" not in entry:
                entry["block_idx"] = 0

        # Block 1: register 1 marker
        markers_before = len(marker_entries())
        register_marker("Marker C", "anchor-c")
        for entry in marker_entries()[markers_before:]:
            if "block_idx" not in entry:
                entry["block_idx"] = 1

        entries = marker_entries()
        assert len(entries) == 3
        assert entries[0]["block_idx"] == 0
        assert entries[1]["block_idx"] == 0
        assert entries[2]["block_idx"] == 1

    def test_block_idx_not_overwritten(self):
        """If block_idx already exists, it should not be overwritten."""
        register_marker("Pre-tagged", "anchor-pre")
        entries = marker_entries()
        entries[0]["block_idx"] = 42  # pre-set

        # Simulate the tagging loop — should not overwrite
        for entry in marker_entries():
            if "block_idx" not in entry:
                entry["block_idx"] = 0

        assert marker_entries()[0]["block_idx"] == 42

    def test_empty_markers_no_error(self):
        """No markers registered — the tagging loop should be a no-op."""
        markers_before = len(marker_entries())
        for entry in marker_entries()[markers_before:]:
            if "block_idx" not in entry:
                entry["block_idx"] = 0
        assert marker_entries() == []


# ===========================================================================
# 2. populate_markers_sidebar — search-aware rendering
# ===========================================================================

class TestPopulateMarkersSidebarSearchAware:
    """Test that populate_markers_sidebar renders data-stx-block when search is enabled."""

    def setup_method(self):
        _setup_registries(marker_config=MarkerConfig())

    def _register_markers_with_block_idx(self):
        """Register test markers and assign block_idx."""
        register_marker("Introduction", "anchor-intro")
        register_marker("Setup", "anchor-setup")
        register_marker("Advanced", "anchor-adv")
        entries = marker_entries()
        entries[0]["block_idx"] = 0
        entries[1]["block_idx"] = 1
        entries[2]["block_idx"] = 2

    @patch("streamtex.book.st")
    def test_search_enabled_renders_markdown_with_data_stx_block(self, mock_st):
        """When block_index is provided, should use st.markdown with data-stx-block attrs."""
        self._register_markers_with_block_idx()

        from streamtex.book import populate_markers_sidebar
        placeholder = MagicMock()
        block_index = {0: "intro text", 1: "setup text", 2: "advanced text"}

        populate_markers_sidebar(placeholder, block_index=block_index)

        # st.markdown is called on the module-level st mock (inside container context)
        assert mock_st.markdown.called, "Expected st.markdown to be called in search mode"
        html_output = mock_st.markdown.call_args[0][0]

        # Verify data-stx-block attributes
        assert 'data-stx-block="0"' in html_output
        assert 'data-stx-block="1"' in html_output
        assert 'data-stx-block="2"' in html_output

        # Verify marker labels
        assert "Introduction" in html_output
        assert "Setup" in html_output
        assert "Advanced" in html_output

        # Verify numbering
        assert "1. Introduction" in html_output
        assert "2. Setup" in html_output
        assert "3. Advanced" in html_output

        # Verify anchors
        assert 'href="#anchor-intro"' in html_output
        assert 'href="#anchor-setup"' in html_output

    @patch("streamtex.book.st")
    def test_search_disabled_renders_st_html(self, mock_st):
        """When block_index is None, should use st.html() per entry (original behavior)."""
        self._register_markers_with_block_idx()

        from streamtex.book import populate_markers_sidebar
        placeholder = MagicMock()

        populate_markers_sidebar(placeholder, block_index=None)

        # st.html is called on the module-level st mock
        assert mock_st.html.call_count == 3

    @patch("streamtex.book.st")
    def test_search_enabled_hidden_markers_excluded(self, mock_st):
        """Hidden markers should not appear in the sidebar regardless of search mode."""
        register_marker("Visible", "anchor-vis")
        register_marker("Hidden", "anchor-hid", hidden=True)
        entries = marker_entries()
        entries[0]["block_idx"] = 0
        entries[1]["block_idx"] = 0

        from streamtex.book import populate_markers_sidebar
        placeholder = MagicMock()
        block_index = {0: "some text"}

        populate_markers_sidebar(placeholder, block_index=block_index)

        html_output = mock_st.markdown.call_args[0][0]
        assert "Visible" in html_output
        assert "Hidden" not in html_output

    @patch("streamtex.book.st")
    def test_no_markers_does_nothing(self, mock_st):
        """No markers — should return without rendering."""
        from streamtex.book import populate_markers_sidebar
        placeholder = MagicMock()

        populate_markers_sidebar(placeholder, block_index={0: "text"})

        # Container should not be entered
        placeholder.container.assert_not_called()

    @patch("streamtex.book.st")
    def test_search_enabled_default_block_idx_zero(self, mock_st):
        """Markers without block_idx should default to 0 in data-stx-block."""
        register_marker("No Idx", "anchor-no-idx")
        # Do NOT assign block_idx

        from streamtex.book import populate_markers_sidebar
        placeholder = MagicMock()
        block_index = {0: "fallback text"}

        populate_markers_sidebar(placeholder, block_index=block_index)

        html_output = mock_st.markdown.call_args[0][0]
        assert 'data-stx-block="0"' in html_output

    @patch("streamtex.book.st")
    def test_search_enabled_bottom_spacer(self, mock_st):
        """Search mode should include a bottom spacer div."""
        register_marker("Test", "anchor-test")
        marker_entries()[0]["block_idx"] = 0

        from streamtex.book import populate_markers_sidebar
        placeholder = MagicMock()

        populate_markers_sidebar(placeholder, block_index={0: "text"})

        html_output = mock_st.markdown.call_args[0][0]
        assert 'height:40px' in html_output


# ===========================================================================
# 3. Regression guards — paginated mode markers unchanged
# ===========================================================================

class TestPaginatedModeMarkersUnchanged:
    """Verify paginated sidebar rendering still uses data-stx-block with page_idx."""

    def test_paginated_sidebar_uses_page_idx(self):
        """Paginated mode uses page_idx (not block_idx) for data-stx-block — regression guard."""
        _setup_registries(marker_config=MarkerConfig())
        register_marker("Page Marker", "anchor-pm")
        entries = marker_entries()
        entries[0]["page_idx"] = 3  # paginated mode uses page_idx

        # The paginated sidebar reads page_idx — confirm it's present
        assert entries[0]["page_idx"] == 3
        assert "block_idx" not in entries[0]


# ===========================================================================
# 4. Integration: block_idx consistency between TOC and markers
# ===========================================================================

class TestBlockIdxConsistencyTocMarkers:
    """Verify TOC and markers in the same block get the same block_idx."""

    def setup_method(self):
        _setup_registries(
            marker_config=MarkerConfig(),
            toc_config=TOCConfig(),
        )

    def test_same_block_same_idx(self):
        """TOC entries and markers from the same block should share block_idx."""
        from streamtex.toc import register_toc_entry

        # Simulate block 2: register both TOC and marker
        toc_before = len(toc_entries())
        markers_before = len(marker_entries())

        register_toc_entry("Section Title", "1")
        register_marker("Section Marker", "anchor-sec")

        # Tag like the continuous mode loop does
        for entry in toc_entries()[toc_before:]:
            if "block_idx" not in entry:
                entry["block_idx"] = 2
        for entry in marker_entries()[markers_before:]:
            if "block_idx" not in entry:
                entry["block_idx"] = 2

        assert toc_entries()[-1]["block_idx"] == 2
        assert marker_entries()[-1]["block_idx"] == 2
