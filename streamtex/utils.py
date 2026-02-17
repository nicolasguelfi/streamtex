"""StreamTeX utilities — backward-compatible re-exports from split modules.

Generic utilities (strip_html, generate_key) remain here.
Image utilities re-exported from image_utils.py.
Link preview utilities re-exported from link_preview.py.
"""

import re
import uuid

# Re-export image utilities (backward compat for `from .utils import __is_url` etc.)
from .image_utils import (
    _is_url as __is_url,
    _is_absolute_path as __is_absolute_path,
    _is_relative_path as __is_relative_path,
    _get_mime_type as __get_mime_type,
    _get_base64_encoded_image as __get_base64_encoded_image,
)

# Re-export link preview utilities
from .link_preview import (
    inject_link_preview_scaffold,
    contain_link,
    _get_page_preview as __get_page_preview,
)


def strip_html(html_string):
    """Remove all HTML tags from a string and return plain text."""
    html_tag_pattern = re.compile(r'<.*?>')
    plain_text = re.sub(html_tag_pattern, '', html_string)
    return plain_text


def generate_key(prefix: str = "block"):
    """Generate a unique key with the given prefix."""
    return f"{prefix}-{uuid.uuid4().hex}"
