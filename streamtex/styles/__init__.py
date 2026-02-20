"""
StreamTeX Styles package — backward-compatible re-exports.

All public names from the old monolithic styles.py are available here,
so `from streamtex.styles import *` continues to work.
"""

# Core primitives
from .core import Style, ListStyle, StyleGrid, theme, add_css, remove_css

# Text styles
from .text import (
    Decors, Weights, Alignments, Colors, Sizes, Fonts, Wrap,
    Titles, Text,
)

# Container styles
from .container import (
    BackgroundColors, Paddings, Margins, ContainerSizes,
    Flex, Layouts, Borders, Positions,
    ListStyles, Container,
)

# Visibility
from .visibility import Visibility

# Aggregation class and module-level aliases
from .base import StxStyles, StreamTeX_Styles, text, container, visibility
