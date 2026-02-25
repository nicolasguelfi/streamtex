"""Image utility functions: base64 encoding, MIME detection, URL/path detection."""

import base64
import logging
import os

import streamlit as st

logger = logging.getLogger(__name__)


def _is_url(path: str):
    """Checks if the given path is a URL."""
    return path.startswith(("http://", "https://", "www."))


def _is_absolute_path(path: str):
    """Checks if the given path is an absolute path."""
    return os.path.isabs(path)


def _is_relative_path(path: str):
    """Checks if the given path is a relative path."""
    return path.startswith((".", "..", "/", "\\"))


def _get_mime_type(file_path: str):
    """Determine the MIME type based on the file extension."""
    import mimetypes
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith('image/'):
        return mime
    # Fallback for common types not in mimetypes DB
    ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ''
    fallback = {
        'svg': 'image/svg+xml',
        'webp': 'image/webp',
        'bmp': 'image/bmp',
        'ico': 'image/x-icon',
    }
    return fallback.get(ext)


@st.cache_data(show_spinner=False)
def _get_base64_encoded_image(file_path: str, _mtime: float = 0):
    """Converts an image to a base64 encoded string.

    The result is cached by Streamlit based on (file_path, _mtime).
    The _mtime parameter ensures the cache is invalidated when the file
    changes on disk.
    """
    try:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.warning("Error reading file %s: %s", file_path, e)
        return None
