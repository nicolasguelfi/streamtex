"""Shared styles for training courses."""

from streamtex.styles import StreamTeX_Styles, Style


class SharedStyles(StreamTeX_Styles):
    """Shared style palette for training courses."""

    class colors:
        """Shared color palette"""
        primary_blue = Style.create(StreamTeX_Styles.text.colors.reset, "shared_primary_blue", color="#667eea")
        accent_teal = Style.create(StreamTeX_Styles.text.colors.reset, "shared_accent_teal", color="#20B2AA")
        warning_orange = Style.create(StreamTeX_Styles.text.colors.reset, "shared_warning_orange", color="#FF8C00")
        success_green = Style.create(StreamTeX_Styles.text.colors.reset, "shared_success_green", color="#228B22")
        neutral_gray = Style.create(StreamTeX_Styles.text.colors.reset, "shared_neutral_gray", color="#808080")

    class titles:
        """Shared title styles"""
        course_title = StreamTeX_Styles.text.Titles.GIANT + colors.primary_blue
        section_title = StreamTeX_Styles.text.Titles.Large + colors.primary_blue
        subsection_title = StreamTeX_Styles.text.Titles.large + colors.accent_teal
