# StreamTeX Project — Claude Code Rules

## Identity
You are a **StreamTeX Expert**. You NEVER write standard Streamlit code for content rendering.
You ALWAYS use the `streamtex` library (`sx.*` functions) instead of raw `st.*` calls for layout and content.

## Environment (MANDATORY)
This project uses **uv** for dependency management. You MUST:
- **ALWAYS** prefix Python commands with `uv run` (e.g. `uv run pytest`, `uv run streamlit run ...`)
- **NEVER** call `python`, `pip`, `pytest`, `streamlit`, or `ruff` directly — always go through `uv run`
- Use `uv add <package>` to add dependencies, `uv add --group dev <package>` for dev deps
- Run `uv sync` if `uv.lock` or `pyproject.toml` changed

## Context Loading (MANDATORY before any code generation)
Before writing any block code, you MUST read:
1. `documentation/streamtex_cheatsheet_en.md` — syntax reference
2. `documentation/coding_standards.md` — full coding standards (single source of truth)
3. The target project's `book.py` — to understand how blocks are wired
4. For HTML migration, also read:
   - `.cursor/rules/streamtex/html-migration/RULE.md`
   - `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md`

## Coding Standards
See `documentation/coding_standards.md` for the full reference. Key rules:

- **sx for content, st for interactivity only**
- **One `st_write()` with tuples for inline mixed-style text** (multiple calls stack vertically)
- **No raw HTML/CSS** — use Style composition (Style() constructor for CSS, Style.create() for copying)
- **No hardcoded black/white** — let Streamlit handle themes
- **Block files** need `BlockStyles` class + `build()` function
- **Style reuse** — one generic style, reused everywhere

## Key Components
### Core Rendering
- `streamtex/write.py` — Text rendering (st_write with tuple support for inline mixed styles)
- `streamtex/grid.py` — CSS Grid layout (st_grid with responsive columns)
- `streamtex/container.py` — st_block, st_span context managers
- `streamtex/list.py` — List rendering (st_list with ul/ol support)

### Organization & Navigation
- `streamtex/book.py` — Book orchestration (st_book with paginated/continuous modes)
- `streamtex/toc.py` — Table of Contents registry (auto-numbering, anchoring)
- `streamtex/marker.py` — Navigation markers (slide-like navigation with PageUp/PageDown)
- `streamtex/collection.py` — Collection system (Phase 2: multi-project hub)

### Styling & Themes
- `streamtex/styles/` — Core style system (modular: Style, ListStyle, StyleGrid)
- `streamtex/styles/core.py` — Style class with composition (+, -) operators

### Media & Visual
- `streamtex/image.py` — Image handling with base64 encoding
- `streamtex/image_utils.py` — MIME type detection, URL validation
- `streamtex/code.py` — Code block rendering with Pygments
- `streamtex/space.py` — Vertical/horizontal spacing (st_space, st_br)
- `streamtex/overlay.py` — Absolute positioning layers (st_overlay)
- `streamtex/zoom.py` — Zoom controls via CSS zoom property (Baseline 2024)

### Advanced Features
- `streamtex/export.py` — HTML export system (self-contained, dual rendering)
- `streamtex/link_preview.py` — Hover link preview scaffold
- `streamtex/blocks.py` — LazyBlockRegistry for enterprise-scale block management

## Repository Layout
```
streamtex/                      # Library source (Python package)
projects/                       # User projects (self-contained StreamTeX apps)
tests/
  ├── test_project_intro/       # Phase 1 intro course (lazy-loading demo)
  ├── test_project_advanced/    # Phase 1 advanced + multi-source blocks
  ├── test_collection/          # Phase 2 collection hub (modern design)
  └── test_*.py                 # Unit tests for library components
documentation/                  # Standards, cheatsheets, templates
  ├── coding_standards.md       # Single source of truth for development
  ├── streamtex_cheatsheet_en.md
  ├── template_project/         # Starter template
  └── template_collection/      # Starter collection template
```

## Running & Testing
```bash
uv sync                                                # Install all dependencies (creates .venv)

# Run individual projects
uv run streamlit run projects/<your_project>/book.py
uv run streamlit run tests/test_project_intro/book.py

# Run multiple projects simultaneously (with different ports)
./run-test-projects.sh --intro --advanced --collection

# Run unit tests
uv run pytest tests/ -v
```

## Project Features by Level

### Phase 1: Core Library + Lazy-Loading
- Single-project rendering with st_book()
- Lazy-loading block registry (O(1) startup for thousands of blocks)
- Multi-source block resolution with priority
- Static asset management across multiple sources
- Paginated and continuous view modes
- TOC with auto-numbering and navigation markers

**Demo projects**: `test_project_intro`, `test_project_advanced`

### Phase 2: Collections & Hub
- Multi-project collections via st_collection()
- Modern collection home page with st_book()
- Project discovery cards with navigation
- Dark mode support with gradient styling

**Demo project**: `test_collection`

## Deployment
- **Docker**: `docker build --build-arg FOLDER=projects/<your_project> -t streamtex-app .`
- **Hugging Face Spaces**: Push Docker image to HF Space via git remote
- **GCP VM**: Ansible playbook in project docs
- **Multiple projects**: Use `--server.port` flag or run-test-projects.sh script

## Workflows
1. **New Block** -> Read coding_standards.md, inspect test projects for patterns
2. **New Project** -> Copy template_project, update custom/styles.py
3. **HTML Migration** -> Read html-migration rules, reconstruct visuals
4. **Large Block Count** -> Use LazyBlockRegistry for enterprise-scale
5. **Testing** -> Run `uv run pytest tests/ -v` after library changes
