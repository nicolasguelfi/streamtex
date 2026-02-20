# StreamTeX Coding Standards

> **Single source of truth** for development guidelines.
> Referenced by both `CLAUDE.md` and `.cursor/rules/streamtex/development/RULE.md`.

## 1. The StreamTeX Philosophy
StreamTeX wraps Streamlit with a block-based architecture. Never manually write HTML or CSS strings in Python code.
- **BAD:** `st.markdown("<div style='color:red'>Text</div>", unsafe_allow_html=True)`
- **GOOD:** `sx.st_write(s.text.colors.red, "Text")`

## 2. Source of Truth
- **Syntax Reference:** `documentation/streamtex_cheatsheet_en.md`
- **Architecture Reference:** Any project's `book.py` (orchestrates blocks/). See `tests/test_project/` or `documentation/template_project/` for illustration.

## 3. Project Structure
```
project_name/
  book.py                  # Entry point (imports setup, calls st_book())
  setup.py                 # PATH setup (adds parent dir to sys.path)
  blocks/                  # Content modules
    __init__.py            # Dynamic import via importlib
    bck_*.py               # Each block has a build() function
  custom/
    styles.py              # Project-specific styles (inherits StreamTeX_Styles)
    themes.py              # Theme overrides (dict)
  static/images/           # Image assets
  .streamlit/config.toml   # MUST have enableStaticServing = true
```

## 4. Mandatory Imports

### Block Files (`blocks/bck_*.py`)
```python
import streamlit as st
from streamtex import *
import streamtex as sx
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
- **ALL layout and content** -> `sx.*`: st_write, st_image, st_grid, st_list, st_block, st_span, st_space, st_br, st_overlay
- **Data visualization (export-aware)** -> `sx.*`: st_dataframe, st_table, st_metric, st_json, st_graphviz, st_line_chart, st_bar_chart, st_area_chart, st_scatter_chart, st_audio, st_video
- **ONLY interactivity** -> `st.*`: buttons, inputs, sliders, forms, selectbox, checkbox

### Export-Aware Widgets
When HTML export is enabled, native `st.*` widgets (charts, tables, etc.) are **invisible** in the exported HTML because they use Streamlit's protobuf/React pipeline.

Use the `sx.st_*` wrappers instead — they call the native widget AND inject a static HTML fallback (SVG chart, HTML table, etc.) into the export buffer:

```python
# BAD — invisible in export
st.line_chart(data)
st.dataframe(df)
st.graphviz_chart(dot)

# GOOD — visible in both live app AND export
sx.st_line_chart(data)
sx.st_dataframe(df)
sx.st_graphviz(dot)
```

For any widget not covered by the helpers, use `sx.st_export()`:
```python
with sx.st_export('<p>Static fallback for export</p>'):
    st.plotly_chart(fig)
```

Interactive widgets (`st.button`, `st.slider`, etc.) have no meaningful static representation and are expected to be absent from the export.

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
- **Custom colors**: Define in `custom/styles.py`, inherit `StreamTeX_Styles`
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

## 10. Running the App
```bash
# Single project
uv run streamlit run projects/<project_name>/book.py

# Test projects
uv run streamlit run tests/test_project_intro/book.py
uv run streamlit run tests/test_project_advanced/book.py
uv run streamlit run tests/test_collection/book.py

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
import streamtex as sx
from pathlib import Path

shared_path = str(Path(__file__).parent.parent / "shared-blocks" / "blocks")
shared_blocks = sx.LazyBlockRegistry([shared_path])

st_book([
    shared_blocks.bck_header,    # From shared-blocks
    blocks.bck_content,          # From local blocks/
    shared_blocks.bck_footer,    # From shared-blocks
])
```

Priority: first source directory in the list wins. Once loaded, blocks are cached.

### When to use which?

| Use Case | Registry |
|----------|----------|
| Local blocks (blocks/) | `ProjectBlockRegistry` |
| Shared blocks from other dirs | `LazyBlockRegistry` |
| Both in same project | One of each (see test_project_advanced) |

## 14. Hybrid Helper Patterns

Block helpers (`show_code`, `show_explanation`, `show_details`) support 3 usage modes.

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
show_code("print('hello')")           # Uses injected config style
show_code("print('hello')", style=s)  # Override with explicit style
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
import streamtex as sx
from pathlib import Path

sx.set_static_sources([
    str(Path(__file__).parent / "static"),          # Local (highest priority)
    str(Path(__file__).parent.parent / "shared-blocks" / "static"),  # Shared
])

# resolve_static("logo.png") searches each source in order
# st_image() calls resolve_static() internally
```

Priority: first directory containing the file wins. If not found, falls back to
Streamlit's built-in `app/static/images/` path.
