"""Container-related style definitions: BackgroundColors, Paddings, Margins, Borders, etc."""

from typing import Optional, Union

from .core import ListStyle, Style


class BackgroundColors:
    reset_bg              = Style("background-color: initial;",           "reset_bg")
    alice_blue_bg         = Style("background-color: AliceBlue;",         "alice_blue_bg")
    antique_white_bg      = Style("background-color: AntiqueWhite;",      "antique_white_bg")
    aqua_bg               = Style("background-color: Aqua;",              "aqua_bg")
    aquamarine_bg         = Style("background-color: Aquamarine;",        "aquamarine_bg")
    azure_bg              = Style("background-color: Azure;",             "azure_bg")
    beige_bg              = Style("background-color: Beige;",             "beige_bg")
    bisque_bg             = Style("background-color: Bisque;",            "bisque_bg")
    black_bg              = Style("background-color: Black;",             "black_bg")
    blanched_almond_bg    = Style("background-color: BlanchedAlmond;",    "blanched_almond_bg")
    blue_bg               = Style("background-color: Blue;",              "blue_bg")
    blue_violet_bg        = Style("background-color: BlueViolet;",        "blue_violet_bg")
    brown_bg              = Style("background-color: Brown;",             "brown_bg")
    burly_wood_bg         = Style("background-color: BurlyWood;",         "burly_wood_bg")
    cadet_blue_bg         = Style("background-color: CadetBlue;",         "cadet_blue_bg")
    chartreuse_bg         = Style("background-color: Chartreuse;",        "chartreuse_bg")
    chocolate_bg          = Style("background-color: Chocolate;",         "chocolate_bg")
    coral_bg              = Style("background-color: Coral;",             "coral_bg")
    cornflower_blue_bg    = Style("background-color: CornflowerBlue;",    "cornflower_blue_bg")
    cornsilk_bg           = Style("background-color: Cornsilk;",          "cornsilk_bg")
    crimson_bg            = Style("background-color: Crimson;",           "crimson_bg")
    cyan_bg               = Style("background-color: Cyan;",              "cyan_bg")
    dark_blue_bg          = Style("background-color: DarkBlue;",          "dark_blue_bg")
    dark_cyan_bg          = Style("background-color: DarkCyan;",          "dark_cyan_bg")
    dark_golden_rod_bg    = Style("background-color: DarkGoldenRod;",     "dark_golden_rod_bg")
    dark_gray_bg          = Style("background-color: DarkGray;",          "dark_gray_bg")
    dark_grey_bg          = Style("background-color: DarkGrey;",          "dark_grey_bg")
    dark_green_bg         = Style("background-color: DarkGreen;",         "dark_green_bg")
    dark_khaki_bg         = Style("background-color: DarkKhaki;",         "dark_khaki_bg")
    dark_magenta_bg       = Style("background-color: DarkMagenta;",       "dark_magenta_bg")
    dark_olive_green_bg   = Style("background-color: DarkOliveGreen;",    "dark_olive_green_bg")
    dark_orange_bg        = Style("background-color: DarkOrange;",        "dark_orange_bg")
    dark_orchid_bg        = Style("background-color: DarkOrchid;",        "dark_orchid_bg")
    dark_red_bg           = Style("background-color: DarkRed;",           "dark_red_bg")
    dark_salmon_bg        = Style("background-color: DarkSalmon;",        "dark_salmon_bg")
    dark_sea_green_bg     = Style("background-color: DarkSeaGreen;",      "dark_sea_green_bg")
    dark_slate_blue_bg    = Style("background-color: DarkSlateBlue;",     "dark_slate_blue_bg")
    dark_slate_gray_bg    = Style("background-color: DarkSlateGray;",     "dark_slate_gray_bg")
    dark_slate_grey_bg    = Style("background-color: DarkSlateGrey;",     "dark_slate_grey_bg")
    dark_turquoise_bg     = Style("background-color: DarkTurquoise;",     "dark_turquoise_bg")
    dark_violet_bg        = Style("background-color: DarkViolet;",        "dark_violet_bg")
    deep_pink_bg          = Style("background-color: DeepPink;",          "deep_pink_bg")
    deep_sky_blue_bg      = Style("background-color: DeepSkyBlue;",       "deep_sky_blue_bg")
    dim_gray_bg           = Style("background-color: DimGray;",           "dim_gray_bg")
    dim_grey_bg           = Style("background-color: DimGrey;",           "dim_grey_bg")
    dodger_blue_bg        = Style("background-color: DodgerBlue;",        "dodger_blue_bg")
    fire_brick_bg         = Style("background-color: FireBrick;",         "fire_brick_bg")
    floral_white_bg       = Style("background-color: FloralWhite;",       "floral_white_bg")
    forest_green_bg       = Style("background-color: ForestGreen;",       "forest_green_bg")
    fuchsia_bg            = Style("background-color: Fuchsia;",           "fuchsia_bg")
    gainsboro_bg          = Style("background-color: Gainsboro;",         "gainsboro_bg")
    ghost_white_bg        = Style("background-color: GhostWhite;",        "ghost_white_bg")
    gold_bg               = Style("background-color: Gold;",              "gold_bg")
    golden_rod_bg         = Style("background-color: GoldenRod;",         "golden_rod_bg")
    gray_bg               = Style("background-color: Gray;",              "gray_bg")
    grey_bg               = Style("background-color: Grey;",              "grey_bg")
    green_bg              = Style("background-color: Green;",             "green_bg")
    green_yellow_bg       = Style("background-color: GreenYellow;",       "green_yellow_bg")
    honey_dew_bg          = Style("background-color: HoneyDew;",          "honey_dew_bg")
    hot_pink_bg           = Style("background-color: HotPink;",           "hot_pink_bg")
    indian_red_bg         = Style("background-color: IndianRed;",         "indian_red_bg")
    indigo_bg             = Style("background-color: Indigo;",            "indigo_bg")
    ivory_bg              = Style("background-color: Ivory;",             "ivory_bg")
    khaki_bg              = Style("background-color: Khaki;",             "khaki_bg")
    lavender_bg           = Style("background-color: Lavender;",          "lavender_bg")
    lavender_blush_bg     = Style("background-color: LavenderBlush;",     "lavender_blush_bg")
    lawn_green_bg         = Style("background-color: LawnGreen;",         "lawn_green_bg")
    lemon_chiffon_bg      = Style("background-color: LemonChiffon;",      "lemon_chiffon_bg")
    light_blue_bg         = Style("background-color: LightBlue;",         "light_blue_bg")
    light_coral_bg        = Style("background-color: LightCoral;",        "light_coral_bg")
    light_cyan_bg         = Style("background-color: LightCyan;",         "light_cyan_bg")
    light_golden_rod_yellow_bg = Style("background-color: LightGoldenRodYellow;", "light_golden_rod_yellow_bg")
    light_gray_bg         = Style("background-color: LightGray;",         "light_gray_bg")
    light_grey_bg         = Style("background-color: LightGrey;",         "light_grey_bg")
    light_green_bg        = Style("background-color: LightGreen;",        "light_green_bg")
    light_pink_bg         = Style("background-color: LightPink;",         "light_pink_bg")
    light_salmon_bg       = Style("background-color: LightSalmon;",       "light_salmon_bg")
    light_sea_green_bg    = Style("background-color: LightSeaGreen;",     "light_sea_green_bg")
    light_sky_blue_bg     = Style("background-color: LightSkyBlue;",      "light_sky_blue_bg")
    light_slate_gray_bg   = Style("background-color: LightSlateGray;",    "light_slate_gray_bg")
    light_slate_grey_bg   = Style("background-color: LightSlateGrey;",    "light_slate_grey_bg")
    light_steel_blue_bg   = Style("background-color: LightSteelBlue;",    "light_steel_blue_bg")
    light_yellow_bg       = Style("background-color: LightYellow;",       "light_yellow_bg")
    lime_bg               = Style("background-color: Lime;",              "lime_bg")
    lime_green_bg         = Style("background-color: LimeGreen;",         "lime_green_bg")
    linen_bg              = Style("background-color: Linen;",             "linen_bg")
    magenta_bg            = Style("background-color: Magenta;",           "magenta_bg")
    maroon_bg             = Style("background-color: Maroon;",            "maroon_bg")
    medium_aqua_marine_bg = Style("background-color: MediumAquaMarine;",  "medium_aqua_marine_bg")
    medium_blue_bg        = Style("background-color: MediumBlue;",        "medium_blue_bg")
    medium_orchid_bg      = Style("background-color: MediumOrchid;",      "medium_orchid_bg")
    medium_purple_bg      = Style("background-color: MediumPurple;",      "medium_purple_bg")
    medium_sea_green_bg   = Style("background-color: MediumSeaGreen;",    "medium_sea_green_bg")
    medium_slate_blue_bg  = Style("background-color: MediumSlateBlue;",   "medium_slate_blue_bg")
    medium_spring_green_bg= Style("background-color: MediumSpringGreen;", "medium_spring_green_bg")
    medium_turquoise_bg   = Style("background-color: MediumTurquoise;",   "medium_turquoise_bg")
    medium_violet_red_bg  = Style("background-color: MediumVioletRed;",   "medium_violet_red_bg")
    midnight_blue_bg      = Style("background-color: MidnightBlue;",      "midnight_blue_bg")
    mint_cream_bg         = Style("background-color: MintCream;",         "mint_cream_bg")
    misty_rose_bg         = Style("background-color: MistyRose;",         "misty_rose_bg")
    moccasin_bg           = Style("background-color: Moccasin;",          "moccasin_bg")
    navajo_white_bg       = Style("background-color: NavajoWhite;",       "navajo_white_bg")
    navy_bg               = Style("background-color: Navy;",              "navy_bg")
    old_lace_bg           = Style("background-color: OldLace;",           "old_lace_bg")
    olive_bg              = Style("background-color: Olive;",             "olive_bg")
    olive_drab_bg         = Style("background-color: OliveDrab;",         "olive_drab_bg")
    orange_bg             = Style("background-color: Orange;",            "orange_bg")
    orange_red_bg         = Style("background-color: OrangeRed;",         "orange_red_bg")
    orchid_bg             = Style("background-color: Orchid;",            "orchid_bg")
    pale_golden_rod_bg    = Style("background-color: PaleGoldenRod;",     "pale_golden_rod_bg")
    pale_green_bg         = Style("background-color: PaleGreen;",         "pale_green_bg")
    pale_turquoise_bg     = Style("background-color: PaleTurquoise;",     "pale_turquoise_bg")
    pale_violet_red_bg    = Style("background-color: PaleVioletRed;",     "pale_violet_red_bg")
    papaya_whip_bg        = Style("background-color: PapayaWhip;",        "papaya_whip_bg")
    peach_puff_bg         = Style("background-color: PeachPuff;",         "peach_puff_bg")
    peru_bg               = Style("background-color: Peru;",              "peru_bg")
    pink_bg               = Style("background-color: Pink;",              "pink_bg")
    plum_bg               = Style("background-color: Plum;",              "plum_bg")
    powder_blue_bg        = Style("background-color: PowderBlue;",        "powder_blue_bg")
    purple_bg             = Style("background-color: Purple;",            "purple_bg")
    rebecca_purple_bg     = Style("background-color: RebeccaPurple;",     "rebecca_purple_bg")
    red_bg                = Style("background-color: Red;",               "red_bg")
    rosy_brown_bg         = Style("background-color: RosyBrown;",         "rosy_brown_bg")
    royal_blue_bg         = Style("background-color: RoyalBlue;",         "royal_blue_bg")
    saddle_brown_bg       = Style("background-color: SaddleBrown;",       "saddle_brown_bg")
    salmon_bg             = Style("background-color: Salmon;",            "salmon_bg")
    sandy_brown_bg        = Style("background-color: SandyBrown;",        "sandy_brown_bg")
    sea_green_bg          = Style("background-color: SeaGreen;",          "sea_green_bg")
    sea_shell_bg          = Style("background-color: SeaShell;",          "sea_shell_bg")
    sienna_bg             = Style("background-color: Sienna;",            "sienna_bg")
    silver_bg             = Style("background-color: Silver;",            "silver_bg")
    sky_blue_bg           = Style("background-color: SkyBlue;",           "sky_blue_bg")
    slate_blue_bg         = Style("background-color: SlateBlue;",         "slate_blue_bg")
    slate_gray_bg         = Style("background-color: SlateGray;",         "slate_gray_bg")
    slate_grey_bg         = Style("background-color: SlateGrey;",         "slate_grey_bg")
    snow_bg               = Style("background-color: Snow;",              "snow_bg")
    spring_green_bg       = Style("background-color: SpringGreen;",       "spring_green_bg")
    steel_blue_bg         = Style("background-color: SteelBlue;",         "steel_blue_bg")
    tan_bg                = Style("background-color: Tan;",               "tan_bg")
    teal_bg               = Style("background-color: Teal;",              "teal_bg")
    thistle_bg            = Style("background-color: Thistle;",           "thistle_bg")
    tomato_bg             = Style("background-color: Tomato;",            "tomato_bg")
    turquoise_bg          = Style("background-color: Turquoise;",         "turquoise_bg")
    violet_bg             = Style("background-color: Violet;",            "violet_bg")
    wheat_bg              = Style("background-color: Wheat;",             "wheat_bg")
    white_bg              = Style("background-color: White;",             "white_bg")
    white_smoke_bg        = Style("background-color: WhiteSmoke;",        "white_smoke_bg")
    yellow_bg             = Style("background-color: Yellow;",            "yellow_bg")
    yellow_green_bg       = Style("background-color: YellowGreen;",       "yellow_green_bg")


class Paddings:
    @staticmethod
    def size(*sizes: Union[str, int], style_id: Optional[str] = None):
        """Creates a padding style with specified sizes (1-4 values, CSS convention)."""
        converted_sizes = []
        for size in sizes[:4]:
            if isinstance(size, int):
                size = f"{size}pt"
            converted_sizes.append(str(size))
        padding_value = " ".join(converted_sizes)
        if not style_id:
            style_id = f"padding_{padding_value.replace(' ', '_')}"
        return Style(f"padding: {padding_value};", style_id)

    Giant_padding   = Style("padding: 96pt;",  "Giant_padding")
    giant_padding   = Style("padding: 84pt;",  "giant_padding")
    Huge_padding    = Style("padding: 72pt;",  "Huge_padding")
    huge_padding    = Style("padding: 60pt;",  "huge_padding")
    LARGE_padding   = Style("padding: 48pt;",  "LARGE_padding")
    Large_padding   = Style("padding: 36pt;",  "Large_padding")
    large_padding   = Style("padding: 24pt;",  "large_padding")
    big_padding     = Style("padding: 18pt;",  "big_padding")
    medium_padding  = Style("padding: 12pt;",  "medium_padding")
    little_padding  = Style("padding: 9pt;",   "little_padding")
    small_padding   = Style("padding: 6pt;",   "small_padding")
    tiny_padding    = Style("padding: 3pt;",   "tiny_padding")
    none_padding    = Style("padding: 0pt;",   "none_padding")

    Giant_em_padding   = Style("padding: 8em;",   "Giant_em_padding")
    giant_em_padding   = Style("padding: 7em;",   "giant_em_padding")
    Huge_em_padding    = Style("padding: 6em;",   "Huge_em_padding")
    huge_em_padding    = Style("padding: 5em;",   "huge_em_padding")
    LARGE_em_padding   = Style("padding: 4em;",   "LARGE_em_padding")
    Large_em_padding   = Style("padding: 3em;",   "Large_em_padding")
    large_em_padding   = Style("padding: 2em;",   "large_em_padding")
    big_em_padding     = Style("padding: 1.5em;", "big_em_padding")
    medium_em_padding  = Style("padding: 1em;",   "medium_em_padding")
    little_em_padding  = Style("padding: 0.75em;","little_em_padding")
    small_em_padding   = Style("padding: 0.5em;", "small_em_padding")
    tiny_em_padding    = Style("padding: 0.25em;","tiny_em_padding")
    none_em_padding    = Style("padding: 0em;",   "none_em_padding")


class Margins:
    @staticmethod
    def size(*sizes: Union[str, int], style_id: Optional[str] = None):
        """Creates a margin style with specified sizes (1-4 values, CSS convention)."""
        converted_sizes = []
        for size in sizes[:4]:
            if isinstance(size, int):
                size = f"{size}pt"
            converted_sizes.append(str(size))
        margin_value = " ".join(converted_sizes)
        if not style_id:
            style_id = f"margin_{margin_value.replace(' ', '_')}"
        return Style(f"margin: {margin_value};", style_id)

    Giant_margin    = Style("margin: 96pt;",  "Giant_margin")
    giant_margin    = Style("margin: 84pt;",  "giant_margin")
    Huge_margin     = Style("margin: 72pt;",  "Huge_margin")
    huge_margin     = Style("margin: 60pt;",  "huge_margin")
    LARGE_margin    = Style("margin: 48pt;",  "LARGE_margin")
    Large_margin    = Style("margin: 36pt;",  "Large_margin")
    large_margin    = Style("margin: 24pt;",  "large_margin")
    big_margin      = Style("margin: 18pt;",  "big_margin")
    medium_margin   = Style("margin: 12pt;",  "medium_margin")
    little_margin   = Style("margin: 9pt;",   "little_margin")
    small_margin    = Style("margin: 6pt;",   "small_margin")
    tiny_margin     = Style("margin: 3pt;",   "tiny_margin")
    none_margin     = Style("margin: 0pt;",   "none_margin")
    auto_margin     = Style("margin: auto;",  "auto_margin")

    Giant_em_margin    = Style("margin: 8em;",   "Giant_em_margin")
    giant_em_margin    = Style("margin: 7em;",   "giant_em_margin")
    Huge_em_margin     = Style("margin: 6em;",   "Huge_em_margin")
    huge_em_margin     = Style("margin: 5em;",   "huge_em_margin")
    LARGE_em_margin    = Style("margin: 4em;",   "LARGE_em_margin")
    Large_em_margin    = Style("margin: 3em;",   "Large_em_margin")
    large_em_margin    = Style("margin: 2em;",   "large_em_margin")
    big_em_margin      = Style("margin: 1.5em;","big_em_margin")
    medium_em_margin   = Style("margin: 1em;",   "medium_em_margin")
    little_em_margin   = Style("margin: 0.75em;","little_em_margin")
    small_em_margin    = Style("margin: 0.5em;", "small_em_margin")
    tiny_em_margin     = Style("margin: 0.25em;","tiny_em_margin")
    none_em_margin     = Style("margin: 0em;",   "none_em_margin")


class ContainerSizes:
    width_full = Style("width: 100%;", "width_full")
    width_half = Style("width: 50%;",  "width_half")
    width_auto = Style("width: auto;", "width_auto")
    width_fit = Style("width: fit-content;", "width_fit")
    height_full = Style("height: 100%;", "height_full")
    height_half = Style("height: 50%;",  "height_half")
    height_auto = Style("height: auto;", "height_auto")
    height_fit = Style("height: fit-content;", "height_fit")


class Flex:
    flex               = Style("display: flex;", "flex")
    row_flex           = Style("display: flex; flex-direction: row;",    "row_flex")
    col_flex           = Style("display: flex; flex-direction: column;", "col_flex")
    wrap_flex          = Style("display: flex; flex-wrap: wrap;",        "wrap_flex")
    space_between_justify = Style("justify-content: space-between;", "space_between_justify")
    center_justify        = Style("justify-content: center;",        "center_justify")
    center_align_items    = Style("align-items: center;",            "center_align_items")
    center_flex = Style.create(flex + center_align_items, "center_flex")


class Layouts:
    fix_ratio             = Style("display: block;",               "fix_ratio")
    inline                = Style("display: inline-block;",        "inline")
    col_layout            = Style("display: flex; flex-direction: column;", "col_layout")
    row_layout            = Style("display: flex; flex-direction: row;",    "row_layout")
    vertical_center_layout = Style(
        "display: flex; align-items: center; justify-content: center; align-content: center",
        "vertical_center_layout"
    )
    table_layout          = Style("table-layout: fixed; width: 100%;",      "table_layout")
    list_layout           = Style("display: list-item;",  "list_layout")
    fit                   = Style("object-fit: contain;", "fit_layout")
    center                = Style.create(ContainerSizes.width_fit + Margins.size("auto", "auto"), "center_layout")
    span                  = Style.create(Flex.row_flex + ContainerSizes.width_fit, "span_layout")
    span_center           = Style.create(Flex.row_flex + center, "spa_center_layout")


class Borders:
    @staticmethod
    def size(*sizes: Union[str, int], style_id: Optional[str] = None):
        """Creates a border width style with specified sizes (1-4 values)."""
        converted_sizes = []
        for size in sizes[:4]:
            if isinstance(size, int):
                size = f"{size}pt"
            converted_sizes.append(str(size))
        border_width_value = " ".join(converted_sizes)
        if not style_id:
            clean_id = border_width_value.replace(" ", "_")
            style_id = f"border_size_{clean_id}"
        return Style(f"border-width: {border_width_value};", style_id)

    thin_border   = Style("border-width: thin;",   "thin_border")
    medium_border = Style("border-width: medium;", "medium_border")
    thick_border  = Style("border-width: thick;",  "thick_border")
    solid_border  = Style("border-style: solid;",  "solid_border")
    dotted_border = Style("border-style: dotted;", "dotted_border")
    dashed_border = Style("border-style: dashed;", "dashed_border")
    double_border = Style("border-style: double;", "double_border")
    groove_border = Style("border-style: groove;", "groove_border")
    ridge_border  = Style("border-style: ridge;",  "ridge_border")
    inset_border  = Style("border-style: inset;",  "inset_border")
    outset_border = Style("border-style: outset;", "outset_border")
    none_border   = Style("border-style: none;",   "none_border")
    hidden_border = Style("border-style: hidden;", "hidden_border")

    @staticmethod
    def color(color: Union[Style, str], style_id: Optional[str] = None):
        """Converts a text color Style or string into a border color Style."""
        if isinstance(color, Style):
            color_str = str(color)
            if "color:" in color_str:
                color = color_str.split("color:")[1].split(";")[0].strip()
        if not style_id:
            clean_id = str(color).replace(" ", "_").replace(":", "").replace(";", "")
            style_id = f"border_color_{clean_id}"
        return Style(f"border-color: {color};", style_id)

    table_border = Style("""
        border: 1px solid rgba(0, 0, 0, 1);
        border-collapse: collapse;
        opacity: 1;
    """.strip(), "table_border")


class Positions:
    initial  = Style("position: initial;",  "initial")
    static   = Style("position: static;",   "static")
    relative = Style("position: relative;", "relative")
    absolute = Style("position: absolute;", "absolute")
    fixed    = Style("position: fixed;",    "fixed")
    sticky   = Style("position: sticky;",   "sticky")

    @staticmethod
    def top(offset: Union[str, int], style_id: Optional[str] = None):
        if isinstance(offset, int):
            offset = f"{offset}px"
        if not style_id:
            style_id = f"top_{offset}"
        return Style(f"top: {offset};", style_id)

    @staticmethod
    def bottom(offset: Union[str, int], style_id: Optional[str] = None):
        if isinstance(offset, int):
            offset = f"{offset}px"
        if not style_id:
            style_id = f"bottom_{offset}"
        return Style(f"bottom: {offset};", style_id)

    @staticmethod
    def left(offset: Union[str, int], style_id: Optional[str] = None):
        if isinstance(offset, int):
            offset = f"{offset}px"
        if not style_id:
            style_id = f"left_{offset}"
        return Style(f"left: {offset};", style_id)

    @staticmethod
    def right(offset: Union[str, int], style_id: Optional[str] = None):
        if isinstance(offset, int):
            offset = f"{offset}px"
        if not style_id:
            style_id = f"right_{offset}"
        return Style(f"right: {offset};", style_id)


class ListStyles:
    g_docs = ListStyle(symbols=["❖", "➢", "◼", "●", "◆", "➢", "◼", "●", "◆", "◆", "◆", "◆", "◆", "◆", "◆", "◆"])
    ordered_lowercase = Style("list-style-type: lower-alpha;", "ordered_lowercase")


class GridStyles:
    """Grid gap presets for use with st_grid's grid_style parameter."""
    gap_0  = Style("gap: 0;",    "grid_gap_0")
    gap_8  = Style("gap: 8px;",  "grid_gap_8")
    gap_12 = Style("gap: 12px;", "grid_gap_12")
    gap_16 = Style("gap: 16px;", "grid_gap_16")
    gap_24 = Style("gap: 24px;", "grid_gap_24")
    gap_32 = Style("gap: 32px;", "grid_gap_32")
    gap_48 = Style("gap: 48px;", "grid_gap_48")


class Container:
    sizes = ContainerSizes
    bg_colors = BackgroundColors
    borders = Borders
    paddings = Paddings
    margins = Margins
    layouts = Layouts
    flex = Flex
    lists = ListStyles
    positions = Positions
    grid = GridStyles
