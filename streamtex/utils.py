"""StreamTeX utilities — backward-compatible re-exports from split modules.

Generic utilities (strip_html, generate_key) remain here.
Image utilities re-exported from image_utils.py.
Link preview utilities re-exported from link_preview.py.
"""

import inspect
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


def exec_static(
    path: str,
    context: dict | None = None,
    start_line: int | None = None,
    end_line: int | None = None,
) -> None:
    """Load a Python file via ``resolve_static()`` and execute it.

    If *context* is ``None``, the caller's ``globals + locals`` are used so
    that names like ``st_write``, ``s``, ``bs`` etc. are available.

    *start_line* / *end_line* allow executing only a slice of the file
    (1-based, inclusive).
    """
    from .blocks import resolve_static

    resolved = resolve_static(path)
    code = Path(resolved).read_text(encoding="utf-8")
    if start_line or end_line:
        lines = code.splitlines()
        s = (start_line or 1) - 1
        e = end_line or len(lines)
        code = "\n".join(lines[s:e])
    if context is None:
        frame = inspect.currentframe().f_back
        context = {**frame.f_globals, **frame.f_locals}
    exec(code, context)  # noqa: S102


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
