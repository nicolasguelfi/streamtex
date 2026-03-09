<p align="center">
  <img src="https://media.githubusercontent.com/media/nicolasguelfi/streamtex/main/documentation/images/logos/logo-stx-full.png" alt="StreamTeX" width="200">
</p>

<h1 align="center">StreamTeX</h1>

<p align="center">
  <a href="https://github.com/sponsors/nicolasguelfi">
    <img src="https://img.shields.io/badge/%E2%9D%A4%EF%B8%8F_Support_us!-Sponsor-ea4aaa?style=for-the-badge&logo=githubsponsors" alt="Support us!">
  </a>
</p>

[![PyPI version](https://img.shields.io/pypi/v/streamtex)](https://pypi.org/project/streamtex/)
[![Python](https://img.shields.io/pypi/pyversions/streamtex)](https://pypi.org/project/streamtex/)
[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-blue.svg)](https://github.com/nicolasguelfi/streamtex/blob/main/LICENSE)
[![CI](https://github.com/nicolasguelfi/streamtex/actions/workflows/ci.yml/badge.svg)](https://github.com/nicolasguelfi/streamtex/actions/workflows/ci.yml)
[![Works with Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-blueviolet)](https://claude.ai/claude-code)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-blue)](https://cursor.com)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink)](https://github.com/sponsors/nicolasguelfi)

**AI-powered content framework for Streamlit** — create presentations, courses,
and web-books with Claude or Cursor. No coding required.

> StreamTeX combines a modular block architecture with AI-powered workflows.
> Describe your project in natural language, and let Claude or Cursor build it —
> or use the Python API for full control.

## Getting Started

StreamTeX supports 4 installation levels. Pick the one that fits your needs.

### Quick Start (minimal, no workspace)

From zero to a running project in 3 commands:

```bash
uv tool install "streamtex[cli]" -U
stx project new my-project
cd my-project && uv sync && uv run streamlit run book.py
```

### Standard Setup (recommended)

Full workspace with rich templates, documentation, and Claude AI profiles:

```bash
uv tool install "streamtex[cli]" -U
mkdir streamtex-dev && cd streamtex-dev
stx workspace init .
stx workspace update
stx project new my-project --template project
cd projects/my-project
stx claude install project .
uv run streamlit run book.py
```

**Prerequisites**: Python 3.11+, git, [uv](https://docs.astral.sh/uv/).

### Zero-Code with Claude or Cursor

Install StreamTeX and a Claude AI profile, then let the AI build your project:

```bash
uv tool install "streamtex[cli]" -U
mkdir streamtex-dev && cd streamtex-dev
stx workspace init . && stx workspace update
stx project new my-project
cd projects/my-project
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

See the **[AI Guide](https://github.com/nicolasguelfi/streamtex/blob/main/AI_GUIDE.md)** for all commands, agents, and workflows.

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

### Manual Installation (without stx CLI)

```bash
pip install streamtex
git clone https://github.com/nicolasguelfi/streamtex-claude.git
mkdir my-project && cd my-project
python ../streamtex-claude/install.py project .
uv run streamlit run book.py
```

### Workspace Presets

The `stx workspace init` command supports 4 presets:

| Preset | Repos | Use case |
|--------|-------|----------|
| `basic` | none | Workspace only, upgrade later |
| `user` | streamtex-claude | + Claude AI profiles |
| `standard` (default) | streamtex-docs + streamtex-claude | + rich templates + local docs |
| `developer` | all 3 repos | + library source + editable install |

```bash
stx workspace init . --preset user       # Claude profiles only
stx workspace init .                     # standard (default)
stx workspace init . --preset developer  # full developer setup
```

Upgrade an existing workspace:

```bash
stx workspace upgrade developer
stx workspace update
```

### Optional Extras

StreamTeX uses optional dependency groups so you install only what you need:

```bash
uv add "streamtex[ai]"           # AI image generation (OpenAI + Google Imagen + fal.ai)
uv add "streamtex[ai-openai]"    # AI images — OpenAI only
uv add "streamtex[ai-google]"    # AI images — Google Imagen only
uv add "streamtex[ai-fal]"       # AI images — fal.ai only
uv add "streamtex[pdf]"          # PDF export via Playwright
uv add "streamtex[inspector]"    # Live code inspector sidebar
uv add "streamtex[cli]"          # stx CLI (already installed as a global tool above)
```

> See the **[AI Image Generation](https://github.com/nicolasguelfi/streamtex/blob/main/AI_GUIDE.md#ai-image-generation)** section in the AI Guide for configuration and usage.

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

See the **[AI Guide](https://github.com/nicolasguelfi/streamtex/blob/main/AI_GUIDE.md)** for the complete reference.

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
- **AI image generation** — `st_ai_image` / `st_ai_image_widget` with OpenAI, Google Imagen, fal.ai
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
- [AI & Claude](https://streamtex-ai.onrender.com)
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

- [AI Guide](https://github.com/nicolasguelfi/streamtex/blob/main/AI_GUIDE.md) — zero-code workflows with Claude/Cursor
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
# Install or upgrade the CLI as a global tool
uv tool install "streamtex[cli]" -U

# Or as a project dependency
uv add streamtex
```

Optional extras:

```bash
uv add "streamtex[cli]"          # stx CLI commands
uv add "streamtex[inspector]"    # Live code inspector sidebar
uv add "streamtex[ai]"           # AI image generation (OpenAI + Google Imagen + fal.ai)
uv add "streamtex[ai-openai]"    # AI images — OpenAI only
uv add "streamtex[ai-google]"    # AI images — Google Imagen only
uv add "streamtex[ai-fal]"       # AI images — fal.ai only
uv add "streamtex[pdf]"          # PDF export via Playwright
```

### Prerequisites

- Python >= 3.11
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

## Keeping Up to Date

### Update the CLI

The `stx` CLI is installed as a global tool with its own frozen copy of
the library. You must upgrade it explicitly after each release:

```bash
uv tool install "streamtex[cli]" -U
```

### Update your workspace

```bash
cd streamtex-dev/
stx workspace update         # pulls repos, syncs deps, updates profiles
```

Fine-grained control:
```bash
stx workspace update --skip-sync      # skip uv sync
stx workspace update --skip-profiles  # skip Claude profile update
```

### Update a standalone project (no workspace)

```bash
cd my-project/
uv add streamtex --upgrade   # update the library dependency
```

> Use `/stx-guide update` inside Claude Code for guided assistance.

## Contributing

See [CONTRIBUTING.md](https://github.com/nicolasguelfi/streamtex/blob/main/CONTRIBUTING.md) for guidelines on code, content,
and AI profile contributions.

## Support the Project

If StreamTeX is useful to you, consider [sponsoring the project](https://github.com/sponsors/nicolasguelfi) to help maintain and improve it.

## License

[BUSL-1.1](https://github.com/nicolasguelfi/streamtex/blob/main/LICENSE) — Copyright (c) 2026 Nicolas Guelfi
Converts to Apache 2.0 on 2030-11-29.
