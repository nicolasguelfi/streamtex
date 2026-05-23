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
    # Anchored on the BASE palier (idx_7 = base_pt_desktop). text_base is
    # literally the source-of-truth base. Smaller aliases (text_xs/sm)
    # render at floor-respecting sizes ≥ 14pt = 18.7px on desktop with
    # default base_pt_desktop=18. Larger aliases scale up by curve ratios.
    # The base re-anchors automatically if the user passes
    # st_book(scale=ScaleConfig(base_pt_desktop=...)).
    text_xs    = text.sizes.idx_5    # palier 5 = 0.78 × base = 14pt @18
    text_sm    = text.sizes.idx_6    # palier 6 = 0.89 × base = 16pt @18
    text_base  = text.sizes.idx_7    # palier 7 = 1.00 × base = 18pt @18 (BASE)
    text_lg    = text.sizes.idx_8    # palier 8 = 1.11 × base = 20pt @18
    text_xl    = text.sizes.idx_9    # palier 9 = 1.22 × base = 22pt @18
    text_2xl   = text.sizes.idx_10   # palier 10 = 1.33 × base = 24pt @18
    text_3xl   = text.sizes.idx_11   # palier 11 = 1.56 × base = 28pt @18
    text_4xl   = text.sizes.idx_12   # palier 12 = 1.78 × base = 32pt @18
    text_5xl   = text.sizes.idx_13   # palier 13 = 2.00 × base = 36pt @18
    text_6xl   = text.sizes.idx_15   # palier 15 = 2.67 × base = 48pt @18
    text_7xl   = text.sizes.idx_16   # palier 16 = 3.33 × base = 60pt @18
    text_8xl   = text.sizes.idx_17   # palier 17 = 4.00 × base = 72pt @18
    text_9xl   = text.sizes.idx_19   # palier 19 = 7.11 × base = 128pt @18
