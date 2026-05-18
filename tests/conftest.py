"""Shared fixtures for StreamTeX tests."""

from pathlib import Path
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


@pytest.fixture(autouse=True)
def _isolate_global_dev_config(tmp_path_factory, monkeypatch):
    """Redirect ~/.config/streamtex/dev.json to a tmp path during tests.

    Without this, tests that exercise repo resolution (template lookup,
    install/status flows) inherit the developer's actual `stx dev register`
    entries and may fall through to a path that doesn't match the fixture.
    """
    import streamtex.cli.dev_config as dev_config

    isolated_dir = Path(tmp_path_factory.mktemp("stx-dev-config"))
    monkeypatch.setattr(dev_config, "_GLOBAL_DIR", isolated_dir)
    monkeypatch.setattr(dev_config, "_GLOBAL_FILE", isolated_dir / "dev.json")
