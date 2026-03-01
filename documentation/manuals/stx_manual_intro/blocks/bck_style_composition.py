"""Style composition: combining and modifying styles using operators.

This block explains how to compose, combine, and modify styles using + and - operators.
Essential for DRY styling practices in StreamTeX.
"""

from streamtex import st_write, st_block, st_space, Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details


class BlockStyles:
    """Styles for this block."""
    example_box = Style("background:rgba(100,150,200,0.08);padding:12px;border-radius:6px;", "example_box")


bs = BlockStyles


def build():
    """Build the style composition documentation block."""

    st_write(s.project.titles.page_title, "Style Composition: Operators", tag=t.h1, toc_lvl="1")
    st_space("v", 1)

    show_explanation("""
StreamTeX styles can be combined and modified using operators.

Use + to add styles together, and - to remove properties.

This enables DRY (Don't Repeat Yourself) styling.
    """)

    # ========================================================================
    # STYLE ADDITION (+)
    # ========================================================================
    st_write(s.project.titles.section_title, "Adding Styles (+ operator)", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
Use the + operator to combine two styles into one.

The result is a new style with properties from both.

Order matters: second style can override first style's properties.
    """)

    st_write(s.project.titles.feature_title, "Style + Style combination:")
    show_code("""
from streamtex import Style

# Base styles
heading = Style("font-size:24px;font-weight:bold;", "heading")
red = Style("color:red;", "red")

# Combine them
red_heading = heading + red

# Result: font-size:24px + font-weight:bold + color:red
    """, language="python")

    with st_block(bs.example_box):
        st_write(s.large, "💡 Tip: Combine base + modifier styles for consistency")

    st_space("v", 2)

    st_write(s.project.titles.feature_title, "Style + String combination:")
    show_code("""
from streamtex import Style

# Start with existing style
base_style = Style("font-size:16px;", "base")

# Add CSS string to it
modified = base_style + "color:blue;text-decoration:underline;"

# Result: font-size:16px + color:blue + text-decoration:underline
    """, language="python")

    with st_block(bs.example_box):
        st_write(s.large, "💡 Tip: CSS strings are automatically turned into Style objects")

    st_space("v", 2)

    # ========================================================================
    # STYLE SUBTRACTION (-)
    # ========================================================================
    st_write(s.project.titles.section_title, "Removing Properties (- operator)", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
Use the - operator to remove a property from a style.
Useful when you want most of a style but need to override one property.
    """)

    st_write(s.project.titles.feature_title, "Removing properties:")
    show_code("""
from streamtex import Style

# Style with multiple properties
box_style = Style(
    "background:blue;color:white;padding:16px;border-radius:8px;",
    "box"
)

# Remove the background color
text_only = box_style - "background"

# Result: color:white + padding:16px + border-radius:8px (no background)
    """, language="python")

    with st_block(bs.example_box):
        st_write(s.large, "💡 Tip: Provide property name only (no value) with - operator")

    st_space("v", 2)

    # ========================================================================
    # PRACTICAL PATTERNS
    # ========================================================================
    st_write(s.project.titles.section_title, "Practical Composition Patterns", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Pattern 1: Base + Modifiers")
    show_code("""
# Define base styles once
base_text = Style("font-family:sans-serif;font-size:16px;", "base_text")
bold = Style("font-weight:bold;", "bold")
red = Style("color:red;", "red")

# Compose as needed
title = base_text + bold
error = base_text + red + bold
success = base_text + Style("color:green;", "green")
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Pattern 2: Remove and Replace")
    show_code("""
# Start with a complex style
primary_button = Style(
    "background:blue;color:white;padding:12px;border-radius:6px;cursor:pointer;",
    "primary_btn"
)

# Create variants by removing and adding
secondary_button = (primary_button - "background") + "background:gray;"
danger_button = (primary_button - "background") + "background:red;"
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Pattern 3: Progressive Enhancement")
    show_code("""
# Start minimal
simple = Style("font-size:14px;", "simple")

# Build up as needed
medium = simple + "padding:8px;"
advanced = medium + "border:1px solid #ccc;background:#f5f5f5;"
full = advanced + "box-shadow:0 2px 4px rgba(0,0,0,0.1);"
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # OPERATOR PRECEDENCE
    # ========================================================================
    st_write(s.project.titles.section_title, "Operator Precedence & Overrides", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
When combining styles, the RIGHTMOST style wins if properties conflict.

Use this to your advantage for predictable overrides.
    """)

    st_write(s.project.titles.feature_title, "Override behavior:")
    show_code("""
from streamtex import Style

style_a = Style("color:blue;font-size:16px;", "a")
style_b = Style("color:red;padding:8px;", "b")

# Right side wins on conflicts
result = style_a + style_b
# Result: color:red (b overrides a) + font-size:16px + padding:8px
    """, language="python")

    with st_block(bs.example_box):
        st_write(s.large, "💡 Tip: Place overrides on the right side of + for clarity")

    st_space("v", 2)

    # ========================================================================
    # REAL-WORLD EXAMPLE
    # ========================================================================
    st_write(s.project.titles.section_title, "Real-World Example", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
Complete example: building a theme system using style composition.
    """)

    show_code("""
from streamtex import Style, st_write, st_block

# 1. Define base styles (reusable)
text_base = Style("font-family:sans-serif;line-height:1.6;", "text_base")
box_base = Style("padding:16px;border-radius:8px;", "box_base")

# 2. Define color/theme modifiers
light_theme = Style("background:#f5f5f5;color:#333;", "light")
dark_theme = Style("background:#1a1a1a;color:#fff;", "dark")
accent = Style("border-left:4px solid #007bff;", "accent")

# 3. Compose specific styles
light_text = text_base + light_theme
light_box = box_base + light_theme + accent
dark_text = text_base + dark_theme
dark_box = box_base + dark_theme + accent

# 4. Use in code
with st_block(light_box):
    st_write(light_text, "Light theme box with accent border")

with st_block(dark_box):
    st_write(dark_text, "Dark theme box with accent border")
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # BEST PRACTICES
    # ========================================================================
    st_write(s.project.titles.section_title, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, """
✓ **DO:**
- Use + to combine related styles
- Place overrides on the right side
- Name composed styles meaningfully
- Create base styles for reuse
- Use - when removing is clearer than rewriting

✗ **DON'T:**
- Create new styles when composition works
- Use overly complex chains (style_a + b + c + d + e)
- Rely on + for conflicting properties (use - then +)
- Mix logical operations (hard to understand)
    """)

    st_space("v", 2)

    show_details("""
Complex style chains

- If you have style_a + style_b + style_c + ...
- Better: Create intermediate "combo" styles
- Example: base + theme is clearer than 10-property string
    """)
