from streamtex.styles import StxStyles, Style, Text


class ColorsCustom:
    structure = Style("color: #2c5282;", "structure")
    structure_light = Style("color: #4299e1;", "structure_light")
    red_error = Style("color: #c53030;", "red_error")
    red_light = Style("color: #fc8181;", "red_light")
    green_pass = Style("color: #276749;", "green_pass")
    green_light = Style("color: #68d391;", "green_light")
    gray_baseline = Style("color: #718096;", "gray_baseline")
    gray_dark = Style("color: #4a5568;", "gray_dark")
    orange_accent = Style("color: #dd6b20;", "orange_accent")
    white = Style("color: #ffffff;", "white_text")


class BgColorsCustom:
    structure_bg = Style("background-color: rgba(44, 82, 130, 0.12);", "structure_bg")
    structure_dark_bg = Style("background-color: rgba(44, 82, 130, 0.25);", "structure_dark_bg")
    red_bg = Style("background-color: rgba(197, 48, 48, 0.08);", "red_bg")
    green_bg = Style("background-color: rgba(39, 103, 73, 0.08);", "green_bg")
    gray_bg = Style("background-color: rgba(113, 128, 150, 0.08);", "gray_bg")
    dark_bg = Style("background-color: rgba(26, 32, 44, 0.95);", "dark_bg")


class ContainersCustom:
    beamer_block = Style(
        "border-left: 4px solid #2c5282;"
        "background-color: rgba(44, 82, 130, 0.08);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "beamer_block"
    )
    beamer_block_red = Style(
        "border-left: 4px solid #c53030;"
        "background-color: rgba(197, 48, 48, 0.06);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "beamer_block_red"
    )
    beamer_block_green = Style(
        "border-left: 4px solid #276749;"
        "background-color: rgba(39, 103, 73, 0.06);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "beamer_block_green"
    )
    slide_container = Style(
        "border: 1px solid rgba(44, 82, 130, 0.2);"
        "border-radius: 8px;"
        "padding: 24px 32px;",
        "slide_container"
    )
    table_header = Style(
        "background-color: rgba(44, 82, 130, 0.15);"
        "padding: 8px 12px;"
        "border-bottom: 2px solid #2c5282;",
        "table_header"
    )
    table_cell = Style(
        "padding: 8px 12px;"
        "border-bottom: 1px solid rgba(113, 128, 150, 0.2);",
        "table_cell"
    )
    gap_24 = Style("gap: 24px;", "gap_24")
    gap_16 = Style("gap: 16px;", "gap_16")
    gap_12 = Style("gap: 12px;", "gap_12")


class TextStylesCustom:
    # Standard 4-level hierarchy: 96pt → 64pt → 48pt → 32pt (floor)
    main_title = Style.create(
        ColorsCustom.structure + Text.weights.bold_weight + Text.sizes.Huge_size,
        "main_title"
    )
    section_title = Style.create(
        ColorsCustom.structure_light + Text.weights.bold_weight + Text.sizes.LARGE_size,
        "section_title"
    )
    section_subtitle = Style.create(
        ColorsCustom.orange_accent + Text.weights.bold_weight + Text.sizes.Large_size,
        "section_subtitle"
    )
    subsection_title = Style.create(
        ColorsCustom.green_pass + Text.weights.bold_weight + Text.sizes.large_size,
        "subsection_title"
    )
    # Beamer-specific titles (kept for existing blocks)
    slide_title = Style.create(
        ColorsCustom.structure + Text.weights.bold_weight + Text.sizes.large_size,
        "slide_title"
    )
    slide_subtitle = Style.create(
        ColorsCustom.structure_light + Text.sizes.big_size,
        "slide_subtitle"
    )
    block_title = Style.create(
        ColorsCustom.structure + Text.weights.bold_weight + Text.sizes.big_size,
        "block_title"
    )
    emphasis_red = Style.create(
        ColorsCustom.red_error + Text.weights.bold_weight,
        "emphasis_red"
    )
    emphasis_green = Style.create(
        ColorsCustom.green_pass + Text.weights.bold_weight,
        "emphasis_green"
    )
    emphasis_structure = Style.create(
        ColorsCustom.structure + Text.weights.bold_weight,
        "emphasis_structure"
    )


class Custom:
    colors = ColorsCustom
    bg_colors = BgColorsCustom
    containers = ContainersCustom
    titles = TextStylesCustom


class Styles(StxStyles):
    project = Custom
