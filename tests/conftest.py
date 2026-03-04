"""Shared fixtures for StreamTeX tests."""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_streamlit():
    """Mock streamlit.html and other st calls to prevent actual rendering."""
    with patch("streamlit.html") as mock_html, \
         patch("streamlit.markdown") as mock_md:
        mock_html.return_value = None
        mock_md.return_value = None
        yield {"html": mock_html, "markdown": mock_md}
