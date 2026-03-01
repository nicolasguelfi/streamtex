# StreamTeX Coding Standards

> **Single source of truth** for development guidelines.
> Referenced by both `CLAUDE.md` and `.cursor/rules/streamtex/development/RULE.md`.

## 1. The StreamTeX Philosophy
StreamTeX wraps Streamlit with a block-based architecture. Never manually write HTML or CSS strings in Python code.
- **BAD:** `st.markdown("<div style='color:red'>Text</div>", unsafe_allow_html=True)`
- **GOOD:** `stx.st_write(s.text.colors.red, "Text")`

## 2. Source of Truth
- **Syntax Reference:** `documentation/streamtex_cheatsheet_en.md`
- **Architecture Reference:** Any project's `book.py` (orchestrates blocks/). See `documentation/template_project/` or `documentation/manuals/stx_manual_intro/` for illustration.

## 3. Project Structure
```
project_name/
  book.py                  # Entry point (imports setup, calls st_book())
  setup.py                 # PATH setup (adds parent dir to sys.path)
  blocks/                  # Content modules
    __init__.py            # Dynamic import via importlib
    bck_*.py               # Each block has a build() function
  custom/
    styles.py              # Project-specific styles (inherits StxStyles)
    themes.py              # Theme overrides (dict)
  static/images/           # Image assets
  .streamlit/config.toml   # MUST have enableStaticServing = true
```

## 4. Mandatory Imports

### Block Files (`blocks/bck_*.py`)
```python
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
```

### Entry Point (`book.py`)
```python
import streamlit as st
import setup
import blocks
```

## 5. sx vs st — When to Use What
- **ALL layout and content** -> `stx.*`: st_write, st_image, st_grid, st_list, st_block, st_span, st_space, st_br, st_overlay, st_html
- **Data visualization (export-aware)** -> `stx.*`: st_dataframe, st_table, st_metric, st_json, st_graphviz, st_line_chart, st_bar_chart, st_area_chart, st_scatter_chart, st_audio, st_video
- **ONLY interactivity** -> `st.*`: buttons, inputs, sliders, forms, selectbox, checkbox

### Export-Aware Widgets
When HTML export is enabled, native `st.*` widgets (charts, tables, etc.) are **invisible** in the exported HTML because they use Streamlit's protobuf/React pipeline.

Use the `stx.st_*` wrappers instead — they call the native widget AND inject a static HTML fallback (SVG chart, HTML table, etc.) into the export buffer:

```python
# BAD — invisible in export
st.line_chart(data)
st.dataframe(df)
st.graphviz_chart(dot)

# GOOD — visible in both live app AND export
stx.st_line_chart(data)
stx.st_dataframe(df)
stx.st_graphviz(dot)
```

For any widget not covered by the helpers, use `stx.st_export()`:
```python
with stx.st_export('<p>Static fallback for export</p>'):
    st.plotly_chart(fig)
```

Interactive widgets (`st.button`, `st.slider`, etc.) have no meaningful static representation and are expected to be absent from the export.

### Raw HTML (`st_html`)
When you need to render raw HTML (e.g. custom bar charts, decorative rules, embedded iframes), use `stx.st_html()` instead of `st.html()` or `components.html()`. It routes through the dual-rendering pipeline (live + export buffer) and auto-injects `font-family: Source Sans Pro` in iframes.

```python
# BAD — bypasses export pipeline
st.html('<hr style="border:none;height:3px;">')
import streamlit.components.v1 as components
components.html('<div>chart</div>', height=400)

# GOOD — goes through st_html (export-aware, auto font in iframes)
stx.st_html('<hr style="border:none;height:3px;">')
stx.st_html('<div>chart</div>', height=400)
stx.st_html('<div>long content</div>', height=600, scrolling=True)
```

## 6. Critical Layout Rules
1. **Inline text**: Multiple `st_write()` calls STACK VERTICALLY. For inline mixed-style text, use ONE `st_write()` with tuple arguments:
   ```python
   # WRONG — stacks vertically
   st_write(s.red, "Red")
   st_write(s.blue, "Blue")

   # CORRECT — flows inline
   st_write(s.Large, (s.red, "Red"), (s.blue, "Blue"))
   ```
2. **Link font size**: Links default to 12pt. Include font size in link style when surrounding text is larger.
3. **Dark mode**: Never hardcode black/white — let Streamlit handle Light/Dark mode.
4. **No raw HTML/CSS**: Never write inline CSS strings or HTML in Python code. Use Style composition.

### Grid Layout (`st_grid`)
```python
# st_grid(cols, grid_style, cell_styles) signature
# - cols: int (number of columns) or CSS string ("1fr 1fr 1fr")
# - grid_style: Style object for the entire grid (includes gap via CSS)
# - cell_styles: Style(s) for individual cells

# Gap between cells goes in grid_style, NOT as a parameter
gap_style = Style("gap:24px;", "grid_gap")
with st_grid(cols=2, grid_style=gap_style):
    # 2-column layout with 24px gap

# Common column patterns:
st_grid(cols=2)                                    # 2 equal columns
st_grid(cols="1fr 1fr 1fr")                       # 3 equal columns (CSS syntax)
st_grid(cols="auto 1fr")                          # First col: fit content, second: rest
st_grid(cols="repeat(auto-fill, minmax(200px, 1fr))")  # Responsive cards
```

### Responsive-First Grid Design (MANDATORY)
Content is designed for **variable-width screens** (laptop, tablet, projected). All multi-column layouts MUST use responsive CSS Grid patterns so columns stack vertically when the viewport is too narrow.

```python
# BAD — fixed columns, breaks on narrow screens
st_grid(cols=2)                       # Never wraps
st_grid(cols="2fr 3fr")              # Never wraps

# GOOD — responsive columns, auto-wrap below minmax threshold
st_grid(cols="repeat(auto-fit, minmax(350px, 1fr))")   # 2-col → 1-col
st_grid(cols="repeat(auto-fit, minmax(280px, 1fr))")   # 3-col → fewer
st_grid(cols="repeat(auto-fit, minmax(200px, 1fr))")   # Card grid

# Use project responsive presets (defined in custom/styles.py):
with st_grid(cols=s.project.containers.responsive_2col, grid_style=s.project.containers.gap_24):
    # columns auto-wrap below 350px min-width
```

**Rules:**
1. **Default to responsive** — Every `st_grid()` with 2+ columns MUST use `repeat(auto-fit, minmax(...))` or a responsive preset
2. **Fixed columns only for data tables** — Use `st_grid(cols=N)` only when rendering tabular data with a known column count
3. **Test narrow viewport** — Resize the browser to ~600px to verify stacking behavior
4. **Define responsive presets** in `custom/styles.py` — Reuse across blocks instead of repeating minmax strings

## 7. Block Architecture
Every block file MUST contain:
```python
class BlockStyles:
    """Local styles for this block only"""
    pass
bs = BlockStyles

def build():
    """Required entry point — renders the block content"""
    pass
```

## 8. Naming Conventions
- **Block files**: `bck_[description]_[suffix].py`
- **Image assets**: `[block_filename_no_ext]_image_[00index].[ext]`
- **Style names**: English-only, generic, descriptive (`title_giant_green`, `subtitle_blue_01`)
- **Style classes**: `BlockStyles` or `BStyles`, aliased as `bs = BlockStyles`
- **Variables**: `snake_case` | **Classes**: `PascalCase`

## 9. Style System

### Style Creation & Composition
- **New from CSS**: `Style("color:red;", "my_style")` — create style from CSS string
- **Copy existing**: `Style.create(existing_style, "new_id")` — copy with new ID
- **Compose**: `s.bold + s.Large + s.center_txt` — combine styles (returns Style)
- **Remove**: `style - s.bold` — subtract CSS properties
- **Grid styles**: `sg.create("A1:B3", style)` — apply styles to grid cells
- **Custom colors**: Define in `custom/styles.py`, inherit `StxStyles`
- **Theme overrides**: Define in `custom/themes.py` (dict of style_id → CSS)
- **Reuse**: Never duplicate identical style definitions. One generic style, reused everywhere.

### Common Patterns
```python
# Create container style with gradient
container = Style(
    "background:linear-gradient(135deg, rgba(40,44,52,0.9) 0%, rgba(30,33,40,0.9) 100%);"
    + "border-radius:12px;padding:24px;",
    "container_modern"
)

# Copy and modify text style
my_title = Style.create(s.Large + s.text.weights.bold_weight, "my_title")

# Grid with gap
grid_gap = Style("gap:24px;", "grid_with_gap")
with st_grid(cols=2, grid_style=grid_gap):
    # cells here
```

### Style Hierarchy
- `s.text.*` — text colors, sizes, weights, decorations, fonts, alignments
- `s.container.*` — sizes, bg_colors, borders, paddings, margins, layouts, flex
- `s.project.*` — project-specific custom styles (colors, titles)
- `s.visibility.*` — hidden, visible, invisible

### Text Sizes (reference)
- Titles: `GIANT`(196pt), `Giant`(128pt), `giant`(112pt), `Huge`(96pt), `huge`(80pt)
- Headers: `LARGE`(64pt), `Large`(48pt), `large`(32pt)
- Body: `big`(24pt), `medium`(16pt), `little`(12pt/default), `small`(8pt), `tiny`(4pt)
- Code: responsive via `--stx-code-size` (desktop 18pt, tablet 14pt, mobile 11pt)

### Code Block Rendering (`st_code`)
- Default font size is responsive via the CSS variable `--stx-code-size` (18pt desktop, 14pt tablet, 11pt mobile)
- Override with `font_size="14pt"` for specific sizes
- Use `wrap=True` for prose-like code (JSON, logs) where horizontal alignment doesn't matter
- Use `wrap=False` (default) for code where columns must align (tables, diffs, ASCII art)
- `show_code()` and `show_code_inline()` forward the `wrap` parameter to `st_code()`

### External File Loading (`file=` parameter)
- All `st_*` content-rendering functions accept a `file=` parameter for loading from external files
- `file=` is mutually exclusive with inline content (passing both raises `ValueError`)
- File paths are resolved via `resolve_static()` — relative paths search configured static source directories
- `resolve_content(content, file=, encoding=)` is the shared utility (in `streamtex/utils.py`)
- Supported functions: `st_code`, `st_mermaid`, `st_plantuml`, `st_tikz`, `st_graphviz`, `st_markdown`
- Example: `stx.st_mermaid(file="diagrams/flowchart.mmd", height=500)`

## 10. Running the App
```bash
# Single project
uv run streamlit run projects/<project_name>/book.py

# Manual projects (documentation/manuals/)
uv run streamlit run documentation/manuals/stx_manual_intro/book.py
uv run streamlit run documentation/manuals/stx_manual_advanced/book.py
uv run streamlit run documentation/manuals/stx_manuals_collection/book.py

# Multiple projects simultaneously (different ports)
./run-test-projects.sh --intro --advanced --collection
./run-test-projects.sh --all                  # Launch all 3 projects
```

## 11. Deployment
- **Docker**: `docker build --build-arg FOLDER=projects/<project_name> -t streamtex-app .`
- **Multiple on VM**: Run each on different port, load-balance with nginx/caddy
- **Hugging Face Spaces**: Push Docker image to HF Space via git remote
- **pip install**: `pip install -e .` for development (eliminates setup.py PATH hack)

## 12. Testing
```bash
# Unit tests (all)
uv run pytest tests/ -v

# Specific test file
uv run pytest tests/test_export.py -v

# Watch mode (requires pytest-watch)
uv run pytest-watch tests/
```

## 13. Block Registry Patterns

StreamTeX provides two registries for lazy-loading blocks.

### ProjectBlockRegistry — Single project (local blocks/)

Used in every project's `blocks/__init__.py` for local block discovery:

```python
# blocks/__init__.py
from pathlib import Path
from streamtex import ProjectBlockRegistry

registry = ProjectBlockRegistry(Path(__file__).parent)

def __getattr__(name: str):
    return registry.get(name)

def __dir__():
    return sorted(registry.list_blocks())
```

Features: `registry.list_blocks()`, `registry.get_stats()`, `registry.load_all()`,
manifest-based discovery, block type detection (atomic vs composite).

### LazyBlockRegistry — Multi-source (shared blocks)

Used in `book.py` to load blocks from external directories:

```python
# book.py
import streamtex as stx
from pathlib import Path

shared_path = str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "blocks")
shared_blocks = stx.LazyBlockRegistry([shared_path])

st_book([
    shared_blocks.bck_header,    # From stx_manuals_shared-blocks
    blocks.bck_content,          # From local blocks/
    shared_blocks.bck_footer,    # From stx_manuals_shared-blocks
])
```

Priority: first source directory in the list wins. Once loaded, blocks are cached.

### Composite Blocks — load_atomic_block()

Composite blocks group multiple atomic blocks (from `_atomic/` subfolder) into a single section.
Use `stx.load_atomic_block()` to load them:

```python
# blocks/bck_text_and_styling.py — Composite block
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

`load_atomic_block(name, __file__)` loads `_atomic/{name}.py` relative to the caller's directory.
Raises `BlockNotFoundError` if not found, `BlockImportError` on import failure.

### When to use which?

| Use Case | Registry / Function |
|----------|----------|
| Local blocks (blocks/) | `ProjectBlockRegistry` |
| Shared blocks from other dirs | `LazyBlockRegistry` |
| Atomic sub-blocks (_atomic/) | `load_atomic_block()` |
| Both in same project | One of each (see stx_manual_advanced) |

## 14. Hybrid Helper Patterns

Block helpers (`show_code`, `show_explanation`, `show_details`) support 3 usage modes.

**Important:** `show_explanation()` and `show_details()` render the body text via
`st_markdown()`, so standard Markdown formatting works: **bold**, *italic*, `code`,
lists, links, etc. The text is displayed at `StxStyles.big` font size with
`p { font-size: inherit; }` to ensure Streamlit's `<p>` elements inherit the
container size.

### Mode 1: Config Injection (Recommended)

```python
# blocks/helpers.py — inject project styles globally
from streamtex import BlockHelperConfig, set_block_helper_config
from custom.styles import Styles as s

class ProjectBlockHelperConfig(BlockHelperConfig):
    def get_code_style(self):
        return s.project.containers.code_box
    def get_explanation_style(self):
        return s.project.containers.info_box

set_block_helper_config(ProjectBlockHelperConfig())
```

All `show_code()` calls in the project automatically use the injected style.

### Mode 2: Standalone Functions

```python
from streamtex import show_code
show_code("print('hello')")                             # Uses injected config style
show_code("print('hello')", style=s)                    # Override with explicit style
show_code('{"key": "value"}', language="json", wrap=True)  # Wrapping for JSON
```

### Mode 3: OOP Inheritance

```python
from streamtex import BlockHelper

class ProjectBlockHelper(BlockHelper):
    def show_comparison(self, before, after):
        # Custom method unique to this project
        self.show_code(before, style=s.before_style)
        self.show_code(after, style=s.after_style)

helper = ProjectBlockHelper()
helper.show_comparison(old_code, new_code)
```

### When to use which mode?

| User Level | Mode | Complexity |
|------------|------|------------|
| Beginner | Standalone functions | Minimal |
| Intermediate | Config Injection (DI) | One-time setup |
| Advanced | OOP Inheritance | Full customization |

## 15. Multi-Source Block & Static Resolution

### Block resolution

`LazyBlockRegistry([path1, path2])` searches sources in order. First match wins.
Use this for override patterns: project-specific blocks take priority over shared ones.

### Static asset resolution

```python
import streamtex as stx
from pathlib import Path

stx.set_static_sources([
    str(Path(__file__).parent / "static"),          # Local (highest priority)
    str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "static"),  # Shared
])

# resolve_static("logo.png") searches each source in order
# st_image() calls resolve_static() internally
```

Priority: first directory containing the file wins. If not found, falls back to
Streamlit's built-in `app/static/images/` path.

## 16. Marker Navigation

### When to use markers

Use markers for slide-like or section-based navigation in long documents
and presentations. They provide keyboard shortcuts (PageDown/PageUp) and a
floating widget with prev/next buttons and a popup list of all waypoints.

### Recommended setup

The recommended approach is `auto_marker_on_toc=1` in MarkerConfig, which
automatically bridges level-1 TOC headings to markers — no manual `st_marker()` calls
needed for standard content.

```python
from streamtex import MarkerConfig, st_book, TOCConfig

toc = TOCConfig(
    sidebar_max_level=None,  # None = auto (paginated: 1, continuous: 2)
)
marker_config = MarkerConfig(
    auto_marker_on_toc=1,
    next_keys=["PageDown"],
    prev_keys=["PageUp"],
)
st_book([...], toc_config=toc, marker_config=marker_config)
```

### Per-heading overrides

Use `marker=False` on `st_write()` to exclude specific headings (appendices,
indexes). Use `marker=True` to force-include a heading even when auto is off.

### Manual markers

Call `st_marker("Label", visible=True)` for visible waypoints or
`st_marker("Label")` for invisible ones (scroll-only targets).

### Architecture

Three files collaborate:
- `marker.py` — MarkerConfig dataclass, MarkerRegistry singleton, st_marker(),
  inject_marker_navigation() (floating widget + JS)
- `book.py` — Lifecycle: reset_marker_registry() → render blocks →
  inject_marker_navigation(). In paginated mode, provides cross-page callbacks.
- `write.py` — _handle_toc() bridges TOC headings to markers based on
  auto_marker_on_toc and the per-heading marker= parameter.

## 17. Banner Configuration

### Overview

Navigation banners in paginated mode are configured via `BannerConfig`.
Three modes: `FULL` (default, prominent), `COMPACT` (slim), `HIDDEN` (no visual).

### Recommended setup

Always pass an explicit `banner=` parameter to `st_book()` in paginated projects:

```python
from streamtex import BannerConfig, st_book

st_book([...], paginate=True, banner=BannerConfig.full())
```

### Presets

```python
BannerConfig.full()              # Default — large, rounded, dividers
BannerConfig.full(color="navy")  # Full with custom colour
BannerConfig.compact()           # Slim, no dividers
BannerConfig.compact_gray()      # Compact with neutral gray
BannerConfig.hidden()            # No visual, keyboard/auto-scroll preserved
```

### Custom configuration

```python
BannerConfig(
    mode=BannerMode.COMPACT,
    color="#1a5276",
    text_color="#ecf0f1",
    padding="8px 20px",
    show_arrows=False,
)
```

Fields set to `None` use mode-specific auto values.
Explicit values always override auto defaults.

### Architecture

- `banner.py` — BannerMode enum, BannerConfig dataclass, _render_banner()
- `book.py` — Resolves banner config (banner > monties_color > banner_color),
  passes BannerConfig to _paginated_book(), calls _render_banner() for top/bottom banners.
