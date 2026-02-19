"""Styles for the collection home page."""

from streamtex.styles import StreamTeX_Styles, Style


class Styles(StreamTeX_Styles):
    """
    Project-specific styles for the collection home page.

    Inherits from StreamTeX_Styles and can be extended with custom styles.
    """

    class project:
        """Project-specific style groups"""

        class titles:
            """Title styles for the collection"""
            main_title = Styles.text.Titles.GIANT + Styles.text.colors.reset

        class cards:
            """Card styling for project displays"""
            # Add any custom card styles here
            pass
