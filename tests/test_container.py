"""Tests for streamtex.container — st_block and st_span context managers."""

from unittest.mock import MagicMock, patch

from streamtex.container import st_block, st_span
from streamtex.export import ExportConfig, reset_export_buffer
from streamtex.styles import Style


class TestStBlockBasic:
    """Tests for st_block without export."""

    def setup_method(self):
        """Reset export buffer before each test."""
        reset_export_buffer(None)

    def teardown_method(self):
        """Clean up after each test."""
        reset_export_buffer(None)

    def test_st_block_generates_css(self, mock_streamlit):
        """st_block should generate CSS with style applied."""
        style = Style("color: red;", "red_text")

        with st_block(style):
            pass

        # Verify st.html was called for CSS injection
        assert mock_streamlit["html"].call_count >= 1

        # First call should be CSS injection
        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # CSS should contain style tags
        assert "<style>" in css_content
        assert "</style>" in css_content

        # CSS should contain the injected style
        assert "color: red;" in css_content

    def test_st_block_uses_default_style(self, mock_streamlit):
        """st_block should use StxStyles.none by default."""
        with st_block():
            pass

        # Verify st.html was called
        assert mock_streamlit["html"].call_count >= 1
        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should contain style tags
        assert "<style>" in css_content

    def test_st_block_generates_unique_block_id(self, mock_streamlit):
        """st_block should generate a unique ID for each block."""
        with st_block():
            pass

        block_ids = []
        for call_args in mock_streamlit["html"].call_args_list:
            html_content = call_args[0][0]
            if "block-" in html_content:
                # Extract block IDs
                import re
                matches = re.findall(r'block-[a-f0-9]+', html_content)
                block_ids.extend(matches)

        # Should have at least one block ID
        assert len(block_ids) > 0
        # All block IDs in the same block should be the same
        assert len(set(block_ids)) == 1

    def test_st_block_different_ids_for_different_blocks(self, mock_streamlit):
        """Different st_block calls should generate different IDs."""
        import re

        block_ids_list = []

        for _ in range(2):
            with st_block():
                pass

            # Extract block IDs from all calls
            block_ids = set()
            for call_args in mock_streamlit["html"].call_args_list:
                html_content = call_args[0][0]
                if "block-" in html_content:
                    matches = re.findall(r'block-[a-f0-9]+', html_content)
                    block_ids.update(matches)

            if block_ids:
                block_ids_list.append(block_ids)

        # Should have different IDs for different blocks
        if len(block_ids_list) >= 2:
            assert block_ids_list[0] != block_ids_list[1]

    def test_st_block_creates_streamlit_container(self, mock_streamlit):
        """st_block should create a Streamlit container."""
        with patch("streamlit.container") as mock_container:
            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock()

            with st_block():
                pass

            # Container should be called
            mock_container.assert_called()

    def test_st_block_inserts_marker_span(self, mock_streamlit):
        """st_block should insert a marker span element."""
        with st_block():
            pass

        # Find the marker span call
        marker_found = False
        for call_args in mock_streamlit["html"].call_args_list:
            html_content = call_args[0][0]
            if '<span class="block-' in html_content and 'style="display:none;"' in html_content:
                marker_found = True
                break

        assert marker_found, "Marker span not found in st.html calls"

    def test_st_block_uses_has_selector(self, mock_streamlit):
        """st_block CSS should use :has() selector."""
        with st_block():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should use :has() selector
        assert ":has(" in css_content

    def test_st_block_width_auto(self, mock_streamlit):
        """st_block CSS should set width: auto."""
        with st_block():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should set width: auto
        assert "width: auto" in css_content


class TestStSpanBasic:
    """Tests for st_span without export."""

    def setup_method(self):
        """Reset export buffer before each test."""
        reset_export_buffer(None)

    def teardown_method(self):
        """Clean up after each test."""
        reset_export_buffer(None)

    def test_st_span_generates_css(self, mock_streamlit):
        """st_span should generate CSS with style applied."""
        style = Style("color: blue;", "blue_text")

        with st_span(style):
            pass

        # Verify st.html was called for CSS injection
        assert mock_streamlit["html"].call_count >= 1

        # First call should be CSS injection
        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # CSS should contain style tags
        assert "<style>" in css_content
        assert "</style>" in css_content

        # CSS should contain the injected style
        assert "color: blue;" in css_content

    def test_st_span_uses_default_style(self, mock_streamlit):
        """st_span should use StxStyles.none by default."""
        with st_span():
            pass

        # Verify st.html was called
        assert mock_streamlit["html"].call_count >= 1
        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should contain style tags
        assert "<style>" in css_content

    def test_st_span_sets_display_flex(self, mock_streamlit):
        """st_span CSS should set display: flex."""
        with st_span():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should set display: flex
        assert "display: flex" in css_content

    def test_st_span_sets_flex_direction_row(self, mock_streamlit):
        """st_span CSS should set flex-direction: row."""
        with st_span():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should set flex-direction: row
        assert "flex-direction: row" in css_content

    def test_st_span_preserves_whitespace(self, mock_streamlit):
        """st_span CSS should set white-space: pre."""
        with st_span():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should set white-space: pre
        assert "white-space: pre" in css_content

    def test_st_span_generates_unique_span_id(self, mock_streamlit):
        """st_span should generate a unique ID for each span."""
        with st_span():
            pass

        span_ids = []
        for call_args in mock_streamlit["html"].call_args_list:
            html_content = call_args[0][0]
            if "span-" in html_content:
                # Extract span IDs
                import re
                matches = re.findall(r'span-[a-f0-9]+', html_content)
                span_ids.extend(matches)

        # Should have at least one span ID
        assert len(span_ids) > 0

    def test_st_span_width_auto(self, mock_streamlit):
        """st_span CSS should set width: auto for elements."""
        with st_span():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should set width: auto
        assert "width: auto" in css_content

    def test_st_span_inserts_marker_span(self, mock_streamlit):
        """st_span should insert a marker span element."""
        with st_span():
            pass

        # Find the marker span call
        marker_found = False
        for call_args in mock_streamlit["html"].call_args_list:
            html_content = call_args[0][0]
            if '<span class="span-' in html_content and 'style="display:none;"' in html_content:
                marker_found = True
                break

        assert marker_found, "Marker span not found in st.html calls"


class TestStBlockExport:
    """Tests for st_block with export enabled."""

    def setup_method(self):
        """Reset export buffer before each test."""
        reset_export_buffer(None)

    def teardown_method(self):
        """Clean up after each test."""
        reset_export_buffer(None)

    def test_st_block_inactive_export_noop(self, mock_streamlit):
        """st_block should not push/pop when export is inactive."""
        reset_export_buffer(ExportConfig(enabled=False))

        with patch("streamtex.container.export_push_wrapper") as mock_push, \
             patch("streamtex.container.export_pop_wrapper") as mock_pop:
            with st_block():
                pass

            # Should not call push/pop when export is inactive
            mock_push.assert_not_called()
            mock_pop.assert_not_called()

    def test_st_block_active_export_pushes_wrapper(self, mock_streamlit):
        """st_block should push wrapper when export is active."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_push_wrapper") as mock_push:
            style = Style("color: red;", "red")
            with st_block(style):
                pass

            # Should push wrapper
            mock_push.assert_called_once()
            # Check that it contains the style
            call_arg = mock_push.call_args[0][0]
            assert 'style=' in call_arg or 'div' in call_arg

    def test_st_block_active_export_pops_wrapper(self, mock_streamlit):
        """st_block should pop wrapper when export is active."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_pop_wrapper") as mock_pop:
            with st_block():
                pass

            # Should pop wrapper
            mock_pop.assert_called_once()
            # Should pop with </div>
            call_arg = mock_pop.call_args[0][0]
            assert "</div>" in call_arg

    def test_st_block_export_wrapper_contains_style(self, mock_streamlit):
        """st_block export wrapper should include the style."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_push_wrapper") as mock_push:
            style = Style("color: green; font-weight: bold;", "green_bold")
            with st_block(style):
                pass

            call_arg = mock_push.call_args[0][0]
            # Should contain div with style
            assert "color: green;" in call_arg or "green" in call_arg

    def test_st_block_export_wrapper_false_skips_wrapper(self, mock_streamlit):
        """st_block with _export_wrapper=False should not push/pop."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_push_wrapper") as mock_push, \
             patch("streamtex.container.export_pop_wrapper") as mock_pop:
            with st_block(_export_wrapper=False):
                pass

            # Should not push/pop when _export_wrapper=False
            mock_push.assert_not_called()
            mock_pop.assert_not_called()

    def test_st_block_push_pop_order(self, mock_streamlit):
        """st_block should push before content and pop after."""
        reset_export_buffer(ExportConfig(enabled=True))

        call_order = []

        def track_push(arg):
            call_order.append(("push", arg))

        def track_pop(arg):
            call_order.append(("pop", arg))

        with patch("streamtex.container.export_push_wrapper", side_effect=track_push), \
             patch("streamtex.container.export_pop_wrapper", side_effect=track_pop):
            with st_block():
                call_order.append(("content",))

        # Should be: push, content, pop
        assert len(call_order) == 3
        assert call_order[0][0] == "push"
        assert call_order[1][0] == "content"
        assert call_order[2][0] == "pop"


class TestStSpanExport:
    """Tests for st_span with export enabled."""

    def setup_method(self):
        """Reset export buffer before each test."""
        reset_export_buffer(None)

    def teardown_method(self):
        """Clean up after each test."""
        reset_export_buffer(None)

    def test_st_span_inactive_export_noop(self, mock_streamlit):
        """st_span should not push/pop when export is inactive."""
        reset_export_buffer(ExportConfig(enabled=False))

        with patch("streamtex.container.export_push_wrapper") as mock_push, \
             patch("streamtex.container.export_pop_wrapper") as mock_pop:
            with st_span():
                pass

            # Should not call push/pop when export is inactive
            mock_push.assert_not_called()
            mock_pop.assert_not_called()

    def test_st_span_active_export_pushes_wrapper(self, mock_streamlit):
        """st_span should push wrapper when export is active."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_push_wrapper") as mock_push:
            style = Style("color: blue;", "blue")
            with st_span(style):
                pass

            # Should push wrapper
            mock_push.assert_called_once()
            call_arg = mock_push.call_args[0][0]
            # Should contain flex display
            assert "display:flex" in call_arg or "flex" in call_arg

    def test_st_span_active_export_pops_wrapper(self, mock_streamlit):
        """st_span should pop wrapper when export is active."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_pop_wrapper") as mock_pop:
            with st_span():
                pass

            # Should pop wrapper
            mock_pop.assert_called_once()
            # Should pop with </div>
            call_arg = mock_pop.call_args[0][0]
            assert "</div>" in call_arg

    def test_st_span_export_wrapper_includes_flex(self, mock_streamlit):
        """st_span export wrapper should include flex display."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_push_wrapper") as mock_push:
            with st_span():
                pass

            call_arg = mock_push.call_args[0][0]
            # Should contain flex direction row
            assert "flex-direction:row" in call_arg or "flex" in call_arg

    def test_st_span_export_wrapper_includes_whitespace(self, mock_streamlit):
        """st_span export wrapper should include white-space: pre."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_push_wrapper") as mock_push:
            with st_span():
                pass

            call_arg = mock_push.call_args[0][0]
            # Should contain white-space: pre
            assert "white-space:pre" in call_arg or "pre" in call_arg

    def test_st_span_export_wrapper_contains_style(self, mock_streamlit):
        """st_span export wrapper should include the style."""
        reset_export_buffer(ExportConfig(enabled=True))

        with patch("streamtex.container.export_push_wrapper") as mock_push:
            style = Style("color: orange;", "orange")
            with st_span(style):
                pass

            call_arg = mock_push.call_args[0][0]
            # Should contain the style
            assert "color: orange;" in call_arg or "orange" in call_arg

    def test_st_span_push_pop_order(self, mock_streamlit):
        """st_span should push before content and pop after."""
        reset_export_buffer(ExportConfig(enabled=True))

        call_order = []

        def track_push(arg):
            call_order.append(("push", arg))

        def track_pop(arg):
            call_order.append(("pop", arg))

        with patch("streamtex.container.export_push_wrapper", side_effect=track_push), \
             patch("streamtex.container.export_pop_wrapper", side_effect=track_pop):
            with st_span():
                call_order.append(("content",))

        # Should be: push, content, pop
        assert len(call_order) == 3
        assert call_order[0][0] == "push"
        assert call_order[1][0] == "content"
        assert call_order[2][0] == "pop"


class TestStBlockEdgeCases:
    """Edge cases and error handling for st_block."""

    def setup_method(self):
        """Reset export buffer before each test."""
        reset_export_buffer(None)

    def teardown_method(self):
        """Clean up after each test."""
        reset_export_buffer(None)

    def test_st_block_empty_style(self, mock_streamlit):
        """st_block should handle empty style."""
        empty_style = Style("", "empty")

        with st_block(empty_style):
            pass

        # Should still generate CSS without errors
        assert mock_streamlit["html"].call_count >= 1

    def test_st_block_complex_style(self, mock_streamlit):
        """st_block should handle complex multi-property styles."""
        complex_style = Style(
            "color: red; background: blue; padding: 10px; margin: 5px; border: 1px solid black;",
            "complex"
        )

        with st_block(complex_style):
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should contain all properties
        assert "color: red;" in css_content
        assert "background: blue;" in css_content

    def test_st_block_multiple_calls_independent(self, mock_streamlit):
        """Multiple st_block calls should be independent."""
        style1 = Style("color: red;", "red")
        style2 = Style("color: blue;", "blue")

        with st_block(style1):
            pass

        mock_streamlit["html"].reset_mock()

        with st_block(style2):
            pass

        # Second block should have different style
        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        assert "color: blue;" in css_content


class TestStSpanEdgeCases:
    """Edge cases and error handling for st_span."""

    def setup_method(self):
        """Reset export buffer before each test."""
        reset_export_buffer(None)

    def teardown_method(self):
        """Clean up after each test."""
        reset_export_buffer(None)

    def test_st_span_empty_style(self, mock_streamlit):
        """st_span should handle empty style."""
        empty_style = Style("", "empty")

        with st_span(empty_style):
            pass

        # Should still generate CSS without errors
        assert mock_streamlit["html"].call_count >= 1

    def test_st_span_complex_style(self, mock_streamlit):
        """st_span should handle complex multi-property styles."""
        complex_style = Style(
            "color: green; font-size: 14pt; font-weight: bold; letter-spacing: 2px;",
            "complex"
        )

        with st_span(complex_style):
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Should contain all properties
        assert "color: green;" in css_content
        assert "font-size: 14pt;" in css_content

    def test_st_span_multiple_calls_independent(self, mock_streamlit):
        """Multiple st_span calls should be independent."""
        style1 = Style("color: red;", "red")
        style2 = Style("color: blue;", "blue")

        with st_span(style1):
            pass

        mock_streamlit["html"].reset_mock()

        with st_span(style2):
            pass

        # Second span should have different style
        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        assert "color: blue;" in css_content

    def test_st_span_nested_in_block(self, mock_streamlit):
        """st_span should work nested inside st_block."""
        block_style = Style("color: red;", "red")
        span_style = Style("font-weight: bold;", "bold")

        with st_block(block_style):
            with st_span(span_style):
                pass

        # Should have st.html calls (fused CSS+marker for block + fused CSS+marker for span)
        assert mock_streamlit["html"].call_count >= 2


class TestContainerCssStructure:
    """Tests for CSS structure and selectors."""

    def setup_method(self):
        """Reset export buffer before each test."""
        reset_export_buffer(None)

    def teardown_method(self):
        """Clean up after each test."""
        reset_export_buffer(None)

    def test_st_block_css_has_element_container_selector(self, mock_streamlit):
        """st_block CSS should have .element-container selector."""
        with st_block():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        assert ".element-container" in css_content

    def test_st_block_css_has_stHtml_selector(self, mock_streamlit):
        """st_block CSS should have .stHtml selector."""
        with st_block():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        assert ".stHtml" in css_content

    def test_st_span_css_has_element_container_selector(self, mock_streamlit):
        """st_span CSS should have .element-container selector."""
        with st_span():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        assert ".element-container" in css_content

    def test_st_span_css_has_stHtml_selector(self, mock_streamlit):
        """st_span CSS should have .stHtml selector."""
        with st_span():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        assert ".stHtml" in css_content

    def test_st_block_css_well_formed(self, mock_streamlit):
        """st_block CSS should be well-formed."""
        with st_block():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Count opening and closing braces
        open_braces = css_content.count("{")
        close_braces = css_content.count("}")

        assert open_braces == close_braces

    def test_st_span_css_well_formed(self, mock_streamlit):
        """st_span CSS should be well-formed."""
        with st_span():
            pass

        css_call = mock_streamlit["html"].call_args_list[0]
        css_content = css_call[0][0]

        # Count opening and closing braces
        open_braces = css_content.count("{")
        close_braces = css_content.count("}")

        assert open_braces == close_braces
