import streamlit as st
from typing import Literal
from .export import _render

def st_space(direction: Literal["v", "h"] = "v", size="1em") -> str:
    """
    Generates an HTML tag to create vertical or horizontal spacing.

    :param direction: "v" for vertical spacing, "h" for horizontal spacing. Defaults to "v".
    :param size: The size of the space (e.g., "10px" or an integer, which will be converted to "em"). Defaults to "1em".
    :return: A string containing an HTML tag for the specified spacing.

    Notes:
    - Vertical spacing is implemented using `padding-top` and horizontal spacing uses `padding-left`.
    """
    # Convert integer size to em-based string
    if isinstance(size, int):
        size = str(size) + "em"

    # Return appropriate HTML based on orientation
    if direction == "v":
        # Vertical space with padding-top
        space_tag = f"""<div style="padding-top: {size};"></div>"""
    else:
        # Horizontal space with padding-left
        space_tag = f"""<span style="padding-left: {size};"></span>"""
    
    _render(space_tag)

def st_br(count: int = 1):
    """Add vertical line breaks. count=1 adds one <br>, count=2 adds two, etc."""
    html = "<br>" * max(1, count)
    _render(html)