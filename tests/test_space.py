"""Unit tests for streamtex.space — vertical and horizontal spacing."""

from unittest.mock import patch

from streamtex.space import st_br, st_space


class TestStSpace:
    """Tests for st_space function."""

    def test_vertical_space_with_int_size(self):
        """Test st_space('v', 2) generates <div style='height: 2em;'></div>"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 2)
            mock_render.assert_called_once_with('<div style="height: 2em;"></div>')

    def test_horizontal_space_with_int_size(self):
        """Test st_space('h', 3) generates <span style='padding-left: 3em;'></span>"""
        with patch('streamtex.space._render') as mock_render:
            st_space("h", 3)
            mock_render.assert_called_once_with('<span style="padding-left: 3em;"></span>')

    def test_vertical_space_with_string_size(self):
        """Test st_space('v', '20px') uses the string value directly"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", "20px")
            mock_render.assert_called_once_with('<div style="height: 20px;"></div>')

    def test_horizontal_space_with_string_size(self):
        """Test st_space('h', '15px') uses the string value directly"""
        with patch('streamtex.space._render') as mock_render:
            st_space("h", "15px")
            mock_render.assert_called_once_with('<span style="padding-left: 15px;"></span>')

    def test_default_direction_is_vertical(self):
        """Test st_space() defaults to vertical spacing with '1em'"""
        with patch('streamtex.space._render') as mock_render:
            st_space()
            mock_render.assert_called_once_with('<div style="height: 1em;"></div>')

    def test_default_size_is_1em(self):
        """Test st_space('v') uses default size of '1em'"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v")
            mock_render.assert_called_once_with('<div style="height: 1em;"></div>')

    def test_default_size_horizontal(self):
        """Test st_space('h') uses default size of '1em' with horizontal orientation"""
        with patch('streamtex.space._render') as mock_render:
            st_space("h")
            mock_render.assert_called_once_with('<span style="padding-left: 1em;"></span>')

    def test_vertical_space_zero_size(self):
        """Test st_space('v', 0) generates <div style='height: 0em;'></div>"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 0)
            mock_render.assert_called_once_with('<div style="height: 0em;"></div>')

    def test_horizontal_space_zero_size(self):
        """Test st_space('h', 0) generates <span style='padding-left: 0em;'></span>"""
        with patch('streamtex.space._render') as mock_render:
            st_space("h", 0)
            mock_render.assert_called_once_with('<span style="padding-left: 0em;"></span>')

    def test_large_int_size(self):
        """Test st_space with large integer size (100)"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 100)
            mock_render.assert_called_once_with('<div style="height: 100em;"></div>')

    def test_float_size_string(self):
        """Test st_space with float size as string"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", "1.5em")
            mock_render.assert_called_once_with('<div style="height: 1.5em;"></div>')

    def test_rem_unit_size(self):
        """Test st_space with rem units"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", "2rem")
            mock_render.assert_called_once_with('<div style="height: 2rem;"></div>')

    def test_percent_unit_size(self):
        """Test st_space with percentage units"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", "50%")
            mock_render.assert_called_once_with('<div style="height: 50%;"></div>')

    def test_negative_int_size(self):
        """Test st_space with negative integer uses margin-top"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", -5)
            mock_render.assert_called_once_with('<div style="margin-top: -5em;"></div>')

    def test_render_called_once_vertical(self):
        """Test that _render is called exactly once for vertical space"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 2)
            assert mock_render.call_count == 1

    def test_render_called_once_horizontal(self):
        """Test that _render is called exactly once for horizontal space"""
        with patch('streamtex.space._render') as mock_render:
            st_space("h", 3)
            assert mock_render.call_count == 1

    def test_integer_converted_to_string_with_em(self):
        """Test that integer 5 becomes '5em' string"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 5)
            call_arg = mock_render.call_args[0][0]
            assert "5em" in call_arg
            assert "height: 5em;" in call_arg

    def test_string_size_unchanged(self):
        """Test that string size is used without modification"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", "10pt")
            call_arg = mock_render.call_args[0][0]
            assert "10pt" in call_arg
            assert "height: 10pt;" in call_arg

    def test_horizontal_uses_padding_left(self):
        """Test that horizontal space uses padding-left property"""
        with patch('streamtex.space._render') as mock_render:
            st_space("h", "25px")
            call_arg = mock_render.call_args[0][0]
            assert "padding-left" in call_arg
            assert "height" not in call_arg

    def test_vertical_uses_padding_top(self):
        """Test that vertical space uses height property"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", "25px")
            call_arg = mock_render.call_args[0][0]
            assert "height" in call_arg
            assert "padding-left" not in call_arg

    def test_vertical_uses_div_tag(self):
        """Test that vertical space uses <div> tag"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 2)
            call_arg = mock_render.call_args[0][0]
            assert call_arg.startswith("<div")
            assert call_arg.endswith("</div>")

    def test_horizontal_uses_span_tag(self):
        """Test that horizontal space uses <span> tag"""
        with patch('streamtex.space._render') as mock_render:
            st_space("h", 2)
            call_arg = mock_render.call_args[0][0]
            assert call_arg.startswith("<span")
            assert call_arg.endswith("</span>")

    def test_no_return_value(self):
        """Test that st_space returns None"""
        with patch('streamtex.space._render') as mock_render:
            result = st_space("v", 2)
            assert result is None

    def test_multiple_calls_independent(self):
        """Test that multiple calls to st_space are independent"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 2)
            st_space("h", 3)
            assert mock_render.call_count == 2
            assert mock_render.call_args_list[0][0][0] == '<div style="height: 2em;"></div>'
            assert mock_render.call_args_list[1][0][0] == '<span style="padding-left: 3em;"></span>'


class TestStBr:
    """Tests for st_br function."""

    def test_default_single_br(self):
        """Test st_br() generates one <br>"""
        with patch('streamtex.space._render') as mock_render:
            st_br()
            mock_render.assert_called_once_with("<br>")

    def test_multiple_br_count_3(self):
        """Test st_br(3) generates three <br> tags"""
        with patch('streamtex.space._render') as mock_render:
            st_br(3)
            mock_render.assert_called_once_with("<br><br><br>")

    def test_br_count_zero_generates_one(self):
        """Test st_br(0) generates at least one <br> (max(1, count))"""
        with patch('streamtex.space._render') as mock_render:
            st_br(0)
            mock_render.assert_called_once_with("<br>")

    def test_br_count_1(self):
        """Test st_br(1) generates one <br>"""
        with patch('streamtex.space._render') as mock_render:
            st_br(1)
            mock_render.assert_called_once_with("<br>")

    def test_br_count_2(self):
        """Test st_br(2) generates two <br> tags"""
        with patch('streamtex.space._render') as mock_render:
            st_br(2)
            mock_render.assert_called_once_with("<br><br>")

    def test_br_large_count(self):
        """Test st_br(10) generates ten <br> tags"""
        with patch('streamtex.space._render') as mock_render:
            st_br(10)
            expected = "<br>" * 10
            mock_render.assert_called_once_with(expected)

    def test_br_negative_count_generates_one(self):
        """Test st_br(-5) generates at least one <br> due to max(1, count)"""
        with patch('streamtex.space._render') as mock_render:
            st_br(-5)
            mock_render.assert_called_once_with("<br>")

    def test_render_called_once(self):
        """Test that _render is called exactly once for st_br"""
        with patch('streamtex.space._render') as mock_render:
            st_br(3)
            assert mock_render.call_count == 1

    def test_br_no_return_value(self):
        """Test that st_br returns None"""
        with patch('streamtex.space._render') as mock_render:
            result = st_br(2)
            assert result is None

    def test_br_count_concatenation(self):
        """Test that br tags are properly concatenated"""
        with patch('streamtex.space._render') as mock_render:
            st_br(5)
            call_arg = mock_render.call_args[0][0]
            # Verify exact string format
            assert call_arg == "<br><br><br><br><br>"
            # Verify no spaces or other characters between tags
            assert call_arg.count("<br>") == 5

    def test_multiple_br_calls(self):
        """Test multiple calls to st_br with different counts"""
        with patch('streamtex.space._render') as mock_render:
            st_br(1)
            st_br(2)
            st_br(3)
            assert mock_render.call_count == 3
            assert mock_render.call_args_list[0][0][0] == "<br>"
            assert mock_render.call_args_list[1][0][0] == "<br><br>"
            assert mock_render.call_args_list[2][0][0] == "<br><br><br>"

    def test_br_count_behavior_with_max_function(self):
        """Test that st_br respects max(1, count) behavior"""
        with patch('streamtex.space._render') as mock_render:
            # Test that 0 and -1 both produce 1 br
            st_br(0)
            first_call = mock_render.call_args[0][0]

            st_br(-1)
            second_call = mock_render.call_args[0][0]

            assert first_call == second_call == "<br>"

    def test_br_count_100(self):
        """Test st_br with a large count of 100"""
        with patch('streamtex.space._render') as mock_render:
            st_br(100)
            call_arg = mock_render.call_args[0][0]
            assert call_arg.count("<br>") == 100


class TestIntegration:
    """Integration tests for st_space and st_br."""

    def test_multiple_spaces_and_breaks(self):
        """Test calling st_space and st_br in sequence"""
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 2)
            st_br(2)
            st_space("h", "10px")

            assert mock_render.call_count == 3
            calls = [call[0][0] for call in mock_render.call_args_list]
            assert '<div style="height: 2em;"></div>' in calls
            assert "<br><br>" in calls
            assert '<span style="padding-left: 10px;"></span>' in calls

    def test_space_and_br_with_mock_side_effects(self):
        """Test that _render is called with correct arguments using side effects"""
        rendered_html = []

        def capture_html(html):
            rendered_html.append(html)

        with patch('streamtex.space._render', side_effect=capture_html) as mock_render:
            st_space("v", 3)
            st_br(2)
            st_space("h", "5em")

            assert len(rendered_html) == 3
            assert rendered_html[0] == '<div style="height: 3em;"></div>'
            assert rendered_html[1] == "<br><br>"
            assert rendered_html[2] == '<span style="padding-left: 5em;"></span>'

    def test_render_is_from_export_module(self):
        """Verify that _render is imported from streamtex.export"""
        import streamtex.export
        # Verify that _render is accessible through the export module
        assert hasattr(streamtex.export, '_render')
        # Verify the patch target is correct
        with patch('streamtex.space._render') as mock_render:
            st_space("v", 1)
            mock_render.assert_called_once()
