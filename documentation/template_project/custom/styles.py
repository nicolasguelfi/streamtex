"""Project-specific styles. Extend StreamTeX_Styles with your custom colors and compositions.

Usage in blocks:
    from custom.styles import Styles as s
    st_write(s.project.colors.my_color, "Hello")
    st_write(s.project.titles.my_title, "Title")
"""

from streamtex.styles import Style, Text, Container, StreamTeX_Styles


class ColorsCustom:
    """Define project-specific colors here."""
    # example = Style("color: #FF6B35;", "example")
    pass


class TextStylesCustom:
    """Define project-specific title/subtitle compositions here.

    Example:
        my_title = Style.create(
            ColorsCustom.example + Text.weights.bold_weight + Text.sizes.Giant_size,
            "my_title"
        )
    """
    pass


class Custom:
    """Aggregation class for all project-specific styles."""
    colors = ColorsCustom
    titles = TextStylesCustom


class Styles(StreamTeX_Styles):
    """Main Styles class — inherits all StreamTeX styles + project-specific ones."""
    project = Custom
