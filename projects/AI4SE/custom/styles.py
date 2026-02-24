"""AI4SE project styles — Generative Software Engineering course.

Dark-mode-first palette with AI/tech aesthetic.
Modular, generic, reusable design.

Usage in blocks:
    from custom.styles import Styles as s
    st_write(s.project.colors.primary, "Hello")
    st_write(s.project.titles.course_title, "Generative SE")
"""

from streamtex.styles import StxStyles, Style, Text

# ---------------------------------------------------------------------------
# 1. COLOR PALETTE (dark-mode-first: bright on dark backgrounds)
# ---------------------------------------------------------------------------

class ColorsCustom:
    """Text colors — bright variants optimized for dark backgrounds."""
    primary = Style("color: #5B9CF6;", "primary")           # Bright blue
    accent = Style("color: #00D4AA;", "accent")              # Electric teal
    highlight = Style("color: #FFB547;", "highlight")        # Warm amber
    success = Style("color: #4ADE80;", "success")            # Bright green
    error = Style("color: #F87171;", "error")                # Coral red
    muted = Style("color: #94A3B8;", "muted")               # Slate gray
    subtle = Style("color: #64748B;", "subtle")              # Dim slate


class BackgroundsCustom:
    """Semi-transparent backgrounds for containers on dark surfaces."""
    primary_bg = Style("background-color: rgba(91, 156, 246, 0.10);", "primary_bg")
    accent_bg = Style("background-color: rgba(0, 212, 170, 0.10);", "accent_bg")
    highlight_bg = Style("background-color: rgba(255, 181, 71, 0.10);", "highlight_bg")
    success_bg = Style("background-color: rgba(74, 222, 128, 0.10);", "success_bg")
    error_bg = Style("background-color: rgba(248, 113, 113, 0.10);", "error_bg")
    surface_bg = Style("background-color: rgba(30, 41, 59, 0.80);", "surface_bg")
    overlay_bg = Style("background-color: rgba(15, 23, 42, 0.90);", "overlay_bg")


# ---------------------------------------------------------------------------
# 2. TEXT STYLES (composed from palette + StreamTeX primitives)
# ---------------------------------------------------------------------------

class TextStylesCustom:
    """Reusable text compositions for titles, labels, and emphasis."""
    # Titles — 4-level hierarchy: 96pt → 64pt → 48pt → 32pt (floor)
    course_title = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight + Text.sizes.Huge_size,
        "course_title",
    )
    page_title = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight + Text.sizes.Huge_size,
        "page_title",
    )
    section_title = Style.create(
        ColorsCustom.accent + Text.weights.bold_weight + Text.sizes.LARGE_size,
        "section_title",
    )
    section_subtitle = Style.create(
        ColorsCustom.highlight + Text.weights.bold_weight + Text.sizes.Large_size,
        "section_subtitle",
    )
    subsection_title = Style.create(
        ColorsCustom.success + Text.weights.bold_weight + Text.sizes.large_size,
        "subsection_title",
    )

    # Labels
    tip_label = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight + Text.sizes.large_size,
        "tip_label",
    )
    warning_label = Style.create(
        ColorsCustom.error + Text.weights.bold_weight + Text.sizes.large_size,
        "warning_label",
    )
    highlight_label = Style.create(
        ColorsCustom.highlight + Text.weights.bold_weight + Text.sizes.large_size,
        "highlight_label",
    )

    # Emphasis
    emphasis_primary = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight, "emphasis_primary"
    )
    emphasis_accent = Style.create(
        ColorsCustom.accent + Text.weights.bold_weight, "emphasis_accent"
    )
    emphasis_highlight = Style.create(
        ColorsCustom.highlight + Text.weights.bold_weight, "emphasis_highlight"
    )
    emphasis_success = Style.create(
        ColorsCustom.success + Text.weights.bold_weight, "emphasis_success"
    )
    emphasis_error = Style.create(
        ColorsCustom.error + Text.weights.bold_weight, "emphasis_error"
    )


# ---------------------------------------------------------------------------
# 3. CONTAINER STYLES (callouts, cards, gaps)
# ---------------------------------------------------------------------------

class ContainersCustom:
    """Reusable container styles for cards, callouts, and layout gaps."""
    # Callouts (left-border accent)
    callout_primary = Style(
        "border-left: 4px solid #5B9CF6;"
        "background-color: rgba(91, 156, 246, 0.08);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "callout_primary",
    )
    callout_accent = Style(
        "border-left: 4px solid #00D4AA;"
        "background-color: rgba(0, 212, 170, 0.08);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "callout_accent",
    )
    callout_highlight = Style(
        "border-left: 4px solid #FFB547;"
        "background-color: rgba(255, 181, 71, 0.08);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "callout_highlight",
    )
    callout_success = Style(
        "border-left: 4px solid #4ADE80;"
        "background-color: rgba(74, 222, 128, 0.08);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "callout_success",
    )
    callout_error = Style(
        "border-left: 4px solid #F87171;"
        "background-color: rgba(248, 113, 113, 0.08);"
        "border-radius: 4px;"
        "padding: 12px 16px;",
        "callout_error",
    )

    # Cards (rounded, surface background)
    card = Style(
        "background-color: rgba(30, 41, 59, 0.60);"
        "border: 1px solid rgba(91, 156, 246, 0.20);"
        "border-radius: 12px;"
        "padding: 24px 32px;",
        "card",
    )
    card_accent = Style(
        "background-color: rgba(30, 41, 59, 0.60);"
        "border: 1px solid rgba(0, 212, 170, 0.20);"
        "border-radius: 12px;"
        "padding: 24px 32px;",
        "card_accent",
    )

    # Code box
    code_box = Style(
        "background-color: rgba(91, 156, 246, 0.06);"
        "border: 1px solid rgba(91, 156, 246, 0.25);"
        "border-radius: 6px;"
        "padding: 12px;",
        "code_box",
    )

    # Table styles
    table_header = Style(
        "background-color: rgba(91, 156, 246, 0.15);"
        "padding: 8px 12px;"
        "border-bottom: 2px solid #5B9CF6;",
        "table_header",
    )
    table_cell = Style(
        "padding: 8px 12px;"
        "border-bottom: 1px solid rgba(148, 163, 184, 0.15);",
        "table_cell",
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

    # Separator
    separator = Style(
        "border: none; border-top: 2px solid rgba(91, 156, 246, 0.25);"
        "margin: 0 10%; height: 0;",
        "separator",
    )


# ---------------------------------------------------------------------------
# 4. AGGREGATION
# ---------------------------------------------------------------------------

class Custom:
    """Project-specific style namespace — accessed via s.project.*"""
    colors = ColorsCustom
    backgrounds = BackgroundsCustom
    titles = TextStylesCustom
    containers = ContainersCustom


class Styles(StxStyles):
    """Main Styles class — inherits all StreamTeX styles + AI4SE project styles."""
    project = Custom
