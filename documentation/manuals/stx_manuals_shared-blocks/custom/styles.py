"""Shared styles for training courses."""

from streamtex.styles import StxStyles, Style


class SharedStyles(StxStyles):
    """Shared style palette for training courses."""

    class colors:
        """Shared color palette"""
        primary_blue = Style("color: #667eea;", "shared_primary_blue")
        accent_teal = Style("color: #20B2AA;", "shared_accent_teal")
        warning_orange = Style("color: #FF8C00;", "shared_warning_orange")
        success_green = Style("color: #228B22;", "shared_success_green")
        neutral_gray = Style("color: #808080;", "shared_neutral_gray")

    class titles:
        """Shared title styles"""
        course_title = StxStyles.GIANT + colors.primary_blue
        section_title = StxStyles.Large + colors.primary_blue
        subsection_title = StxStyles.large + colors.accent_teal
