"""Theme dictionaries for dark/light mode.

4 themes total:
  - pres_light / pres_dark  (for bck_* presentation blocks)
  - doc_light  / doc_dark   (for bckcp_* course pack blocks)

Dark colors are BRIGHT / NEON to be highly visible on dark backgrounds.
"""

# ============================================================
# Shared dark color overrides — bright neon for dark backgrounds
# ============================================================
_colors_dark = {
    # Greens — bright neon
    "clr_forest_green": "color: #00ff88;",
    "clr_olive_green":  "color: #7fff00;",
    "clr_light_green":  "color: #90ee90;",
    # Blues — vivid
    "clr_link_blue":    "color: #00bfff;",
    "clr_navy_blue":    "color: #6eb5ff;",
    "clr_sky_blue":     "color: #87ceeb;",
    "clr_teal":         "color: #00e5cc;",
    # Reds — bright, not dark
    "clr_bright_red":   "color: #ff4444;",
    "clr_deep_red":     "color: #ff6b6b;",
    "clr_salmon":       "color: #ff9999;",
    # Oranges — vivid
    "clr_orange":       "color: #ffaa00;",
    "clr_burnt_orange": "color: #ffbb33;",
    "clr_gold":         "color: #ffd700;",
    # Purples — bright
    "clr_purple":       "color: #bb86fc;",
    "clr_dark_purple":  "color: #cf9fff;",
    # Gray — lighter
    "clr_gray":         "color: #b0b0b0;",
    # Backgrounds
    "bg_light_gray":    "background-color: rgba(255, 255, 255, 0.06);",
    "bg_accent":        "background-color: rgba(0, 191, 255, 0.12);",
    "bg_warning":       "background-color: rgba(255, 68, 68, 0.12);",
}

# ============================================================
# Presentation themes
# ============================================================

pres_light = {}

pres_dark = {
    **_colors_dark,
}

# ============================================================
# Document themes
# ============================================================

doc_light = {}

doc_dark = {
    **_colors_dark,
    # Document-specific dark adjustments for readability at 12pt
    "doc_tbl_border": "border: 1px solid rgba(255, 255, 255, 0.2);",
    "doc_bordered": (
        "border: 1px solid rgba(255, 255, 255, 0.2);"
        " border-radius: 4px; padding: 12px;"
    ),
}
