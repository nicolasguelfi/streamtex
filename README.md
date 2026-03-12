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
[![Best on Chrome](https://img.shields.io/badge/Best%20on-Chrome-4285F4?logo=googlechrome&logoColor=white)](https://www.google.com/chrome/)

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
cd my-project && uv sync && stx run
```

### Standard Setup (recommended)

Full workspace with rich templates, documentation, and Claude AI profiles:

```bash
uv tool install "streamtex[cli]" -U
mkdir streamtex-dev && cd streamtex-dev
stx install
stx update
stx project new my-project --template project   # CLI templates: project, collection, slides
cd projects/my-project
stx claude install project .
stx run
```

### Full Setup (all optional features)

Everything above, plus AI image generation, PDF export, and live inspector:

```bash
uv tool install "streamtex[cli]" -U
mkdir streamtex-dev && cd streamtex-dev
stx install --preset power --project my-project --template project
stx update
cd projects/my-project
stx run
```

The `power` preset automatically installs PDF export, AI image generation, and the live
inspector into your project. To add Playwright for PDF export, run:

```bash
uv run playwright install chromium
```

Each `uv add` installs optional features into the **current project's environment**.
Pick only what you need — or install individual AI providers:

```bash
uv add "streamtex[ai-openai]"    # OpenAI only
uv add "streamtex[ai-google]"    # Google Imagen only
uv add "streamtex[ai-fal]"       # fal.ai only
```

> **AI image generation** requires API keys in your `.env` file:
> `STX_OPENAI_API_KEY`, `STX_GOOGLE_AI_KEY`, `STX_FAL_KEY` (only the providers you use).
> See the [AI Guide](https://github.com/nicolasguelfi/streamtex/blob/main/AI_GUIDE.md#ai-image-generation) for configuration details.

**Prerequisites**: Python 3.11+, git, [uv](https://docs.astral.sh/uv/).

### Zero-Code with Claude or Cursor

Install StreamTeX and a Claude AI profile, then let the AI build your project:

```bash
uv tool install "streamtex[cli]" -U
mkdir streamtex-dev && cd streamtex-dev
stx install && stx update
stx project new my-project
cd projects/my-project
stx claude install project .
```

Open in Claude Code or Cursor, then use slash commands:

```
/stx-project:project-init
> "Create a Docker course with 12 slides, dark theme,
>  table of contents and page navigation"
```

The AI agent designs the project structure, proposes it for your approval,
and generates all files — blocks, styles, book.py — ready to run:

```bash
stx run
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
stx run app.py
```

### Manual Installation (without stx CLI)

```bash
pip install streamtex
git clone https://github.com/nicolasguelfi/streamtex-claude.git
mkdir my-project && cd my-project
python ../streamtex-claude/install.py project .
stx run
```

### Workspace Presets

The `stx install` command supports 5 presets:

| Preset | Repos | Extras (with --project) | Use case |
|--------|-------|------------------------|----------|
| `basic` | none | pdf | Workspace only, upgrade later |
| `user` | streamtex-claude | pdf | + Claude AI profiles |
| `standard` (default) | streamtex-docs + streamtex-claude | pdf, ai | + rich templates + local docs |
| `power` | streamtex-docs + streamtex-claude | pdf, ai, inspector | + all extras, requires --project |
| `developer` | all 3 repos | pdf, ai, inspector | + library source + editable install |

```bash
stx install --preset user       # Claude profiles only
stx install                     # standard (default)
stx install --preset developer  # full developer setup
stx install --preset power --project my-project  # all extras with a project
```

Upgrade an existing workspace to a higher preset:

```bash
stx install --preset developer
stx update
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
| `/stx-project:project-init` | Create a complete project from a natural-language description |
| `/stx-project:project-customize` | Change theme, typography, navigation without editing code |
| `/stx-project:course-generate` | Generate `book.py` structure from a CSV block list |
| `/stx-project:collection-new` | Create a multi-project hub |

### Design & Content

| Command | What it does |
|---------|-------------|
| `/stx-designer:slide-new` | Create slides from descriptions |
| `/stx-designer:slide-audit` | Validate design rules (font sizes, line lengths, spacing) |
| `/stx-designer:slide-fix` | Auto-fix design violations |
| `/stx-designer:style-audit` | Check styles for consistency |

### Migration

| Command | What it does |
|---------|-------------|
| `/stx-migration:html-migrate` | Convert HTML (Google Docs) to StreamTeX blocks |
| `/stx-migration:html-convert-batch` | Batch conversion of multiple files |
| `/stx-migration:conversion-audit` | Audit conversion quality |

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
cd manuals/stx_manual_intro && stx run
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
stx update                   # pulls repos, syncs deps, updates profiles
```

Fine-grained control:
```bash
stx update --skip-sync      # skip uv sync
stx update --skip-profiles  # skip Claude profile update
```

### Check workspace status

```bash
stx status                   # show preset, repos, profiles, project list
```

### Upgrade a project

```bash
stx project upgrade          # upgrade project deps and extras to match current preset
```

### Update a standalone project (no workspace)

```bash
cd my-project/
uv add streamtex --upgrade   # update the library dependency
```

> Use `/stx-guide update` inside Claude Code for guided assistance.

## Report Issues & Feedback

Found a bug? Have a suggestion? We'd love to hear from you.

- **Bug report**: [Open a bug report](https://github.com/nicolasguelfi/streamtex/issues/new?template=bug_report.md) — include the error message, steps to reproduce, and your environment
- **Feature request**: [Request a feature](https://github.com/nicolasguelfi/streamtex/issues/new?template=feature_request.md) — describe the problem and your proposed solution
- **Questions & discussions**: [GitHub Discussions](https://github.com/nicolasguelfi/streamtex/discussions) — ask questions, share ideas, show your projects

When reporting a bug, please include:
1. The **full error traceback** (copy-paste from the terminal)
2. The **command** you ran (e.g. `stx project new`, `/stx-designer:init`, `stx run`)
3. Your **StreamTeX version** (`uv pip show streamtex | grep Version`)

## Contributing

See [CONTRIBUTING.md](https://github.com/nicolasguelfi/streamtex/blob/main/CONTRIBUTING.md) for guidelines on code, content,
and AI profile contributions.

## Support the Project

If StreamTeX is useful to you, consider [sponsoring the project](https://github.com/sponsors/nicolasguelfi) to help maintain and improve it.

## License

[BUSL-1.1](https://github.com/nicolasguelfi/streamtex/blob/main/LICENSE) — Copyright (c) 2026 Nicolas Guelfi
Converts to Apache 2.0 on 2030-11-29.
