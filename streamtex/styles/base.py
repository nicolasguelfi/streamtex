"""StxStyles — the aggregation class that composes all style categories."""

from .container import BackgroundColors, Container
from .core import Style
from .text import Text
from .visibility import Visibility

# Wire up Text.bg_colors now that BackgroundColors is available
Text.bg_colors = BackgroundColors

# Module-level convenience aliases
text = Text
container = Container
visibility = Visibility


class StxStyles:

    ### Enums #####
    none = Style("", "none")
    text = Text
    container = Container
    visibility = Visibility

    bold = text.weights.bold_weight
    reset_bold = text.weights.normal_weight
    italic = text.decors.italic_text
    center_txt = text.alignments.center_align

    reset = (text.colors.reset + BackgroundColors.reset_bg
             + text.weights.normal_weight + text.sizes.medium_size + text.alignments.left_align)

    light_bg = Style("background-color: White; padding: 8px;", "light_bg")
    """White background with padding — use with ``st_block``, ``st_image``,
    ``st_mermaid``, or ``st_tikz`` to make diagrams readable on dark pages."""

    GIANT = text.sizes.GIANT_size
    """196pt"""
    Giant = text.sizes.Giant_size
    """128pt"""
    giant = text.sizes.giant_size
    """112pt"""
    Huge = text.sizes.Huge_size
    """96pt"""
    huge = text.sizes.huge_size
    """80pt"""
    LARGE = text.sizes.LARGE_size
    """64pt"""
    Large = text.sizes.Large_size
    """48pt"""
    large = text.sizes.large_size
    """32pt"""
    big = text.sizes.big_size
    """24pt"""
    medium = text.sizes.medium_size
    """16pt"""
    little = text.sizes.little_size
    """12pt"""
    small = text.sizes.small_size
    """8pt"""
    tiny = text.sizes.tiny_size
    """4pt"""


# Backward compatibility alias (deprecated)
StreamTeX_Styles = StxStyles
