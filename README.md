# StreamTeX

**A block-based content framework for Streamlit** — build styled, structured web books with Python.

StreamTeX provides a modular "block" architecture on top of Streamlit, letting you compose rich
styled pages with CSS Grid layouts, inline mixed-style text, diagrams, LaTeX, bibliography,
navigation, and more — all without writing raw HTML or CSS.

## Installation

```bash
pip install streamtex
```

Optional: enable the live code inspector sidebar:

```bash
pip install streamtex[inspector]
```

## Quick Start

```python
import streamlit as st
import streamtex as sx
from streamtex.styles.core import Style

st.set_page_config(page_title="My Book", layout="wide")

style = Style("color: navy; font-size: 1.2em;", "my-style")
sx.st_write(style, "Hello StreamTeX!")
```

Run it:

```bash
streamlit run app.py
```

## Features

- **Styled text** — `st_write` with tuple support for inline mixed-style text
- **CSS Grid layouts** — `st_grid` with responsive columns
- **Block containers** — `st_block` / `st_span` context managers
- **Lists** — `st_list` with ul/ol, custom bullets, centered alignment
- **Images** — `st_image` with base64 encoding and MIME detection
- **Code blocks** — `st_code` with Pygments syntax highlighting
- **Diagrams** — Mermaid, PlantUML, TikZ with pan/zoom
- **LaTeX** — math formulas and full documents
- **Bibliography** — BibTeX/RIS/CSL-JSON import, citations, formatted references
- **Book orchestration** — `st_book` with paginated and continuous modes
- **Table of Contents** — auto-numbering and anchor navigation
- **Navigation markers** — slide-like PageUp/PageDown navigation
- **Collections** — multi-project hubs with TOML configuration
- **HTML export** — self-contained dual-rendering pipeline
- **Style composition** — `Style` objects with `+` / `-` operators
- **Zoom controls** — CSS-based width and zoom adjustments
- **Block inspector** — live code editor in sidebar (optional)
- **Block helpers** — DI-injectable helpers with 3 usage modes

## Documentation

### Online manuals (read & explore)

- [All manuals (hub)](https://streamtex.onrender.com)
- [Introduction](https://intro-manual-streamtex.onrender.com)
- [Advanced](https://advanced-manual-streamtex.onrender.com)
- [Deployment Guide](https://deploy-manual-streamtex.onrender.com)

### Examples (source code)

The manuals are also available as source code — clone and run them locally
to study the examples:

```bash
git clone https://github.com/nicolasguelfi/streamtex-manuals
cd streamtex-manuals
uv sync
uv run streamlit run stx_manual_intro/book.py
```

See [streamtex-manuals](https://github.com/nicolasguelfi/streamtex-manuals)
for the full list of example projects.

### Reference

- [Cheatsheet (EN)](https://github.com/nicolasguelfi/streamtex/blob/main/documentation/streamtex_cheatsheet_en.md)
- [Coding Standards](https://github.com/nicolasguelfi/streamtex/blob/main/documentation/coding_standards.md)

## Project Structure

A StreamTeX project follows this layout:

```
my-project/
├── .streamlit/
│   └── config.toml          # enableStaticServing = true
├── blocks/
│   ├── __init__.py           # Block registry
│   └── bck_intro.py          # Your blocks (build() function each)
├── static/
│   └── images/               # Static assets
├── custom/
│   └── styles.py             # Project-specific styles
└── book.py                   # Entry point with st_book()
```

## Requirements

- Python >= 3.10
- Streamlit >= 1.54.0

## License

[MIT](LICENSE) — Copyright (c) 2026 Nicolas Guelfi
