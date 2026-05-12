"""Tests for streamtex.browser — Chrome recommendation banner."""

from unittest.mock import patch

from streamtex.browser import _CHROME_BANNER_JS, st_chrome_banner


def test_chrome_banner_calls_st_iframe():
    """st_chrome_banner() should inject JS via st.iframe with height=1."""
    with patch("streamtex.browser.st.iframe") as mock_iframe:
        st_chrome_banner()
        mock_iframe.assert_called_once_with(_CHROME_BANNER_JS, height=1)


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


def test_st_book_chrome_banner_default_is_false():
    """Since 0.6.25 the Chrome banner is OFF by default — the marker-runtime
    migration eliminated the Chrome-specific advantage that motivated it.
    The function remains exported so users can opt back in explicitly."""
    import inspect

    from streamtex.book import st_book

    sig = inspect.signature(st_book)
    default = sig.parameters["chrome_banner"].default
    assert default is False, (
        f"chrome_banner default should be False since 0.6.25, got {default!r}"
    )
