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
- **ONLY interactivity** -> `st.*`: buttons, inputs, sliders, media players, dataframes

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
- **Compose**: `s.bold + s.Large + s.center_txt`
- **Remove**: `style - s.bold`
- **Factory**: `Style.create(existing_style, "new_id")`
- **Grid styles**: `sg.create("A1:B3", style)`
- **Custom colors**: Define in `custom/styles.py`
- **Theme overrides**: Define in `custom/themes.py`
- **Reuse**: Never duplicate identical style definitions. One generic style, reused everywhere.

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
uv run streamlit run projects/<project_name>/book.py
```

To run multiple projects simultaneously, specify a different port (default is 8501):
```bash
uv run streamlit run projects/<project_name>/book.py --server.port 8502
```

## 11. Deployment
- **Docker**: `docker build -t streamtex-app . && docker run -p 8501:8501 streamtex-app`
- **Configurable**: `docker build --build-arg FOLDER=project_name -t streamtex-app .`
- **pip install**: `pip install -e .` for development (eliminates setup.py PATH hack)

## 12. Testing
```bash
pytest tests/          # Run all tests
pytest tests/ -v       # Verbose output
```
