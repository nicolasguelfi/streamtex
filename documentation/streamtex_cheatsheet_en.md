# StreamTeX Complete Cheatsheet

## Essential Imports

```python
# Block files (mandatory)
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s

# Book entry point (book.py)
import streamlit as st
import setup
import streamtex as stx
from streamtex import st_book, TOCConfig, MarkerConfig
from pathlib import Path
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts
import blocks
```

## Style Organization

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

### Style Composition

```python
# Create from CSS string
my_style = Style("color: red; font-weight: bold;", "my_style")

# Copy existing style with new ID
my_title = Style.create(s.bold + s.Large + s.center_txt, "my_title")

# Compose with + operator
heading = s.huge + s.bold + s.project.colors.primary

# Remove properties with - operator
no_bold = heading - s.bold
```

## Basic Elements

### Blocks and Text

```python
# Simple block with style
with st_block(s.center_txt):
    st_write(bs.green_title, "My Title")
    st_space(size=3)

# Block with list
with st_block(s.center_txt):
    with st_list(
        list_type=lt.ordered,
        li_style=bs.content) as l:
        with l.item(): st_write("First item")
        with l.item(): st_write("Second item")
```

### st_write — Full Signature

```python
st_write(
    *args,                          # Style objects, text, or (Style, text) tuples
    tag=t.span,                     # HTML tag: t.div, t.span, t.h1, t.p, t.section...
    link="",                        # Optional hyperlink URL
    no_link_decor=False,            # Remove underline from links
    toc_lvl=None,                   # TOC level: "1", "+1", "-1"
    label="",                       # Custom TOC entry label
    marker=None,                    # Per-heading marker control (True/False/None=auto)
)

# Inline mixed styles — ONE st_write with tuples (multiple calls stack vertically!)
st_write(s.Large, (s.text.colors.red, "Red "), (s.text.colors.blue, "Blue"))

# Register in TOC
st_write(bs.title, "Section Title", tag=t.div, toc_lvl="1")
st_write(bs.subtitle, "Subsection", toc_lvl="+1")

# Exclude a heading from marker navigation
st_write(s.huge, "Appendix", toc_lvl="1", marker=False)
# Force include in markers
st_write(s.huge, "Important", toc_lvl="2", marker=True)
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

### Grids and Tables (Responsive-First)

Multi-column grids MUST use responsive patterns so columns stack on narrow screens.

```python
# GOOD — responsive 2-column (stacks below 350px per column)
with st_grid(
    cols=s.project.containers.responsive_2col,
    grid_style=s.project.containers.gap_24,
    ) as g:
    with g.cell(): st_write("Panel A")
    with g.cell(): st_write("Panel B")

# GOOD — responsive 3-column
with st_grid(cols=s.project.containers.responsive_3col) as g:
    with g.cell(): st_write("Card 1")
    with g.cell(): st_write("Card 2")
    with g.cell(): st_write("Card 3")

# GOOD — responsive card grid
with st_grid(cols=s.project.containers.responsive_cards) as g:
    with g.cell(): st_image(uri="image1.png")
    with g.cell(): st_image(uri="image2.png")
    with g.cell(): st_image(uri="image3.png")

# Responsive presets (defined in custom/styles.py):
#   responsive_2col  = "repeat(auto-fit, minmax(350px, 1fr))"
#   responsive_3col  = "repeat(auto-fit, minmax(280px, 1fr))"
#   responsive_cards = "repeat(auto-fit, minmax(200px, 1fr))"

# BAD — fixed columns, never wraps on narrow screens
# st_grid(cols=2)
# st_grid(cols="2fr 3fr")

# OK — fixed columns ONLY for data tables with known column count
with st_grid(cols=2, cell_styles=bs.border) as g:
    with g.cell(): st_write("Header 1")
    with g.cell(): st_write("Header 2")

# Grid (table) with per-cell styles
with st_grid(
    cols=2,
    cell_styles=sg.create("A1,A3", s.project.colors.orange_02) +
                sg.create("A2", s.project.colors.red_01) +
                sg.create("A1:B3", s.bold + s.LARGE)
    ) as g:
    with g.cell(): st_write("Title")
    with g.cell(): st_write("Link")
    with g.cell(): st_write("Item 1")
    with g.cell(): st_write("link1")
    with g.cell(): st_write("Item 2")
    with g.cell(): st_write("link2")
```

### Overlays (Absolute Positioning)

```python
with st_overlay() as ov:
    with ov.layer(top=10, left=20):
        st_write(s.large, "Positioned at top:10px left:20px")
    with ov.layer(top=50, right=20):
        st_image(uri="badge.png", width="80px")
```

## Links and Navigation

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
# Register headings
st_write(style, "Section", toc_lvl="1")
st_write(style, "Subsection", toc_lvl="+1")

# TOCConfig — full options
toc = TOCConfig(
    numerate_titles=False,          # Auto-numbering of headings
    toc_position=0,                 # 0=start, -1=end, None=no TOC
    title_style=s.project.titles.section_title + s.center_txt,
    content_style=s.large + s.text.colors.reset,
    sidebar_max_level=None,         # None = auto (paginated: 1, continuous: 2)
    search=True,                    # Full-text search in sidebar
)
```

### Marker Navigation

```python
from streamtex import st_marker, MarkerConfig, st_book

# Place markers manually
st_marker("Section Start", visible=True)   # Visible marker (dashed border + label)
st_marker("Hidden Waypoint")               # Invisible marker (default)

# Auto-markers from TOC headings (in book.py)
marker_config = MarkerConfig(
    auto_marker_on_toc=1,          # Level-1 TOC headings become markers
    next_keys=["PageDown"],        # Navigate forward
    prev_keys=["PageUp"],          # Navigate backward
)
st_book([...], marker_config=marker_config)
```

## Predefined Styles

### Text Colors

```python
s.text.colors.red              # 140+ CSS named colors available
s.text.colors.lime
s.text.colors.alice_blue
s.text.colors.reset            # color: initial
```

### Text Sizes

```python
# Title sizes
s.GIANT     # 196pt    s.Giant     # 128pt    s.giant     # 112pt
s.Huge      # 96pt     s.huge      # 80pt
# Header sizes
s.LARGE     # 64pt     s.Large     # 48pt     s.large     # 32pt
# Body sizes
s.big       # 24pt     s.medium    # 16pt     s.little    # 12pt
s.small     # 8pt      s.tiny      # 4pt
# Dynamic sizes
s.text.sizes.size(20, "custom_20pt")   # Factory method
```

### Alignment and Layout

```python
s.center_txt                            # text-align: center
s.text.alignments.right_align           # text-align: right
s.text.alignments.justify_align         # text-align: justify
s.container.flex.center_align_items     # align-items: center
s.container.layouts.vertical_center_layout  # Flex centered both axes
s.container.layouts.center              # width: fit-content + auto margin
```

### Decorations

```python
s.bold                          # font-weight: bold
s.italic                        # font-style: italic
s.text.decors.underline_text    # text-decoration: underline
s.text.decors.strike_text       # text-decoration: line-through
```

### Container Styles

```python
# Padding
s.container.paddings.little_padding     # 9pt
s.container.paddings.small_padding      # 6pt
s.container.paddings.medium_padding     # 12pt
s.container.paddings.size("10px", "20px", style_id="custom_pad")  # Factory

# Borders
s.container.borders.solid_border
s.container.borders.dashed_border
s.container.borders.size("2px")         # Factory
s.container.borders.color(s.text.colors.blue)  # Factory

# Background colors
s.container.bg_colors.red_bg            # 140+ named background colors
s.container.bg_colors.reset_bg          # background-color: initial

# Flex
s.container.flex.flex                   # display: flex
s.container.flex.center_flex            # flex + center both axes
s.container.flex.space_between_justify  # justify-content: space-between

# Sizes
s.container.sizes.width_full            # width: 100%
s.container.sizes.height_auto           # height: auto

# Lists
s.container.lists.g_docs                # Google Docs symbols
s.container.lists.ordered_lowercase     # lower-alpha list
```

## Book Orchestration

### book.py Pattern

```python
import streamlit as st
import setup
import streamtex as stx
from streamtex import st_book, TOCConfig, MarkerConfig
from pathlib import Path
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts
import blocks

# Configure static sources
stx.set_static_sources([str(Path(__file__).parent / "static")])

# Page configuration
st.set_page_config(
    page_title="My Project",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject dark theme
sts.theme = dark

# TOC + Markers
toc = TOCConfig(numerate_titles=False, toc_position=0, search=True)
marker_config = MarkerConfig(auto_marker_on_toc=1, next_keys=["PageDown"], prev_keys=["PageUp"])

# Orchestrate blocks
st_book(
    [
        blocks.bck_01_welcome,
        blocks.bck_02_content,
    ],
    toc_config=toc,
    marker_config=marker_config,
    paginate=True,
    inspector=stx.InspectorConfig(enabled=True),
)
```

### st_book — Full Signature

```python
st_book(
    module_list,                    # List of block modules
    toc_config=None,                # TOCConfig object
    marker_config=None,             # MarkerConfig object
    separator=None,                 # Module rendered between blocks (optional)
    export=True,                    # Enable HTML export
    export_title="StreamTeX Export",
    paginate=False,                 # One block per page
    bib_sources=None,               # List of .bib/.json/.ris paths
    bib_config=None,                # BibConfig for bibliography
    inspector=None,                 # InspectorConfig for block inspector
    page_width=None,                # Page width (CSS value, default: "100%")
)
```

### InspectorConfig

```python
import streamtex as stx

# Enable the block inspector panel
st_book([...], inspector=stx.InspectorConfig(enabled=True))

# Full options
stx.InspectorConfig(
    enabled=True,
    password=None,          # Optional password protection
    panel_width="35vw",     # Right panel width
    backup=True,            # Create .bak files before saving
)
```

## Block Infrastructure

### Block Registry — blocks/__init__.py

```python
"""Blocks package — lazy-loaded via streamtex.ProjectBlockRegistry."""
from pathlib import Path
from streamtex import ProjectBlockRegistry, BlockNotFoundError, BlockImportError

registry = ProjectBlockRegistry(Path(__file__).parent)
__all__ = ["registry", "BlockNotFoundError", "BlockImportError"]

def __getattr__(name: str):
    try:
        return registry.get(name)
    except (BlockNotFoundError, BlockImportError) as e:
        raise AttributeError(str(e)) from e

def __dir__():
    return sorted(registry.list_blocks() + __all__)
```

### LazyBlockRegistry — Shared Blocks

```python
# In book.py — load blocks from external directories
shared_path = str(Path(__file__).parent.parent / "shared-blocks" / "blocks")
shared_blocks = stx.LazyBlockRegistry([shared_path])

st_book([
    shared_blocks.bck_header,       # From shared library
    blocks.bck_content,             # From local blocks/
    shared_blocks.bck_footer,       # From shared library
])

# Multi-source with priority (first source wins)
shared = stx.LazyBlockRegistry([
    "blocks/overrides",             # Checked first (project overrides)
    "../../shared-blocks/blocks",   # Checked second (originals)
])
```

### Composite Blocks (Atomic Sub-blocks)

```python
# Composite block: loads atomic sub-blocks from _atomic/ subfolder
import streamtex as stx
from streamtex import st_include

bck_text_basics = stx.load_atomic_block("bck_text_basics", __file__)
bck_text_styles = stx.load_atomic_block("bck_text_styles", __file__)

class BlockStyles:
    pass

def build():
    st_include(bck_text_basics)
    st_include(bck_text_styles)
```

- `load_atomic_block(name, __file__)` loads `_atomic/{name}.py` relative to caller
- Raises `BlockNotFoundError` / `BlockImportError` on failure

### Static Asset Resolution

```python
import streamtex as stx
from pathlib import Path

# Single source
stx.set_static_sources([str(Path(__file__).parent / "static")])

# Multi-source with priority (first directory containing the file wins)
stx.set_static_sources([
    str(Path(__file__).parent / "static"),                        # Local (highest priority)
    str(Path(__file__).parent.parent / "shared-blocks" / "static"),  # Shared fallback
])

# Manual resolution
path = stx.resolve_static("logo.png")   # Searches each source in order
# st_image() calls resolve_static() internally
```

## Block Helpers

### Config Injection Pattern (Recommended)

```python
# blocks/helpers.py — inject project styles globally
from streamtex import (
    BlockHelperConfig, set_block_helper_config,
    show_code as _show_code,
    show_explanation as _show_explanation,
    show_details as _show_details,
)
from custom.styles import Styles as s

class ProjectBlockHelperConfig(BlockHelperConfig):
    def get_code_style(self):
        return s.project.containers.code_box
    def get_explanation_style(self):
        return s.project.containers.explanation_box
    def get_details_style(self):
        return s.project.containers.details_box

set_block_helper_config(ProjectBlockHelperConfig())

# Convenience wrappers
def show_code(code_string: str, language: str = "python", line_numbers: bool = True):
    return _show_code(code_string, language, line_numbers)

def show_explanation(text: str):
    return _show_explanation(text)

def show_details(text: str):
    return _show_details(text)
```

### Standalone Functions

```python
from streamtex import show_code, show_explanation, show_details

show_code("print('hello')")                          # Uses injected config style
show_code("print('hello')", style=s.custom.style)    # Override with explicit style
show_explanation("This explains the concept...")
show_details("Additional details here...")
```

### OOP Inheritance (Advanced)

```python
from streamtex import BlockHelper

class ProjectBlockHelper(BlockHelper):
    def show_comparison(self, before: str, after: str):
        self.show_code(before)
        self.show_code(after)

helper = ProjectBlockHelper()
helper.show_comparison(old_code, new_code)
```

## Raw HTML (`st_html`)

Use `stx.st_html()` when you need to render raw HTML content (bar charts, decorative rules, embedded iframes). It routes through the dual-rendering pipeline (live + export buffer) and auto-injects `font-family: Source Sans Pro` in iframes.

```python
# Inline HTML (height=0, default) — renders via st.html()
stx.st_html('<hr style="border:none;height:3px;">')

# Iframe HTML (height>0) — renders via components.html() with auto font injection
stx.st_html('<div>chart content</div>', height=400)

# Iframe with scrolling
stx.st_html('<div>long content</div>', height=600, scrolling=True)

# Light background (force white bg in dark mode)
stx.st_html('<svg>...</svg>', height=300, light_bg=True)
```

**Parameters:**
- `html` — HTML string to render
- `height` — When > 0, render in an iframe with explicit pixel height (default: 0 = inline)
- `light_bg` — Force light color-scheme in the iframe (default: False)
- `scrolling` — Enable scrolling in the iframe (default: False)

## Export-Aware Widgets

Use `stx.st_*` wrappers instead of raw `st.*` calls for data visualization — they appear in both the live app AND the HTML export.

### Charts

```python
stx.st_line_chart(data, x="col_x", y="col_y")
stx.st_bar_chart(data, x="Category", y="Value")
stx.st_area_chart(data)
stx.st_scatter_chart(data, x="x", y="y")
```

### Tables & Data

```python
stx.st_dataframe(df, use_container_width=True)   # Interactive table
stx.st_table(data)                                # Static table
stx.st_json({"key": "value"})                     # JSON viewer
stx.st_metric("Revenue", "$1M", delta="+5%")      # KPI metric
```

### Diagrams

```python
# Graphviz (DOT language)
stx.st_graphviz('digraph { A -> B -> C }')

# Mermaid (interactive zoom/pan support)
stx.st_mermaid("""
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[OK]
    B -->|No| D[End]
""")

# Mermaid with options
stx.st_mermaid(code, style=my_style, light_bg=True, height=500)

# TikZ (requires LaTeX + Ghostscript)
stx.st_tikz(r"""
\begin{tikzpicture}
  \draw (0,0) -- (1,1) -- (2,0) -- cycle;
\end{tikzpicture}
""", preamble=r"\usepackage{tikz}")
```

### Audio & Video

```python
stx.st_audio("path/to/audio.wav", format="audio/wav")
stx.st_video("path/to/video.mp4")
stx.st_video("https://www.youtube.com/watch?v=...")
```

### Generic Fallback

```python
# For any widget not covered above
with stx.st_export('<p>Fallback HTML for export</p>'):
    st.plotly_chart(fig)
```

> **Note:** Interactive widgets (`st.button`, `st.slider`, `st.selectbox`) have no static representation and are absent from the export.

## Zoom Control

```python
import streamtex as stx

# Zoom is managed automatically by st_book().
# Available modes: Fit (never exceeds 100%), Fill (scales up to fill width), 50%-200% fixed.

# If calling manually:
stx.add_zoom_options()                          # Default page width (100%)
stx.add_zoom_options(page_width="1224pt")       # Custom fixed page width

# Low-level injection (rarely needed):
stx.inject_zoom_logic("Fit")                    # Fit: Math.min(1, available/page)
stx.inject_zoom_logic("Fill")                   # Fill: Math.min(2, available/page)
stx.inject_zoom_logic(100)                      # Fixed 100%
stx.inject_zoom_logic("Fit", page_width="800px")  # Custom page width
```

## Bibliography

```python
from streamtex.bib import BibConfig, BibFormat, CitationStyle

# Configure bibliography
bib_config = BibConfig(
    format=BibFormat.APA,
    citation_style=CitationStyle.AUTHOR_YEAR,
    hover_enabled=True,             # Hover preview of citations
    hover_show_abstract=True,
)

# Load sources (supports .bib, .json, .ris, .csl-json)
bib_sources = ["references.bib"]

# Pass to st_book
st_book([...], bib_sources=bib_sources, bib_config=bib_config)

# In-text citations (inside blocks)
from streamtex.bib import st_cite, st_bibliography
st_cite("author2024key")           # Inline citation widget
st_bibliography()                   # Render full bibliography
```

## Collection System (Multi-Project Hub)

### collection.toml

```toml
[collection]
title = "My Course Library"
description = "A collection of StreamTeX courses"
cards_per_row = 2

[projects.intro]
title = "Introduction Course"
description = "Learn the basics"
cover = "static/images/covers/intro.png"
project_url = "http://localhost:8502"
order = 1

[projects.advanced]
title = "Advanced Course"
description = "Master advanced concepts"
cover = "static/images/covers/advanced.png"
project_url = "http://localhost:8503"
order = 2
```

### Automatic Collection UI

```python
from streamtex import st_collection, CollectionConfig

config = CollectionConfig.from_toml("collection.toml")
st_collection(config=config, home_styles=s)
```

### Custom Collection with st_book

```python
# For full control over the collection UI
st_book([
    blocks.bck_home,              # Custom home page with cards
    blocks.bck_management,        # Documentation
], toc_config=toc, paginate=False)
```

## Google Sheets Import

```python
from streamtex import GSheetConfig, set_gsheet_config, load_gsheet, load_gsheet_df

# Configure
config = GSheetConfig(...)
set_gsheet_config(config)

# Load as module or DataFrame
block_module = load_gsheet("path/to/source")
df = load_gsheet_df("path/to/source")
```

## Utilities

### Spacing

```python
st_space(size=3)            # 3em vertical space
st_space("v", size=2)       # 2em vertical space
st_space("h", size=1)       # 1em horizontal space
st_space("h", size="40px")  # 40px horizontal space
st_br()                     # Line break
st_br(count=3)              # 3 line breaks
```

### Containers

```python
# Styled block container (vertical)
with st_block(s.center_txt):
    st_write("Centered content")

# Inline styled container
with st_span(s.bold + s.text.colors.red):
    st_write("Inline bold red")
```

## Project Structure

```
project_name/
  book.py                  # Entry point
  setup.py                 # PATH setup
  blocks/
    __init__.py            # ProjectBlockRegistry
    bck_*.py               # Each block: BlockStyles + build()
    helpers.py             # Block helper configuration
    _atomic/               # Atomic sub-blocks (optional)
  custom/
    styles.py              # Project styles (extends StxStyles)
    themes.py              # Dark theme overrides (dict)
  static/images/           # Image assets
  .streamlit/config.toml   # enableStaticServing = true
```

## Custom Styles Pattern (custom/styles.py)

```python
from streamtex.styles import Style, Text, Container, StxStyles

class ColorsCustom:
    primary = Style("color: #4A90D9;", "primary")
    accent = Style("color: #2EC4B6;", "accent")

class BackgroundsCustom:
    callout_bg = Style("background-color: rgba(74, 144, 217, 0.12);", "callout_bg")

class TextStylesCustom:
    course_title = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight + Text.sizes.Giant_size,
        "course_title"
    )

class ContainerStylesCustom:
    callout = Style.create(
        BackgroundsCustom.callout_bg
        + Container.borders.solid_border
        + Style("border-color: #4A90D9; border-width: 0 0 0 4px;", "callout_border")
        + Container.paddings.medium_padding,
        "callout"
    )

class Custom:
    colors = ColorsCustom
    backgrounds = BackgroundsCustom
    titles = TextStylesCustom
    containers = ContainerStylesCustom

class Styles(StxStyles):
    project = Custom
```

## Theme Overrides (custom/themes.py)

```python
# Keys are style_ids, values are replacement CSS strings
dark = {
    "primary": "color: #7AB8F5;",
    "course_title": "color: #7AB8F5; font-weight: bold; font-size: 128pt;",
    "callout_bg": "background-color: rgba(74, 144, 217, 0.20);",
}
```

## Tips and Best Practices

1. Group common styles in a `BlockStyles` class — one per block
2. ONE `st_write()` with tuples for inline mixed-style text (multiple calls stack vertically)
3. Never hardcode black/white — let Streamlit handle Light/Dark mode
4. No raw HTML/CSS — use Style composition
5. Use `stx.*` for content, `st.*` only for interactivity (buttons, sliders, inputs)
6. One generic style, reused everywhere — no duplicates
7. Use `tag=t.div` for block-level elements, default `t.span` for inline
