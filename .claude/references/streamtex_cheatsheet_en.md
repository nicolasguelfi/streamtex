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

# Centered list (bullet + text centered as a unit)
with st_block(s.center_txt):
    with st_list(
        list_type=lt.unordered,
        li_style=bs.content,
        align="center") as l:
        with l.item(): st_write("Centered item")
```

### st_list — Full Signature

```python
st_list(
    list_type=lt.unordered,             # lt.ordered or lt.unordered
    l_style=s.none,                     # Style for the list container (ListStyle for custom symbols)
    li_style=s.none,                    # Style for individual list items
    align=None,                         # "center" to center list block, None for left (default)
    alt_li_styles=None,                 # list[Style] — cycle styles per list item (optional)
)
```

### st_write — Full Signature

```python
st_write(
    *args,                          # Style objects, text, or (Style, text) tuples
    style=s.none,                   # Base style (can also be passed as first positional arg)
    tag=t.span,                     # HTML tag: t.div, t.span, t.h1, t.p, t.section...
    link="",                        # Optional hyperlink URL
    no_link_decor=False,            # Remove underline from links
    hover=True,                     # Enable hover effect on links (default: True)
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

### st_image — Full Signature

```python
st_image(
    style=s.none,                   # Style for the image container
    width="100%",                   # CSS width
    height="auto",                  # CSS height
    uri="",                         # Image path (resolved via resolve_static())
    alt="",                         # Alt text for accessibility
    link="",                        # Optional hyperlink URL wrapping the image
    hover=True,                     # Enable hover effect on linked images
    light_bg=False,                 # Force white background (dark-mode compatibility)
    *,                              # --- keyword-only below ---
    editable=False,                 # Enable inline editing panel (prompt + regenerate)
    name="",                        # Managed image name (for versioning/save)
    prompt=None,                    # AI generation prompt (enables AI features)
    provider=None,                  # AI provider ("openai", "google", "fal")
    model=None,                     # AI model override
    ai_size=None,                   # AI image size (e.g. "1024x1024")
    quality="standard",             # AI quality ("standard" or "hd")
)
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

# Image with light background (adds white bg for dark-mode compatibility)
st_image(uri="diagram.png", light_bg=True)

# Editable AI image — unified st_image with editing panel
st_image(uri="ai/concept.png", editable=True, name="concept",
         prompt="a minimalist neural network, flat design, dark bg",
         provider="openai")
```

### AI Image Generation

```python
from streamtex import set_ai_image_config, AIImageConfig
from streamtex import st_ai_image, st_ai_image_widget, generate_image

# Configure in book.py (once)
set_ai_image_config(AIImageConfig(
    provider="openai",             # "openai" | "google" | "fal"
    default_size="1024x1024",
    output_dir="static/images/ai",
    auto_generate=False,           # Manual mode (button) by default
))

# Declarative — in block code
st_ai_image("a minimalist neural network diagram, flat design, dark bg",
            width="100%", provider="openai", size="1024x1024",
            api_key=None)  # Per-call API key override (bypasses config/env)

# Interactive — widget with prompt input + generate button
st_ai_image_widget(default_prompt="a serene landscape", key="my_gen",
                   show_save=True, api_key=None,
                   style=s.ai_image, width="100%", height="auto",
                   size="1024x1024", quality="standard", model=None,
                   alt="", light_bg=False, config=None)

# Programmatic — generate without displaying (e.g. Claude workflow)
path = generate_image("a futuristic city", provider="openai",
                      save=True, base_image=None)  # save=True caches to disk; base_image for img2img
st_image(uri=path, width="100%")
```

**API keys** via environment variables (`.env` or Render):
```bash
STX_OPENAI_API_KEY=sk-...
STX_GOOGLE_AI_KEY=AIza...
STX_FAL_KEY=fal-...
```

**Install providers**: `uv add "streamtex[ai]"` (all) or `uv add "streamtex[ai-openai]"` (single).

### AI Image — Models & Providers

```python
from streamtex import get_available_models

# List available models for a provider
models = get_available_models("openai")   # e.g. ["gpt-image-1"]
models = get_available_models("google")   # e.g. ["imagen-3.0-generate-002"]
models = get_available_models("fal")      # e.g. ["sd-v3.5"]
```

### AI Image — History & Versioning

```python
from streamtex import (
    save_image_version, get_current_image, list_image_versions,
    rollback_image, rename_image, ImageMetadata,
)

# Save a new version of a managed image
path = save_image_version(
    "hero_intro",                    # Semantic name
    "static/images/hero.png",       # Source image path
    source_type="ai_generated",     # "local" | "url" | "ai_generated"
    prompt="a futuristic skyline",  # AI prompt (optional)
    provider="openai",              # AI provider (optional)
    model="gpt-image-1",           # AI model (optional)
    size="1024x1024",              # AI size (optional)
    quality="standard",            # AI quality (optional)
)

# Get current version path (None if not found)
current = get_current_image("hero_intro")

# List all versions — returns list of (version_number, ImageMetadata)
versions = list_image_versions("hero_intro")

# Rollback to a previous version (archives current first)
restored = rollback_image("hero_intro", version=2)

# Rename a managed image (current + all archived versions)
new_path = rename_image("hero_intro", "hero_welcome")
```

`ImageMetadata` — dataclass for image version metadata:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Semantic name (e.g. `"hero_intro"`) |
| `version` | `int` | Version number (default `1`) |
| `timestamp` | `str` | ISO 8601 creation time |
| `source_type` | `str` | `"local"`, `"url"`, or `"ai_generated"` |
| `original_path` | `str` | Original source path or URL |
| `prompt` | `str \| None` | AI prompt |
| `provider` | `str \| None` | AI provider name |
| `model` | `str \| None` | AI model identifier |
| `size` | `str \| None` | AI generation size |
| `quality` | `str \| None` | AI generation quality |
| `base_image` | `str \| None` | Base image path for img2img |
| `revised_prompt` | `str \| None` | Provider-revised prompt |

### st_grid — Full Signature

```python
st_grid(
    cols=2,                             # int or CSS string ("1fr 1fr", "repeat(auto-fit, ...)")
    grid_style=s.none,                  # Style for the grid container
    cell_styles=s.none,                 # Style(s) for cells (or StyleGrid for per-cell)
    gap=None,                           # CSS gap string (e.g. "24px") — shorthand for gap in grid_style
    responsive=False,                   # When True, auto-wraps columns using min_width
    min_width=None,                     # Min column width for responsive mode (e.g. "350px" or 350)
    breakpoint=None,                    # Viewport width below which grid collapses to 1 column (e.g. "600px")
)
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
    numbering=NumberingMode.SIDEBAR_ONLY,  # Numbered in sidebar TOC, not in document
    toc_position=0,                 # 0=start, -1=end, None=no TOC
    title_style=s.project.titles.section_title + s.center_txt,
    content_style=s.large + s.text.colors.reset,
    sidebar_max_level=2,            # Number headings up to level 2
    search=True,                    # Full-text search in sidebar
)
# NumberingMode options: SIDEBAR_ONLY (default), ALL (sidebar + document), NONE
```

### Marker Navigation

```python
from streamtex import st_marker, MarkerConfig, st_book

# Place markers manually
st_marker("Section Start", visible=True)   # Visible marker (dashed border + label)
st_marker("Hidden Waypoint")               # Invisible marker (default)
st_marker("Nav Only", hidden=True)         # PageDown stops here, not shown in sidebar list

# Auto-markers from TOC headings (in book.py)
marker_config = MarkerConfig(
    auto_marker_on_toc=1,          # Level-1 TOC headings become markers
    next_keys=["PageDown"],        # Navigate forward
    prev_keys=["PageUp"],          # Navigate backward
    draggable=True,                # User can drag the widget anywhere on screen
    collapsible=True,              # ⋮ button to collapse/expand the widget
)
st_book([...], marker_config=marker_config)
```

> **Search + Markers:** When `search=True` in TOCConfig and markers are enabled,
> the sidebar search also filters marker entries — only markers belonging to
> blocks that match the search query are shown (both paginated and continuous modes).

### Link Configuration

```python
from streamtex import LinkConfig, set_link_config

set_link_config(LinkConfig(
    internal_target="_self",     # Same-domain links open in same tab
    external_target="_blank",    # External links open in new tab
))

# Retrieve current configuration
cfg = get_link_config()             # Returns current LinkConfig
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
from streamtex import st_book, TOCConfig, MarkerConfig, BannerConfig
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
    initial_sidebar_state="expanded",
)

# Inject dark theme
sts.theme = dark

# TOC + Markers
toc = TOCConfig(numbering=NumberingMode.SIDEBAR_ONLY, toc_position=0, sidebar_max_level=2, search=True)
marker_config = MarkerConfig(auto_marker_on_toc=1, next_keys=["PageDown"], prev_keys=["PageUp"])

# Orchestrate blocks
st_book(
    [
        blocks.bck_welcome,
        blocks.bck_content,
    ],
    toc_config=toc,
    marker_config=marker_config,
    paginate=True,
    banner=BannerConfig.full(),
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
    view_modes=None,                # List[ViewMode] — restrict allowed view modes (None=both)
    banner=None,                    # BannerConfig for paginated navigation banners
    bib_sources=None,               # List of .bib/.json/.ris paths
    bib_config=None,                # BibConfig for bibliography
    inspector=None,                 # InspectorConfig for block inspector
    page_width=90,                  # Page width as % of browser width (default 90)
    zoom=100,                       # Default zoom level as % (default 100)
    pdf_config=None,                # PdfConfig for PDF export defaults
    exports=None,                   # List[ExportConfig] — auto-export to disk (new)
    presentation_profiles=None,     # List[PresentationProfile] — display profiles
    chrome_banner=True,             # Show browser recommendation banner (Chrome/Edge)
    doc_version=None,               # str | None — version string shown in sidebar
    loading=True,                   # Show loading overlay with progress (default True)
    banner_color="rgba(211,47,47,0.8)",  # Legacy — use banner=BannerConfig(...) instead
    monties_color=None,             # Legacy — use banner=BannerConfig(...) instead
)
```

### Presentation Profiles — Display Configurations

Named display configurations switchable at runtime via the sidebar or the floating navigation bar.

#### View Mode Restriction (`view_modes`)

Control which view modes are available in the sidebar Settings radio:

```python
from streamtex import st_book, ViewMode

# Both modes available (default — same as view_modes=None)
st_book(blocks, view_modes=[ViewMode.PAGINATED, ViewMode.CONTINUOUS])

# Lock to paginated only (hides the View radio)
st_book(blocks, paginate=True, view_modes=[ViewMode.PAGINATED])

# Lock to continuous only
st_book(blocks, view_modes=[ViewMode.CONTINUOUS])
```

When a single mode is given, the View radio is hidden and the document is locked to that mode.
Useful for deployed documents where switching modes should be disabled.

```python
from streamtex import (
    PresentationProfile, PageLayout, ViewMode,
    SlideBreakDisplayConfig, ProfileConfig,
)

# Define custom profiles
profiles = [
    PresentationProfile(
        name="Desktop",
        layout=PageLayout(width=90, zoom=100),
    ),
    PresentationProfile(
        name="Mobile",
        layout=PageLayout(width=100, zoom=60),
        breaks=SlideBreakDisplayConfig(enabled=False),
    ),
]

st_book([...], presentation_profiles=profiles)
```

**Factory presets** (all default to `PAGINATED` mode):

```python
# Desktop + Mobile pair
st_book([...], presentation_profiles=PresentationProfile.desktop_mobile_preset())

# Desktop + Tablet + Mobile
st_book([...], presentation_profiles=PresentationProfile.responsive_preset())

# Presenter + Audience + Handout (for slide decks)
st_book([...], presentation_profiles=PresentationProfile.presentation_preset())
```

**Data types**:

| Type | Fields | Description |
|------|--------|-------------|
| `PresentationProfile` | name, mode, layout, wrap, breaks | Top-level profile |
| `PageLayout` | width, zoom | Page dimensions (no range limits) |
| `ViewMode` | PAGINATED, CONTINUOUS | View mode enum |
| `SlideBreakDisplayConfig` | enabled, mode, space | Slide break settings |

**JSON save/load** (`ProfileConfig`):

```python
from streamtex import ProfileConfig

# Save
config = ProfileConfig(name="my_config", profiles=profiles)
config.save("config.json")

# Load
config = ProfileConfig.load("config.json")
st_book([...], presentation_profiles=config.profiles)
```

### st_chrome_banner — Browser Recommendation

```python
from streamtex import st_chrome_banner

# Show a dismissible banner recommending Chrome if the browser is not Chrome.
# Injects a fixed-position banner in the parent Streamlit frame — does not
# create a component in the block flow (no effect on TOC or block numbering).
# Called automatically by st_book() when chrome_banner=True (the default).
st_chrome_banner()
```

### BannerConfig — Paginated Navigation Banners

Controls the appearance of navigation banners in paginated mode.
Three display modes: `FULL` (prominent), `COMPACT` (slim), `HIDDEN` (no visual).

```python
from streamtex import BannerConfig, BannerMode

# Presets
banner=BannerConfig.full()                    # Default — large, rounded, with dividers
banner=BannerConfig.compact()                 # Slim, discreet
banner=BannerConfig.compact_gray()            # Compact with neutral gray
banner=BannerConfig.hidden()                  # No visual, navigation preserved

# Custom
banner=BannerConfig(
    mode=BannerMode.COMPACT,
    color="#1a5276",
    text_color="#ecf0f1",
    padding="8px 20px",
    show_arrows=False,
)
```

**BannerConfig fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `BannerMode` | `FULL` | Display mode (FULL, COMPACT, HIDDEN) |
| `color` | `str` | `"rgba(211,47,47,0.8)"` | Background colour (CSS) |
| `text_color` | `str` | `"white"` | Text colour (CSS) |
| `font_size` | `str \| None` | auto | Font size (None = auto per mode) |
| `font_weight` | `str \| None` | auto | Font weight (None = auto per mode) |
| `padding` | `str \| None` | auto | Padding (None = auto per mode) |
| `border_radius` | `str \| None` | auto | Border radius (None = auto per mode) |
| `show_title` | `bool` | `True` | Show target page title |
| `show_arrows` | `bool` | `True` | Show directional arrows |
| `show_dividers` | `bool \| None` | auto | Dividers between banner and content |

**Auto values by mode:**

| Field | FULL | COMPACT |
|-------|------|---------|
| font_size | 1.3rem | 0.8rem |
| font_weight | bold | 500 |
| padding | 18px 24px | 5px 16px |
| border_radius | 8px | 4px |
| show_dividers | True | False |

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

### Block Management — Advanced API

#### LazyBlockRegistry

```python
from streamtex import LazyBlockRegistry

# LazyBlockRegistry(sources) — lazy-load blocks from multiple directories
shared = LazyBlockRegistry([
    "blocks/overrides",             # Checked first (project overrides)
    "../../shared-blocks/blocks",   # Checked second (originals)
])
mod = shared.bck_header             # Lazy-loaded on first access, then cached

# Key methods
shared.list_blocks()                # List all discoverable bck_*.py block names
shared.get("bck_header")            # Explicit block access (same as attribute access)
shared.invalidate()                 # Clear cache so modules reload from disk
LazyBlockRegistry.invalidate_all()  # Clear caches on ALL LazyBlockRegistry instances
```

#### ProjectBlockRegistry

```python
from streamtex import ProjectBlockRegistry
from pathlib import Path

# ProjectBlockRegistry(blocks_dir) — registry for a project's blocks/ directory
registry = ProjectBlockRegistry(Path("blocks"))

# Key methods
registry.get("bck_intro")           # Load and return block module (cached)
registry.list_blocks()              # All bck_*.py names in the directory
registry.list_blocks("composite")   # Filter by type: "composite" or "atomic"
registry.load_all()                 # Force-load every block (for testing)
registry.get_stats()                # {"total": N, "loaded": N, "composites": N, "atomics": N}
registry.invalidate()               # Clear cache and manifest (reload from disk)
ProjectBlockRegistry.invalidate_all()  # Clear caches on ALL instances
```

#### Static Source Management

```python
from streamtex import get_static_sources, set_static_sources

# set_static_sources(sources) — set directories for static file resolution
set_static_sources([
    str(Path(__file__).parent / "static"),
    str(Path(__file__).parent.parent / "shared-blocks" / "static"),
])

# get_static_sources() — retrieve currently configured static source directories
sources = get_static_sources()       # Returns list of absolute paths (copy)
```

## Code Blocks — `st_code()`

```python
# Basic code block (responsive font size: desktop 18pt, tablet 14pt, mobile 11pt)
stx.st_code(style, code="print('hello')", language="python", line_numbers=True)

# With line wrapping (useful for JSON, logs, prose-like code on mobile)
stx.st_code(style, code='{"key": "long value..."}', language="json", wrap=True)

# Custom font size (overrides responsive default)
stx.st_code(style, code="print('hello')", font_size="14pt")
```

**Parameters:**
- `style` — Style object for the outer container
- `code` — Source code string
- `language` — Language for syntax highlighting (default: `"python"`)
- `line_numbers` — Show line numbers (default: `True`)
- `font_size` — CSS font size (default: responsive via `--stx-code-size`)
- `line_number_color` — Color for line numbers (default: `"#6A9BC5"`)
- `wrap` — When `True`, long lines wrap instead of scrolling horizontally (default: `None` — resolves to the global toggle set by `add_wrap_all_option()`, which defaults to `True` when called by `st_book()`)
- `file` — Path to a source file (resolved via `resolve_static()`). Mutually exclusive with `code`
- `encoding` — File encoding when using `file=` (default: `"utf-8"`)
- `line_start` — Starting line number for display (default: `None` — starts at 1)
- `start_line` — Extract from this line number when using `file=` (default: `None`)
- `end_line` — Extract up to this line number when using `file=` (default: `None`)

```python
# Load code from an external file
stx.st_code(style, file="code/example.py", language="python")
```

**Responsive font size** (via CSS variable `--stx-code-size`):

| Breakpoint | Font size |
|-----------|-----------|
| Desktop (default) | 18pt |
| Tablet (≤1024px) | 14pt |
| Mobile (≤480px) | 11pt |

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
def show_code(code_string: str = "", language: str = "python", line_numbers: bool = True,
              style=None, wrap=None, file=None, encoding="utf-8",
              line_start=None, start_line=None, end_line=None):
    return _show_code(code_string, language, line_numbers, wrap=wrap)

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
show_code('{"key": "value"}', language="json", wrap=True)  # Wrapping for JSON
show_code(file="examples/demo.py", start_line=5, end_line=15)  # From file with line range

# show_explanation / show_details render Markdown (bold, italic, lists, links…)
show_explanation("""\
    **st_markdown()** renders interpreted Markdown content.
    Use it for documentation with *formatting* and `code`.
""")
show_details("""\
    **Key point**: this is the main takeaway.

    Additional details with *emphasis* and `code`.
""")
```

### Block Helper Functions — Additional API

```python
from streamtex import (
    show_code_inline, get_block_helper_config,
    BlockHelperConfig, set_block_helper_config,
)

# show_code_inline(code_string, ...) — display code without the box wrapper
# Same parameters as show_code but renders raw code inside any container
show_code_inline("x = 42", language="python")
show_code_inline(file="examples/snippet.py", start_line=5, end_line=10)

# get_block_helper_config() — retrieve the current global BlockHelperConfig
config = get_block_helper_config()   # Returns active BlockHelperConfig instance

# BlockHelperConfig — base configuration class (override in subclass)
# Override methods: get_code_style(), get_code_inline_style(),
#                   get_explanation_style(), get_details_style()
class MyConfig(BlockHelperConfig):
    def get_code_style(self):
        return s.project.containers.code_box
    def get_code_inline_style(self):
        return s.project.containers.code_inline

# set_block_helper_config(config) — inject project-specific helper styles
set_block_helper_config(MyConfig())
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

# Mermaid fit modes (initial zoom on first render)
stx.st_mermaid(code, fit="contain")  # default: fit entire diagram in viewport
stx.st_mermaid(code, fit="width")    # fill viewport width
stx.st_mermaid(code, fit="none")     # natural size (scale 1)

# TikZ (requires LaTeX + Ghostscript)
stx.st_tikz(r"""
\begin{tikzpicture}
  \draw (0,0) -- (1,1) -- (2,0) -- cycle;
\end{tikzpicture}
""", preamble=r"\usepackage{tikz}")

# PlantUML (server-rendered, configurable)
stx.st_plantuml("""
@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response
@enduml
""")

# PlantUML with options
stx.st_plantuml(code, style=my_style, light_bg=True, height=500,
                server="https://www.plantuml.com/plantuml")

# All diagram functions accept file= for external files
stx.st_mermaid(file="diagrams/flowchart.mmd", height=500)
stx.st_tikz(file="diagrams/network.tex", height=800)
stx.st_plantuml(file="diagrams/class.puml", height=500)
stx.st_graphviz(file="diagrams/graph.dot")
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

## Document Languages — Markdown & LaTeX

### Markdown — `st_markdown()`

```python
# Render Markdown via Streamlit's native engine
stx.st_markdown("# Hello **World**")

# Render with StreamTeX styling (wraps in st_block)
stx.st_markdown("# Styled content", style=my_style)

# Load Markdown from an external file
stx.st_markdown(file="docs/readme.md")
```

**Supported syntax:** headings, bold, italic, strikethrough, lists, blockquotes,
links, pipe tables, fenced code blocks with syntax highlighting,
inline math (`$...$`), display math (`$$...$$`).

```python
# Tables (pipe syntax)
stx.st_markdown("""
| Feature | Support |
|---------|---------|
| Bold    | **yes** |
| Math    | $x^2$   |
""")

# Math in Markdown
stx.st_markdown("Inline $E=mc^2$ and display: $$\\int_0^1 x\\,dx$$")
```

**Parameters:**
- `content` — Markdown source string (mutually exclusive with `file`)
- `style` — Optional StreamTeX Style wrapping the rendered content
- `file` — Path to a `.md` file (resolved via `resolve_static()`)
- `encoding` — File encoding when using `file=` (default: `"utf-8"`)

**HTML export:** Uses python-markdown with `tables` and `fenced_code` extensions.

**st_markdown() vs st_write():**
- `st_markdown()` interprets Markdown syntax into formatted HTML
- `st_write()` applies StreamTeX styles to plain text (styled spans)
- Use `st_markdown()` for existing Markdown content (README, docs)
- Use `st_write()` for StreamTeX-styled inline text with composition
- `show_explanation()` and `show_details()` use `st_markdown()` internally — Markdown works in helper text

### LaTeX — `st_latex()` & `st_latex_doc()`

```python
# Math formula (Streamlit native KaTeX — fast, math only)
stx.st_latex(r"E = mc^2")
stx.st_latex(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}", style=my_style)

# Load formula from file
stx.st_latex(file="formulas/euler.tex")

# Document / fragment via LaTeX.js (CDN, client-side, zero system dependency)
stx.st_latex_doc(r"""
\section{Introduction}
This is a \textbf{bold} statement with math: $x^2 + y^2 = z^2$.

\begin{itemize}
  \item First item
  \item Second item
\end{itemize}
""", height=400)

# With options
stx.st_latex_doc(code, style=my_style, light_bg=True, height=600, hyphenate=False)

# Load from file
stx.st_latex_doc(file="docs/intro.tex", height=500)
```

**`st_latex()` parameters:**
- `content` — LaTeX math expression (mutually exclusive with `file`)
- `style` — Optional StreamTeX Style wrapping
- `file` — Path to a `.tex` file (resolved via `resolve_static()`)
- `encoding` — File encoding (default: `"utf-8"`)

**`st_latex_doc()` parameters:**
- `code` — LaTeX source. Fragments are auto-wrapped in a minimal article document; full documents (with `\documentclass`) are passed as-is
- `style` — Optional StreamTeX Style wrapping the iframe
- `light_bg` — White background (default: `True`)
- `height` — Iframe height in pixels (default: `600`)
- `hyphenate` — Enable LaTeX.js hyphenation (default: `True`)
- `file` — Path to a `.tex` file (resolved via `resolve_static()`)
- `encoding` — File encoding (default: `"utf-8"`)

Zero system dependency — LaTeX.js runs client-side via CDN.

**LaTeX parsing utilities** (reusable in blocks and conversion tools):

```python
from streamtex import extract_tikz, extract_math, extract_frames

tikz_blocks = extract_tikz(latex_source)   # List of tikzpicture blocks
math_exprs = extract_math(latex_source)     # List of $, $$, \[, \( formulas
frames = extract_frames(latex_source)       # List of Beamer frames
```

## Zoom Control

```python
import streamtex as stx

# Zoom is managed automatically by st_book().
# Two independent sidebar controls: Width % and Zoom % (pure CSS, no JavaScript).
# WYSIWYG export: Width % is propagated to HTML export (max-width).
# Zoom % is propagated to HTML export (CSS zoom) and PDF export (scale default).

# If calling manually:
stx.add_zoom_options()                                  # Defaults: width=100%, zoom=100%
stx.add_zoom_options(default_page_width=80)             # Start at 80% width
stx.add_zoom_options(default_page_width=80, default_zoom=125)  # 80% width, 125% zoom
stx.add_zoom_options(container=st.sidebar)              # Render controls in specific container

# Low-level injection (rarely needed):
stx.inject_zoom_logic(100, 100)      # Width 100%, Zoom 100%
stx.inject_zoom_logic(80, 150)       # Width 80%, Zoom 150%
stx.inject_zoom_logic(120, 50)       # Width 120%, Zoom 50%
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
from streamtex.bib import cite, st_cite, st_bibliography
st_cite("author2024key")           # Inline citation widget
cite("key1", "key2")               # Multi-key inline citation string
st_bibliography()                   # Render full bibliography
```

### Output Formats (BibFormat)

```python
BibFormat.APA       # Author, A. B. (Year). Title. Journal.
BibFormat.MLA       # Author. "Title." Journal, vol. N, Year.
BibFormat.IEEE      # [1] A. Author, "Title," Journal, Year.
BibFormat.CHICAGO   # Author. "Title." Journal N (Year): Pages.
BibFormat.HARVARD   # Author Year, 'Title', Journal, vol. N.
```

### Citation Styles (CitationStyle)

```python
CitationStyle.AUTHOR_YEAR  # (Smith et al., 2020)
CitationStyle.NUMERIC      # [1]
CitationStyle.SUPERSCRIPT  # Text^1
```

### Custom Parsers

```python
from streamtex.bib import register_bib_parser, BibEntry

def my_parser(filepath: str) -> list[BibEntry]:
    ...
register_bib_parser("myformat", my_parser)  # Auto-detect .myformat files
```

### Bibliography Advanced API

#### Configuration and Registry

```python
from streamtex import (
    get_bib_config, set_bib_config, get_bib_registry, reset_bib_registry,
    BibRegistry, BibParseError,
)

# get_bib_config() — retrieve current global bibliography configuration
cfg = get_bib_config()               # Returns the active BibConfig instance
print(cfg.format, cfg.citation_style)

# set_bib_config(config) — set the global bibliography configuration
from streamtex.bib import BibConfig, BibFormat
set_bib_config(BibConfig(format=BibFormat.IEEE, sort_by="year"))

# get_bib_registry() — access the global BibRegistry singleton
registry = get_bib_registry()
print(len(registry))                 # Number of registered entries
entry = registry.get("vaswani2017")  # Retrieve a BibEntry by key
keys = registry.list_keys()          # Sorted list of all entry keys

# reset_bib_registry() — clear all entries and citation tracking
reset_bib_registry()

# BibRegistry — singleton storing entries and citation tracking
registry = get_bib_registry()
registry.register(entry)             # Register a single BibEntry
registry.register_many(entries)      # Register a list of BibEntry objects
registry.cite("key")                 # Mark key as cited, returns 1-based number
cited = registry.get_cited_entries()  # List of cited BibEntry in citation order
all_entries = registry.get_all_entries()  # All registered entries
registry.reset()                     # Clear all entries and citations

# BibParseError — raised when bibliography file parsing fails
try:
    entries = load_bib("malformed.bib")
except BibParseError as e:
    print(f"Parse error: {e}")
```

#### Multi-Format Loaders

```python
from streamtex import (
    load_bib, load_bibtex, load_bib_json, load_bib_ris, load_bib_csl_json,
    parse_bibtex_string, parse_ris_string,
)

# load_bib(path) — auto-detect format by extension and parse
entries = load_bib("refs.bib")           # .bib → BibTeX parser
entries = load_bib("refs.json")          # .json → JSON parser
entries = load_bib("refs.ris")           # .ris → RIS parser
entries = load_bib("refs.csl-json")      # .csl-json → CSL-JSON parser

# Format-specific loaders (for explicit control)
entries = load_bibtex("refs.bib")        # Parse a .bib file into BibEntry list
entries = load_bib_json("refs.json")     # Parse JSON array of {key, title, authors, ...}
entries = load_bib_ris("refs.ris")       # Parse RIS format (TY, AU, TI tags)
entries = load_bib_csl_json("refs.csl-json")  # Parse Zotero/Mendeley CSL-JSON

# String parsers (for inline content, not files)
entries = parse_bibtex_string(bibtex_content)  # Parse BibTeX from a string
entries = parse_ris_string(ris_content)        # Parse RIS from a string
```

#### Formatting and Export

```python
from streamtex import format_entry, export_bibtex
from streamtex.bib import BibFormat

# format_entry(entry, fmt, number) — format a BibEntry as an HTML string
html = format_entry(entry, BibFormat.APA)          # APA formatted HTML string
html = format_entry(entry, BibFormat.IEEE, number=3)  # IEEE with [3] prefix

# export_bibtex(only_cited) — generate .bib file content from the registry
bib_text = export_bibtex()                  # Export only cited entries
bib_text = export_bibtex(only_cited=False)  # Export all registered entries
with open("output.bib", "w") as f:
    f.write(bib_text)
```

#### BibRefs Proxy and Stub Generation

```python
from streamtex import st_refs, BibRefs, generate_bib_stubs

# st_refs — global BibRefs proxy; attribute access calls cite()
st_write(s.big, "According to ", st_refs.vaswani2017, " transformers...")
# Equivalent to: st_write(s.big, "According to ", cite("vaswani2017"), "...")

# BibRefs — proxy class mapping attribute access to cite() calls
refs = BibRefs()
html_citation = refs.some_key          # Returns cite("some_key") HTML string

# generate_bib_stubs(*paths, output_path) — generate typed Python module for IDE completion
content = generate_bib_stubs("refs.bib", output_path="custom/bib_refs.py")
# Generates a .py file with @property per key for full IDE autocompletion
# CLI: uv run python -m streamtex generate-stubs refs.bib -o custom/bib_refs.py
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
from streamtex import GSheetConfig, GSheetSource, AuthMode
from streamtex import set_gsheet_config, load_gsheet, load_gsheet_df

# Authentication modes
AuthMode.PUBLIC            # No auth (public sheets)
AuthMode.SERVICE_ACCOUNT   # Server-side JSON key (production)
AuthMode.OAUTH2            # Interactive browser auth (dev)

# Configure
config = GSheetConfig(
    auth_mode=AuthMode.PUBLIC,          # or SERVICE_ACCOUNT, OAUTH2
    credentials_path="service.json",    # For SERVICE_ACCOUNT
    cache_ttl=300,                      # Cache seconds (0=no, None=forever)
)
set_gsheet_config(config)

# Retrieve current configuration
cfg = get_gsheet_config()               # Optional[GSheetConfig] — None if not set

# Define source
src = GSheetSource(sheet_id="abc123", tab_name="Sheet1")
src = GSheetSource.from_url("https://docs.google.com/spreadsheets/d/abc123/...")

# Load data
data = load_gsheet(src)                 # List[Dict]
df = load_gsheet_df(src)                # pandas DataFrame
```

Credentials resolution: explicit path > `GSHEET_CREDENTIALS` env > `GOOGLE_APPLICATION_CREDENTIALS` env.

## Configuration Classes

### ExportConfig

```python
from streamtex import ExportConfig, ExportMode

# --- Legacy usage (internal buffer config) ---
config = ExportConfig(
    enabled=True,                    # Enable export buffer (default False)
    page_title="My StreamTeX Export",  # Title of exported HTML document
    page_width="210mm",              # CSS max-width of the page container
    page_padding="20mm 15mm",        # CSS padding around the page
    zoom=0.8,                        # CSS zoom applied to exported page (default 1.0)
)
# Passed internally by st_book(export=True); rarely constructed manually

# --- Auto-export usage (new — via st_book(exports=[...])) ---
from streamtex import PdfConfig

# HTML auto-export with timestamp
html_export = ExportConfig(
    format="html",                   # "html" or "pdf"
    mode=ExportMode.ALWAYS,          # ALWAYS (auto) | MANUAL (sidebar) | NEVER
    output_dir="./exports",          # Directory for exported files
    filename="my-course",            # Base filename (default: book name)
    timestamp=True,                  # Append -YYMMDD-HHMMSS to filename
)

# PDF auto-export with custom config
pdf_export = ExportConfig(
    format="pdf",
    mode=ExportMode.ALWAYS,
    output_dir="./exports",
    filename="my-slides",
    timestamp=False,
    pdf=PdfConfig(format="A4", landscape=True, margin_top="0", margin_bottom="0"),
)

# Pass list to st_book — each config = one output file
st_book([...], exports=[html_export, pdf_export])
```

### ExportMode

```python
from streamtex import ExportMode

ExportMode.ALWAYS   # Auto-export to disk after every render
ExportMode.MANUAL   # Show sidebar panel — user clicks Generate (default sidebar)
ExportMode.NEVER    # Disable export entirely
```

### FileCategoryRegistry

```python
from streamtex import FileCategoryRegistry
from streamtex.inspector import FileCategory

# FileCategoryRegistry — extensible mapping of file extensions to categories
# Pre-registers: Python (.py), Diagrams (.mmd,.tex,.puml,.dot),
#                Data (.json,.csv,.toml,.yaml,.yml), Texts (.txt,.md,.bib,.ris)
registry = FileCategoryRegistry()

# Register a custom category
registry.register(FileCategory(
    name="Config",
    extensions={".ini", ".cfg"},
    ace_mode="text",
))

# Detect category for a file path
cat = registry.detect("blocks/bck_intro.py")  # Returns FileCategory(name="Python", ...)
all_cats = registry.categories                 # List of all registered FileCategory objects
```

### GSheetError

```python
from streamtex import GSheetError

# GSheetError — raised when Google Sheets data cannot be loaded
try:
    data = load_gsheet(src)
except GSheetError as e:
    st.error(f"Google Sheets error: {e}")
```

### BibParseError

```python
from streamtex import BibParseError

# BibParseError — raised when bibliography file parsing fails
try:
    entries = load_bib("refs.bib")
except BibParseError as e:
    st.error(f"Bibliography parse error: {e}")
```

### BibRegistry

```python
from streamtex import BibRegistry, get_bib_registry

# BibRegistry — singleton storing bibliographic entries and citation tracking
registry = get_bib_registry()
registry.register(entry)             # Register a BibEntry (overwrites if key exists)
registry.register_many(entries)      # Register multiple entries
entry = registry.get("key")          # Retrieve by key (None if not found)
num = registry.cite("key")           # Mark as cited, returns 1-based citation number
cited = registry.get_cited_entries()  # Cited entries in citation order
all_e = registry.get_all_entries()   # All registered entries
keys = registry.list_keys()          # Sorted list of all keys
registry.reset()                     # Clear entries and citations
len(registry)                        # Number of entries
"key" in registry                    # Membership test
```

### ProjectMeta

```python
from streamtex import ProjectMeta

# ProjectMeta — metadata for a single project in a collection
meta = ProjectMeta(
    title="Introduction Course",
    description="Learn the basics",
    cover="static/images/covers/intro.png",
    project_url="http://localhost:8502",
    order=1,
)
```

## Style System — Advanced

### StyleGrid

```python
from streamtex.styles import StyleGrid as sg, Style as ns

# StyleGrid — grid of styles for per-cell styling in st_grid
# Create with cell ranges in Excel-like notation (A1, B2, A1:C3)
header = sg.create("A1:B1", s.bold + s.container.bg_colors.blue_bg)
first_col = sg.create("A1:A5", s.text.colors.white)

# Combine grids with + (add styles) or * (override: right-hand side wins)
combined = header + first_col
overridden = header * sg.create("A1", s.text.colors.red)  # A1 gets red

# Subtract styles
cleaned = combined - sg.create("A1:A5", s.text.colors.white)
```

### StreamTeX_Styles

```python
from streamtex import StreamTeX_Styles

# StreamTeX_Styles — alias for StxStyles, the full aggregation class
# Provides: .none, .text, .container, .visibility, .bold, .italic,
#           .center_txt, .reset, .GIANT through .tiny, .light_bg
# Used as the base class for project Styles:
#   class Styles(StxStyles):
#       project = Custom
```

### ListStyle

```python
from streamtex.styles import ListStyle

# ListStyle — Style subclass for lists with custom bullet symbols
custom_list = ListStyle(
    css="color: blue;",
    style_id="blue_list",
    symbols=["►", "○", "■"],       # Cycles through symbols per nesting level
)
custom_list.lvl(1)                   # Returns "list-style-type: '►';"
custom_list.lvl(2)                   # Returns "list-style-type: '○';"
custom_list.lvl(4)                   # Returns "list-style-type: '►';" (cycles)
```

## Utilities

### responsive_cols

```python
from streamtex import responsive_cols

# responsive_cols(cols, min_width) — generate responsive CSS grid-template-columns
template = responsive_cols(3)              # "repeat(auto-fit, minmax(280px, 1fr))"
template = responsive_cols(2, 400)         # "repeat(auto-fit, minmax(400px, 1fr))"
template = responsive_cols(4, "15em")      # "repeat(auto-fit, minmax(15em, 1fr))"
template = responsive_cols(1)              # "1fr" (single column, no repeat)

# Use with st_grid
with st_grid(cols=responsive_cols(3)) as g:
    with g.cell(): st_write("A")
    with g.cell(): st_write("B")
    with g.cell(): st_write("C")
```

### st_toc

```python
from streamtex import st_toc

# st_toc(toc_title_style) — render a TOC placeholder in the main content area
# Writes a "Table of Contents" heading and returns an st.empty() container
# The container is filled later by st_book with the generated TOC links
toc_block = st_toc(s.project.titles.section_title)
```

### load_css

```python
from streamtex import load_css

# load_css(file_name) — load a CSS file from the static directory and inject it
load_css("custom-theme.css")         # Reads static/{file_name} and injects <style>
```

### reset_toc_registry

```python
from streamtex import reset_toc_registry, TOCConfig

# reset_toc_registry(toc_config) — clear all registered TOC entries for the current run
reset_toc_registry()                          # Reset with default TOCConfig
reset_toc_registry(TOCConfig(max_level=3))    # Reset with custom config
```

### toc_entries

```python
from streamtex import toc_entries

# toc_entries() — retrieve the list of registered TOC entries
entries = toc_entries()
# Each entry: {"level": int, "title": str, "section_number": str, "key_anchor": str}
for e in entries:
    print(f"Level {e['level']}: {e['title']} -> #{e['key_anchor']}")
```

### exec_static

```python
from streamtex import exec_static

# exec_static(path, context, start_line, end_line) — load and execute a Python file
# Path is resolved via resolve_static(). Uses caller's globals/locals if context is None.
exec_static("examples/demo.py")                       # Execute entire file
exec_static("examples/demo.py", start_line=5, end_line=20)  # Execute lines 5-20 only
exec_static("examples/demo.py", context={"s": s, "stx": stx})  # Custom context
```

### inject_link_preview_scaffold

```python
from streamtex import inject_link_preview_scaffold

# inject_link_preview_scaffold() — inject CSS/JS for link hover preview cards
# Called once by st_book(). Adds a hidden tooltip container and mouse event listeners
# that show page title + favicon on link hover.
inject_link_preview_scaffold()
```

### resolve_content

```python
from streamtex import resolve_content

# resolve_content(content, file, encoding) — resolve text from string or file
# When file is provided, resolve_static() is used for path resolution.
text = resolve_content(content="Hello world")        # Returns "Hello world"
text = resolve_content(file="docs/intro.txt")        # Reads file via resolve_static()
# Raises ValueError if both content and file are provided
```

### configure_image_path

```python
from streamtex import configure_image_path

# configure_image_path(base_path) — set the base path for static image URI resolution
# Default is "app/static/images". Call before rendering images if using a custom layout.
configure_image_path("app/static/assets")
```

### add_wrap_all_option

```python
from streamtex import add_wrap_all_option

# add_wrap_all_option(default) — add a "Wrap All" toggle to the sidebar
# When toggled, all st_code() blocks wrap long lines on the next re-render.
add_wrap_all_option()                # Default: wrap enabled (True)
add_wrap_all_option(default=False)   # Default: wrap disabled
```

### st_space — Full Signature

```python
st_space(
    direction="v",              # "v" for vertical, "h" for horizontal
    size="1em",                 # CSS size value (e.g. "1em", "20px", 3)
)
```

### Spacing

```python
st_space(size=3)            # 3em vertical space
st_space("v", size=2)       # 2em vertical space
st_space("h", size=1)       # 1em horizontal space
st_space("h", size="40px")  # 40px horizontal space
st_br()                     # Line break
st_br(count=3)              # 3 line breaks
```

### st_slide_break — Full Signature

```python
st_slide_break(
    marker_label="",           # Custom label for the hidden marker (default: auto)
    config=None,               # Optional SlideBreakConfig override
)
```

### SlideBreakMode Enum

```python
from streamtex import SlideBreakMode

SlideBreakMode.FULL          # Rule + spacer + marker (default)
SlideBreakMode.RULE_ONLY     # Rule + marker, no spacer
SlideBreakMode.SPACER_ONLY   # Spacer + marker, no rule
SlideBreakMode.MARKER_ONLY   # Hidden marker only (no visual)
SlideBreakMode.HIDDEN        # Completely hidden (no marker either)
```

### Presentation Config (Fullscreen 16:9)

```python
from streamtex import (
    set_presentation_config, PresentationConfig,
    st_presentation_footer, add_presentation_options,
)

# Configure in book.py (before st_book call)
set_presentation_config(PresentationConfig(
    title="My Presentation",
    aspect_ratio="16/9",       # 16:9 viewport fitting
    footer=True,               # Auto footer via st_presentation_footer()
    center_content=True,       # Center slide content vertically
    hide_streamlit_header=True, # Hide Streamlit hamburger menu
))

# Footer is rendered automatically when footer=True.
# To render manually (rare): st_presentation_footer()

# Sidebar options for presentation mode:
add_presentation_options()     # Adds fullscreen toggle + aspect ratio selector
```

### SlideBreakConfig — Fullscreen Mode

```python
from streamtex import set_slide_break_config, SlideBreakConfig, SlideBreakMode

# Fullscreen presentation: hidden breaks with marker navigation
set_slide_break_config(SlideBreakConfig(
    mode=SlideBreakMode.HIDDEN,  # No visible rule/spacer
    fullscreen=True,             # Each slide = 100vh viewport
    marker=True,                 # Hidden marker for PageDown nav
))
```

### Slide Break (Presentation Mode)

```python
from streamtex import st_slide_break, SlideBreakConfig, SlideBreakMode, set_slide_break_config

st_slide_break()            # Styled rule + 100vh spacer + hidden marker

# Customize globally (in helpers.py):
set_slide_break_config(SlideBreakConfig(
    mode=SlideBreakMode.FULL, # Display mode (default FULL)
    space="80vh",           # Vertical space (CSS value)
    thickness="2px",        # Rule thickness
    color="79, 172, 254",   # RGB values
    opacity=0.5,            # 0.0–1.0
    marker=True,            # Hidden marker for PageDown (default True)
))

# Per-call override:
st_slide_break(config=SlideBreakConfig(mode=SlideBreakMode.RULE_ONLY, space="50vh", marker=False))
```

### Slide Break Options (Sidebar Widget)

```python
import streamtex as stx

# Slide break options are managed automatically by st_book().
# Sidebar controls: Enable/disable slide breaks, mode selection, space %.

# If calling manually:
stx.add_slide_break_options()                           # Defaults: enabled, FULL, 60vh
stx.add_slide_break_options(default_enabled=True, default_mode=SlideBreakMode.FULL, default_space=60)

# CSS variables are injected automatically by add_slide_break_options() and st_slide_break()
```

### Slide Break CSS Variables

```css
--stx-break-space           /* Spacer height (e.g. 60vh) */
--stx-break-thickness       /* Rule thickness (e.g. 1px) */
--stx-break-opacity         /* Rule opacity (0.0–1.0) */
--stx-break-rule-display    /* Rule display: block or none */
--stx-break-spacer-display  /* Spacer display: block or none */
```

`@media print` rules automatically hide slide break visuals (rule and spacer)
and insert `page-break-before` for paginated PDF export.

### PDF Export

```python
from streamtex import export_pdf, PdfConfig, PdfMode

# Requires: uv add "streamtex[pdf]" && playwright install chromium

# Paginated (page break at each slide break):
pdf_bytes = export_pdf(html, "output.pdf", PdfConfig(mode=PdfMode.PAGINATED))

# Continuous (slide breaks removed):
pdf_bytes = export_pdf(html, "output.pdf", PdfConfig(mode=PdfMode.CONTINUOUS))

# Full config:
config = PdfConfig(
    mode=PdfMode.PAGINATED,
    format="A4",              # A4, Letter, A3, Legal, Tabloid
    landscape=True,           # Default True for presentations
    margin_top="10mm",
    margin_bottom="10mm",
    margin_left="15mm",
    margin_right="15mm",
    print_background=True,    # Include background colors
    scale=1.0,                # 0.1–2.0
    page_numbers=False,       # Add "1 / N" footer
    header_template="",       # Chromium print header HTML
    footer_template="",       # Chromium print footer HTML
)

# Pass pdf_config to st_book() — sets defaults for the sidebar PDF options:
st_book([...], pdf_config=PdfConfig(format="A4", landscape=True, page_numbers=True))
```

## Presentation Mode (Fullscreen 16/9)

### PresentationConfig

```python
from streamtex import PresentationConfig, set_presentation_config

set_presentation_config(PresentationConfig(
    title="My Presentation",
    aspect_ratio="16/9",
    footer=True,
    center_content=True,
    hide_streamlit_header=True,
))
```

**PresentationConfig fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `str` | `""` | Title displayed in the presentation footer |
| `subtitle` | `str` | `""` | Optional subtitle (not currently rendered in footer) |
| `aspect_ratio` | `str` | `"16/9"` | CSS aspect-ratio value ("16/9", "4/3", "16/10") |
| `enforce_ratio` | `bool` | `True` | Apply aspect-ratio + overflow:hidden to slide container |
| `footer` | `bool` | `True` | Show fixed slide counter bar at viewport bottom |
| `counter_mode` | `str` | `"bloc"` | Counter display: `"bloc"` (section count) or `"slide"` (marker-based) |
| `footer_height` | `str` | `"48px"` | CSS height of the footer bar |
| `footer_bg` | `str \| None` | `None` | Footer background colour (None = inherit from theme) |
| `footer_text_color` | `str \| None` | `None` | Footer text colour (None = inherit from theme) |
| `footer_font_size` | `str` | `"18px"` | Font size for footer text |
| `center_content` | `bool` | `True` | Vertically centre slide content within viewport |
| `content_padding` | `str` | `"48px 64px"` | CSS padding inside each slide container |
| `hide_streamlit_header` | `bool` | `True` | Hide the Streamlit header bar |
| `hide_streamlit_footer` | `bool` | `True` | Hide the "Made with Streamlit" footer |
| `hide_deploy_button` | `bool` | `True` | Hide the Streamlit deploy button |
| `sidebar_default` | `str` | `"collapsed"` | Initial sidebar state ("collapsed" or "expanded") |
| `slide_transition` | `str` | `"none"` | Transition effect ("none", "fade", "slide") |
| `transition_duration` | `str` | `"0.3s"` | CSS transition duration |

### get_presentation_config()

```python
from streamtex import get_presentation_config

config = get_presentation_config()  # -> PresentationConfig | None
```

### st_presentation_footer()

```python
from streamtex import st_presentation_footer

st_presentation_footer(current_slide=3, total_slides=12, title="My Talk")
```

### add_presentation_options()

```python
from streamtex import add_presentation_options

add_presentation_options()  # Sidebar controls for presenter
```

### SlideBreakConfig (fullscreen)

```python
from streamtex import SlideBreakConfig, SlideBreakMode, set_slide_break_config

set_slide_break_config(SlideBreakConfig(fullscreen=True, mode=SlideBreakMode.HIDDEN, marker=True))
```

> **Important**: `PresentationConfig` requires `paginate=False` (default). Fullscreen mode
> uses continuous scrolling with `st_slide_break()` for visual slide separation and
> PageDown/PageUp keyboard navigation.

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
