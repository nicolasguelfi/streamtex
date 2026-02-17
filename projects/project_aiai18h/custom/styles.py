from streamtex.styles import Style, Text, Container, StreamTeX_Styles


class ColorsCustom:
    # New Colors
    bronze_01    = Style("color: #7f6000;", "bronze_01")
    brown_01     = Style("color: #783f04;", "brown_01")

    green_01     = Style("color: #2f5a1c;", "green_01")

    blue_01      = Style("color: #1155cc;", "blue_01")
    blue_dark_01 = Style("color: #0c343d;", "blue_dark_01")

    purple_01    = Style("color: #9900ff;", "purple_01")
    purple_02    = Style("color: #741b47;", "purple_02")

    red_01       = Style("color: #980000;", "red_01")
    red_02       = Style("color: #cc0000;", "red_02")

    pink_01      = Style("color: #e06666;", "pink_01")

    orange_01    = Style("color: #ff9900;", "orange_01")
    orange_02    = Style("color: #b45f06;", "orange_02")
    orange_03    = Style("color: #cc4125;", "orange_03")

class TextStylesCustom:
    title_intro_green_lime_01 = Style.create(
        Text.colors.lime + Text.weights.bold_weight + Text.sizes.Giant_size + Text.fonts.font_arial,
        "title_intro_green_lime_01"
    )

    title_giant_green_01 = Style.create(
        ColorsCustom.green_01 + Text.weights.bold_weight + Text.sizes.Giant_size,
        "title_giant_green_01"
    )

    title_giant_em_green_01 = Style.create(
        ColorsCustom.green_01 + Text.weights.bold_weight + Text.sizes.Giant_em_size,
        "title_giant_em_green_01"
    )

    title_purple_01 = Style.create(
        ColorsCustom.purple_01 + Text.weights.bold_weight + Text.sizes.Huge_size,
        "title_purple_01"
    )

    title_green_01 = Style.create(
        ColorsCustom.green_01 + Text.weights.bold_weight + Text.sizes.huge_size,
        "title_green_01"
    )

    title_red_01 = Style.create(
        ColorsCustom.red_01 + Text.weights.bold_weight + Text.sizes.Huge_size,
        "title_red_01"
    )

    subtitle_intro_green_lime_01 = Style.create(
        Text.colors.lime + Text.weights.bold_weight + Text.sizes.Large_size,
        "subtitle_intro_green_lime_01"
    )

    subtitle_intro_bronze_01 = Style.create(
        ColorsCustom.bronze_01 + Text.sizes.Large_size,
        "subtitle_intro_bronze_01"
    )

    subtitle_blue_01 = Style.create(
        ColorsCustom.blue_01 + Text.weights.bold_weight + Text.sizes.LARGE_size,
        "subtitle_blue_01"
    )

    subtitle_purple_01 = Style.create(
        ColorsCustom.purple_01 + Text.weights.bold_weight + Text.sizes.Large_size,
        "subtitle_purple_01"
    )


class Custom:
    colors = ColorsCustom
    titles = TextStylesCustom

    # Other styles
    content = Style.create(
        Text.colors.black + Text.sizes.big_size,
        "content"
    )

    new = Style.create(
        Text.colors.black + Text.sizes.big_size,
        "new"
    )

    green_01_bold = Style.create(
        colors.green_01 + Text.weights.bold_weight,
        "green_01_bold"
    )

    bronze_01_bold = Style.create(
        colors.bronze_01 + Text.weights.bold_weight,
        "bronze_01_bold"
    )

    low_pad = Style.create(
        Container.paddings.tiny_padding + Container.borders.none_border,
        "low_pad"
    )



class Styles(StreamTeX_Styles):
    project = Custom
