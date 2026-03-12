"""Tests for link_preview — hover card injection and contain_link helper."""

from unittest.mock import MagicMock, patch

from streamtex.link_config import LinkConfig, set_link_config


class TestContainLink:
    def setup_method(self):
        """Reset link config to defaults."""
        set_link_config(LinkConfig())

    def test_no_link_returns_content(self):
        """When link is empty, return content unchanged."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="Hello", link="")
        assert result == "Hello"

    def test_external_link_has_blank_target(self):
        """External links get target=_blank by default."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="Click", link="https://example.com")
        assert 'target="_blank"' in result
        assert 'href="https://example.com"' in result
        assert "Click" in result

    def test_external_link_has_streamtex_link_class(self):
        """External links with hover=True get the streamtex-link class."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="Link", link="https://example.com", hover=True)
        assert 'class="streamtex-link"' in result

    def test_external_link_no_hover_no_class(self):
        """External links with hover=False have no streamtex-link class."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="Link", link="https://example.com", hover=False)
        assert "streamtex-link" not in result

    def test_internal_link_no_target(self):
        """Internal (#) links use _self target — no target attr emitted."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="Section", link="#intro")
        assert 'href="#intro"' in result
        assert "target=" not in result

    def test_internal_link_no_hover_class(self):
        """Internal links never get the streamtex-link class."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="Section", link="#intro", hover=True)
        assert "streamtex-link" not in result

    def test_no_link_decor(self):
        """no_link_decor=True adds inline style to remove decoration."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="X", link="https://a.com", no_link_decor=True)
        assert "text-decoration: none" in result
        assert "color: inherit" in result

    def test_custom_link_config(self):
        """Custom LinkConfig changes target attribute."""
        from streamtex.link_preview import contain_link
        set_link_config(LinkConfig(external_target="_self"))
        result = contain_link(html_content="Link", link="https://example.com")
        # _self means no target attr emitted
        assert "target=" not in result

    def test_link_strips_whitespace(self):
        """Link URLs are stripped of leading/trailing whitespace."""
        from streamtex.link_preview import contain_link
        result = contain_link(html_content="X", link="  https://example.com  ")
        assert 'href="https://example.com"' in result


class TestGetPagePreview:
    def test_successful_fetch(self):
        """Successful fetch returns title, favicon, and True."""
        from streamtex.link_preview import _get_page_preview

        mock_response = MagicMock()
        mock_response.content = b"""
        <html><head><title>Test Page</title>
        <link rel="icon" href="/favicon.ico">
        </head><body></body></html>
        """
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            title, favicon, success = _get_page_preview("https://example.com")
        assert title == "Test Page"
        assert success is True
        assert favicon is not None

    def test_connection_error_returns_false(self):
        """Connection error returns URL as title and False."""
        import requests

        from streamtex.link_preview import _get_page_preview

        with patch("requests.get", side_effect=requests.exceptions.ConnectionError):
            title, favicon, success = _get_page_preview("https://example.com")
        assert success is False
        assert title == "https://example.com"

    def test_timeout_returns_false(self):
        """Timeout returns URL as title and False."""
        import requests

        from streamtex.link_preview import _get_page_preview

        with patch("requests.get", side_effect=requests.exceptions.Timeout):
            title, favicon, success = _get_page_preview("https://example.com")
        assert success is False


class TestInjectLinkPreviewScaffold:
    def test_injects_css_and_js(self, mock_streamlit):
        """Scaffold injects both CSS and JS via st.html()."""
        from streamtex.link_preview import inject_link_preview_scaffold
        inject_link_preview_scaffold()
        assert mock_streamlit["html"].call_count == 2
        calls = [c[0][0] for c in mock_streamlit["html"].call_args_list]
        assert any("<style>" in c for c in calls)
        assert any("<script>" in c for c in calls)
