---
alwaysApply: true
---

# StreamTeX Development Guidelines

## 1. The StreamTeX Philosophy
StreamTeX is a wrapper around Streamlit with a block-based architecture. You are strictly forbidden from manually writing HTML or CSS strings within the Python code.
- **BAD:** `st.markdown("<div style='color:red'>Text</div>", unsafe_allow_html=True)`
- **GOOD:** `sx.st_write(s.text.colors.red, "Text")`

## 2. Source of Truth
- **Syntax Reference:** Read `documentation/streamtex_cheatsheet_en.md` before writing any block code.
- **Architecture Reference:** Inspect any project's `book.py` to understand how it orchestrates `blocks/`, and how to build a web book with modular blocks that may be nested and reusable. For illustration, see `tests/test_project/book.py` or `documentation/template_project/book.py`.

### Directory Structure
- Follow the standard StreamTeX project structure:
  - `book.py` (main entry point)
  - `setup.py`(sets up PATH)
  - `blocks/` (content modules)
  - `blocks/__init__.py` (sets up block access)
  - `custom/` (themes.py, styles.py)
  - `static/images/` (static assets)
  - `streamtex/` (library)
  - `.streamlit/config.toml` (streamlit configuration, **critical** for static image serving)

## 3. Mandatory Imports

### A. For Block Files (`blocks/bck_*.py`)
Every block file must start with this setup:
```python
import streamlit as st

# StreamTeX Imports
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

# Project Specific Imports
from custom.styles import Styles as s
```

### B. For the Entry Point (`book.py` ONLY)
- This file MUST import `setup.py` to handle the PATH setup.
```python
import streamlit as st
import setup
```
- one may access blocks as such:
```python
import blocks

blocks.bck_name
```

## 4. Coding Standards: `sx` vs `st`

### When to use StreamTeX (`sx`)

Use `sx` functions for **ALL** layout and static content.

- **Text:** Use `sx.st_write(style, ...)` instead of `st.write` or `st.markdown`.
- **Images:** Use `sx.st_image(style, uri=...)` instead of `st.image`.
- **Lists:** Use `sx.st_list()` instead of manual markdown lists.
- **Layouts:** Use `sx.st_grid(cols, ...)` instead of `st.columns`.
- **Content Encapsulation:** Use `st_block()`, sometimes `st_span()`.
- **Spacing:** Use `sx.st_space()` or `sx.st_br()`.

#### Common Parameters
- Always specify `style=` for `st_write()`
- Use `toc_lvl='level'` for table of contents
- Use `link=` for hyperlinks
- Use `tag=` to specify HTML tag

#### Layout & Encapsulation Rules (`st_block`)
- **Vertical Stacking (Default):** Use `with sx.st_block(...):` when you want elements to stack on top of each other. This is the default behavior.
- **Inline Flow (Mixed-Style Text):** For multiple styled segments on *one line* (e.g. link + text, or spans side-by-side), use **one** `st_write` with tuple arguments: `st_write(base_style, (style_a, "text"), (style_b, "more"))`. **Do NOT** use multiple `st_write` calls — they stack vertically and break the inline layout.
- **Horizontal Flow:** Use `with sx.st_span(...):` when you want elements to flow inline (side-by-side), similar to text spans. Only use this if the content isn't wide enough to wrap around. For mixed-style *text* on one line, prefer `st_write` with tuples over `st_span`.

### When to use Streamlit (`st`)

Only use standard `st` functions for:

- Interactivity (Buttons, Inputs, Sliders).
- Media players (Audio/Video) if `sx` lacks a wrapper.
- Dataframes.
- When explicitly asked to use it.

## 5. Block Architecture

### StreamTeX Blocks (`build`)
It must contain a ```build()``` function.

```python
import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block only"""
    # Define block-specific styles
    pass
bs = BlockStyles

def build():
    with sx.st_block(s.center_txt):
        sx.st_write(s.title, "Hello World")
```


## 6. Project Structure

- **Filenames:** `blocks/bck_[description]_[suffix].py`. Examples: `bck_welcome_screen.py`, `bck_title_content.py`.
- **Assets:** Store images in `static/images/`. Refer to them using relative paths. Use `os.path.join()` to build custom paths if needed.

## 7. Styling Guidelines

- **No Inline Strings:** Never write inline CSS strings (e.g., `"font-size: 20px"`).
- **Base Styles:** Use `s.text.*`, `s.container.*` for base styles
- **Project Styles:** Use `s.project.*` for project-specific custom styles
- **Composition:** Combine styles using the `+` operator: `s.bold + s.red + s.Large + s.center_txt`.
- **Definition:** Define styles in `BlockStyles` class within the file or `custom/styles.py`.
- **Text Font and Sizes:**
  - **Default:** The default font is **Arial**. The default unstyled size is **16px** (approx. **12pt**).
  - **Available Sizes:** `s.text.sizes` (often aliased directly as `s.large`, `s.huge`, etc.) provides the following scale:
    - **Titles:** `GIANT` (196pt), `Giant` (128pt), `giant` (112pt), `Huge` (96pt), `huge` (80pt).
    - **Headers:** `LARGE` (64pt), `Large` (48pt), `large` (32pt).
    - **Body/Sub:** `big` (24pt), `medium` (16pt), `little` (12pt/Default), `small` (8pt), `tiny` (4pt).
  - **Usage:** Ensure title-to-body ratios are balanced.
- **Typography Details (Bold & Italic)**
  - **Detection:** Be keenly aware of weight and emphasis.
    - **Bold:** Apply `s.bold` if the text carries visual weight or acts as a sub-header.
    - **Italic:** Apply `s.italic` for citations, emphasis, or captions.
  - **Defaults:** Remember that links (`link=...`) are underlined and blue by default. Use `no_link_decor=True` if the design shows a plain link.
- **Link Font Size:** Links default to 12pt. When the design shows links at a larger size, include the size in the link style (e.g. `link_style = color + underline + s.Large`).
- **Light vs. Dark Mode Awareness:** Do not hardcode black or white unless it is an explicit design choice (e.g., a specific "card" background).
  - **Implicit Colors:** If text is black on a white background (or vice versa), this is usually the *default theme*, not a style. **Do NOT** explicitly style it as `color: black`. Let Streamlit handle the Light/Dark mode switch.
  - **Explicit Colors:** Only define `color` or `background-color` if it is a branding color (Red, Blue, specialized Gray) that must remain constant regardless of the theme.

### Custom Style Creation
- Inherit from `StreamTeX_Styles` in `custom/styles.py`
- Organize by categories: colors, titles, etc.
- Use `Style.create()` to combine existing styles

### Style Reusability & Naming (MANDATORY)
- **Generic Definitions:** Always define and reuse generic styles. If two texts (regardless of content) share the same properties (e.g., pink color, 18pt size), create **ONE** style with a generic name (e.g., `pink_subtitle`) and reuse it.
- **Language Agnostic:** Use **ENGLISH only** for style names. Reuse the same style instance for text in any language. Do not duplicate styles just because the text content differs.
- **Avoid Duplication:** Do not differentiate styles by ID if they have exactly the same definition.

### Visual Considerations
- **Dark Mode:** Ensure your style definitions are dark mode friendly (e.g., avoid pure black text on transparent backgrounds if the default theme is dark). If needed, add theme variants in ```custom/themes.py```.
- **Alignment:** Be keenly aware of centered styles and text alignment.
- **Precision Layout:** Always insert line breaks to match the provided text layout exactly.

## 8. Variable Naming Conventions

### Classes and Variables
- `BlockStyles` or `BStyles` for local styles
- `bs = BlockStyles` for the instance
- `build()` for blocks

### Custom Styles
- Use descriptive names: `title_giant_green_01`, `subtitle_blue_01`
- Suffix custom colors: `green_01`, `blue_dark_01`, `bronze_01`


## 9. Documentation and Comments

### Block Documentation
- Include docstring for `build()`
- Document function parameters with default values
- Add comments for complex styles

### Style Documentation
- Document custom styles in `custom/styles.py`
- Explain style hierarchy in comments
- Use descriptive variable names

## 10. Performance and Optimization

### Style Optimization
- Avoid repeated creation of identical styles
- Use predefined styles instead of inline styles
- Minimize complex style combinations

### Memory Management
- Avoid circular imports
- Use local imports when possible
- Clean up temporary resources

## 11. Development Conventions

### Code Formatting
- Use 4 spaces for indentation
- Limit lines to 100 characters
- Use snake_case for variable names
- Use PascalCase for class names

## 12. StreamTeX Specific Patterns

### Table of Contents
- Use `'1'` for level 1, `'+1'`/`'-1'` for relative levels
- Always provide meaningful labels
- Use `toc_lvl` parameter in `st_write()`

### Style Combinations
- Prefer style composition over inline CSS
- Use `StyleGrid` for complex layouts
- Leverage theme system for global style changes


## 13. Best Practices

### Code Organization
- Keep blocks focused and single-purpose
- Reuse common patterns across blocks
- Maintain consistent naming throughout project

### Style Consistency
- Use project color palette consistently
- Follow typography hierarchy
- Maintain spacing and layout patterns

### Testing and Validation
- Test blocks individually
- Validate HTML output
- Check responsive behavior
- Verify accessibility features
