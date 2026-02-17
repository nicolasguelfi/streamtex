"""Visibility-related style definitions."""

from .core import Style


class Visibility:
    hidden = Style("display: none;", "hidden")
    """block doesn't take up space in page"""

    visible = Style("visibility: visible;", "visible")

    invisible = Style("visibility: hidden;", "invisible")
    """block takes up space in page"""
