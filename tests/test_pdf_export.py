"""Unit tests for streamtex.pdf_export — PDF export configuration and CSS injection."""

from streamtex.pdf_export import (
    PdfConfig,
    PdfMode,
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
        assert cfg.header_template == ""
        assert cfg.footer_template == ""

    def test_custom_values(self):
        cfg = PdfConfig(mode=PdfMode.CONTINUOUS, format="Letter", landscape=False, scale=0.8)
        assert cfg.mode == PdfMode.CONTINUOUS
        assert cfg.format == "Letter"
        assert cfg.landscape is False
        assert cfg.scale == 0.8


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
