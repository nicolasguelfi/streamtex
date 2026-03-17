# StreamTeX Coding Standards

> **Single source of truth** for development guidelines.
> Referenced by both `CLAUDE.md` and `.cursor/rules/streamtex/development/RULE.md`.

## 1. The StreamTeX Philosophy
StreamTeX wraps Streamlit with a block-based architecture. Never manually write HTML or CSS strings in Python code.
- **BAD:** `st.markdown("<div style='color:red'>Text</div>", unsafe_allow_html=True)`
- **GOOD:** `stx.st_write(s.text.colors.red, "Text")`

## 2. Source of Truth
- **Syntax Reference:** `references/streamtex_cheatsheet_en.md`
- **Architecture Reference:** Any project's `book.py` (orchestrates blocks/). See `templates/template_project/` or `manuals/stx_manual_intro/` for illustration.
- **Manuals:** Intro (fundamentals), Advanced (features), Deploy (deployment), Developer (library internals)
- **Developer Guide:** `manuals/stx_manual_developer/` — repo structure, architecture, testing, CI/CD, release

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
- **AI image generation** -> `stx.*`: st_ai_image, st_ai_image_widget, generate_image (requires `streamtex[ai]`)
- **Presentation mode** -> `stx.*`: st_presentation_footer, add_presentation_options
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

### Fundamental rule: use the most specific `stx.*` component

For each type of content, always use the dedicated `stx.*` component when one exists.
It is **forbidden** to simulate a component with more generic functions (`st_write`, `st_html`, markdown).

| Content type | MUST use | NEVER simulate with |
|--------------|----------|---------------------|
| Lists / enumerations | `st_list()` + `l.item()` | `st_write("- item")`, bullets `•`/`‣` in text, `\n`-separated items |
| Grids / columns | `st_grid()` + `g.cell()` | Multiple `st.columns()`, HTML tables |
| Images | `st_image()` | `st.image()`, `st.markdown("![]()")` |
| Code blocks | `st_code()` | `st.code()`, markdown fenced blocks |
| Spacing | `st_space()`, `st_br()` | Empty `st_write("")`, `st.markdown("<br>")` |

### Lists — MANDATORY `st_list()` usage

Any enumeration of 2 or more items MUST use `st_list()`. Never simulate a list
with successive `st_write()` calls, markdown dashes, or unicode bullets.

```python
# BAD — simulated list (no proper indentation, no bullets, no consistent styling)
st_write(bs.body, "- First point")
st_write(bs.body, "- Second point")
st_write(bs.body, "- Third point")

# BAD — bullets in text (bypasses list rendering engine)
st_write(bs.body, "• First point\n• Second point\n• Third point")

# BAD — markdown list in st_write (no style control, no export support)
st_write(bs.body, "1. First\n2. Second\n3. Third")

# GOOD — proper styled list with correct rendering, export support, and style control
with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.unordered) as l:
    with l.item(): st_write(bs.body, "First point")
    with l.item(): st_write(bs.body, "Second point")
    with l.item(): st_write(bs.body, "Third point")

# GOOD — ordered list
with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.ordered) as l:
    with l.item(): st_write(bs.body, "Step one")
    with l.item(): st_write(bs.body, "Step two")
```

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

# Gap between cells — use the dedicated gap parameter or grid_style
with st_grid(cols=2, gap="24px"):
    # 2-column layout with 24px gap (using gap parameter)

# Alternative: gap via grid_style CSS
gap_style = Style("gap:24px;", "grid_gap")
with st_grid(cols=2, grid_style=gap_style):
    # 2-column layout with 24px gap (using grid_style)

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
- **Block files**: `bck_<descriptive_topic>.py` — never use numeric prefixes (`bck_01_`, `bck_02_`). Slide order is defined in `st_book([...])`, not by filename.
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
- Use `wrap=False` for code where columns must align (tables, diffs, ASCII art)
- Default `wrap=None` defers to the global toggle set by `add_wrap_all_option()` (called by `st_book()`), which defaults to `True`. Pass `wrap=False` explicitly when alignment matters.
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
# Single project (from project directory)
stx run                                       # auto-detects book.py
stx run --port 8510 --browser chrome          # custom port + browser

# Manual projects (from manual directory)
cd manuals/stx_manual_intro && stx run
cd manuals/stx_manual_advanced && stx run

# Multiple projects simultaneously (different ports)
./run-manuals.sh --intro --advanced --collection
./run-manuals.sh --all                        # Launch all manuals
```

## 11. Deployment
- **Docker**: `docker build --build-arg FOLDER=projects/<project_name> -t streamtex-app .`
- **Multiple on VM**: Run each on different port, load-balance with nginx/caddy
- **Hugging Face Spaces**: Push Docker image to HF Space via git remote
- **pip install**: `pip install -e .` for development (eliminates setup.py PATH hack)

## 12. Testing & Linting

### Running tests
```bash
uv run pytest tests/ -v              # All tests
uv run pytest tests/test_export.py -v  # Specific file
```

### Ruff configuration (MANDATORY for all projects)

Every StreamTeX project `pyproject.toml` MUST include:
```toml
[tool.ruff.lint]
ignore = ["F403", "F405", "E701", "E741"]
```

These rules are suppressed because they conflict with standard StreamTeX patterns:
- **F403/F405** — `from streamtex import *` is the standard import
- **E701** — `with l.item(): st_write("text")` one-liner list items
- **E741** — `as l` variable name in `with st_list(...) as l:`

### CI configuration (MANDATORY for projects with `[tool.uv.sources]`)

Projects with editable local sources MUST use `UV_NO_SOURCES=1` in CI:
```yaml
jobs:
  check:
    runs-on: ubuntu-latest
    env:
      UV_NO_SOURCES: 1    # Ignore [tool.uv.sources] — resolve from PyPI
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - run: uv sync              # NOT --frozen (lock file encodes local path)
      - run: uv run ruff check .
```

**Why:** `[tool.uv.sources]` points to a local path (e.g. `../../streamtex`) that
does not exist in CI. `UV_NO_SOURCES=1` tells uv to ignore it and resolve from PyPI.
`--frozen` fails because the lock file also encodes the local path.

### Pre-commit hooks (MANDATORY)

Every StreamTeX repo and project MUST have a `.pre-commit-config.yaml` with ruff:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.2
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

This auto-fixes lint issues (including import ordering I001) before each commit.
`--exit-non-zero-on-fix` aborts the commit when files are modified so you can review and re-stage.

**Setup:**
```bash
uv sync                       # Installs pre-commit (dev dep)
uv run pre-commit install     # Activates the git hook
```

**Workspace-wide install:**
```bash
stx update                     # Installs hooks in all repos + projects/
```

`stx project new` automatically generates `.pre-commit-config.yaml` and installs hooks.

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

**Important:** `show_explanation()`, `show_details()`, `show_code()`, `show_code_inline()`,
`st_write()` and `st_code()` apply `textwrap.dedent()` automatically — callers
do NOT need to wrap text in `textwrap.dedent()`.
The body text is rendered via `st_markdown()`, so standard Markdown formatting
works: **bold**, *italic*, `code`, lists, links, etc.

```python
# CORRECT — simple, no textwrap import needed
show_explanation("""\
    **st_write()** renders styled text.

    1. First argument is the style
    2. Second argument is the text
""")

# WRONG — redundant (still works, but unnecessary)
show_code("""\
    ...
"""))
```

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

### MarkerConfig fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `show_nav_ui` | `bool` | `True` | Show/hide the floating navigation widget |
| `auto_marker_on_toc` | `int \| bool` | `False` | Bridge TOC headings to markers (True=all, int N=up to level N) |
| `nav_position` | `str` | `"bottom-right"` | Widget position: `"bottom-right"` or `"bottom-center"` |
| `nav_label_chars` | `int` | `40` | Max characters for current marker label (0 to hide) |
| `popup_open` | `bool` | `False` | Initial state of the marker popup list |
| `next_keys` | `list[str]` | `["PageDown"]` | Keys to navigate forward (supports modifier syntax) |
| `prev_keys` | `list[str]` | `["PageUp"]` | Keys to navigate backward |
| `draggable` | `bool` | `False` | Allow dragging the widget anywhere (position in localStorage) |
| `collapsible` | `bool` | `False` | Show ⋮ button to collapse/expand (state in localStorage) |

### Per-heading overrides

Use `marker=False` on `st_write()` to exclude specific headings (appendices,
indexes). Use `marker=True` to force-include a heading even when auto is off.

### Manual markers

Call `st_marker("Label", visible=True)` for visible waypoints or
`st_marker("Label")` for invisible ones (scroll-only targets).
Use `st_marker("Label", hidden=True)` for navigation-only markers that
do not appear in the sidebar marker list or widget popup.

### Slide breaks (presentation mode)

Use `st_slide_break()` to separate presentation sections. It inserts a
styled horizontal rule + viewport-height spacer + hidden marker so that
PageDown stops between sections without polluting the sidebar.

The `SlideBreakMode` enum controls what is rendered: `FULL` (rule + spacer),
`RULE_ONLY`, `SPACER_ONLY`, `MARKER_ONLY`, or `HIDDEN`.

Customize globally via `set_slide_break_config(SlideBreakConfig(...))` in
the project's `helpers.py`, or per-call with the `config=` parameter.

Call `add_slide_break_options()` in `book.py` alongside `add_zoom_options()`
to add sidebar controls for enabling/disabling slide breaks, selecting the
mode, and adjusting spacer height. CSS variables (`--stx-break-space`,
`--stx-break-thickness`, `--stx-break-opacity`, `--stx-break-rule-display`,
`--stx-break-spacer-display`) control runtime display and sizing of
`st_slide_break()`.

### PDF export

Use `export_pdf()` to convert HTML export output to PDF via Playwright (Chromium headless).
Requires the optional `pdf` extra: `uv add "streamtex[pdf]"` + `playwright install chromium`.

Two modes via `PdfMode`:
- `CONTINUOUS` — slide breaks removed, content flows continuously
- `PAGINATED` — page break inserted at each slide break

CSS classes `.stx-slide-break-rule` and `.stx-slide-break-spacer` are targeted by
`@media print` rules injected by `inject_print_css()`.

#### PDF configuration in `st_book()`

Pass a `PdfConfig` to `st_book()` to set default PDF options for the sidebar UI:

```python
from streamtex import st_book, PdfConfig, PdfMode

st_book([...],
    pdf_config=PdfConfig(
        mode=PdfMode.PAGINATED,
        format="A4",
        landscape=True,
        margin_top="10mm",
        margin_bottom="10mm",
        margin_left="15mm",
        margin_right="15mm",
        print_background=True,
        scale=1.0,
        page_numbers=False,
    ),
)
```

All PdfConfig fields: `mode` (PdfMode), `format` ("A4"), `landscape` (True),
`margin_top/bottom/left/right` ("10mm"/"15mm"), `print_background` (True),
`scale` (1.0), `header_template`/`footer_template` (""), `page_numbers` (False),
`theme_bg` ("#fff"), `theme_text` ("#333").

When `export=True` (default), the sidebar shows a "Download as..." panel where the user can
adjust all PDF parameters before generating. The `pdf_config` values are used as defaults.

#### WYSIWYG export — Width % and Zoom %

The sidebar Width % and Zoom % controls are propagated to exports for WYSIWYG fidelity:
- **HTML export**: Width % sets `max-width` on `.streamtex-page`; Zoom % sets CSS `zoom`.
- **PDF export**: Width % is already in the HTML that Chromium renders. Zoom % is used as the
  default value for the PDF Scale slider (overridable by the user in the export panel).
- The export panel shows "Current view: Width X% · Zoom Y%" for transparency.

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

### BannerConfig fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `BannerMode` | `FULL` | `FULL`, `COMPACT`, or `HIDDEN` |
| `color` | `str` | `"rgba(211,47,47,0.8)"` | Background color |
| `text_color` | `str` | `"white"` | Text color |
| `font_size` | `str \| None` | `None` | Font size (auto if None) |
| `font_weight` | `str \| None` | `None` | Font weight (auto if None) |
| `padding` | `str \| None` | `None` | CSS padding (auto if None) |
| `border_radius` | `str \| None` | `None` | CSS border-radius (auto if None) |
| `show_title` | `bool` | `True` | Show block title in banner |
| `show_arrows` | `bool` | `True` | Show prev/next arrows |
| `show_dividers` | `bool \| None` | `None` | Show separators (auto per mode if None) |

Fields set to `None` use mode-specific auto values.
Explicit values always override auto defaults.

### Architecture

- `banner.py` — BannerMode enum, BannerConfig dataclass, _render_banner()
- `book.py` — Resolves banner config (banner > monties_color > banner_color),
  passes BannerConfig to _paginated_book(), calls _render_banner() for top/bottom banners.
