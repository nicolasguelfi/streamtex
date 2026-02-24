from streamtex.styles import StxStyles, Style, Text


class ColorsCustom:
    """Custom colors defined multiple times."""
    denim_blue = Style("color: #1155cc;", "denim_blue")
    lilac = Style("color: #8b5cf6;", "lilac")
    # Text Generation block colors
    dark_blue = Style("color: #073763;", "dark_blue")
    orange_accent = Style("color: #b45f06;", "orange_accent")
    dark_red = Style("color: #980000;", "dark_red")
    bright_red = Style("color: #ff0000;", "bright_red")
    dark_green = Style("color: #274e13;", "dark_green")
    brown = Style("color: #783f04;", "brown")
    dark_purple = Style("color: #20124d;", "dark_purple")


class TitleStyles:
    """Title styles — 4-level hierarchy with floor at large (32pt)."""
    main_title = Style.create(
        ColorsCustom.lilac + Text.weights.bold_weight + Text.sizes.Huge_size,
        "main_title"
    )
    section_title = Style.create(
        ColorsCustom.denim_blue + Text.weights.bold_weight + Text.sizes.LARGE_size,
        "section_title"
    )
    section_subtitle = Style.create(
        ColorsCustom.orange_accent + Text.weights.bold_weight + Text.sizes.Large_size,
        "section_subtitle"
    )
    subsection_title = Style.create(
        ColorsCustom.dark_green + Text.weights.bold_weight + Text.sizes.large_size,
        "subsection_title"
    )
    table_of_contents = Style.create(
        ColorsCustom.lilac + Text.weights.bold_weight + Text.sizes.large_size + Text.alignments.center_align,
        "callout_title"
    )

class ProjectStyles:
    """Aggregated access point for StreamTeX."""
    colors = ColorsCustom
    titles = TitleStyles


class Styles(StxStyles):
    project = ProjectStyles

