from typing import Literal

from .export import _render


def st_space(direction: Literal["v", "h"] = "v", size="1em") -> str:
    """
    Generates an HTML tag to create vertical or horizontal spacing.

    :param direction: "v" for vertical spacing, "h" for horizontal spacing. Defaults to "v".
    :param size: A CSS string (e.g. "10px", "-5vh") for a fixed value,
        or a number (e.g. 2, -3) for a font-relative value in em. Defaults to "1em".
        Negative values pull content in the opposite direction using CSS margin.
    :return: A string containing an HTML tag for the specified spacing.

    Notes:
    - Positive vertical spacing uses ``height``; positive horizontal uses ``padding-left``.
    - Negative vertical spacing uses ``margin-top``; negative horizontal uses ``margin-left``.
      Negative margins are valid CSS and cause content to overlap or shift.
    """
    # Convert numeric size to em-based string
    if not isinstance(size, str):
        size = f"{size}em"

    # Detect negative values → use margin instead of height/padding
    is_negative = size.lstrip().startswith("-")

    # Return appropriate HTML based on orientation and sign
    if direction == "v":
        if is_negative:
            space_tag = f'<div style="margin-top: {size};"></div>'
        else:
            space_tag = f'<div style="height: {size};"></div>'
    else:
        if is_negative:
            space_tag = f'<span style="margin-left: {size};"></span>'
        else:
            space_tag = f'<span style="padding-left: {size};"></span>'

    _render(space_tag)

def st_br(count: int = 1):
    """Add vertical line breaks. count=1 adds one <br>, count=2 adds two, etc."""
    html = "<br>" * max(1, count)
    _render(html)
