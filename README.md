# StreamTeX

[![PyPI version](https://img.shields.io/pypi/v/streamtex)](https://pypi.org/project/streamtex/)
[![Python](https://img.shields.io/pypi/pyversions/streamtex)](https://pypi.org/project/streamtex/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/nicolasguelfi/streamtex/actions/workflows/ci.yml/badge.svg)](https://github.com/nicolasguelfi/streamtex/actions/workflows/ci.yml)
[![Works with Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-blueviolet)](https://claude.ai/claude-code)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-blue)](https://cursor.com)

**AI-powered content framework for Streamlit** — create presentations, courses,
and web-books with Claude or Cursor. No coding required.

> StreamTeX combines a modular block architecture with AI-powered workflows.
> Describe your project in natural language, and let Claude or Cursor build it —
> or use the Python API for full control.

## Three Ways to Use StreamTeX

### Quick Start with the CLI (recommended)

From zero to a running project in 5 commands:

```bash
# 1. Install the CLI
uv tool install streamtex[cli]

# 2. Create and initialize a workspace
mkdir streamtex-dev && cd streamtex-dev
stx workspace init .
stx workspace clone       # clones streamtex, streamtex-docs, streamtex-claude
stx workspace link        # configures editable installs

# 3. Create a project from the rich template
stx project new mon-projet --template project

# 4. Run it
cd projects/stx-mon-projet
uv run streamlit run book.py
```

**Prerequisites**: Python 3.10+, git, [uv](https://docs.astral.sh/uv/).

### Zero-Code with Claude or Cursor

Install StreamTeX and a Claude AI profile, then let the AI build your project:

```bash
uv tool install streamtex[cli]
mkdir streamtex-dev && cd streamtex-dev
stx workspace init . && stx workspace clone && stx workspace link
stx project new mon-projet
cd projects/stx-mon-projet
stx claude install project .
```

Open in Claude Code or Cursor, then use slash commands:

```
/project:project-init
> "Create a Docker course with 12 slides, dark theme,
>  table of contents and page navigation"
```

The AI agent designs the project structure, proposes it for your approval,
and generates all files — blocks, styles, book.py — ready to run:

```bash
uv run streamlit run book.py
```

See the **[AI Guide](AI_GUIDE.md)** for all commands, agents, and workflows.

### Code-First with Python

```python
import streamlit as st
import streamtex as sx
from streamtex.styles.core import Style

st.set_page_config(page_title="My Book", layout="wide")

style = Style("color: navy; font-size: 1.2em;", "my-style")
sx.st_write(style, "Hello StreamTeX!")
```

```bash
uv run streamlit run app.py
```

## AI-Powered Features

StreamTeX ships with **22 slash commands**, **4 specialized agents**,
and **10 block templates** for AI-assisted development.

### Project Creation & Customization

| Command | What it does |
|---------|-------------|
| `/project:project-init` | Create a complete project from a natural-language description |
| `/project:project-customize` | Change theme, typography, navigation without editing code |
| `/project:course-generate` | Generate `book.py` structure from a CSV block list |
| `/project:collection-new` | Create a multi-project hub |

### Design & Content

| Command | What it does |
|---------|-------------|
| `/designer:slide-new` | Create slides from descriptions |
| `/designer:slide-audit` | Validate design rules (font sizes, line lengths, spacing) |
| `/designer:slide-fix` | Auto-fix design violations |
| `/designer:style-audit` | Check styles for consistency |

### Migration

| Command | What it does |
|---------|-------------|
| `/migration:html-migrate` | Convert HTML (Google Docs) to StreamTeX blocks |
| `/migration:html-convert-batch` | Batch conversion of multiple files |
| `/migration:conversion-audit` | Audit conversion quality |

### AI Agents

| Agent | Role |
|-------|------|
| **Project Architect** | Designs project structure from natural language |
| **Slide Designer** | Creates pedagogically structured, polished slides |
| **Slide Reviewer** | Reviews and validates completed slides |
| **Presentation Designer** | Specialist for live projection (large fonts, minimal text) |

See the **[AI Guide](AI_GUIDE.md)** for the complete reference.

## Claude & Cursor Integration

StreamTeX provides installable AI profiles via
[streamtex-claude](https://github.com/nicolasguelfi/streamtex-claude):

| Profile | Audience | Commands | Agents |
|---------|----------|:--------:|:------:|
| **project** | Content creators | 19 | 3 |
| **presentation** | Live presenters | +3 | +1 |
| **documentation** | Manual authors | 10 | 2 |
| **library** | Library developers | 3 | — |

Install a profile:

```bash
stx claude install project ./my-project
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
- [Introduction](https://streamtex-intro.onrender.com)
- [Advanced](https://streamtex-advanced.onrender.com)
- [Deployment Guide](https://streamtex-deploy.onrender.com)
- [Developer Guide](https://streamtex-developer.onrender.com)

### Examples (source code)

The manuals are also available as source code — clone and run them locally
to study the examples:

```bash
git clone https://github.com/nicolasguelfi/streamtex-docs
cd streamtex-docs
uv sync
uv run streamlit run manuals/stx_manual_intro/book.py
```

See [streamtex-docs](https://github.com/nicolasguelfi/streamtex-docs)
for the full list of example projects.

### Reference

- [AI Guide](AI_GUIDE.md) — zero-code workflows with Claude/Cursor
- [Cheatsheet (EN)](https://github.com/nicolasguelfi/streamtex/blob/main/.claude/references/streamtex_cheatsheet_en.md)
- [Coding Standards](https://github.com/nicolasguelfi/streamtex/blob/main/.claude/references/coding_standards.md)

## Project Structure

A StreamTeX project follows this layout:

```
my-project/
├── .claude/                     # AI profiles (commands, skills, agents)
├── .streamlit/
│   └── config.toml              # enableStaticServing = true
├── blocks/
│   ├── __init__.py              # Block registry
│   └── bck_intro.py             # Your blocks (build() function each)
├── static/
│   └── images/                  # Static assets
├── custom/
│   └── styles.py                # Project-specific styles
└── book.py                      # Entry point with st_book()
```

## Installation

```bash
# Recommended: install the CLI as a global tool
uv tool install streamtex[cli]

# Or as a project dependency
uv add streamtex
```

Optional extras:

```bash
uv add streamtex[inspector]    # Live code inspector sidebar
uv add streamtex[cli]          # stx CLI commands
```

### Prerequisites

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- git

### Project Configuration

StreamTeX projects using `from streamtex import *` require this ruff config
in `pyproject.toml` (automatically generated by `stx project new`):

```toml
[tool.ruff.lint]
ignore = ["F403", "F405", "E701", "E741"]
```

If your project uses `[tool.uv.sources]` for editable installs, set
`UV_NO_SOURCES=1` in CI environments so uv resolves from PyPI instead
of local paths.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code, content,
and AI profile contributions.

## License

[MIT](LICENSE) — Copyright (c) 2026 Nicolas Guelfi
