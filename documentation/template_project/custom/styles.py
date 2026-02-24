"""Project-specific styles. Extends StxStyles with a minimal working palette.

Usage in blocks:
    from custom.styles import Styles as s
    st_write(s.project.colors.primary, "Hello")
    st_write(s.project.titles.main_title, "Title")
"""

from streamtex.styles import Style, Text, Container, StxStyles


class ColorsCustom:
    """Project text colors."""
    primary = Style("color: #4A90D9;", "primary")
    accent = Style("color: #2EC4B6;", "accent")
    muted = Style("color: #95A5A6;", "muted")


class BackgroundsCustom:
    """Project background colors for callout containers."""
    callout_bg = Style("background-color: rgba(74, 144, 217, 0.12);", "callout_bg")
    code_box_bg = Style("background-color: rgba(74, 144, 217, 0.08);", "code_box_bg")


class TextStylesCustom:
    """Project title compositions."""
    main_title = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight + Text.sizes.Giant_size,
        "main_title"
    )
    section_title = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight + Text.sizes.huge_size,
        "section_title"
    )
    section_subtitle = Style.create(
        ColorsCustom.accent + Text.weights.bold_weight + Text.sizes.Large_size,
        "section_subtitle"
    )


class ContainerStylesCustom:
    """Project container styles."""
    callout = Style.create(
        BackgroundsCustom.callout_bg
        + Container.borders.solid_border
        + Style("border-color: #4A90D9; border-width: 0 0 0 4px;", "callout_border")
        + Container.paddings.medium_padding,
        "callout"
    )
    code_box = Style.create(
        BackgroundsCustom.code_box_bg
        + Container.borders.solid_border
        + Style("border-color: #4A90D9; border-width: 1px;", "code_box_border")
        + Style("border-radius: 6px;", "code_box_radius")
        + Container.paddings.medium_padding
        + Container.layouts.center,
        "code_box"
    )

    # Responsive grid column presets (use as cols= value in st_grid)
    responsive_2col = "repeat(auto-fit, minmax(350px, 1fr))"
    responsive_3col = "repeat(auto-fit, minmax(280px, 1fr))"
    responsive_cards = "repeat(auto-fit, minmax(200px, 1fr))"

    # Layout gaps
    gap_32 = Style("gap: 32px;", "gap_32")
    gap_24 = Style("gap: 24px;", "gap_24")
    gap_16 = Style("gap: 16px;", "gap_16")
    gap_12 = Style("gap: 12px;", "gap_12")


class Custom:
    """Aggregation class for all project-specific styles."""
    colors = ColorsCustom
    backgrounds = BackgroundsCustom
    titles = TextStylesCustom
    containers = ContainerStylesCustom


class Styles(StxStyles):
    """Main Styles class — inherits all StreamTeX styles + project-specific ones."""
    project = Custom
