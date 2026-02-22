"""Shared styles for the HTML-to-StreamTeX conversion project.

Two style families:
  - Presentation (pres): for bck_* blocks (slides, large text, visual)
  - Document (doc): for bckcp_* blocks (course packs, compact reading)

Both share the same color palette with dark/light theme support.
"""

from streamtex.styles import Style, StxStyles
from streamtex.styles.text import Text, Sizes, Weights, Decors, Alignments
from streamtex.styles.container import Container

# ============================================================
# PALETTE DE COULEURS — 15 familles semantiques
# ============================================================
# Light values are chosen to be readable on white backgrounds.
# Dark overrides (in themes.py) use bright/neon colors for dark bgs.
# ============================================================

_center = Alignments.center_align


class ColorsCustom:
    """Project colors. style_id enables theme override."""
    forest_green = Style("color: #274e13;", "clr_forest_green")
    olive_green  = Style("color: #37761c;", "clr_olive_green")
    light_green  = Style("color: #6aa84f;", "clr_light_green")
    link_blue    = Style("color: #1155cc;", "clr_link_blue")
    navy_blue    = Style("color: #0b5394;", "clr_navy_blue")
    sky_blue     = Style("color: #3d85c6;", "clr_sky_blue")
    teal         = Style("color: #134f5c;", "clr_teal")
    bright_red   = Style("color: #cc0000;", "clr_bright_red")
    deep_red     = Style("color: #660000;", "clr_deep_red")
    salmon       = Style("color: #e06666;", "clr_salmon")
    orange       = Style("color: #e69137;", "clr_orange")
    burnt_orange = Style("color: #b45f06;", "clr_burnt_orange")
    gold         = Style("color: #7f6000;", "clr_gold")
    purple       = Style("color: #674ea7;", "clr_purple")
    dark_purple  = Style("color: #351b75;", "clr_dark_purple")
    gray         = Style("color: #666666;", "clr_gray")


class BgColorsCustom:
    """Background colors with style_id for theme override."""
    light_gray_bg = Style("background-color: #f5f5f5;", "bg_light_gray")
    accent_bg     = Style("background-color: rgba(17, 85, 204, 0.08);", "bg_accent")
    warning_bg    = Style("background-color: rgba(204, 0, 0, 0.08);", "bg_warning")


# ============================================================
# FAMILY A: PRESENTATION (bck_* blocks — slides)
# Sizes: h1=48pt, h2=36pt, h3=28pt, h4=24pt, h5=20pt, h6=16pt
# All titles and paragraphs are centered by default.
# ============================================================

class PresTitles:
    """Presentation headings: reasonable sizes for projection."""
    _base = Weights.bold_weight + _center

    h1 = Style.create(_base + Sizes.Large_size, "pres_h1")      # 48pt bold centered
    h2 = Style.create(_base + Sizes.size(36, "pres_h2_sz"), "pres_h2")  # 36pt bold centered
    h3 = Style.create(_base + Sizes.size(28, "pres_h3_sz"), "pres_h3")  # 28pt bold centered
    h4 = Style.create(_base + Sizes.big_size, "pres_h4")        # 24pt bold centered
    h5 = Style.create(_base + Sizes.size(20, "pres_h5_sz"), "pres_h5")  # 20pt bold centered
    h6 = Style.create(_base + Sizes.medium_size, "pres_h6")     # 16pt bold centered


class PresParas:
    """Presentation paragraphs: centered text, readable sizes."""
    p_xl   = Style.create(Sizes.size(36, "pres_pxl_sz") + _center, "pres_para_xl")  # 36pt
    p_lg   = Style.create(Sizes.size(28, "pres_plg_sz") + _center, "pres_para_lg")  # 28pt
    p_md   = Style.create(Sizes.big_size + _center, "pres_para_md")                  # 24pt
    p_sm   = Style.create(Sizes.size(20, "pres_psm_sz") + _center, "pres_para_sm")  # 20pt
    p_body = Style.create(Sizes.medium_size + _center, "pres_para_body")             # 16pt


class PresLinks:
    """Presentation links with adapted sizes (avoid 12pt default)."""
    default   = Style.create(
        ColorsCustom.link_blue + Decors.underline_text, "pres_link")
    link_lg   = Style.create(
        ColorsCustom.link_blue + Decors.underline_text + Sizes.size(28, "_plk_lg"),
        "pres_link_lg")   # 28pt
    link_md   = Style.create(
        ColorsCustom.link_blue + Decors.underline_text + Sizes.big_size,
        "pres_link_md")   # 24pt
    link_sm   = Style.create(
        ColorsCustom.link_blue + Decors.underline_text + Sizes.size(20, "_plk_sm"),
        "pres_link_sm")   # 20pt
    link_body = Style.create(
        ColorsCustom.link_blue + Decors.underline_text + Sizes.medium_size,
        "pres_link_body") # 16pt


class PresContainers:
    """Presentation containers: generous padding."""
    slide   = Style("padding: 36pt;", "pres_slide")
    section = Style("padding: 24px 0;", "pres_section")
    card    = Style("border-radius: 16px; padding: 32px;", "pres_card")


class PresGrids:
    """Presentation grids: wide gaps."""
    gap = Style("gap: 36px;", "pres_grid_gap")


class PresLists:
    """Presentation lists: readable items, centered."""
    item = Style.create(Sizes.medium_size + _center, "pres_lst_item")  # 16pt


class PresTables:
    """Presentation tables."""
    header = Style.create(
        Style("padding: 12px 16px;", "_pres_th_pad") + Weights.bold_weight,
        "pres_tbl_header")
    cell   = Style("padding: 12px 16px;", "pres_tbl_cell")


class Presentation:
    """Full style family for bck_* blocks (slides)."""
    titles     = PresTitles
    paragraphs = PresParas
    links      = PresLinks
    containers = PresContainers
    grids      = PresGrids
    lists      = PresLists
    tables     = PresTables


# ============================================================
# FAMILY B: DOCUMENT (bckcp_* blocks — course pack / syllabus)
# Sizes: h1=20pt, h2=16pt, h3=14pt, h4=12pt, h5=12pt, h6=10pt
# ============================================================

class DocTitles:
    """Document headings: compact sizes for screen reading."""
    _base = Weights.bold_weight

    h1 = Style.create(_base + Sizes.size(20, "doc_h1_sz"), "doc_h1")  # 20pt bold
    h2 = Style.create(_base + Sizes.medium_size, "doc_h2")            # 16pt bold
    h3 = Style.create(_base + Sizes.size(14, "doc_h3_sz"), "doc_h3")  # 14pt bold
    h4 = Style.create(_base + Sizes.little_size, "doc_h4")            # 12pt bold
    h5 = Style.create(Sizes.little_size, "doc_h5")                    # 12pt normal
    h6 = Style.create(Sizes.size(10, "doc_h6_sz"), "doc_h6")          # 10pt normal


class DocParas:
    """Document paragraphs: reading-optimized."""
    p_lg   = Style.create(Sizes.size(20, "doc_plg_sz"), "doc_para_lg")  # 20pt
    p_md   = Style.create(Sizes.medium_size, "doc_para_md")             # 16pt
    p_sm   = Style.create(Sizes.size(14, "doc_psm_sz"), "doc_para_sm")  # 14pt
    p_body = Style.create(Sizes.little_size, "doc_para_body")           # 12pt


class DocLinks:
    """Document links: standard reading sizes."""
    default   = Style.create(
        ColorsCustom.link_blue + Decors.underline_text, "doc_link")
    link_lg   = Style.create(
        ColorsCustom.link_blue + Decors.underline_text + Sizes.size(20, "_dlk_lg"),
        "doc_link_lg")    # 20pt
    link_md   = Style.create(
        ColorsCustom.link_blue + Decors.underline_text + Sizes.medium_size,
        "doc_link_md")    # 16pt
    link_body = Style.create(
        ColorsCustom.link_blue + Decors.underline_text + Sizes.little_size,
        "doc_link_body")  # 12pt


class DocContainers:
    """Document containers: tight padding, dense."""
    page     = Style("padding: 16px;", "doc_page")
    section  = Style("padding: 8px 0;", "doc_section")
    card     = Style("border-radius: 8px; padding: 16px;", "doc_card")
    bordered = Style(
        "border: 1px solid; border-radius: 4px; padding: 12px;", "doc_bordered")


class DocGrids:
    """Document grids: tight gaps."""
    gap = Style("gap: 12px;", "doc_grid_gap")


class DocLists:
    """Document lists: compact items."""
    item       = Style.create(Sizes.little_size, "doc_lst_item")       # 12pt
    item_small = Style.create(Sizes.size(10, "doc_lst_sm_sz"), "doc_lst_item_sm")  # 10pt


class DocTables:
    """Document tables: compact cells for dense tables (6-8 cols)."""
    header = Style.create(
        Style("padding: 6px 8px;", "_doc_th_pad") + Weights.bold_weight,
        "doc_tbl_header")
    cell   = Style("padding: 6px 8px;", "doc_tbl_cell")
    border = Style("border: 1px solid;", "doc_tbl_border")


class Document:
    """Full style family for bckcp_* blocks (course pack / syllabus)."""
    titles     = DocTitles
    paragraphs = DocParas
    links      = DocLinks
    containers = DocContainers
    grids      = DocGrids
    lists      = DocLists
    tables     = DocTables


# ============================================================
# ASSEMBLY
# ============================================================

class Custom:
    colors    = ColorsCustom
    bg_colors = BgColorsCustom
    pres      = Presentation   # s.project.pres.titles.h1
    doc       = Document       # s.project.doc.titles.h1


class Styles(StxStyles):
    project = Custom
