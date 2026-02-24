# StreamTeX — Collections & Multi-Repo Architecture

> **Specification document** for two new features:
> 1. `st_collection()` — A course library / project collection layer — **IMPLEMENTED** ✓
> 2. `configure_sources()` — Multi-directory block and static asset resolution — **PLANNED** (not yet implemented; current library uses `set_static_sources()` / `get_static_sources()` / `resolve_static()` instead)
>
> These features are independent but complementary. A collection can contain multi-repo projects, and multi-repo projects can run standalone without a collection.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Multi-Repo Ecosystem](#2-multi-repo-ecosystem)
3. [Feature 1: configure_sources()](#3-feature-1-configure_sources)
4. [Feature 2: st_collection()](#4-feature-2-st_collection)
5. [Docker Deployment](#5-docker-deployment)
6. [Library Changes Summary](#6-library-changes-summary)
7. [Concurrency & Isolation](#7-concurrency--isolation)
8. [Implementation Plan](#8-implementation-plan)

---

## 1. Overview

### Design Principles

- **Total project independence** — A project works identically whether launched standalone or from a collection.
- **No symlinks required** — Multi-repo composition is declarative (configured in `book.py`), not physical (symlinks).
- **Backward compatibility** — Existing projects work without changes. New features are opt-in.
- **Unified namespaces** — `blocks.bck_name` works regardless of which source directory provides the block.
- **Local-first priority** — When the same file name exists in multiple sources, the first (local) source wins.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     st_collection()                             │
│  Collection layer — card grid, routing, project isolation       │
│  (Optional — projects work standalone without this)             │
└────────────┬──────────────────┬──────────────────┬──────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │  Project A   │   │  Project B   │   │  Project C   │
      │  book.py     │   │  book.py     │   │  book.py     │
      │  st_book()   │   │  st_book()   │   │  st_book()   │
      └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
             │                  │                  │
             └──────────┬───────┘──────────┬───────┘
                        ▼                  ▼
               ┌──────────────┐   ┌──────────────────┐
               │ Local blocks │   │ configure_sources │
               │ Local static │   │ Shared blocks     │
               └──────────────┘   │ Shared static     │
                                  └──────────────────┘
```

---

## 2. Multi-Repo Ecosystem

### Workspace Structure

Each component is an independent Git repository:

```
~/dev/
│
├── streamtex/                              # Repo Git: the StreamTeX library
│   ├── streamtex/                          # Python package
│   ├── documentation/
│   ├── tests/
│   └── pyproject.toml
│
├── shared-course-blocks/                   # Repo Git: shared blocks & assets
│   ├── blocks/
│   │   ├── bck_header_university.py
│   │   ├── bck_footer_credits.py
│   │   ├── bck_trainer_ng_profile.py
│   │   └── bck_break_screen.py
│   ├── custom/
│   │   └── university_styles.py
│   └── static/
│       └── images/
│           ├── logo_university.png
│           └── banner_footer.png
│
├── project-aiai18h/                        # Repo Git: individual project
│   ├── book.py
│   ├── setup.py
│   ├── blocks/
│   │   ├── __init__.py                     # v2 multi-source discovery
│   │   ├── bck_content_01.py               # Local block
│   │   └── bck_content_02.py               # Local block
│   ├── custom/
│   │   └── styles.py                       # Project-specific styles
│   ├── static/
│   │   └── images/
│   │       └── specific_diagram.png        # Project-specific asset
│   └── .streamlit/
│       └── config.toml
│
├── project-html-example/                   # Repo Git: another individual project
│   ├── book.py
│   ├── setup.py
│   ├── blocks/
│   │   ├── __init__.py
│   │   └── bck_showcase.py                 # Local block
│   ├── custom/
│   │   └── styles.py
│   └── .streamlit/
│       └── config.toml
│
└── collection-university-2025/             # Repo Git: collection
    ├── book.py                             # st_collection() entry point
    ├── setup.py
    ├── collection.toml                     # Collection metadata
    ├── custom/
    │   ├── styles.py                       # Collection home page styles ONLY
    │   └── themes.py
    ├── static/
    │   └── images/
    │       └── covers/                     # Project cover images
    │           ├── project-aiai18h.png
    │           └── project-html-example.png
    └── .streamlit/
        └── config.toml
```

### Key Properties

| Property | Guaranteed |
|---|---|
| Each repo is a standalone Git repository | Yes |
| A project runs standalone without a collection | Yes |
| A project runs standalone without shared-blocks | Yes (graceful fallback) |
| A collection groups projects without modifying them | Yes |
| Shared blocks work across all projects | Yes |
| No symlinks required | Yes |
| No duplication of shared code | Yes |

---

## 3. Feature 1: `configure_sources()`

### Purpose

Allow a project to declare multiple source directories for blocks and static assets.
The `blocks` namespace becomes a unified view across all declared directories.

### API

```python
import streamtex as stx

stx.configure_sources(
    blocks=[
        "blocks",                                # Local blocks (relative to book.py)
        "../../shared-course-blocks/blocks",     # Shared blocks
    ],
    static=[
        "static",                                # Local static assets
        "../../shared-course-blocks/static",     # Shared static assets
    ],
)
```

**Parameters:**

- `blocks` — List of directory paths containing `.py` block files. Relative to the project root (directory containing `book.py`). First entry has highest priority.
- `static` — List of directory paths containing static assets (images, texts, pdf, videos, etc.). Same resolution rules.

**Call order:** `configure_sources()` MUST be called BEFORE `import blocks`.

### Priority Rules

The order of the list defines priority. First source wins on name collision:

| File exists in... | `blocks.bck_foo` resolves to |
|---|---|
| Local `blocks/` only | Local version |
| Shared `blocks/` only | Shared version |
| Both | **Local version** (override) |

This enables **local overrides**: a project can customize a shared block by creating a local file with the same name.

### `blocks/__init__.py` v2

The template `blocks/__init__.py` is updated to support multi-source discovery while remaining 100% backward compatible:

```python
import os
import glob
import sys
import importlib
import importlib.util

# --- Determine block source directories ---
try:
    from streamtex import get_block_sources
    _sources = get_block_sources()
except (ImportError, AttributeError):
    _sources = []

if not _sources:
    # Backward compatible: current directory only (existing behavior)
    _sources = [os.path.dirname(os.path.abspath(__file__))]

# --- Discover and import blocks from all sources ---
_loaded = {}

for source_dir in _sources:
    if not os.path.isdir(source_dir):
        continue
    for filepath in sorted(glob.glob(os.path.join(source_dir, "*.py"))):
        if not os.path.isfile(filepath) or filepath.endswith("__init__.py"):
            continue
        name = os.path.basename(filepath)[:-3]
        if name in _loaded:
            continue  # First source wins

        spec = importlib.util.spec_from_file_location(
            f"{__name__}.{name}", filepath
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"{__name__}.{name}"] = mod
        spec.loader.exec_module(mod)
        _loaded[name] = mod
        globals()[name] = mod

__all__ = list(_loaded.keys())
```

**Key technique:** `importlib.util.spec_from_file_location()` imports modules by absolute file path, not via `sys.path`. This means:
- No `sys.path` manipulation needed
- No module name conflicts across sources
- Modules appear in the `blocks` namespace as `blocks.bck_name`

**Backward compatibility:** If `configure_sources()` was never called, `get_block_sources()` returns `[]`, and `__init__.py` falls back to globbing its own directory — identical to the current behavior.

### `stx.resolve_static()` — Static File Resolution

A new utility function to find static files across all configured sources:

```python
def resolve_static(relative_path):
    """Find a static file across all configured static source directories.

    Searches each static source in order. Returns the absolute path of the
    first match, or the original relative_path if no match is found.
    """
    for base in _static_sources:
        full = os.path.join(base, relative_path)
        if os.path.exists(full):
            return full
    return relative_path
```

**Usage in blocks:**

```python
import streamtex as stx

def build():
    # Instead of hardcoded path:
    data_path = stx.resolve_static("various/sample_data.json")
    with open(data_path) as f:
        data = json.load(f)
```

### `st_image()` Update

The `get_image_src()` function in `image.py` is updated to search through static sources for image resolution:

```python
def get_image_src(uri: str) -> str:
    if __is_url(uri):
        return uri
    elif __is_absolute_path(uri) or __is_relative_path(uri):
        # Existing logic unchanged: resolve and base64 encode
        file_path = uri if __is_absolute_path(uri) else os.path.join(os.getcwd(), uri)
        if os.path.exists(file_path):
            mime_type = __get_mime_type(file_path)
            encoded = __get_base64_encoded_image(file_path)
            if mime_type and encoded:
                return f"data:{mime_type};base64,{encoded}"
        return ""
    else:
        # Static path: try each configured static source
        for base in get_static_sources():
            full = os.path.join(base, "images", uri)
            if os.path.exists(full):
                mime_type = __get_mime_type(full)
                encoded = __get_base64_encoded_image(full)
                if mime_type and encoded:
                    return f"data:{mime_type};base64,{encoded}"
        # Fallback: Streamlit static serving URL prefix
        return f"{_static_image_base}/{uri}"
```

**Result:** `st_image(uri="logo_university.png")` works regardless of whether the image is in `static/images/` (local) or `shared-course-blocks/static/images/` (shared). No change needed in block code.

### Example: `book.py` of a Multi-Repo Project

```python
import streamlit as st
import setup
import streamtex as stx

# --- Multi-source configuration (BEFORE import blocks) ---
stx.configure_sources(
    blocks=[
        "blocks",                                  # Local blocks (priority 1)
        "../../shared-course-blocks/blocks",       # Shared blocks (priority 2)
    ],
    static=[
        "static",                                  # Local assets (priority 1)
        "../../shared-course-blocks/static",       # Shared assets (priority 2)
    ],
)

from streamtex import st_book, TOCConfig, MarkerConfig
import blocks
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts

st.set_page_config(page_title="AI AI 18h", layout="wide",
                   initial_sidebar_state="collapsed")
sts.theme = dark

toc = TOCConfig(numerate_titles=False, toc_position=0,
                title_style=s.project.titles.main_title + s.center_txt,
                content_style=s.large + s.text.colors.reset)

st_book([
    blocks.bck_header_university,       # from shared-course-blocks/blocks/
    blocks.bck_content_01,              # from blocks/ (local)
    blocks.bck_break_screen,            # from shared-course-blocks/blocks/
    blocks.bck_content_02,              # from blocks/ (local)
    blocks.bck_trainer_ng_profile,      # from shared-course-blocks/blocks/
    blocks.bck_footer_credits,          # from shared-course-blocks/blocks/
], toc_config=toc)
```

### Extreme Case: Project as Pure Curation

A project that contains NO local blocks — it is purely a selection and ordering of shared blocks:

```
project-minimal/
├── book.py             # configure_sources() + block selection
├── setup.py
├── blocks/
│   └── __init__.py     # v2 multi-source (no local .py files)
├── custom/
│   └── styles.py       # Project-specific styles
│   └── themes.py
└── .streamlit/
    └── config.toml
```

```python
# book.py — project-minimal
import streamlit as st
import setup
import streamtex as stx

stx.configure_sources(
    blocks=["blocks", "../../shared-course-blocks/blocks"],
    static=["../../shared-course-blocks/static"],  # No local static/
)

import blocks
from custom.styles import Styles as s

st.set_page_config(page_title="Minimal Course", layout="wide")

st_book([
    blocks.bck_header_university,
    blocks.bck_trainer_ng_profile,
    blocks.bck_break_screen,
    blocks.bck_footer_credits,
])
```

---

## 4. Feature 2: `st_collection()`

### Purpose

Display a card-grid home page that presents a library of StreamTeX projects. Clicking a card opens the selected project in a **new browser tab** for complete isolation.

### Architecture

A collection is a standard StreamTeX project with its own styles, using `st_collection()` instead of `st_book()`.

```
collection-university-2025/
├── book.py                              # Entry point: st_collection()
├── setup.py                             # PATH setup (same as any project)
├── collection.toml                      # Project metadata (titles, covers, order)
├── custom/
│   ├── styles.py                        # Home page styles ONLY
│   └── themes.py                        # Home page theme ONLY
├── static/
│   └── images/
│       └── covers/                      # Cover images for cards
│           ├── project-aiai18h.png
│           └── project-html-example.png
├── .streamlit/
│   └── config.toml
└── projects/                            # References to project directories
    (paths declared in collection.toml)
```

### `collection.toml` Format

```toml
[collection]
title = "University Course Library"
description = "A curated set of StreamTeX training courses"
cards_per_row = 3

[projects.project-aiai18h]
title = "AI & AI 18h"
description = "An 18-hour introduction to Artificial Intelligence"
cover = "static/images/covers/project-aiai18h.png"
path = "../../project-aiai18h"
order = 1

[projects.project-html-example]
title = "HTML Migration"
description = "Showcase: migrating an HTML page to StreamTeX"
cover = "static/images/covers/project-html-example.png"
path = "../../project-html-example"
order = 2
```

- **Key** (`project-aiai18h`): identifier used in URL routing
- **`path`**: relative path to the project directory (from the collection root)
- **`cover`**: relative path to the cover image (from the collection root)
- **`order`**: display order on the home page
- Only projects listed in the TOML are shown (no auto-discovery — intentional for curation control)

### `book.py` of a Collection

```python
import streamlit as st
import setup
from streamtex import st_collection, CollectionConfig
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts

sts.theme = dark

config = CollectionConfig.from_toml("collection.toml")

st_collection(
    config=config,
    home_styles=s,
)
```

### `CollectionConfig` Dataclass

```python
@dataclass
class CollectionConfig:
    title: str = "StreamTeX Collection"
    description: str = ""
    cards_per_row: int = 3
    projects: dict[str, ProjectMeta] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, path: str) -> "CollectionConfig":
        """Parse collection.toml. Uses tomllib (Python 3.11+ stdlib)."""
        ...

@dataclass
class ProjectMeta:
    title: str
    description: str = ""
    cover: str = ""
    path: str = ""
    order: int = 0
```

### Routing Mechanism

Routing uses `st.query_params` — a single URL parameter:

| URL | Behavior |
|---|---|
| `http://localhost:8501/` | Home page (card grid) |
| `http://localhost:8501/?project=project-aiai18h` | Run selected project |

### Home Page: `_show_home()`

1. Call `st.set_page_config(page_title=config.title, layout="wide")`
2. Load CSS, zoom options
3. Render collection title and description using `home_styles`
4. Render card grid with `st_grid(cols=config.cards_per_row)`
5. Each card: cover image + title + description
6. Card click opens `?project=key` in a **new browser tab** (`target="_blank"`)

Card click behavior:

```python
# Each card is an HTML link that opens a new tab
st.html(
    f'<a href="?project={key}" target="_blank" '
    f'style="text-decoration:none; color:inherit;">'
    f'  <div style="...">'
    f'    <img src="{cover_src}" ...>'
    f'    <h3>{title}</h3>'
    f'    <p>{description}</p>'
    f'  </div>'
    f'</a>'
)
```

### Why New Tab?

Opening each project in a new browser tab provides **complete isolation**:

| Resource | Same tab | New tab |
|---|---|---|
| `st.session_state` | Shared (conflicts) | **Isolated** (separate session) |
| `TOCRegistry` singleton | Would conflict | **Isolated** |
| `MarkerRegistry` singleton | Would conflict | **Isolated** |
| Sidebar content | Mixed | **Project-only** |
| `sys.modules` | Needs purging | Fresh per rerun |
| Return to collection | Needs "Home" button | Close tab or click "Home" link |

### Project Execution: `_run_project()`

When the URL contains `?project=project-aiai18h`:

```python
import threading

_project_lock = threading.Lock()

def _run_project(config, project_key):
    project_meta = config.projects[project_key]
    project_dir = os.path.abspath(project_meta.path)
    book_path = os.path.join(project_dir, "book.py")

    # 1. Page config for the project
    st.set_page_config(
        page_title=project_meta.title,
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 2. "Back to Library" button in sidebar
    with st.sidebar:
        base_url = _get_base_url()  # URL without ?project=...
        st.link_button("🏠 Back to Library", base_url)
        st.divider()

    # 3. Isolated module context
    with _project_lock:
        _purge_project_modules()
        sys.path.insert(0, project_dir)

    # 4. Patch st.set_page_config (already called above)
    original_spc = st.set_page_config
    st.set_page_config = lambda **kwargs: None

    # 5. Execute the project's book.py
    with open(book_path) as f:
        code = compile(f.read(), book_path, "exec")
        exec(code, {
            "__name__": "__main__",
            "__file__": book_path,
            "__builtins__": __builtins__,
        })

    # 6. Restore
    st.set_page_config = original_spc
    sys.path.remove(project_dir)
```

#### Module Purge

```python
def _purge_project_modules():
    """Remove project-specific modules from sys.modules cache."""
    for name in list(sys.modules):
        if (name in ("blocks", "custom", "setup")
                or name.startswith(("blocks.", "custom."))):
            del sys.modules[name]
```

#### Thread Safety

The `_project_lock` (a `threading.Lock()`) protects the critical section:
purge → `sys.path` insert → module imports (triggered by the project's `book.py` exec).

Once modules are imported and referenced, the lock is released. The rendering phase
(`st_book()` calling `module.build()`) runs without the lock — references to imported
modules remain valid even if another thread purges `sys.modules` later.

### User Flow

```
User opens http://localhost:8501/
    │
    ▼
st_collection() → no ?project param → _show_home()
    │
    ▼
Home page: "University Course Library"
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ AI & AI  │  │   HTML   │  │  Other   │
    │  18h     │  │ Migration│  │  Course  │
    │ [cover]  │  │ [cover]  │  │ [cover]  │
    └────┬─────┘  └──────────┘  └──────────┘
         │
         │ Click → new browser tab
         ▼
http://localhost:8501/?project=project-aiai18h (NEW TAB)
    │
    ▼
st_collection() → ?project=project-aiai18h → _run_project()
    │
    ▼
Sidebar:
    ┌──────────────────────┐
    │ 🏠 Back to Library   │   ← opens collection URL
    │ ──────────────────── │
    │ View: Paginated      │   ← from st_book()
    │ Zoom: Fit            │   ← from st_book()
    │ Table of Contents    │   ← from st_book()
    │   1. Section A       │
    │   2. Section B       │
    └──────────────────────┘
    │
    ▼
Project renders exactly as if launched standalone.
User navigates normally (pagination, TOC, markers).
    │
    │ Close tab → back to collection (still open in original tab)
    │ OR click "🏠 Back to Library" → navigates to collection URL
    ▼
```

### 5 Tabs Simultaneously

A user can have 1 collection tab + 4 project tabs open simultaneously:

| Aspect | Safe? | Mechanism |
|---|---|---|
| `st.session_state` per tab | Yes | Each tab = separate WebSocket session |
| `TOCRegistry` per tab | Yes | Reset at each `st_book()` call, per session |
| `MarkerRegistry` per tab | Yes | Same as TOC |
| `sys.modules` shared across tabs | Yes | `threading.Lock()` on purge/import sequence |
| `sys.path` shared across tabs | Yes | Protected by same lock |

---

## 5. Docker Deployment

### Single Project (unchanged)

```bash
docker build --build-arg FOLDER=project-aiai18h -t my-course .
```

The existing `Dockerfile` works for standalone projects without multi-repo sources.

### Multi-Repo Project

A project that uses `configure_sources()` with paths outside its own directory needs a deploy script to gather all sources:

```bash
#!/bin/bash
# deploy.sh — Flatten multi-repo sources for Docker build
set -e
DEST=$(mktemp -d)
PROJ_NAME=$(basename "$PWD")

# Copy project
rsync -a --exclude='.git' --exclude='__pycache__' . "$DEST/$PROJ_NAME/"

# Copy shared sources (read from configure_sources paths)
rsync -a --exclude='.git' ../../shared-course-blocks/ "$DEST/shared-course-blocks/"

# Copy streamtex library
rsync -a --exclude='.git' ../../streamtex/ "$DEST/streamtex/"

# Build
docker build --build-arg FOLDER="$PROJ_NAME" -t "$PROJ_NAME" "$DEST/"
rm -rf "$DEST"
```

The `configure_sources()` paths must be valid inside the Docker image. Since `rsync` preserves the relative directory structure, `../../shared-course-blocks/blocks` resolves correctly.

### Collection

```bash
#!/bin/bash
# deploy_collection.sh — Flatten collection + all projects for Docker
set -e
DEST=$(mktemp -d)

# Copy collection
rsync -a --exclude='.git' . "$DEST/collection/"

# Copy each project referenced in collection.toml
# (paths are relative, e.g., ../../project-aiai18h)
rsync -a --exclude='.git' ../../project-aiai18h/ "$DEST/project-aiai18h/"
rsync -a --exclude='.git' ../../project-html-example/ "$DEST/project-html-example/"

# Copy shared blocks (used by projects)
rsync -a --exclude='.git' ../../shared-course-blocks/ "$DEST/shared-course-blocks/"

# Copy streamtex
rsync -a --exclude='.git' ../../streamtex/ "$DEST/streamtex/"

docker build --build-arg FOLDER="collection" -t my-collection "$DEST/"
rm -rf "$DEST"
```

### Dual Deployment Guarantee

| Deployment | Command | Works? |
|---|---|---|
| Standalone project (no shared sources) | `docker build --build-arg FOLDER=project -t app .` | Yes (existing Dockerfile) |
| Standalone project (with shared sources) | `./deploy.sh` | Yes (gathers sources) |
| Collection | `./deploy_collection.sh` | Yes (gathers everything) |

---

## 6. Library Changes Summary

### New Files

| File | Description |
|---|---|
| `streamtex/collection.py` | `st_collection()`, `CollectionConfig`, `ProjectMeta`, `_show_home()`, `_run_project()`, `_purge_project_modules()` |

### Modified Files

| File | Change | Scope |
|---|---|---|
| `streamtex/__init__.py` | Add `configure_sources()`, `get_block_sources()`, `get_static_sources()`, `resolve_static()`, export `st_collection`, `CollectionConfig` | Small — new functions only |
| `streamtex/image.py` | `get_image_src()`: search static sources before Streamlit fallback | Small — 10 lines in one function |
| `streamtex/write.py` | Add optional `target` parameter for links (`target="_blank"`) | Minimal — 1 parameter |
| `streamtex/image.py` | Add optional `target` parameter for clickable images | Minimal — 1 parameter |
| `documentation/template_project/blocks/__init__.py` | v2 multi-source discovery (backward compatible) | Moderate — new logic, same interface |

### Unchanged Files

`book.py`, `toc.py`, `marker.py`, `zoom.py`, `export.py`, `grid.py`, `container.py`, `list.py`, `overlay.py`, `space.py`, `code.py`, `styles/`, `enums.py`, `utils.py`.

### Backward Compatibility

| Scenario | Behavior |
|---|---|
| Existing project, no `configure_sources()` | Identical to current behavior |
| Existing project, old `blocks/__init__.py` | Works (old `__init__.py` ignores missing config) |
| Existing project, new `blocks/__init__.py` v2 | Works (falls back to single-directory glob) |
| New project with `configure_sources()` | Multi-source discovery active |

---

## 7. Concurrency & Isolation

### Session Isolation (Collection Mode)

Each browser tab creates a separate Streamlit WebSocket session:

```
Tab 1 (Collection Home)  ─── Session A ─── st.session_state A
Tab 2 (Project A)         ─── Session B ─── st.session_state B
Tab 3 (Project B)         ─── Session C ─── st.session_state C
Tab 4 (Project C)         ─── Session D ─── st.session_state D
```

Sessions are fully isolated for: `session_state`, sidebar, TOC, markers, zoom, pagination.

### Process-Level Shared Resources

All sessions share one Python process. Resources requiring protection:

| Resource | Risk | Mitigation |
|---|---|---|
| `sys.modules` | Concurrent import/purge of `blocks`, `custom` | `threading.Lock()` around purge + import |
| `sys.path` | Concurrent modification | Same lock |
| Global variables in `streamtex` (`_block_sources`, `_static_sources`) | Concurrent `configure_sources()` calls | Same lock covers this (called during project exec) |

### Lock Scope

```
_project_lock acquired
    │
    ├── _purge_project_modules()     # Clear blocks, custom from sys.modules
    ├── sys.path.insert(0, ...)      # Add project dir
    ├── exec(book.py)                # Triggers:
    │   ├── configure_sources(...)   #   Sets _block_sources, _static_sources
    │   ├── import blocks            #   __init__.py loads all block modules
    │   ├── import custom            #   Loads project styles
    │   └── st_book(...)             #   Renders everything (long operation)
    │
_project_lock released
```

Note: `st_book()` runs under the lock because it's inside the `exec()` of `book.py`. This means only one project renders at a time. In practice, Streamlit already serializes session reruns per process, so this adds negligible latency.

---

## 8. Implementation Plan

### Phase 1 — `configure_sources()` (Foundation)

**Deliverables:**
- `configure_sources()`, `get_block_sources()`, `get_static_sources()`, `resolve_static()` in `streamtex/__init__.py`
- Updated `get_image_src()` in `streamtex/image.py`
- New `blocks/__init__.py` v2 in `documentation/template_project/`
- Unit tests

**Validation:**
- Existing test project runs unchanged
- A test project with multi-source config loads blocks from two directories

### Phase 2 — `st_collection()` (Collection Layer)

**Deliverables:**
- `streamtex/collection.py` with `st_collection()`, `CollectionConfig`, routing, home page, project execution
- `target` parameter in `st_write()` and `st_image()`
- `documentation/template_collection/` starter template

**Validation:**
- Collection home page displays cards
- Clicking a card opens a project in a new tab
- Project renders identically to standalone mode
- "Back to Library" button works
- 3+ tabs open simultaneously without conflicts

### Phase 3 — Deploy & Polish

**Deliverables:**
- `deploy.sh` template for multi-repo Docker builds
- `deploy_collection.sh` template for collection Docker builds
- Documentation in `coding_standards.md`, `README.md`, `CLAUDE.md`
- Card hover effects, search/filter on home page (optional)

---

*Document version: 1.0 — February 2026*
