from typing import Literal

from .export import _render


def st_space(direction: Literal["v", "h"] = "v", size="1em") -> str:
    """
    Generates an HTML tag to create vertical or horizontal spacing.

    :param direction: "v" for vertical spacing, "h" for horizontal spacing. Defaults to "v".
    :param size: A CSS string (e.g. "10px") for a fixed value,
        or a number (e.g. 2) for a font-relative value in em. Defaults to "1em".
    :return: A string containing an HTML tag for the specified spacing.

    Notes:
    - Vertical spacing is implemented using `height` and horizontal spacing uses `padding-left`.
    """
    # Convert numeric size to em-based string
    if not isinstance(size, str):
        size = f"{size}em"

    # Return appropriate HTML based on orientation
    if direction == "v":
        # Vertical space with explicit height
        space_tag = f"""<div style="height: {size};"></div>"""
    else:
        # Horizontal space with padding-left
        space_tag = f"""<span style="padding-left: {size};"></span>"""

    _render(space_tag)

def st_br(count: int = 1):
    """Add vertical line breaks. count=1 adds one <br>, count=2 adds two, etc."""
    html = "<br>" * max(1, count)
    _render(html)
