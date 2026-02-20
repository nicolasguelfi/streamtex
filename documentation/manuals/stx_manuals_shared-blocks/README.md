# Shared Course Blocks

This repository contains reusable blocks and assets for StreamTeX training courses.

## Blocks

- `bck_header_training.py` — Standard header for training courses
- `bck_footer_training.py` — Standard footer with credits
- `bck_welcome.py` — Welcome message
- `bck_style_basics.py` — Introduction to the styling system
- `bck_best_practices.py` — Code patterns and best practices

## Using Shared Blocks

### Option 1: LazyBlockRegistry (Recommended for Phase 1+)

```python
import streamtex as stx
from streamtex import st_book

# Load shared blocks
shared = stx.LazyBlockRegistry(["../stx_manuals_shared-blocks/blocks"])

# Use in st_book()
st_book([
    shared.bck_header_training,
    blocks.bck_my_content,
    shared.bck_best_practices,
    shared.bck_footer_training,
])
```

### Option 2: Direct Import (Python 3.10+)

```python
from pathlib import Path
import sys
import importlib.util

# Load shared blocks module
shared_path = Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "blocks"
sys.path.insert(0, str(shared_path))

import bck_header_training
import bck_footer_training
# ... etc

sys.path.pop(0)
```

## Static Assets

Place your shared images, videos, and other assets in:

- `static/images/` — Images and diagrams
- `static/videos/` — MP4, GIF files
- `static/sounds/` — Audio files
- `static/data/` — JSON, CSV, etc.

Access them via `resolve_static()`:

```python
import streamtex as stx

# Configure static sources
stx.set_static_sources(["static", "../stx_manuals_shared-blocks/static"])

# Resolve a file
logo_path = stx.resolve_static("images/logo.png")
```

## Styles

Reuse shared style palette:

```python
from custom.styles import SharedStyles

# Use shared colors
st_write(SharedStyles.colors.primary_blue, "Blue text")
st_write(SharedStyles.titles.section_title, "Section Header")
```

## Contributing

When adding new shared blocks:

1. Create `bck_<name>.py` with `BlockStyles` class and `build()` function
2. Keep the block independent (no hard dependencies on project-specific styles)
3. Add to this README with a brief description
4. Test that it can be imported and used standalone
