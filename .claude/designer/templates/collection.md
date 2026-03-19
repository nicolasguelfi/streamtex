# Template: collection

StreamTeX collection hub — a multi-project aggregator.

## Defaults

| Setting | Value |
|---------|-------|
| Type | collection |
| Audience | screen |
| Theme | dark |
| Pagination | no |
| TOC | `NumberingMode.SIDEBAR_ONLY`, `sidebar_max_level=2` |
| Sidebar | `initial_sidebar_state="expanded"` |
| Banner | no |
| Marker | no |
| Body font | `s.large` (32pt) |
| Title font | `s.huge` (80pt) |

## Structure

A collection is different from a standard project:
- Uses `st_collection()` instead of `st_book()`
- Has a `collection.toml` configuration file
- Has a home page block (`bck_home.py`) with project cards
- Sub-projects run on separate ports

## Required files

```
[collection_name]/
  book.py                 # st_collection() entry point
  collection.toml         # Collection configuration
  blocks/
    __init__.py            # ProjectBlockRegistry
    helpers.py             # Block helper config
    bck_home.py            # Home page with project cards
  custom/
    styles.py              # Collection styles
    themes.py              # Theme overrides
  static/
    images/
      covers/              # Project cover images
  .streamlit/
    config.toml            # Streamlit config
```

## book.py pattern

```python
from streamtex import st_collection, CollectionConfig

config = CollectionConfig.from_toml("collection.toml")
st_collection(config=config, home_styles=s)
```

## collection.toml pattern

```toml
[collection]
title = "My Collection"
description = "Collection of StreamTeX projects"

[[projects]]
name = "Project 1"
description = "Description of project 1"
port = 8502
path = "../project-1"
cover = "static/images/covers/project1.png"
```

## Reference files

- `streamtex-docs/templates/template_collection/` — canonical template
- `streamtex-docs/manuals/stx_manuals_collection/` — working example
