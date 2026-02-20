"""List styling: customizing list appearance with ListStyle.

This block explains how to customize ul/ol lists with ListStyle.
Control symbols, levels, nesting, and list styling.
"""

from streamtex import st_write, st_block, st_space, st_list, ListStyle, Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details


class BlockStyles:
    """Styles for this block."""
    pass


bs = BlockStyles


def build():
    """Build the ListStyle documentation block."""

    st_write(s.project.titles.page_title, "List Styling with ListStyle", tag=t.h1, toc_lvl="1")
    st_space("v", 1)

    show_explanation("""
ListStyle lets you customize the appearance of lists (ul/ol).
Control bullet symbols, numbering styles, and nested list behavior.
Compose ListStyles just like other styles.
    """)

    # ========================================================================
    # DEFAULT LIST STYLES
    # ========================================================================
    st_write(s.project.titles.section_title, "Default List Styles", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
StreamTeX provides pre-built list styles for common use cases.
Access them from the custom.styles.Styles class.
    """)

    st_write(s.project.titles.feature_title, "Built-in styles:")
    show_code("""
from streamtex import st_list

# Unordered list (bullets)
st_list(["item 1", "item 2", "item 3"], list_type="ul")

# Ordered list (numbers)
st_list(["step 1", "step 2", "step 3"], list_type="ol")

# Custom symbols
st_list(["point a", "point b"], list_type="ul",
        style=custom_list_style)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # CREATING CUSTOM LIST STYLES
    # ========================================================================
    st_write(s.project.titles.section_title, "Creating Custom ListStyle", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
Create a ListStyle to define custom symbols for each nesting level.
Symbols cycle through levels, repeating if needed.
    """)

    st_write(s.project.titles.feature_title, "Basic custom ListStyle:")
    show_code("""
from streamtex import ListStyle, st_list

# Define custom bullet symbols
my_list_style = ListStyle(
    symbols=["→", "◦", "■", "◆"],
    style=None  # Optional: CSS style for list
)

# Use it
items = ["First", "Second", "Third"]
st_list(items, list_type="ul", style=my_list_style)
    """, language="python")

    st_space("v", 2)

    st_write(s.project.titles.feature_title, "Nested list example:")
    show_code("""
from streamtex import ListStyle, st_list

custom_style = ListStyle(
    symbols=["🔹", "◦", "▪"],  # Different symbols per level
    style=None
)

# Three-level nested structure
nested_items = [
    "Level 1 - item 1",
    ("Level 1 - item 2", [
        "Level 2 - item 1",
        ("Level 2 - item 2", [
            "Level 3 - item 1",
            "Level 3 - item 2"
        ])
    ])
]

st_list(nested_items, style=custom_style)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # SYMBOL CYCLING
    # ========================================================================
    st_write(s.project.titles.section_title, "Symbol Cycling Behavior", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
If your list has more nesting levels than symbols defined,
symbols repeat in a cycle from the beginning.
    """)

    st_write(s.project.titles.feature_title, "Cycling example:")
    show_code("""
# Only 2 symbols defined
short_style = ListStyle(symbols=["→", "•"])

# 5 nesting levels will cycle:
# Level 1: →
# Level 2: •
# Level 3: → (cycles back)
# Level 4: •
# Level 5: → (cycles back)
    """, language="python")

    with st_block(Style("background:rgba(255,200,0,0.08);padding:8px;border-radius:4px;", "tip")):
        st_write(s.large, "💡 Define enough symbols to avoid confusion in deeply nested lists")

    st_space("v", 2)

    # ========================================================================
    # LIST STYLE OPERATORS
    # ========================================================================
    st_write(s.project.titles.section_title, "ListStyle Operators (+ and -)", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
Like regular styles, ListStyles can be combined using + and -.
Add symbols or remove/replace them.
    """)

    st_write(s.project.titles.feature_title, "Combining ListStyles:")
    show_code("""
from streamtex import ListStyle

# Base list style
base = ListStyle(symbols=["•", "◦"])

# Add more symbols
extended = base + ListStyle(symbols=["■", "◆"])
# Result: ["•", "◦", "■", "◆"]

# Remove (not common, but possible)
minimal = base - "◦"  # Remove the second symbol
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # STYLING LIST APPEARANCE
    # ========================================================================
    st_write(s.project.titles.section_title, "Styling List HTML/CSS", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
The style parameter in ListStyle applies CSS to the <ul> or <ol> element.
Control spacing, color, margins, etc.
    """)

    st_write(s.project.titles.feature_title, "Styled lists:")
    show_code("""
from streamtex import ListStyle, Style, st_list

# List style with custom CSS
compact_style = ListStyle(
    symbols=["→", "•"],
    style=Style(
        "list-style-position:inside;margin-left:0;padding-left:0;",
        "compact_list"
    )
)

items = ["Compact item 1", "Compact item 2"]
st_list(items, style=compact_style)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # ORDERED LISTS
    # ========================================================================
    st_write(s.project.titles.section_title, "Ordered Lists (ol)", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
For ordered lists, the list_type="ol" generates numbers automatically.
ListStyle symbols don't affect numbering, but CSS styling does.
    """)

    st_write(s.project.titles.feature_title, "Styled ordered list:")
    show_code("""
from streamtex import ListStyle, st_list

# Style the ordered list (not the symbols)
ordered_style = ListStyle(
    style=Style("padding-left:24px;margin-top:8px;", "ordered")
)

steps = ["First step", "Second step", "Third step"]
st_list(steps, list_type="ol", style=ordered_style)
# Renders as: 1. First step, 2. Second step, 3. Third step
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # PRACTICAL EXAMPLES
    # ========================================================================
    st_write(s.project.titles.section_title, "Practical Examples", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Example 1: Task Checklist")
    show_code("""
from streamtex import ListStyle, st_list

checklist = ListStyle(
    symbols=["☐", "✓"],  # Unchecked, checked
    style=None
)

tasks = [
    "Complete setup",
    ("Configure settings", [
        "Add credentials",
        "Set options"
    ]),
    "Deploy"
]

st_list(tasks, style=checklist)
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Example 2: Hierarchical TOC")
    show_code("""
from streamtex import ListStyle, st_list

toc_style = ListStyle(
    symbols=["📖", "📄", "📌"],
    style=None
)

structure = [
    "Part 1: Basics",
    ("Part 2: Advanced", [
        "Chapter 2.1",
        "Chapter 2.2",
        ("Section 2.2.1", [
            "Subsection A",
            "Subsection B"
        ])
    ])
]

st_list(structure, style=toc_style)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # BEST PRACTICES
    # ========================================================================
    st_write(s.project.titles.section_title, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, """
✓ **DO:**
- Define ListStyle once, reuse everywhere
- Use meaningful symbols (emoji, arrows, bullets)
- Provide enough symbols for expected nesting
- Style the container (padding, margins) not symbols
- Combine ListStyles with + for theme variations

✗ **DON'T:**
- Create new ListStyle for each list (not DRY)
- Mix symbols and numbering (confusing)
- Use too many different symbols (hard to read)
- Put CSS in symbol names (won't work)
    """)

    st_space("v", 2)

    show_details("""
Complex nested structures
- Test your list_style with expected nesting depth
- If symbols don't cycle well, add more symbols
- Consider readability over visual appeal
    """)
