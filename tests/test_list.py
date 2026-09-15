"""Tests for the list module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from streamtex.enums import ListTypes
from streamtex.list import ListController, _current_list_level, st_list
from streamtex.styles import ListStyle, StxStyles, Style


# Module-level autouse fixture: keep the legacy :has() path as the test
# default so historical assertions remain valid after Phase 4's default
# flip.  Marker-path tests opt in via `_marker_runtime_on` below.
@pytest.fixture(autouse=True)
def _force_legacy_by_default():
    prev_legacy = os.environ.get("STX_USE_LEGACY_HAS")
    prev_marker = os.environ.get("STX_USE_MARKER_RUNTIME")
    os.environ["STX_USE_LEGACY_HAS"] = "1"
    os.environ.pop("STX_USE_MARKER_RUNTIME", None)
    yield
    if prev_legacy is None:
        os.environ.pop("STX_USE_LEGACY_HAS", None)
    else:
        os.environ["STX_USE_LEGACY_HAS"] = prev_legacy
    if prev_marker is None:
        os.environ.pop("STX_USE_MARKER_RUNTIME", None)
    else:
        os.environ["STX_USE_MARKER_RUNTIME"] = prev_marker


class TestListController:
    """Tests for ListController class."""

    def test_list_controller_creation_unordered(self):
        """Test creating a ListController with unordered list settings."""
        li_style = Style("color: red;", "red_item")
        bullet = "'●'"
        controller = ListController(li_style, bullet, is_ordered=False)

        assert controller.li_style is li_style
        assert controller.bullet_content == "'●'"
        assert controller.is_ordered is False

    def test_list_controller_creation_ordered(self):
        """Test creating a ListController with ordered list settings."""
        li_style = Style("font-weight: bold;", "bold_item")
        bullet = "counter(streamtex-counter, decimal)"
        controller = ListController(li_style, bullet, is_ordered=True)

        assert controller.li_style is li_style
        assert controller.bullet_content == bullet
        assert controller.is_ordered is True

    def test_list_controller_with_empty_style(self):
        """Test ListController with empty style."""
        li_style = StxStyles.none
        controller = ListController(li_style, "'●'", is_ordered=False)

        assert controller.li_style is li_style
        assert bool(controller.li_style) is False

    def test_list_controller_item_context_manager(self, mock_streamlit):
        """Test that item() method is a context manager."""
        controller = ListController(StxStyles.none, "'●'", is_ordered=False)

        # Check that item() is callable and returns a context manager
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            # Configure mocks
            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with controller.item():
                pass

            # Verify st_block was called
            assert mock_st_block.called

    def test_list_controller_item_with_custom_style(self, mock_streamlit):
        """Test item() context manager with custom style."""
        li_base = Style("color: red;", "red")
        li_custom = Style("font-weight: bold;", "bold")
        controller = ListController(li_base, "'●'", is_ordered=False)

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with controller.item(style=li_custom):
                pass

            # Verify st_block was called with combined style
            assert mock_st_block.called
            call_args = mock_st_block.call_args
            # The style passed should be the combination of li_base and li_custom
            assert call_args is not None


class TestCurrentListLevel:
    """Tests for _current_list_level ContextVar."""

    def test_initial_level_is_zero(self):
        """Test that the initial nesting level is 0."""
        # Reset the context var to default
        token = _current_list_level.set(0)
        try:
            level = _current_list_level.get()
            assert level == 0
        finally:
            _current_list_level.reset(token)

    def test_level_increments_with_nesting(self):
        """Test that nesting level increments correctly."""
        # Start at level 0
        token0 = _current_list_level.set(0)
        try:
            assert _current_list_level.get() == 0

            # First level increment
            token1 = _current_list_level.set(1)
            try:
                assert _current_list_level.get() == 1

                # Second level increment
                token2 = _current_list_level.set(2)
                try:
                    assert _current_list_level.get() == 2
                finally:
                    _current_list_level.reset(token2)

                # Back to level 1
                assert _current_list_level.get() == 1
            finally:
                _current_list_level.reset(token1)

            # Back to level 0
            assert _current_list_level.get() == 0
        finally:
            _current_list_level.reset(token0)

    def test_context_var_isolation(self):
        """Test that ContextVar provides proper isolation."""
        # Set level to 1
        token = _current_list_level.set(1)
        try:
            level = _current_list_level.get()
            assert level == 1
        finally:
            _current_list_level.reset(token)

        # After reset, should be back to default (0)
        assert _current_list_level.get() == 0


class TestStList:
    """Tests for st_list context manager."""

    def test_st_list_unordered_default(self, mock_streamlit):
        """Test creating an unordered list with defaults."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list() as controller:
                assert isinstance(controller, ListController)
                assert controller.is_ordered is False
                assert controller.bullet_content == "'•'"

    def test_st_list_ordered(self, mock_streamlit):
        """Test creating an ordered list."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(list_type=ListTypes.ordered) as controller:
                assert isinstance(controller, ListController)
                assert controller.is_ordered is True
                assert "counter(streamtex-counter, decimal)" in controller.bullet_content

    def test_st_list_with_custom_list_style(self, mock_streamlit):
        """Test st_list with custom ListStyle."""
        custom_style = ListStyle(symbols=["▸", "○", "■"])

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(list_type=ListTypes.unordered, l_style=custom_style) as controller:
                assert isinstance(controller, ListController)
                # At nesting level 1, should use first symbol
                assert "'▸'" in controller.bullet_content

    def test_st_list_nesting_changes_bullet(self, mock_streamlit):
        """Test that bullet symbols change based on nesting level."""
        custom_style = ListStyle(symbols=["▸", "○", "■"])

        def mock_list_context():
            with patch("streamtex.list.st_block") as mock_st_block, \
                 patch("streamtex.list.st.html") as mock_html, \
                 patch("streamtex.list.is_export_active", return_value=False):

                mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
                mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

                # First level (level 1)
                with st_list(list_type=ListTypes.unordered, l_style=custom_style) as ctrl1:
                    assert "'▸'" in ctrl1.bullet_content

                    # Simulate second level
                    with st_list(list_type=ListTypes.unordered, l_style=custom_style) as ctrl2:
                        assert "'○'" in ctrl2.bullet_content

                        # Simulate third level
                        with st_list(list_type=ListTypes.unordered, l_style=custom_style) as ctrl3:
                            assert "'■'" in ctrl3.bullet_content

        mock_list_context()

    def test_st_list_resets_context_on_exit(self, mock_streamlit):
        """Test that ContextVar is properly reset after st_list exits."""
        initial_level = _current_list_level.get()

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list():
                pass

            final_level = _current_list_level.get()
            assert final_level == initial_level

    def test_st_list_with_li_style(self, mock_streamlit):
        """Test st_list with custom list item style."""
        li_style = Style("padding: 10px;", "padded_item")

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(li_style=li_style) as controller:
                assert controller.li_style is li_style


class TestListStyleIntegration:
    """Integration tests for ListStyle with st_list."""

    def test_list_style_lvl_method(self):
        """Test ListStyle.lvl() method for symbol cycling."""
        ls = ListStyle(symbols=["▸", "○", "■"])

        assert ls.lvl(1) == "list-style-type: '▸';"
        assert ls.lvl(2) == "list-style-type: '○';"
        assert ls.lvl(3) == "list-style-type: '■';"
        assert ls.lvl(4) == "list-style-type: '▸';"  # Cycles back

    def test_list_style_lvl_with_single_symbol(self):
        """Test lvl() with single symbol always returns that symbol."""
        ls = ListStyle(symbols=["•"])

        assert ls.lvl(1) == "list-style-type: '•';"
        assert ls.lvl(2) == "list-style-type: '•';"
        assert ls.lvl(3) == "list-style-type: '•';"

    def test_list_style_lvl_with_empty_symbols_raises(self):
        """Test that lvl() with empty symbols raises ZeroDivisionError."""
        ls = ListStyle(symbols=[])

        with pytest.raises(ZeroDivisionError):
            ls.lvl(1)

    def test_list_style_default_symbols(self):
        """Test that ListStyle has default bullet symbol."""
        ls = ListStyle()
        assert ls.symbols == ["●"]
        assert ls.lvl(1) == "list-style-type: '●';"

    def test_list_style_add_preserves_symbols(self):
        """Test that adding ListStyle preserves and combines symbols."""
        ls1 = ListStyle(symbols=["●"])
        ls2 = ListStyle(symbols=["○"])
        combined = ls1 + ls2

        assert combined.symbols == ["●", "○"]
        assert combined.lvl(1) == "list-style-type: '●';"
        assert combined.lvl(2) == "list-style-type: '○';"

    def test_list_style_sub_removes_symbols(self):
        """Test that subtracting ListStyle removes symbols."""
        ls1 = ListStyle(symbols=["●", "○", "■"])
        ls2 = ListStyle(symbols=["○"])
        result = ls1 - ls2

        assert result.symbols == ["●", "■"]


class TestListNestingBehavior:
    """Tests for nested list behavior and level tracking."""

    def test_nested_list_level_progression(self, mock_streamlit):
        """Test that nesting levels progress correctly."""
        levels_seen = []

        # Capture levels at each nesting stage
        def capture_level():
            levels_seen.append(_current_list_level.get())

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list():
                capture_level()
                with st_list():
                    capture_level()
                    with st_list():
                        capture_level()

        # Should have seen levels 1, 2, 3
        assert levels_seen == [1, 2, 3]

    def test_st_list_with_default_symbols_at_levels(self, mock_streamlit):
        """Test default bullet symbol behavior at different levels."""
        bullets_seen = []

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list() as l1:
                bullets_seen.append(l1.bullet_content)
                with st_list() as l2:
                    bullets_seen.append(l2.bullet_content)
                    with st_list() as l3:
                        bullets_seen.append(l3.bullet_content)

        # Level 1: •, Level 2: ○, Level 3+: ■
        assert bullets_seen[0] == "'•'"
        assert bullets_seen[1] == "'○'"
        assert bullets_seen[2] == "'■'"


class TestListExportBehavior:
    """Tests for export-aware behavior of st_list."""

    def test_st_list_calls_export_wrappers_when_active(self, mock_streamlit):
        """Test that export wrappers are called when export is active."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=True), \
             patch("streamtex.list.export_push_wrapper") as mock_push, \
             patch("streamtex.list.export_pop_wrapper") as mock_pop:

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(list_type=ListTypes.unordered):
                pass

            # Verify export wrappers were called
            assert mock_push.called
            assert mock_pop.called

    def test_st_list_ordered_export_uses_ol_tag(self, mock_streamlit):
        """Test that ordered list uses <ol> tag in export."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=True), \
             patch("streamtex.list.export_push_wrapper") as mock_push, \
             patch("streamtex.list.export_pop_wrapper") as mock_pop:

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(list_type=ListTypes.ordered):
                pass

            # Check that <ol> was used
            push_call_args = mock_push.call_args[0][0]
            pop_call_args = mock_pop.call_args[0][0]
            assert "<ol" in push_call_args
            assert "</ol>" in pop_call_args

    def test_st_list_unordered_export_uses_ul_tag(self, mock_streamlit):
        """Test that unordered list uses <ul> tag in export."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=True), \
             patch("streamtex.list.export_push_wrapper") as mock_push, \
             patch("streamtex.list.export_pop_wrapper") as mock_pop:

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(list_type=ListTypes.unordered):
                pass

            # Check that <ul> was used
            push_call_args = mock_push.call_args[0][0]
            pop_call_args = mock_pop.call_args[0][0]
            assert "<ul" in push_call_args
            assert "</ul>" in pop_call_args


class TestListControllerItemExport:
    """Tests for ListController.item() export behavior."""

    def test_list_item_export_uses_li_tag(self, mock_streamlit):
        """Test that list item uses <li> tag in export."""
        controller = ListController(StxStyles.none, "'●'", is_ordered=False)

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=True), \
             patch("streamtex.list.export_push_wrapper") as mock_push, \
             patch("streamtex.list.export_pop_wrapper") as mock_pop:

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with controller.item():
                pass

            # Verify <li> tag was used
            push_call_args = mock_push.call_args[0][0]
            pop_call_args = mock_pop.call_args[0][0]
            assert "<li" in push_call_args
            assert "</li>" in pop_call_args

    def test_list_item_export_inactive_does_not_call_wrappers(self, mock_streamlit):
        """Test that export wrappers are not called when export is inactive."""
        controller = ListController(StxStyles.none, "'●'", is_ordered=False)

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False), \
             patch("streamtex.list.export_push_wrapper") as mock_push, \
             patch("streamtex.list.export_pop_wrapper") as mock_pop:

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with controller.item():
                pass

            # Verify export wrappers were NOT called
            assert not mock_push.called
            assert not mock_pop.called


class TestListOrderedCounter:
    """Tests for ordered list counter behavior."""

    def test_ordered_list_default_counter_style(self, mock_streamlit):
        """Test that ordered list uses decimal counter by default."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(list_type=ListTypes.ordered) as controller:
                assert "counter(streamtex-counter, decimal)" in controller.bullet_content

    def test_ordered_list_custom_counter_style(self, mock_streamlit):
        """Test that ordered list can use custom counter style."""
        custom_style = Style("list-style-type: roman;", "roman_style")

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(list_type=ListTypes.ordered, l_style=custom_style) as controller:
                # Should extract counter style from l_style
                assert "counter(streamtex-counter, roman)" in controller.bullet_content or \
                       "counter(streamtex-counter, decimal)" in controller.bullet_content


class TestListAlign:
    """Tests for the align parameter of st_list."""

    def test_st_list_default_align_none(self, mock_streamlit):
        """Test that align defaults to None — no data-stx-list-width attribute."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list() as controller:
                pass

            marker = mock_html.call_args_list[0][0][0]
            assert "data-stx-list-width" not in marker
            # The default width (100%) lives in the global stylesheet.

    def test_st_list_align_center(self, mock_streamlit):
        """Test that align='center' forwards data-stx-list-width=fit-content."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(align="center") as controller:
                pass

            marker = mock_html.call_args_list[0][0][0]
            assert 'data-stx-list-width="fit-content"' in marker
            # The global stylesheet rule converts that into
            # `width: fit-content; margin-inline: auto`.

    def test_st_list_align_does_not_affect_controller(self, mock_streamlit):
        """Test that align parameter does not change the ListController."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(align="center") as controller:
                assert isinstance(controller, ListController)
                assert controller.bullet_content == "'•'"
                assert controller.is_ordered is False


class TestListCssGeneration:
    """Tests for CSS generation in st_list."""

    def test_st_list_generates_css(self, mock_streamlit):
        """Test that st_list generates and renders CSS."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list():
                pass

            # Verify that st.html was called for CSS
            assert mock_html.called

    def test_list_item_generates_css(self, mock_streamlit):
        """Test that ListController.item() generates and renders CSS."""
        controller = ListController(StxStyles.none, "'●'", is_ordered=False)

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with controller.item():
                pass

            # Verify that st.html was called for CSS
            assert mock_html.called


class TestAltLiStyles:
    """Tests for the alt_li_styles feature."""

    def test_controller_stores_alt_li_styles(self):
        """Test that ListController stores alt_li_styles and initializes index."""
        styles = [Style("color: red;", "red"), Style("color: blue;", "blue")]
        ctrl = ListController(StxStyles.none, "'•'", is_ordered=False, alt_li_styles=styles)

        assert ctrl.alt_li_styles is styles
        assert ctrl._item_index == 0

    def test_controller_default_alt_li_styles_none(self):
        """Test that alt_li_styles defaults to None."""
        ctrl = ListController(StxStyles.none, "'•'", is_ordered=False)

        assert ctrl.alt_li_styles is None
        assert ctrl._item_index == 0

    def test_item_cycles_through_alt_styles(self, mock_streamlit):
        """Test that item() cycles through alt_li_styles."""
        s1 = Style("color: red;", "red")
        s2 = Style("color: blue;", "blue")
        ctrl = ListController(StxStyles.none, "'•'", is_ordered=False, alt_li_styles=[s1, s2])

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            # First item → s1 (index 0)
            with ctrl.item():
                pass
            call1_style = mock_st_block.call_args_list[0][1]["style"]
            assert "color: red" in str(call1_style)

            # Second item → s2 (index 1)
            with ctrl.item():
                pass
            call2_style = mock_st_block.call_args_list[1][1]["style"]
            assert "color: blue" in str(call2_style)

            # Third item → s1 again (index 2 % 2 = 0)
            with ctrl.item():
                pass
            call3_style = mock_st_block.call_args_list[2][1]["style"]
            assert "color: red" in str(call3_style)

        assert ctrl._item_index == 3

    def test_item_index_increments(self, mock_streamlit):
        """Test that _item_index increments after each item() call."""
        s1 = Style("color: red;", "red")
        ctrl = ListController(StxStyles.none, "'•'", is_ordered=False, alt_li_styles=[s1])

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            assert ctrl._item_index == 0
            with ctrl.item():
                pass
            assert ctrl._item_index == 1
            with ctrl.item():
                pass
            assert ctrl._item_index == 2

    def test_alt_style_merges_with_li_style(self, mock_streamlit):
        """Test that alt style is merged after li_style."""
        li = Style("font-size: 14px;", "base")
        alt = Style("color: green;", "green")
        ctrl = ListController(li, "'•'", is_ordered=False, alt_li_styles=[alt])

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with ctrl.item():
                pass

            final = mock_st_block.call_args_list[0][1]["style"]
            final_str = str(final)
            assert "font-size: 14px" in final_str
            assert "color: green" in final_str

    def test_per_item_style_overrides_alt(self, mock_streamlit):
        """Test that per-item style is applied after alt_li_styles (highest priority)."""
        alt = Style("color: red;", "red")
        per_item = Style("color: blue;", "blue")
        ctrl = ListController(StxStyles.none, "'•'", is_ordered=False, alt_li_styles=[alt])

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with ctrl.item(style=per_item):
                pass

            final = mock_st_block.call_args_list[0][1]["style"]
            # Both colors should be present in the CSS chain
            final_str = str(final)
            assert "color: red" in final_str
            assert "color: blue" in final_str

    def test_no_alt_styles_preserves_behavior(self, mock_streamlit):
        """Test that without alt_li_styles, behavior is unchanged."""
        li = Style("font-weight: bold;", "bold")
        ctrl = ListController(li, "'•'", is_ordered=False, alt_li_styles=None)

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.container") as mock_container, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st_block.return_value.__enter__ = MagicMock()
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with ctrl.item():
                pass

            final = mock_st_block.call_args_list[0][1]["style"]
            assert "font-weight: bold" in str(final)
            assert ctrl._item_index == 0  # No increment when alt_li_styles is None

    def test_st_list_passes_alt_li_styles(self, mock_streamlit):
        """Test that st_list passes alt_li_styles to ListController."""
        styles = [Style("color: red;", "red"), Style("color: blue;", "blue")]

        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list(alt_li_styles=styles) as ctrl:
                assert ctrl.alt_li_styles is styles

    def test_st_list_default_no_alt_li_styles(self, mock_streamlit):
        """Test that st_list defaults to no alt_li_styles."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):

            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)

            with st_list() as ctrl:
                assert ctrl.alt_li_styles is None


# ===========================================================================
# Phase 2 — marker-runtime path (STX_USE_MARKER_RUNTIME=1)
# ===========================================================================
#
# Validates that st_list / ListController.item emit sentinel marker spans
# (`data-stx-kind="list"`, `data-stx-kind="list-item"`) instead of the
# legacy :has() stylesheets when the marker runtime is enabled.


@pytest.fixture
def _marker_runtime_on():
    prev_legacy = os.environ.get("STX_USE_LEGACY_HAS")
    prev_marker = os.environ.get("STX_USE_MARKER_RUNTIME")
    os.environ.pop("STX_USE_LEGACY_HAS", None)
    os.environ["STX_USE_MARKER_RUNTIME"] = "1"
    yield
    if prev_legacy is None:
        os.environ.pop("STX_USE_LEGACY_HAS", None)
    else:
        os.environ["STX_USE_LEGACY_HAS"] = prev_legacy
    if prev_marker is None:
        os.environ.pop("STX_USE_MARKER_RUNTIME", None)
    else:
        os.environ["STX_USE_MARKER_RUNTIME"] = prev_marker


def _collect_html(mock_streamlit):
    """Concatenate every st.html() call argument seen by the mock."""
    return "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)


class TestStListMarkerPath:
    def test_emits_list_marker(self, mock_streamlit, _marker_runtime_on):
        with st_list() as _:
            pass
        joined = _collect_html(mock_streamlit)
        assert 'data-stx-kind="list"' in joined
        assert 'data-stx-uid="ul-' in joined

    def test_no_has_selector_in_list_root(self, mock_streamlit, _marker_runtime_on):
        with st_list():
            pass
        joined = _collect_html(mock_streamlit)
        assert ":has(" not in joined

    def test_align_center_carries_width_data_attr(self, mock_streamlit, _marker_runtime_on):
        with st_list(align="center"):
            pass
        joined = _collect_html(mock_streamlit)
        assert 'data-stx-list-width="fit-content"' in joined


class TestListItemMarkerPath:
    def test_emits_list_item_marker(self, mock_streamlit, _marker_runtime_on):
        with st_list() as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        assert 'data-stx-kind="list-item"' in joined
        assert 'data-stx-uid="li-' in joined

    def test_unordered_item_does_not_set_ordered_attr(self, mock_streamlit, _marker_runtime_on):
        with st_list() as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        assert "data-stx-ordered" not in joined

    def test_ordered_item_sets_ordered_attr(self, mock_streamlit, _marker_runtime_on):
        with st_list(list_type=ListTypes.ordered) as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        assert "data-stx-ordered" in joined

    def test_bullet_uses_per_item_attribute_selector(self, mock_streamlit, _marker_runtime_on):
        """The bullet `content:` value is injected as a per-item stylesheet
        keyed by [data-stx-list-item-uid=…] — not a :has() selector."""
        with st_list() as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        assert '[data-stx-list-item-uid="li-' in joined
        assert "content:" in joined
        assert ":has(" not in joined

    def test_ordered_bullet_contains_counter(self, mock_streamlit, _marker_runtime_on):
        with st_list(list_type=ListTypes.ordered) as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        assert "counter(streamtex-counter" in joined

    def test_unordered_bullet_contains_dot(self, mock_streamlit, _marker_runtime_on):
        with st_list() as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        # Default level-1 unordered bullet is `'•'`.
        assert "'•'" in joined


class TestListAlignmentParameters:
    """0.7.33 — text_align (text) and block_align (box) are distinct notions."""

    @staticmethod
    def _marker(mock_html):
        return mock_html.call_args_list[0][0][0]

    @staticmethod
    def _run(**kwargs):
        """Open a list with *kwargs* and return (marker_html, pushed_wrappers)."""
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html") as mock_html, \
             patch("streamtex.list.is_export_active", return_value=True), \
             patch("streamtex.list.export_push_wrapper") as mock_push, \
             patch("streamtex.list.export_pop_wrapper"):
            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)
            with st_list(**kwargs):
                pass
            pushed = [c[0][0] for c in mock_push.call_args_list]
            return mock_html.call_args_list[0][0][0], pushed

    # --- text_align: text only, never a width ---------------------------
    @pytest.mark.parametrize("value", ["left", "center", "right", "justify"])
    def test_text_align_only_declares_the_alignment(self, mock_streamlit, value):
        """0.7.34 — the marker mode is no longer carried by the sentinel span.

        It follows the item's EFFECTIVE alignment, which the observer reads
        from the computed style, so the span declares the alignment and
        nothing else — and above all no width.
        """
        marker, _ = self._run(text_align=value)
        assert f'data-stx-list-text-align="{value}"' in marker
        assert "data-stx-list-justify" not in marker
        assert "data-stx-list-grow" not in marker
        assert "data-stx-list-width" not in marker, "text_align must not touch the width"

    def test_no_parameter_emits_no_alignment_attribute(self, mock_streamlit):
        marker, _ = self._run()
        for attr in ("text-align", "justify", "grow", "width", "margin-inline"):
            assert f"data-stx-list-{attr}" not in marker

    # --- block_align: the box, hence a content-driven width -------------
    @pytest.mark.parametrize("value,margin", [
        ("center", "auto"), ("left", "0 auto"), ("right", "auto 0"),
    ])
    def test_block_align_sets_width_and_margins(self, mock_streamlit, value, margin):
        marker, _ = self._run(block_align=value)
        assert 'data-stx-list-width="fit-content"' in marker
        assert f'data-stx-list-margin-inline="{margin}"' in marker
        assert "data-stx-list-text-align" not in marker, "block_align must not touch the text"

    def test_align_is_a_synonym_of_block_align(self, mock_streamlit):
        legacy, _ = self._run(align="center")
        modern, _ = self._run(block_align="center")
        strip = lambda m: m.split('data-stx-uid="')[1].split('"', 1)[1]  # noqa: E731
        assert strip(legacy) == strip(modern)

    def test_block_align_wins_over_the_deprecated_align(self, mock_streamlit):
        marker, _ = self._run(block_align="right", align="center")
        assert 'data-stx-list-margin-inline="auto 0"' in marker

    # --- validation ------------------------------------------------------
    @pytest.mark.parametrize("kwargs", [
        {"text_align": "middle"}, {"block_align": "justify"}, {"align": "top"},
    ])
    def test_unknown_value_raises_value_error(self, mock_streamlit, kwargs):
        with pytest.raises(ValueError, match="unknown value"):
            self._run(**kwargs)

    # --- export ----------------------------------------------------------
    def test_export_emits_list_style_position_inside(self, mock_streamlit):
        _, pushed = self._run(text_align="center")
        assert "text-align: center;" in pushed[0]
        assert "list-style-position: inside;" in pushed[0]
        assert "fit-content" not in pushed[0]

    def test_export_left_align_has_no_inside_marker(self, mock_streamlit):
        _, pushed = self._run(text_align="left")
        assert "text-align: left;" in pushed[0]
        assert "list-style-position" not in pushed[0]

    def test_export_block_align_emits_fit_content(self, mock_streamlit):
        _, pushed = self._run(block_align="center")
        assert "width: fit-content;" in pushed[0]
        assert "margin-inline: auto;" in pushed[0]

    def test_export_merges_with_the_user_style(self, mock_streamlit):
        _, pushed = self._run(l_style=Style("color: red", "t_red"), text_align="center")
        assert "color: red;" in pushed[0]
        assert "text-align: center;" in pushed[0]

    def test_export_without_alignment_is_unchanged(self, mock_streamlit):
        _, pushed = self._run(l_style=Style("color: red", "t_red2"))
        assert pushed[0] == '<ul style="color: red">'

    # --- the left-align floor is gone ------------------------------------
    def test_list_root_no_longer_forces_text_align_left(self, mock_streamlit):
        with patch("streamtex.list.st_block") as mock_st_block, \
             patch("streamtex.list.st.html"), \
             patch("streamtex.list.is_export_active", return_value=False):
            mock_st_block.return_value.__enter__ = MagicMock(return_value=None)
            mock_st_block.return_value.__exit__ = MagicMock(return_value=False)
            with st_list():
                pass
            style = mock_st_block.call_args.kwargs["style"]
            assert "text-align" not in str(style)


class TestInsideMarkerFollowsEffectiveAlignment:
    """0.7.34 — the marker joins the first line whenever the EFFECTIVE
    alignment is centre/right, whether declared or inherited.

    The decision cannot be made in Python (an inherited value is only known
    to the browser), so the contract is split across three files and each
    half is pinned here: list.py emits the bullet for both pseudo-elements,
    the observer stamps ``.stx-list-item--inside`` from the computed style,
    and the stylesheet shows exactly one of the two markers.
    """

    CSS = (Path(__file__).resolve().parents[1]
           / "streamtex" / "static" / "css" / "stx_global.css").read_text(encoding="utf-8")
    JS = (Path(__file__).resolve().parents[1]
          / "streamtex" / "static" / "js" / "stx_marker_observer.js").read_text(encoding="utf-8")

    # --- list.py: one `content`, two pseudo-elements --------------------
    def test_bullet_content_is_declared_for_both_markers(self, mock_streamlit,
                                                         _marker_runtime_on):
        with st_list() as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        assert '[data-stx-list-item-uid="li-' in joined
        # the outside marker, on the item row
        assert "::before, " in joined
        # the inside marker, on the item's content wrapper (both Streamlit shapes)
        assert '> [data-testid="stVerticalBlock"]::before' in joined
        assert ('> [data-testid="stLayoutWrapper"] > '
                '[data-testid="stVerticalBlock"]::before') in joined
        assert joined.count("content:") == 1, "one declaration must serve both markers"

    def test_ordered_counter_reaches_the_inside_marker(self, mock_streamlit,
                                                       _marker_runtime_on):
        with st_list(list_type=ListTypes.ordered) as lst:
            with lst.item():
                pass
        joined = _collect_html(mock_streamlit)
        assert joined.count("counter(streamtex-counter") == 1
        assert '> [data-testid="stVerticalBlock"]::before' in joined

    # --- the observer: computed, not declared ---------------------------
    def test_observer_reads_the_computed_alignment(self):
        assert "computedModifiers: { 'stx-list-item--inside': isInsideAligned }" in self.JS
        assert "getComputedStyle(el).textAlign" in self.JS
        # `start` is what Chromium reports for the initial value — it must NOT
        # switch the mode on, or every plain list would change.
        assert "var INSIDE_ALIGNS = { 'center': 1, 'right': 1, 'end': 1 };" in self.JS

    def test_observer_undoes_the_computed_modifier(self):
        """clearMarker must strip it, like every other thing applyMarker adds —
        otherwise a DOM node reused by Streamlit for another construct keeps
        an inside marker that no longer belongs to it (the 0.6.27 bleed)."""
        clear = self.JS.split("function clearMarker")[1]
        assert "spec.computedModifiers" in clear
        assert "parent.classList.remove(compCls)" in clear

    def test_observer_repropagates_when_a_list_changes_alignment(self):
        assert "syncsItemAlign: true" in self.JS
        assert "function syncItemAlignModes" in self.JS

    # --- the stylesheet: exactly one marker, no width change ------------
    def test_outside_mode_hides_the_inside_marker(self):
        assert ('[data-testid="stVerticalBlock"].stx-list-item > '
                '[data-testid="stVerticalBlock"]::before') in self.CSS

    def test_inside_mode_hides_the_outside_marker(self):
        assert '.stx-list-item--inside::before' in self.CSS
        outside = self.CSS.index('.stx-list-item > [data-testid="stVerticalBlock"]::before')
        inside = self.CSS.index('.stx-list-item--inside::before')
        assert inside > outside, (
            "the two modes have the same specificity: the inside rules must come "
            "last or they never win"
        )

    def test_the_content_wrapper_always_keeps_the_full_width(self):
        """The 0.7.33 procedure shrank the text cell (`--stx-list-grow: 0`),
        which also shrank every nested list inside it."""
        assert "var(--stx-list-grow" not in self.CSS
        assert "var(--stx-list-justify" not in self.CSS
        assert "flex-grow: 1;" in self.CSS

    def test_the_first_cell_joins_the_marker_line(self):
        assert '.stx-list-item--inside > [data-testid="stLayoutWrapper"] > ' \
               '[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]' \
               ':first-child' in self.CSS
        assert "display: inline;" in self.CSS
