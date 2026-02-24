"""Unit tests for streamtex.plantuml — PlantUML diagram rendering."""

from unittest.mock import MagicMock, patch

import streamtex.export as export_mod
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.plantuml import _encode, st_plantuml

SAMPLE_CODE = """\
@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response
@enduml"""

FAKE_SVG = '<svg xmlns="http://www.w3.org/2000/svg"><text>diagram</text></svg>'


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

class TestEncoding:
    """Tests for the PlantUML text encoding function."""

    def test_returns_string(self):
        """_encode() returns a non-empty string."""
        result = _encode(SAMPLE_CODE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_url_safe_characters(self):
        """Encoded string contains only URL-safe characters (PlantUML alphabet)."""
        result = _encode(SAMPLE_CODE)
        allowed = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_")
        assert all(c in allowed for c in result), (
            f"Non-URL-safe characters found: {set(result) - allowed}"
        )

    def test_deterministic(self):
        """Same input always produces the same encoding."""
        assert _encode(SAMPLE_CODE) == _encode(SAMPLE_CODE)

    def test_different_inputs_differ(self):
        """Different inputs produce different encodings."""
        other = "@startuml\nBob -> Alice: Hello\n@enduml"
        assert _encode(SAMPLE_CODE) != _encode(other)


# ---------------------------------------------------------------------------
# Live rendering (via components.html with pan/zoom)
# ---------------------------------------------------------------------------

class TestLiveRendering:
    """Tests for the live components.html() rendering path."""

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_renders_via_components_html(self, mock_components, mock_fetch):
        """The diagram is rendered via components.html()."""
        st_plantuml(SAMPLE_CODE)
        mock_components.html.assert_called_once()
        html_arg = mock_components.html.call_args[0][0]
        assert "<svg" in html_arg

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_light_bg_true_sets_white_background(self, mock_components, mock_fetch):
        """When light_bg=True, background is white."""
        st_plantuml(SAMPLE_CODE, light_bg=True)
        html_arg = mock_components.html.call_args[0][0]
        assert "#fff" in html_arg

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_light_bg_false_sets_transparent_background(self, mock_components, mock_fetch):
        """When light_bg=False, background is transparent."""
        st_plantuml(SAMPLE_CODE, light_bg=False)
        html_arg = mock_components.html.call_args[0][0]
        assert "transparent" in html_arg

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_default_height_500(self, mock_components, mock_fetch):
        """Default height is 500 pixels."""
        st_plantuml(SAMPLE_CODE)
        assert mock_components.html.call_args[1]["height"] == 500

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_custom_height(self, mock_components, mock_fetch):
        """Height parameter is forwarded to components.html()."""
        st_plantuml(SAMPLE_CODE, height=800)
        assert mock_components.html.call_args[1]["height"] == 800

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_scrolling_enabled(self, mock_components, mock_fetch):
        """scrolling=True is passed to components.html() for interactivity."""
        st_plantuml(SAMPLE_CODE)
        assert mock_components.html.call_args[1]["scrolling"] is True

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_style_wraps_in_st_block(self, mock_components, mock_fetch):
        """When style is provided, diagram is wrapped in st_block."""
        from streamtex.styles import Style
        my_style = Style("border: 1px solid red;")
        with patch("streamtex.plantuml.st_block") as mock_block:
            mock_block.return_value.__enter__ = MagicMock()
            mock_block.return_value.__exit__ = MagicMock(return_value=False)
            st_plantuml(SAMPLE_CODE, style=my_style)
            mock_block.assert_called_once_with(my_style)

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_pan_zoom_js_included(self, mock_components, mock_fetch):
        """The HTML includes pan-zoom JavaScript (wheel, mousedown)."""
        st_plantuml(SAMPLE_CODE)
        html_arg = mock_components.html.call_args[0][0]
        assert "addEventListener" in html_arg
        assert "wheel" in html_arg
        assert "mousedown" in html_arg
        assert "zoomIn" in html_arg
        assert "resetView" in html_arg

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_full_html_document(self, mock_components, mock_fetch):
        """The HTML is a complete document (DOCTYPE, html, body)."""
        st_plantuml(SAMPLE_CODE)
        html_arg = mock_components.html.call_args[0][0]
        assert "<!DOCTYPE html>" in html_arg
        assert "<html>" in html_arg
        assert "<body>" in html_arg

    @patch("streamtex.plantuml._fetch_svg", side_effect=Exception("network error"))
    @patch("streamtex.plantuml.st")
    @patch("streamtex.plantuml.components")
    def test_fallback_on_network_error(self, mock_components, mock_st, mock_fetch):
        """When fetch fails, a warning + raw code is shown."""
        st_plantuml(SAMPLE_CODE)
        mock_st.warning.assert_called_once()
        mock_st.code.assert_called_once()
        assert mock_st.code.call_args[0][0] == SAMPLE_CODE

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_svg_injected_in_html(self, mock_components, mock_fetch):
        """The fetched SVG is injected into the HTML template."""
        st_plantuml(SAMPLE_CODE)
        html_arg = mock_components.html.call_args[0][0]
        assert FAKE_SVG in html_arg

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_custom_server(self, mock_components, mock_fetch):
        """Custom server URL is forwarded to _fetch_svg."""
        st_plantuml(SAMPLE_CODE, server="http://localhost:8080")
        mock_fetch.assert_called_with(SAMPLE_CODE, "http://localhost:8080")


# ---------------------------------------------------------------------------
# Export rendering
# ---------------------------------------------------------------------------

class TestExportRendering:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_noop_when_inactive(self, mock_components, mock_fetch):
        """No export output when export is not active."""
        st_plantuml(SAMPLE_CODE)
        assert generate_export_html() is None

    @patch("streamtex.plantuml._fetch_svg", return_value=FAKE_SVG)
    @patch("streamtex.plantuml.components")
    def test_export_svg_when_active(self, mock_components, mock_fetch):
        """When export is active and fetch succeeds, SVG is appended."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_plantuml(SAMPLE_CODE)
        html = generate_export_html()
        assert "stx-plantuml" in html
        assert FAKE_SVG in html

    @patch("streamtex.plantuml._fetch_svg", side_effect=Exception("network error"))
    @patch("streamtex.plantuml.st")
    @patch("streamtex.plantuml.components")
    def test_export_fallback_on_error(self, mock_components, mock_st, mock_fetch):
        """When fetch fails, raw code is exported as <pre>."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_plantuml(SAMPLE_CODE)
        html = generate_export_html()
        assert "stx-plantuml" in html
        assert "<pre" in html
        assert "Alice" in html

    @patch("streamtex.plantuml._fetch_svg", side_effect=Exception("fail"))
    @patch("streamtex.plantuml.st")
    @patch("streamtex.plantuml.components")
    def test_export_escapes_html(self, mock_components, mock_st, mock_fetch):
        """Fallback properly escapes HTML special characters."""
        reset_export_buffer(ExportConfig(enabled=True))
        malicious = '@startuml\nAlice -> Bob: <script>alert(1)</script>\n@enduml'
        st_plantuml(malicious)
        html = generate_export_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
