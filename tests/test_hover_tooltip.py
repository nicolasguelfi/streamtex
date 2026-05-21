"""Unit tests for streamtex.hover_tooltip."""

from unittest.mock import patch

from streamtex.hover_tooltip import _build_tooltip_html, st_hover_tooltip


class TestBuildTooltipHtml:
    def test_title_and_entries_present(self):
        html = _build_tooltip_html(
            title="What is GSE?",
            entries=[("GSE", "Generative Software Engineering"), ("Capsule", "packaged context")],
        )
        assert "What is GSE?" in html
        assert "GSE" in html
        assert "Generative Software Engineering" in html
        assert "packaged context" in html

    def test_position_left_anchors_right(self):
        # "left" = opens toward the left → panel anchored to the right edge.
        html = _build_tooltip_html(title="x", position="left")
        assert "right: 0;" in html

    def test_position_right_anchors_left(self):
        html = _build_tooltip_html(title="x", position="right")
        assert "left: 0;" in html

    def test_position_center_translates(self):
        html = _build_tooltip_html(title="x", position="center")
        assert "translateX(-50%)" in html

    def test_direction_up_opens_above(self):
        assert "bottom: 2.2rem;" in _build_tooltip_html(title="x", direction="up")

    def test_direction_down_opens_below(self):
        assert "top: 2.2rem;" in _build_tooltip_html(title="x", direction="down")

    def test_max_height_and_scroll(self):
        html = _build_tooltip_html(title="x", max_height="50vh")
        assert "max-height: 50vh;" in html
        assert "overflow-y: auto;" in html

    def test_custom_bg_color(self):
        html = _build_tooltip_html(title="x", bg_color="rgba(1,2,3,0.9)")
        assert "rgba(1,2,3,0.9)" in html

    def test_style_overrides_win(self):
        html = _build_tooltip_html(
            title="x",
            entries=[("a", "b")],
            title_style="color:hotpink;",
            term_style="color:lime;",
            def_style="color:gold;",
        )
        assert "color:hotpink;" in html
        assert "color:lime;" in html
        assert "color:gold;" in html

    def test_scale_drives_default_font_sizes(self):
        html = _build_tooltip_html(title="x", entries=[("a", "b")], scale="2vw")
        # title 1.3×, term 1.1×, def 1.0× of scale
        assert "calc(1.3 * 2vw)" in html
        assert "calc(1.1 * 2vw)" in html
        assert "calc(1.0 * 2vw)" in html

    def test_unique_class_prefix(self):
        html = _build_tooltip_html(title="abc", entries=[("a", "b")])
        assert "stx-tt-" in html

    def test_empty_entries_ok(self):
        html = _build_tooltip_html(title="only title")
        assert "only title" in html


class TestStHoverTooltip:
    def test_routes_through_st_html(self):
        with patch("streamtex.hover_tooltip.st_html") as mock_html:
            st_hover_tooltip(title="T", entries=[("a", "b")], position="left")
        mock_html.assert_called_once()
        sent = mock_html.call_args.args[0]
        assert "T" in sent and "right: 0;" in sent
