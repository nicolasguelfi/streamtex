import streamlit as st
from typing import Literal

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
    if type(size) is int:
        size = str(size) + "em"

    # Return appropriate HTML based on orientation
    if direction == "v":
        # Vertical space with padding-top
        space_tag = f"""<div style="padding-top: {size};"></div>"""
    else:
        # Horizontal space with padding-left
        space_tag = f"""<span style="padding-left: {size};"></span>"""
    
    st.html(space_tag)

def st_br():
   
   return st_space("v", 0)