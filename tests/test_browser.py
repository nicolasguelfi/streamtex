"""Tests for streamtex.browser — Chrome recommendation banner."""

from unittest.mock import patch

from streamtex.browser import _CHROME_BANNER_JS, st_chrome_banner


def test_chrome_banner_calls_components_html():
    """st_chrome_banner() should inject JS via components.html with height=0."""
    with patch("streamtex.browser._components.html") as mock_html:
        st_chrome_banner()
        mock_html.assert_called_once_with(_CHROME_BANNER_JS, height=0)


def test_chrome_banner_js_contains_detection():
    """The injected JS should contain Chrome user-agent detection."""
    assert "Chrome\\/" in _CHROME_BANNER_JS
    assert "stx-chrome-banner" in _CHROME_BANNER_JS


def test_chrome_banner_js_excludes_edge_opera():
    """The detection should exclude Edge and Opera (Chromium-based but not Chrome)."""
    assert "Edg\\/" in _CHROME_BANNER_JS
    assert "OPR\\/" in _CHROME_BANNER_JS


def test_chrome_banner_js_is_dismissible():
    """The banner should have a close button (onclick removes parent)."""
    assert "this.parentElement.remove()" in _CHROME_BANNER_JS


def test_chrome_banner_js_detects_ios():
    """The banner should skip entirely on iOS (all browsers use WebKit)."""
    assert "isIOS" in _CHROME_BANNER_JS
    assert "iPad|iPhone|iPod" in _CHROME_BANNER_JS
    assert "maxTouchPoints" in _CHROME_BANNER_JS


def test_chrome_banner_js_detects_crios():
    """The detection should recognize Chrome on iOS (CriOS user-agent token)."""
    assert "CriOS\\/" in _CHROME_BANNER_JS
