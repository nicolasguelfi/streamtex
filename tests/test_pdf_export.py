"""Unit tests for streamtex.pdf_export — PDF export configuration and CSS injection."""

import pytest

from streamtex.pdf_export import (
    PdfConfig,
    PdfMode,
    _compute_viewport_width,
    _inject_content_width_css,
    _page_dimensions_mm,
    _parse_margin,
    inject_print_css,
)


class TestPdfMode:
    """Tests for PdfMode enum."""

    def test_continuous_value(self):
        assert PdfMode.CONTINUOUS.value == "continuous"

    def test_paginated_value(self):
        assert PdfMode.PAGINATED.value == "paginated"


class TestPdfConfig:
    """Tests for PdfConfig dataclass."""

    def test_defaults(self):
        cfg = PdfConfig()
        assert cfg.mode == PdfMode.PAGINATED
        assert cfg.format == "A4"
        assert cfg.landscape is True
        assert cfg.margin_top == "10mm"
        assert cfg.margin_bottom == "10mm"
        assert cfg.margin_left == "15mm"
        assert cfg.margin_right == "15mm"
        assert cfg.print_background is True
        assert cfg.scale == 1.0
        assert cfg.content_width == 100
        assert cfg.header_template == ""
        assert cfg.footer_template == ""
        assert cfg.page_numbers is False
        assert cfg.theme_bg == "#fff"
        assert cfg.theme_text == "#333"

    def test_custom_values(self):
        cfg = PdfConfig(mode=PdfMode.CONTINUOUS, format="Letter", landscape=False, scale=0.8)
        assert cfg.mode == PdfMode.CONTINUOUS
        assert cfg.format == "Letter"
        assert cfg.landscape is False
        assert cfg.scale == 0.8

    def test_content_width(self):
        cfg = PdfConfig(content_width=80)
        assert cfg.content_width == 80

    def test_theme_colors(self):
        cfg = PdfConfig(theme_bg="#111111", theme_text="#fafafa")
        assert cfg.theme_bg == "#111111"
        assert cfg.theme_text == "#fafafa"

    def test_page_numbers_with_theme(self):
        cfg = PdfConfig(page_numbers=True, theme_bg="#0e1117", theme_text="#fafafa")
        assert cfg.page_numbers is True
        assert cfg.theme_bg == "#0e1117"
        assert cfg.theme_text == "#fafafa"


class TestInjectPrintCss:
    """Tests for inject_print_css function."""

    def test_continuous_mode_hides_all(self):
        html = "<html><head><title>Test</title></head><body></body></html>"
        result = inject_print_css(html, PdfMode.CONTINUOUS)
        assert "@media print" in result
        assert ".stx-slide-break-rule { display: none !important; }" in result
        assert ".stx-slide-break-spacer { display: none !important; }" in result

    def test_paginated_mode_adds_page_break(self):
        html = "<html><head><title>Test</title></head><body></body></html>"
        result = inject_print_css(html, PdfMode.PAGINATED)
        assert "@media print" in result
        assert "page-break-after: always;" in result
        assert "break-after: page;" in result
        assert ".stx-slide-break-rule { display: none !important; }" in result

    def test_css_injected_before_head_close(self):
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        result = inject_print_css(html, PdfMode.CONTINUOUS)
        assert "<style>" in result
        assert result.index("<style>") < result.index("</head>")

    def test_body_preserved(self):
        html = "<html><head></head><body><div class='stx-slide-break-spacer'>spacer</div></body></html>"
        result = inject_print_css(html, PdfMode.PAGINATED)
        assert '<div class=\'stx-slide-break-spacer\'>spacer</div>' in result

    def test_no_head_tag_no_injection(self):
        html = "<html><body>No head</body></html>"
        result = inject_print_css(html, PdfMode.CONTINUOUS)
        # No </head> to replace, so CSS is not injected
        assert result == html


class TestParseMargin:
    """Tests for _parse_margin helper."""

    def test_mm(self):
        assert _parse_margin("10mm") == 10.0

    def test_zero(self):
        assert _parse_margin("0") == 0.0

    def test_cm(self):
        assert _parse_margin("1cm") == 10.0

    def test_inches(self):
        assert _parse_margin("1in") == 25.4

    def test_px(self):
        assert abs(_parse_margin("100px") - 26.4583) < 0.01

    def test_pt(self):
        assert abs(_parse_margin("10pt") - 3.52778) < 0.01

    def test_empty(self):
        assert _parse_margin("") == 0.0

    def test_whitespace(self):
        assert _parse_margin("  10mm  ") == 10.0

    def test_no_unit_defaults_mm(self):
        assert _parse_margin("15") == 15.0

    def test_decimal(self):
        assert _parse_margin("2.5mm") == 2.5

    def test_invalid(self):
        assert _parse_margin("auto") == 0.0


class TestPageDimensionsMm:
    """Tests for _page_dimensions_mm helper."""

    def test_a4_portrait(self):
        w, h = _page_dimensions_mm("A4", landscape=False)
        assert w == 210
        assert h == 297

    def test_a4_landscape(self):
        w, h = _page_dimensions_mm("A4", landscape=True)
        assert w == 297
        assert h == 210

    def test_letter_portrait(self):
        w, h = _page_dimensions_mm("Letter", landscape=False)
        assert w == 215.9
        assert h == 279.4

    def test_letter_landscape(self):
        w, h = _page_dimensions_mm("Letter", landscape=True)
        assert w == 279.4
        assert h == 215.9

    def test_a3_landscape(self):
        w, h = _page_dimensions_mm("A3", landscape=True)
        assert w == 420
        assert h == 297

    def test_case_insensitive(self):
        w1, h1 = _page_dimensions_mm("a4", landscape=False)
        w2, h2 = _page_dimensions_mm("A4", landscape=False)
        assert w1 == w2 and h1 == h2

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown page format"):
            _page_dimensions_mm("B7", landscape=False)

    def test_tabloid(self):
        w, h = _page_dimensions_mm("Tabloid", landscape=False)
        assert w == 279.4
        assert h == 431.8

    def test_16_9_format(self):
        w, h = _page_dimensions_mm("16:9", landscape=False)
        assert abs(w / h - 16 / 9) < 0.01

    def test_16_10_format(self):
        w, h = _page_dimensions_mm("16:10", landscape=False)
        assert abs(w / h - 16 / 10) < 0.01

    def test_4_3_format(self):
        w, h = _page_dimensions_mm("4:3", landscape=False)
        assert abs(w / h - 4 / 3) < 0.01

    def test_free_ratio(self):
        w, h = _page_dimensions_mm("21:9", landscape=False)
        assert abs(w / h - 21 / 9) < 0.01

    def test_free_ratio_decimal(self):
        w, h = _page_dimensions_mm("2.35:1", landscape=False)
        assert abs(w / h - 2.35) < 0.01

    def test_invalid_ratio_raises(self):
        with pytest.raises(ValueError):
            _page_dimensions_mm("0:0", landscape=False)


class TestComputeViewportWidth:
    """Tests for _compute_viewport_width."""

    def test_a4_landscape_no_margins_scale1(self):
        vw = _compute_viewport_width("A4", True, "0mm", "0mm", 1.0)
        # 297mm / 25.4 * 96 = 1122.52 → 1123
        assert vw == 1123

    def test_a4_landscape_no_margins_scale08(self):
        vw = _compute_viewport_width("A4", True, "0mm", "0mm", 0.8)
        # 297mm / 25.4 * 96 / 0.8 = 1403.15 → 1403
        assert vw == 1403

    def test_a4_landscape_with_margins(self):
        vw = _compute_viewport_width("A4", True, "15mm", "15mm", 1.0)
        # (297 - 30)mm / 25.4 * 96 = 1009.13 → 1009
        assert vw == 1009

    def test_a4_portrait_scale1(self):
        vw = _compute_viewport_width("A4", False, "0mm", "0mm", 1.0)
        # 210mm / 25.4 * 96 = 793.70 → clamped to minimum 800
        assert vw == 800

    def test_minimum_800(self):
        # Very small available width should clamp to 800
        vw = _compute_viewport_width("A6", False, "50mm", "50mm", 1.0)
        assert vw == 800

    def test_letter_landscape_scale05(self):
        vw = _compute_viewport_width("Letter", True, "0mm", "0mm", 0.5)
        # 279.4mm / 25.4 * 96 / 0.5 = 2113.51 → 2114
        expected = round(279.4 / 25.4 * 96 / 0.5)
        assert vw == expected


class TestInjectContentWidthCss:
    """Tests for _inject_content_width_css."""

    def test_100_percent_full_width(self):
        html = "<html><head></head><body>Test</body></html>"
        result = _inject_content_width_css(html, 100)
        assert ".streamtex-page" in result
        assert "width: 100% !important" in result
        assert "padding: 0.0% !important" in result

    def test_80_percent_injects_padding(self):
        html = "<html><head></head><body>Test</body></html>"
        result = _inject_content_width_css(html, 80)
        assert ".streamtex-page" in result
        assert "padding: 10.0% !important" in result

    def test_60_percent_padding(self):
        html = "<html><head></head><body>Test</body></html>"
        result = _inject_content_width_css(html, 60)
        assert "padding: 20.0% !important" in result

    def test_clamped_below_10(self):
        html = "<html><head></head><body>Test</body></html>"
        result = _inject_content_width_css(html, 5)
        # Clamped to 10 → padding = 45%
        assert "padding: 45.0% !important" in result

    def test_above_100_clamped(self):
        html = "<html><head></head><body>Test</body></html>"
        result = _inject_content_width_css(html, 120)
        # Clamped to 100 → padding = 0%
        assert "width: 100% !important" in result
        assert "padding: 0.0% !important" in result

    def test_injected_before_head_close(self):
        html = "<html><head><title>T</title></head><body>B</body></html>"
        result = _inject_content_width_css(html, 80)
        assert result.index("<style>") < result.index("</head>")

    def test_no_head_tag_unchanged(self):
        html = "<html><body>No head</body></html>"
        result = _inject_content_width_css(html, 80)
        assert result == html
