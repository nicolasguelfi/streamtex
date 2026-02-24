"""Shared styles for training courses."""

from streamtex.styles import StxStyles, Style


class _SharedColors:
    """Shared color palette — defined at module level for cross-reference."""
    primary_blue = Style("color: #667eea;", "shared_primary_blue")
    accent_teal = Style("color: #20B2AA;", "shared_accent_teal")
    warning_orange = Style("color: #FF8C00;", "shared_warning_orange")
    success_green = Style("color: #228B22;", "shared_success_green")
    neutral_gray = Style("color: #808080;", "shared_neutral_gray")


class SharedStyles(StxStyles):
    """Shared style palette for training courses."""

    colors = _SharedColors

    class titles:
        """Shared title styles — 4-level hierarchy with floor at large (32pt)."""
        course_title = StxStyles.Huge + StxStyles.bold + _SharedColors.primary_blue
        section_title = StxStyles.LARGE + StxStyles.bold + _SharedColors.accent_teal
        section_subtitle = StxStyles.Large + StxStyles.bold + _SharedColors.warning_orange
        subsection_title = StxStyles.large + StxStyles.bold + _SharedColors.success_green
