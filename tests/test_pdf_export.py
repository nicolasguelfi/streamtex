"""Unit tests for streamtex.pdf_export — PDF export configuration and CSS injection."""

import pytest

from streamtex.pdf_export import (
    PdfConfig,
    PdfMode,
    _compute_viewport_width,
    _inject_content_width_css,
    _inject_toc_headings,
    _page_dimensions_mm,
    _parse_margin,
    export_pdf,
    inject_base_href,
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


class TestInjectTocHeadings:
    """Tests for _inject_toc_headings — TOC → PDF bookmark headings."""

    _BASE_HTML = (
        '<html><head><title>T</title></head><body>'
        '<div id="1-intro" style="color:red;">Introduction</div>'
        '<p>Content here</p>'
        "<div id='2-chapter' style='font-size:20px;'>Chapter</div>"
        '</body></html>'
    )

    def test_empty_toc_returns_unchanged(self):
        result = _inject_toc_headings(self._BASE_HTML, [])
        assert result == self._BASE_HTML

    def test_none_toc_returns_unchanged(self):
        result = _inject_toc_headings(self._BASE_HTML, None)
        assert result == self._BASE_HTML

    def test_injects_h1_at_anchor(self):
        toc = [{"key_anchor": "1-intro", "title": "Introduction", "level": 1}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert '<h1 class="stx-pdf-outline-heading">Introduction</h1>' in result

    def test_injects_h2_at_anchor(self):
        toc = [{"key_anchor": "2-chapter", "title": "Chapter Two", "level": 2}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert '<h2 class="stx-pdf-outline-heading">Chapter Two</h2>' in result

    def test_heading_injected_after_anchor_tag(self):
        toc = [{"key_anchor": "1-intro", "title": "Intro", "level": 1}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        idx_anchor = result.index('id="1-intro"')
        idx_close = result.index(">", idx_anchor)
        idx_heading = result.index('<h1 class="stx-pdf-outline-heading">')
        assert idx_heading == idx_close + 1

    def test_multiple_toc_entries(self):
        toc = [
            {"key_anchor": "1-intro", "title": "Introduction", "level": 1},
            {"key_anchor": "2-chapter", "title": "Chapter", "level": 2},
        ]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert '<h1 class="stx-pdf-outline-heading">Introduction</h1>' in result
        assert '<h2 class="stx-pdf-outline-heading">Chapter</h2>' in result

    def test_css_injected_in_head(self):
        toc = [{"key_anchor": "1-intro", "title": "Intro", "level": 1}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert ".stx-pdf-outline-heading" in result
        assert result.index(".stx-pdf-outline-heading") < result.index("</head>")

    def test_level_clamped_to_1_min(self):
        toc = [{"key_anchor": "1-intro", "title": "Intro", "level": 0}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert "<h1 " in result

    def test_level_clamped_to_6_max(self):
        toc = [{"key_anchor": "1-intro", "title": "Intro", "level": 9}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert "<h6 " in result

    def test_missing_anchor_skipped(self):
        toc = [{"key_anchor": "nonexistent", "title": "Ghost", "level": 1}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert "Ghost" not in result

    def test_entry_without_title_skipped(self):
        toc = [{"key_anchor": "1-intro", "title": "", "level": 1}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert "<h1" not in result

    def test_entry_without_anchor_skipped(self):
        toc = [{"key_anchor": "", "title": "Intro", "level": 1}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert "stx-pdf-outline-heading" not in result

    def test_single_quoted_id_attribute(self):
        toc = [{"key_anchor": "2-chapter", "title": "Chapter", "level": 2}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert '<h2 class="stx-pdf-outline-heading">Chapter</h2>' in result

    def test_preserves_original_content(self):
        toc = [{"key_anchor": "1-intro", "title": "Intro", "level": 1}]
        result = _inject_toc_headings(self._BASE_HTML, toc)
        assert "Introduction</div>" in result
        assert "<p>Content here</p>" in result


class TestInjectBaseHref:
    """<base href> injection for relative-media resolution (issue #44)."""

    _BASE_HTML = ("<html><head><title>T</title></head>"
                  "<body><img src='app/static/media/x.png'></body></html>")

    def test_empty_base_url_is_noop(self):
        assert inject_base_href(self._BASE_HTML, "") == self._BASE_HTML

    def test_injected_right_after_head(self):
        out = inject_base_href(self._BASE_HTML, "http://localhost:8501/")
        assert '<head><base href="http://localhost:8501/">' in out

    def test_trailing_slash_normalised(self):
        out = inject_base_href(self._BASE_HTML, "http://localhost:8501")
        assert '<base href="http://localhost:8501/">' in out

    def test_existing_base_wins(self):
        html = "<html><head><base href='http://other/'></head><body></body></html>"
        assert inject_base_href(html, "http://localhost:8501/") == html

    def test_no_head_is_noop(self):
        html = "<div>no head</div>"
        assert inject_base_href(html, "http://localhost:8501/") == html

    def test_attribute_escaped(self):
        out = inject_base_href(self._BASE_HTML, 'http://h/"><script>/')
        head_part = out.split("</title>")[0]
        assert "<script>" not in head_part
        assert "&quot;&gt;&lt;script&gt;" in head_part

    def test_body_preserved(self):
        out = inject_base_href(self._BASE_HTML, "http://localhost:8501/")
        assert "app/static/media/x.png" in out

    def test_config_default_empty(self):
        assert PdfConfig().base_url == ""


class TestExportPdfBaseUrl:
    """export_pdf hands Chromium unchanged HTML without base_url, and the
    <base> tag when configured (fake Playwright, no browser needed)."""

    _HTML = ("<html><head><style>.x{}</style></head>"
             "<body><img src='app/static/media/x.png'></body></html>")

    def _run(self, monkeypatch, config):
        import sys
        import types

        captured = {}

        class _FakePage:
            def set_content(self, html, wait_until=None):
                captured["html"] = html
                captured["wait_until"] = wait_until

            def pdf(self, **kwargs):
                return b"%PDF-fake"

        class _FakeBrowser:
            def new_page(self, viewport=None):
                return _FakePage()

            def close(self):
                pass

        class _FakeChromium:
            def launch(self):
                return _FakeBrowser()

        class _FakeP:
            chromium = _FakeChromium()

        class _FakeSyncPlaywright:
            def __enter__(self):
                return _FakeP()

            def __exit__(self, *args):
                return False

        fake_mod = types.ModuleType("playwright.sync_api")
        fake_mod.sync_playwright = lambda: _FakeSyncPlaywright()
        fake_pkg = types.ModuleType("playwright")
        fake_pkg.sync_api = fake_mod
        monkeypatch.setitem(sys.modules, "playwright", fake_pkg)
        monkeypatch.setitem(sys.modules, "playwright.sync_api", fake_mod)

        result = export_pdf(self._HTML, config=config)
        assert result == b"%PDF-fake"
        return captured

    def test_without_base_url_html_unchanged_except_print_css(self, monkeypatch):
        captured = self._run(monkeypatch, PdfConfig())
        # The exact pre-#44 pipeline: print CSS + content-width CSS,
        # nothing else — byte-identical to 0.7.27 without base_url.
        expected = _inject_content_width_css(
            inject_print_css(self._HTML, PdfMode.PAGINATED), 100)
        assert captured["html"] == expected
        assert "<base" not in captured["html"]
        assert captured["wait_until"] == "networkidle"

    def test_with_base_url_tag_present(self, monkeypatch):
        captured = self._run(
            monkeypatch, PdfConfig(base_url="http://localhost:9999/"))
        assert '<head><base href="http://localhost:9999/">' in captured["html"]
        assert "app/static/media/x.png" in captured["html"]
