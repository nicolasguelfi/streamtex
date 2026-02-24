"""Styles for the collection home page."""

from streamtex.styles import StxStyles, Style, Text


class Styles(StxStyles):
    """Collection-specific styles for the home page."""

    class project:
        """Project-specific style groups"""

        class colors:
            """Collection color palette"""
            accent_teal = Style("color: #2EC4B6;", "collection_accent_teal")
            highlight_amber = Style("color: #F39C12;", "collection_highlight_amber")
            success_green = Style("color: #27AE60;", "collection_success_green")
            neutral_gray = Style("color: #95A5A6;", "collection_neutral_gray")

        class titles:
            """Title styles — 4-level hierarchy with floor at large (32pt)."""
            main_title = Style.create(
                StxStyles.Huge + Text.weights.bold_weight,
                "collection_main_title"
            )
            section_title = Style.create(
                Style("color: #2EC4B6;", "_ct") + Text.weights.bold_weight + Text.sizes.LARGE_size,
                "collection_section_title"
            )
            section_subtitle = Style.create(
                Style("color: #F39C12;", "_cst") + Text.weights.bold_weight + Text.sizes.Large_size,
                "collection_section_subtitle"
            )
            subsection_title = Style.create(
                Style("color: #27AE60;", "_csst") + Text.weights.bold_weight + Text.sizes.large_size,
                "collection_subsection_title"
            )

    class container:
        """Container and layout styles"""

        class bg_colors:
            """Background colors for dark mode"""
            dark_bg_secondary = Style(
                "background:linear-gradient(135deg, rgba(40, 44, 52, 0.9) 0%, rgba(30, 33, 40, 0.9) 100%);"
                + "box-shadow:inset 0 1px 0 rgba(255,255,255,0.05);",
                "dark_bg_secondary"
            )
