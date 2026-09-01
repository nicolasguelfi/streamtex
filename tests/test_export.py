"""Unit tests for streamtex.export — buffer, config, global functions, st_html."""

import os
import re
import tempfile
from unittest.mock import patch

import streamtex.export as export_mod
from streamtex.export import (
    ExportConfig,
    ExportMode,
    HtmlExportBuffer,
    _render,
    build_export_filename,
    export_append,
    export_pop_wrapper,
    export_push_wrapper,
    generate_export_html,
    is_export_active,
    reset_export_buffer,
    st_export,
    st_html,
)

# ---------------------------------------------------------------------------
# ExportConfig
# ---------------------------------------------------------------------------

class TestExportConfig:
    def test_defaults(self):
        cfg = ExportConfig()
        assert cfg.enabled is False
        assert cfg.page_title == "StreamTeX Export"
        assert cfg.page_width == "100%"
        assert cfg.page_padding == "var(--stx-page-padding, 36pt)"
        assert cfg.zoom == 1.0

    def test_custom(self):
        cfg = ExportConfig(enabled=True, page_title="My Book", page_width="800px", page_padding="20px")
        assert cfg.enabled is True
        assert cfg.page_title == "My Book"

    def test_custom_zoom(self):
        cfg = ExportConfig(enabled=True, zoom=0.8)
        assert cfg.zoom == 0.8

    def test_theme_overrides_default_none(self):
        cfg = ExportConfig()
        assert cfg.theme_bg is None
        assert cfg.theme_text is None
        assert cfg.theme_primary is None

    def test_theme_overrides_set(self):
        cfg = ExportConfig(theme_bg="#0e1117", theme_text="#fafafa", theme_primary="#ff4b4b")
        assert cfg.theme_bg == "#0e1117"
        assert cfg.theme_text == "#fafafa"
        assert cfg.theme_primary == "#ff4b4b"


class TestThemeInExport:
    """Theme colors are applied in generate_full_html() from ExportConfig overrides."""

    def test_dark_theme_override_in_html(self):
        cfg = ExportConfig(enabled=True, theme_bg="#0e1117", theme_text="#fafafa")
        buf = HtmlExportBuffer(cfg)
        buf.append("<p>Dark content</p>")
        html = buf.generate_full_html()
        assert "background: #0e1117" in html
        assert "color: #fafafa" in html

    def test_light_theme_fallback_without_override(self):
        cfg = ExportConfig(enabled=True)
        buf = HtmlExportBuffer(cfg)
        buf.append("<p>Light content</p>")
        html = buf.generate_full_html()
        # Without override, falls back to _get_theme_color defaults
        assert "background:" in html

    def test_primary_color_override(self):
        cfg = ExportConfig(enabled=True, theme_primary="#4da6ff")
        buf = HtmlExportBuffer(cfg)
        buf.append("<p>Content</p>")
        html = buf.generate_full_html()
        assert "color: #4da6ff" in html


# ---------------------------------------------------------------------------
# HtmlExportBuffer
# ---------------------------------------------------------------------------

class TestHtmlExportBuffer:
    def _make_buffer(self):
        return HtmlExportBuffer(ExportConfig(enabled=True))

    def test_empty_buffer(self):
        buf = self._make_buffer()
        assert buf.get_body_html() == ""

    def test_append(self):
        buf = self._make_buffer()
        buf.append("<p>hello</p>")
        assert "<p>hello</p>" in buf.get_body_html()

    def test_multiple_appends(self):
        buf = self._make_buffer()
        buf.append("<p>a</p>")
        buf.append("<p>b</p>")
        body = buf.get_body_html()
        assert "<p>a</p>" in body
        assert "<p>b</p>" in body

    def test_push_pop_wrapper(self):
        buf = self._make_buffer()
        buf.push_wrapper('<div class="outer">')
        buf.append("<p>inner</p>")
        buf.pop_wrapper("</div>")
        body = buf.get_body_html()
        assert '<div class="outer">' in body
        assert "<p>inner</p>" in body
        assert "</div>" in body

    def test_nested_push_pop(self):
        buf = self._make_buffer()
        buf.push_wrapper("<div>")
        buf.push_wrapper("<section>")
        buf.append("<p>deep</p>")
        buf.pop_wrapper("</section>")
        buf.pop_wrapper("</div>")
        body = buf.get_body_html()
        assert "<div>" in body
        assert "<section>" in body
        assert "<p>deep</p>" in body
        assert "</section>" in body
        assert "</div>" in body

    def test_pop_on_root_is_safe(self):
        buf = self._make_buffer()
        buf.pop_wrapper("</div>")  # should not raise
        assert buf.get_body_html() == ""

    def test_reset(self):
        buf = self._make_buffer()
        buf.append("<p>data</p>")
        buf.reset()
        assert buf.get_body_html() == ""

    def test_generate_full_html(self):
        buf = self._make_buffer()
        buf.append("<p>content</p>")
        html = buf.generate_full_html()
        assert "<!DOCTYPE html>" in html
        assert "<title>StreamTeX Export</title>" in html
        assert "streamtex-page" in html
        assert "<p>content</p>" in html

    def test_generate_full_html_no_zoom_when_default(self):
        buf = self._make_buffer()
        buf.append("<p>test</p>")
        html = buf.generate_full_html()
        assert "zoom:" not in html

    def test_generate_full_html_with_zoom(self):
        buf = HtmlExportBuffer(ExportConfig(enabled=True, zoom=0.8))
        buf.append("<p>test</p>")
        html = buf.generate_full_html()
        assert "zoom: 0.8;" in html

    def test_generate_full_html_zoom_100_no_css(self):
        buf = HtmlExportBuffer(ExportConfig(enabled=True, zoom=1.0))
        buf.append("<p>test</p>")
        html = buf.generate_full_html()
        assert "zoom:" not in html

    def test_generate_full_html_lang_default_en(self):
        buf = self._make_buffer()
        html = buf.generate_full_html()
        assert '<html lang="en">' in html

    def test_generate_full_html_lang_from_config(self):
        buf = HtmlExportBuffer(ExportConfig(enabled=True, lang="fr"))
        html = buf.generate_full_html()
        assert '<html lang="fr">' in html
        assert '<html lang="en">' not in html

    def test_generate_full_html_lang_region_tag(self):
        buf = HtmlExportBuffer(ExportConfig(enabled=True, lang="de-CH"))
        assert '<html lang="de-CH">' in buf.generate_full_html()

    def test_generate_full_html_lang_invalid_falls_back_to_en(self):
        buf = HtmlExportBuffer(ExportConfig(enabled=True, lang='fr"><script>'))
        html = buf.generate_full_html()
        assert '<html lang="en">' in html
        assert "<script>" not in html.split("<head>")[0]


# ---------------------------------------------------------------------------
# Global functions
# ---------------------------------------------------------------------------

class TestGlobalFunctions:
    def setup_method(self):
        # Ensure clean state
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_inactive_by_default(self):
        assert is_export_active() is False

    def test_activate(self):
        reset_export_buffer(ExportConfig(enabled=True))
        assert is_export_active() is True

    def test_deactivate(self):
        reset_export_buffer(ExportConfig(enabled=True))
        reset_export_buffer(ExportConfig(enabled=False))
        assert is_export_active() is False

    def test_reset_none_config(self):
        reset_export_buffer(ExportConfig(enabled=True))
        reset_export_buffer(None)
        assert is_export_active() is False

    def test_noop_when_inactive(self):
        # These should not raise
        export_append("<p>x</p>")
        export_push_wrapper("<div>")
        export_pop_wrapper("</div>")
        assert generate_export_html() is None

    def test_export_append_when_active(self):
        reset_export_buffer(ExportConfig(enabled=True))
        export_append("<p>hello</p>")
        html = generate_export_html()
        assert "<p>hello</p>" in html

    def test_push_pop_when_active(self):
        reset_export_buffer(ExportConfig(enabled=True))
        export_push_wrapper("<div>")
        export_append("<p>inner</p>")
        export_pop_wrapper("</div>")
        html = generate_export_html()
        assert "<div>" in html
        assert "<p>inner</p>" in html
        assert "</div>" in html


# ---------------------------------------------------------------------------
# st_html — public dual-rendering bridge
# ---------------------------------------------------------------------------

class TestStHtml:
    """Tests for the public st_html() function."""

    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.export.st")
    def test_inline_calls_st_html(self, mock_st):
        st_html("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")

    @patch("streamtex.export.st")
    def test_appends_to_buffer(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_html("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")
        assert "<p>hi</p>" in generate_export_html()

    @patch("streamtex.export.st")
    def test_no_buffer_when_inactive(self, mock_st):
        st_html("<p>hi</p>")
        mock_st.html.assert_called_once()
        assert generate_export_html() is None

    def test_alias_is_same_function(self):
        assert _render is st_html

    @patch("streamlit.iframe")
    def test_iframe_injects_font(self, mock_iframe):
        st_html("<p>chart</p>", height=300)
        call_args = mock_iframe.call_args
        html_arg = call_args[0][0]
        assert "font-family:Source Sans Pro,sans-serif" in html_arg
        assert "margin:0" in html_arg
        assert "<p>chart</p>" in html_arg

    @patch("streamlit.iframe")
    def test_iframe_scrolling_accepted_but_noop(self, mock_iframe):
        """``scrolling`` is kept in the signature for backwards compat
        but no longer forwarded — st.iframe has no scrolling parameter."""
        st_html("<p>long</p>", height=400, scrolling=True)
        call_args = mock_iframe.call_args
        # The kwarg is NOT forwarded to st.iframe (no error, just no-op).
        assert "scrolling" not in call_args[1]

    @patch("streamlit.iframe")
    def test_iframe_default_no_scrolling_kwarg(self, mock_iframe):
        st_html("<p>short</p>", height=200)
        call_args = mock_iframe.call_args
        assert "scrolling" not in call_args[1]

    @patch("streamlit.iframe")
    def test_iframe_buffer_gets_raw_html(self, mock_iframe):
        """Export buffer receives the original HTML, not the iframe-wrapped version."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_html("<p>chart</p>", height=300)
        exported = generate_export_html()
        assert "<p>chart</p>" in exported
        # _IFRAME_BASE should NOT leak into export buffer
        assert "font-family:Source Sans Pro" not in exported


# ---------------------------------------------------------------------------
# _render — backward-compat alias (legacy tests kept for safety)
# ---------------------------------------------------------------------------

class TestRender:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.export.st")
    def test_render_calls_st_html(self, mock_st):
        _render("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")

    @patch("streamtex.export.st")
    def test_render_appends_to_buffer(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        _render("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")
        assert "<p>hi</p>" in generate_export_html()

    @patch("streamtex.export.st")
    def test_render_no_buffer_when_inactive(self, mock_st):
        _render("<p>hi</p>")
        mock_st.html.assert_called_once()
        assert generate_export_html() is None


# ---------------------------------------------------------------------------
# st_export — context manager
# ---------------------------------------------------------------------------

class TestStExport:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_noop_when_inactive(self):
        with st_export("<p>fallback</p>"):
            pass
        assert generate_export_html() is None

    def test_appends_when_active(self):
        reset_export_buffer(ExportConfig(enabled=True))
        with st_export("<p>fallback</p>"):
            pass
        html = generate_export_html()
        assert "<p>fallback</p>" in html

    def test_multiple_exports(self):
        reset_export_buffer(ExportConfig(enabled=True))
        with st_export("<p>first</p>"):
            pass
        with st_export("<p>second</p>"):
            pass
        html = generate_export_html()
        assert "<p>first</p>" in html
        assert "<p>second</p>" in html

    def test_yield_executes_body(self):
        reset_export_buffer(ExportConfig(enabled=True))
        executed = False
        with st_export("<p>fb</p>"):
            executed = True
        assert executed is True


# ---------------------------------------------------------------------------
# ExportMode enum
# ---------------------------------------------------------------------------

class TestExportMode:
    def test_always_value(self):
        assert ExportMode.ALWAYS.value == "always"

    def test_manual_value(self):
        assert ExportMode.MANUAL.value == "manual"

    def test_never_value(self):
        assert ExportMode.NEVER.value == "never"

    def test_all_modes(self):
        modes = [*ExportMode]
        assert len(modes) == 3


# ---------------------------------------------------------------------------
# ExportConfig — new auto-export fields
# ---------------------------------------------------------------------------

class TestExportConfigAutoExport:
    def test_default_auto_export_fields(self):
        cfg = ExportConfig()
        assert cfg.format == "html"
        assert cfg.mode == ExportMode.ALWAYS
        assert cfg.output_dir == "./exports"
        assert cfg.filename is None
        assert cfg.timestamp is False
        assert cfg.pdf is None

    def test_custom_auto_export_html(self):
        cfg = ExportConfig(
            format="html",
            mode=ExportMode.ALWAYS,
            output_dir="/tmp/out",
            filename="my-book",
            timestamp=True,
        )
        assert cfg.format == "html"
        assert cfg.mode == ExportMode.ALWAYS
        assert cfg.output_dir == "/tmp/out"
        assert cfg.filename == "my-book"
        assert cfg.timestamp is True

    def test_custom_auto_export_pdf(self):
        from streamtex.pdf_export import PdfConfig
        pdf = PdfConfig(format="A3", landscape=False)
        cfg = ExportConfig(
            format="pdf",
            mode=ExportMode.ALWAYS,
            filename="slides",
            pdf=pdf,
        )
        assert cfg.format == "pdf"
        assert cfg.pdf is not None
        assert cfg.pdf.format == "A3"
        assert cfg.pdf.landscape is False

    def test_manual_mode(self):
        cfg = ExportConfig(mode=ExportMode.MANUAL)
        assert cfg.mode == ExportMode.MANUAL

    def test_never_mode(self):
        cfg = ExportConfig(mode=ExportMode.NEVER)
        assert cfg.mode == ExportMode.NEVER

    def test_backward_compat_enabled_field(self):
        """Legacy 'enabled' field still works for buffer config."""
        cfg = ExportConfig(enabled=True, page_title="Test")
        assert cfg.enabled is True
        assert cfg.page_title == "Test"


# ---------------------------------------------------------------------------
# build_export_filename
# ---------------------------------------------------------------------------

class TestBuildExportFilename:
    def test_html_no_timestamp(self, tmp_path):
        cfg = ExportConfig(
            format="html",
            output_dir=str(tmp_path),
            filename="my-doc",
            timestamp=False,
        )
        path = build_export_filename(cfg, "fallback")
        assert path == str(tmp_path / "my-doc.html")

    def test_pdf_no_timestamp(self, tmp_path):
        cfg = ExportConfig(
            format="pdf",
            output_dir=str(tmp_path),
            filename="slides",
            timestamp=False,
        )
        path = build_export_filename(cfg, "fallback")
        assert path == str(tmp_path / "slides.pdf")

    def test_uses_base_name_when_filename_none(self, tmp_path):
        cfg = ExportConfig(
            format="html",
            output_dir=str(tmp_path),
            filename=None,
            timestamp=False,
        )
        path = build_export_filename(cfg, "my_book")
        assert path == str(tmp_path / "my_book.html")

    def test_timestamp_appended(self, tmp_path):
        cfg = ExportConfig(
            format="html",
            output_dir=str(tmp_path),
            filename="doc",
            timestamp=True,
        )
        path = build_export_filename(cfg, "fallback")
        # Pattern: doc-YYMMDD-HHMMSS.html
        basename = os.path.basename(path)
        assert re.match(r"doc-\d{6}-\d{6}\.html$", basename), f"Unexpected filename: {basename}"

    def test_creates_output_dir(self, tmp_path):
        out = tmp_path / "nested" / "dir"
        assert not out.exists()
        cfg = ExportConfig(
            format="html",
            output_dir=str(out),
            filename="test",
            timestamp=False,
        )
        build_export_filename(cfg, "fallback")
        assert out.exists()

    def test_pdf_timestamp(self, tmp_path):
        cfg = ExportConfig(
            format="pdf",
            output_dir=str(tmp_path),
            filename="report",
            timestamp=True,
        )
        path = build_export_filename(cfg, "fallback")
        basename = os.path.basename(path)
        assert re.match(r"report-\d{6}-\d{6}\.pdf$", basename)


# ---------------------------------------------------------------------------
# _read_streamlit_theme
# ---------------------------------------------------------------------------

class TestReadStreamlitTheme:
    """Tests for theme auto-detection from .streamlit/config.toml."""

    def _write_config(self, tmpdir, content):
        st_dir = os.path.join(tmpdir, ".streamlit")
        os.makedirs(st_dir, exist_ok=True)
        with open(os.path.join(st_dir, "config.toml"), "w") as f:
            f.write(content)

    def test_dark_base_resolves_colors(self):
        from streamtex.cli.export_cmd import _read_streamlit_theme
        with tempfile.TemporaryDirectory() as d:
            self._write_config(d, '[theme]\nbase = "dark"\n')
            t = _read_streamlit_theme(d)
            assert t["bg"] == "#0e1117"
            assert t["text"] == "#fafafa"

    def test_light_base_resolves_colors(self):
        from streamtex.cli.export_cmd import _read_streamlit_theme
        with tempfile.TemporaryDirectory() as d:
            self._write_config(d, '[theme]\nbase = "light"\n')
            t = _read_streamlit_theme(d)
            assert t["bg"] == "#ffffff"
            assert t["text"] == "#31333f"

    def test_explicit_colors_override_base(self):
        from streamtex.cli.export_cmd import _read_streamlit_theme
        with tempfile.TemporaryDirectory() as d:
            self._write_config(d, '[theme]\nbase = "dark"\nbackgroundColor = "#111"\ntextColor = "#eee"\n')
            t = _read_streamlit_theme(d)
            assert t["bg"] == "#111"
            assert t["text"] == "#eee"

    def test_no_config_returns_empty(self):
        from streamtex.cli.export_cmd import _read_streamlit_theme
        with tempfile.TemporaryDirectory() as d:
            t = _read_streamlit_theme(d)
            assert t == {}

    def test_no_theme_section_returns_empty(self):
        from streamtex.cli.export_cmd import _read_streamlit_theme
        with tempfile.TemporaryDirectory() as d:
            self._write_config(d, '[server]\nport = 8501\n')
            t = _read_streamlit_theme(d)
            assert t == {}

    def test_partial_colors(self):
        from streamtex.cli.export_cmd import _read_streamlit_theme
        with tempfile.TemporaryDirectory() as d:
            self._write_config(d, '[theme]\nbase = "dark"\nbackgroundColor = "#222"\n')
            t = _read_streamlit_theme(d)
            assert t["bg"] == "#222"
            assert t["text"] == "#fafafa"  # from dark defaults


class TestMaterializeServedMedia:
    """Served media are materialised on the export copy (issue #48)."""

    def _setup_media(self, monkeypatch, tmp_path):
        import streamtex.image as image_mod
        media = tmp_path / "media"
        media.mkdir()
        (media / "portrait.png").write_bytes(b"\x89PNG-fake-bytes")
        monkeypatch.setattr(image_mod, "_static_image_base", "app/static/media")
        monkeypatch.setattr(image_mod, "_static_image_fs_root", str(media))
        return media

    def test_no_served_refs_is_identity(self, monkeypatch, tmp_path):
        from streamtex.export import materialize_served_media
        self._setup_media(monkeypatch, tmp_path)
        html = '<html><body><img src="data:image/png;base64,AAAA"></body></html>'
        assert materialize_served_media(html) == html

    def test_collector_rewrites_to_data_folder(self, monkeypatch, tmp_path):
        from streamtex.export import AssetCollector, materialize_served_media
        self._setup_media(monkeypatch, tmp_path)
        collector = AssetCollector()
        html = '<img src="app/static/media/portrait.png" alt="p">'
        out = materialize_served_media(html, collector)
        assert 'src="data/images/portrait_' in out
        assert len(collector.assets) == 1

    def test_deduplication_two_refs_one_asset(self, monkeypatch, tmp_path):
        from streamtex.export import AssetCollector, materialize_served_media
        self._setup_media(monkeypatch, tmp_path)
        collector = AssetCollector()
        html = ('<img src="app/static/media/portrait.png">'
                '<video poster="app/static/media/portrait.png"></video>')
        out = materialize_served_media(html, collector)
        assert out.count('data/images/portrait_') == 2
        assert len(collector.assets) == 1

    def test_embedded_mode_inlines_data_uri(self, monkeypatch, tmp_path):
        from streamtex.export import materialize_served_media
        self._setup_media(monkeypatch, tmp_path)
        html = '<img src="app/static/media/portrait.png">'
        out = materialize_served_media(html, None)
        assert 'src="data:image/png;base64,' in out
        assert "app/static" not in out

    def test_poster_attribute_rewritten(self, monkeypatch, tmp_path):
        from streamtex.export import AssetCollector, materialize_served_media
        self._setup_media(monkeypatch, tmp_path)
        collector = AssetCollector()
        html = '<video poster="app/static/media/portrait.png"></video>'
        out = materialize_served_media(html, collector)
        assert 'poster="data/images/portrait_' in out

    def test_not_found_left_unchanged(self, monkeypatch, tmp_path):
        from streamtex.export import AssetCollector, materialize_served_media
        self._setup_media(monkeypatch, tmp_path)
        collector = AssetCollector()
        html = '<img src="app/static/media/missing.png">'
        out = materialize_served_media(html, collector)
        assert out == html
        assert len(collector.assets) == 0

    def test_project_root_fallback_headless(self, monkeypatch, tmp_path):
        import streamtex.image as image_mod
        from streamtex.export import AssetCollector, materialize_served_media
        monkeypatch.setattr(image_mod, "_static_image_base", "app/static/media")
        monkeypatch.setattr(image_mod, "_static_image_fs_root", None)
        project = tmp_path / "proj"
        (project / "static" / "images").mkdir(parents=True)
        (project / "static" / "images" / "wave.webp").write_bytes(b"RIFF-fake")
        collector = AssetCollector()
        html = '<img src="app/static/images/wave.webp">'
        out = materialize_served_media(html, collector,
                                       project_root=str(project))
        assert 'src="data/images/wave_' in out

    def test_generic_prefix_outside_configured_base(self, monkeypatch, tmp_path):
        # app/static/... refs NOT under the configured base still resolve
        # via the project_root convention (mixed-prefix decks).
        import streamtex.image as image_mod
        from streamtex.export import materialize_served_media
        monkeypatch.setattr(image_mod, "_static_image_base", "app/static/media")
        monkeypatch.setattr(image_mod, "_static_image_fs_root", None)
        project = tmp_path / "proj2"
        (project / "static" / "docs").mkdir(parents=True)
        (project / "static" / "docs" / "x.png").write_bytes(b"\x89PNG")
        html = '<img src="app/static/docs/x.png">'
        out = materialize_served_media(html, None, project_root=str(project))
        assert 'src="data:image/png;base64,' in out
