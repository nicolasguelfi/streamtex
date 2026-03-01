"""StreamTeX utilities — backward-compatible re-exports from split modules.

Generic utilities (strip_html, generate_key) remain here.
Image utilities re-exported from image_utils.py.
Link preview utilities re-exported from link_preview.py.
"""

import re
import uuid
from pathlib import Path

# Re-export image utilities (backward compat for `from .utils import __is_url` etc.)
from .image_utils import _get_base64_encoded_image as __get_base64_encoded_image  # noqa: F401
from .image_utils import _get_mime_type as __get_mime_type  # noqa: F401
from .image_utils import _is_absolute_path as __is_absolute_path  # noqa: F401
from .image_utils import _is_relative_path as __is_relative_path  # noqa: F401
from .image_utils import _is_url as __is_url  # noqa: F401

# Re-export link preview utilities
from .link_preview import _get_page_preview as __get_page_preview  # noqa: F401
from .link_preview import contain_link  # noqa: F401
from .link_preview import inject_link_preview_scaffold  # noqa: F401


def strip_html(html_string):
    """Remove all HTML tags from a string and return plain text."""
    html_tag_pattern = re.compile(r'<.*?>')
    plain_text = re.sub(html_tag_pattern, '', html_string)
    return plain_text


def generate_key(prefix: str = "block"):
    """Generate a unique key with the given prefix."""
    return f"{prefix}-{uuid.uuid4().hex}"


def resolve_content(
    content: str = "",
    file: str | None = None,
    encoding: str = "utf-8",
) -> str:
    """Resolve textual content from inline string or file.

    When *file* is provided, ``resolve_static()`` is used first so that
    relative paths are searched across configured static source directories.

    Raises ``ValueError`` if both *content* and *file* are provided.
    Raises ``FileNotFoundError`` if *file* does not exist.
    """
    if file and content:
        raise ValueError("Provide 'content' or 'file', not both")
    if file:
        from .blocks import resolve_static

        resolved = resolve_static(file)
        return Path(resolved).read_text(encoding=encoding)
    return content
