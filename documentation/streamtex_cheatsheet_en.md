# 📚 StreamTeX Complete Cheatsheet

## 📥 Essential Imports

```python
from streamtex import *
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
```

## 🎨 Style Organization

### Custom Style Class

```python
class BlockStyles:
    """Custom styles defined locally and used only for this block"""
    # Composed styles
    content = s.Large + s.center_txt
    lime_bold = s.text.colors.lime + s.bold
    bold_green = s.project.colors.green_01 + s.bold
    
    # Styles with alignment
    green_title = bold_green + s.huge + s.center_txt
    
    # Styles with borders
    border = s.container.borders.color(s.text.colors.black) + \
             s.container.borders.solid_border + \
             s.container.borders.size("2px")
    
    # Styles with padding
    side_padding = ns("padding: 10pt 36pt;")
bs = BlockStyles
```

## 📝 Basic Elements

### Blocks and Text

```python
# Simple block with style
with st_block(s.center_txt):
    st_write(bs.green_title, "My Title")
    st_space(size=3)

# Block with list
with st_block(s.center_txt):
    with st_list(
        list_type=l.ordered,
        li_style=bs.content) as l:
        with l.item(): st_write("First item")
        with l.item(): st_write("Second item")

```

### Images and Media

```python
# Simple image
st_image(uri="image.png")

# Image with dimensions
st_image(uri="image.png", width="1150px", height="735.34px")

# Image with link
st_image(uri="image.png", link="https://example.com")

# Image with auto-height style
st_image(s.container.sizes.height_auto, uri="image.png")
```

### Grids and Tables

```python
# 2 equal-width column grid
with st_grid(
    cols=2, 
    cell_styles=bs.border + s.container.paddings.little_padding
    ) as g:
    # row 1
    with g.cell(): st_image(uri="image1.png")
    with g.cell(): st_image(uri="image2.png")
    # row 2
    with g.cell(): st_image(uri="image3.png")


# Grid (table) with custom grid styles
with st_grid(
    cols=2, 
    cell_styles=sg.create("A1,A3", s.project.colors.orange_02) +
                sg.create("A2", s.project.colors.red_01) +
                sg.create("A1:B3", s.bold + s.LARGE)
    ) as g:
    # row 1
    with g.cell(): st_write("Title")
    with g.cell(): st_write("Link")
    # row 2
    with g.cell(): st_write("Item 1")
    with g.cell(): st_write("link1")
    # row 3
    with g.cell(): st_write("Item 2")
    with g.cell(): st_write("link2")
```

## 🔗 Links and Navigation

### Links

```python
# Simple link
st_write("Click here", link="https://example.com")

# Styled link
link_style = s.text.colors.blue + s.text.decors.underline_text
st_write(link_style, "Styled link", link="https://example.com", no_link_decor=True)
```

### Table of Contents

```python
# Top level
st_write(style, "Section", toc_lvl="1")

# Sub-level
st_write(style, "Subsection", toc_lvl="+1")
```

## 🎯 Predefined Styles

### Colors

```python
# Project colors
s.project.colors.blue_01
s.project.colors.green_01
s.project.colors.orange_01
s.project.colors.red_01
s.project.colors.brown_01

# Text colors
s.text.colors.lime
s.text.colors.black
```

### Text Sizes

```python
s.huge          # Very large
s.LARGE         # Larger
s.Large         # Large
s.large         # Normal
```

### Alignment and Layout

```python
s.center_txt
s.container.flex.center_align_items
s.container.layouts.vertical_center_layout
```

### Decorations

```python
s.bold
s.italic
s.text.decors.underline_text
```

## 🔧 Utilities

### Spacing

```python
# Vertical space
st_space(size=3)
st_space("v", size=2)

# Horizontal space
st_space("h", size=1)

# Line break
st_br()
```

### Containers

```python
# Padding
s.container.paddings.little_padding
s.container.paddings.small_padding

# Borders
s.container.borders.solid_border
s.container.borders.size("2px")
```

## 💡 Complete Examples

### Docs Page

```python
def build():
    with st_block(bs.center_txt):
        st_write(bs.green_title, "Documentation")
        st_space(size=3)
        with st_list(l.ordered, bs.content) as l:
            with l.item(): st_write("First point")
            with l.item(): st_write("Second point")
```

### Showcase with Grid

```python
def build():
    ### 2 columns grid
    st_grid(
        cols=2, 
        cell_styles=bs.border) as g:
        with g.cell(): st_image(uri="image1.png")
        with g.cell(): st_image(uri="image2.png")
        with g.cell(): st_write(bs.content, "Description")
```

### Full Page Example

```python
def build():
    # Header with title
    with st_block(s.center_txt + s.LARGE + s.bold):
        st_write(s.project.colors.blue_01 + s.huge, "Main Title", toc_lvl="1")
        st_space(size=2)
        st_write(s.project.colors.orange_01, "Subtitle", toc_lvl="+1")
        st_space(size=3)

    # Main content
    with st_block(s.center_txt):
        with st_list(
            list_type=l.ordered,
            li_style=bs.content) as l:
            with l.item(): st_write("Section 1")
            with l.item(): st_write("Section 2")
            with l.item(): st_write("Section 3")

    # Image grid
    st_grid(
        cols=2,
        cell_styles=bs.border + s.container.paddings.little_padding) as g:
            with g.cell(): st_image(uri="image1.png")
            with g.cell(): st_image(uri="image2.png")
            with g.cell(): st_write(bs.content, "Description 1")
            with g.cell(): st_write(bs.content, "Description 2")

    # Links and references
    with st_block(s.center_txt + s.Large):
        st_write(bs.link_style, "Link 1", link="https://example1.com")
        st_space(size=1)
        st_write(bs.link_style, "Link 2", link="https://example2.com")

    return html
```

## 📌 Important Notes

1. Use style classes to organize code
2. Combine styles with the `+` operator
3. Use `st_space()` to manage spacing
4. Keep a proper heading hierarchy for the table of contents

## 🔍 Tips and Best Practices

1. Group common styles in a `BlockStyles` class
2. Use variables for reusable styles
3. Comment complex sections
4. Structure code into logical sections
5. Use vertical spacing to improve readability
