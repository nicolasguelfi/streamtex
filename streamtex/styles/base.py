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
    """160pt"""
    giant = text.sizes.giant_size
    """128pt"""
    HUGE = text.sizes.HUGE_size
    """96pt"""
    Huge = text.sizes.Huge_size
    """80pt"""
    huge = text.sizes.huge_size
    """64pt"""
    LARGE = text.sizes.LARGE_size
    """48pt"""
    Large = text.sizes.Large_size
    """32pt"""
    large = text.sizes.large_size
    """24pt"""
    big = text.sizes.big_size
    """16pt"""
    medium = text.sizes.medium_size
    """12pt"""
    little = text.sizes.little_size
    """8pt"""
    small = text.sizes.small_size
    """6pt"""
    tiny = text.sizes.tiny_size
    """4pt"""

    # --- Indexed responsive scale (subscript access) ---
    class _IndexedScale:
        """Subscript access: ``s.scale[0]`` … ``s.scale[28]``.

        Out-of-range indices are clamped to the valid range (debug-logged).
        """

        _cache = [getattr(text.sizes, f"idx_{i}") for i in range(29)]
        _count = 29

        def __class_getitem__(cls, i):
            if not isinstance(i, int):
                raise TypeError(
                    f"scale index must be int, got {type(i).__name__}"
                )
            if i < 0:
                import logging
                logging.getLogger("streamtex.styles").debug(
                    "scale[%d] clamped to scale[0]", i
                )
                i = 0
            elif i >= cls._count:
                import logging
                logging.getLogger("streamtex.styles").debug(
                    "scale[%d] clamped to scale[%d]", i, cls._count - 1
                )
                i = cls._count - 1
            return cls._cache[i]

    scale = _IndexedScale

    # --- Tailwind-style aliases ---
    # Names map to specific palier indices. If the user picks a different
    # ScaleCurve at runtime, the index→pt mapping changes but the alias
    # names stay stable.
    text_xs    = text.sizes.idx_2    # 10pt desktop (caption)
    text_sm    = text.sizes.idx_3    # 11pt
    text_base  = text.sizes.idx_4    # 12pt (body baseline)
    text_lg    = text.sizes.idx_5    # 14pt
    text_xl    = text.sizes.idx_6    # 16pt
    text_2xl   = text.sizes.idx_7    # 18pt
    text_3xl   = text.sizes.idx_9    # 22pt
    text_4xl   = text.sizes.idx_10   # 24pt
    text_5xl   = text.sizes.idx_12   # 32pt
    text_6xl   = text.sizes.idx_15   # 48pt
    text_7xl   = text.sizes.idx_16   # 60pt
    text_8xl   = text.sizes.idx_17   # 72pt
    text_9xl   = text.sizes.idx_19   # 128pt


# Backward compatibility alias (deprecated)
StreamTeX_Styles = StxStyles
