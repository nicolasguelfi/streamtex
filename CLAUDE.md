# StreamTeX Project — Claude Code Rules

## Identity
You are a **StreamTeX Expert**. You NEVER write standard Streamlit code for content rendering.
You ALWAYS use the `streamtex` library (`stx.*` functions) instead of raw `st.*` calls for layout and content.

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
- `streamtex/collection.py` — Collection system (st_collection, CollectionConfig, ProjectMeta)

### Styling & Themes
- `streamtex/styles/` — Core style system (modular: Style, ListStyle, StyleGrid)
- `streamtex/styles/core.py` — Style class with composition (+, -) operators, add_css, remove_css

### Media & Visual
- `streamtex/image.py` — Image handling with base64 encoding
- `streamtex/image_utils.py` — MIME type detection, URL validation
- `streamtex/code.py` — Code block rendering with Pygments
- `streamtex/space.py` — Vertical/horizontal spacing (st_space, st_br)
- `streamtex/overlay.py` — Absolute positioning layers (st_overlay)
- `streamtex/zoom.py` — Zoom controls via CSS zoom property (Baseline 2024)

### Export
- `streamtex/export.py` — HTML export system (ExportConfig, HtmlExportBuffer, st_export context manager)
- `streamtex/export_widgets.py` — Export-aware widget wrappers (st_dataframe, st_table, st_metric, st_json, st_graphviz, charts, st_audio, st_video)

### Block Infrastructure
- `streamtex/blocks.py` — ProjectBlockRegistry, LazyBlockRegistry, load_atomic_block, static resolution API (set_static_sources, get_static_sources, resolve_static), BlockNotFoundError, BlockImportError
- `streamtex/block_helpers.py` — BlockHelper, show_code, show_code_inline, show_explanation, show_details (3 usage modes: functions, config injection via BlockHelperConfig, OOP inheritance)

### Utilities & Internal
- `streamtex/constants.py` — Internal constants (PAGE_WIDTH, PAGE_PADDING)
- `streamtex/enums.py` — Tags, ListTypes
- `streamtex/utils.py` — generate_key, contain_link, inject_link_preview_scaffold
- `streamtex/link_preview.py` — Hover link preview scaffold
- `streamtex/search.py` — Full-text search engine (WIP, not yet exported from __init__.py)

## Repository Layout
```
streamtex/                      # Library source (Python package)
projects/                       # User projects (self-contained StreamTeX apps)
  ├── project_aiai18h/          # Projet AIAI18H
  ├── project_html_example/     # HTML migration example
  └── project_modelsward/       # Projet MODELSWARD
tests/
  ├── conftest.py               # Pytest fixtures
  └── test_*.py                 # 19 unit test files
documentation/
  ├── coding_standards.md       # Single source of truth for development
  ├── streamtex_cheatsheet_en.md
  ├── streamtex_cheatsheet_fr.md
  ├── export_to_pdf_cli.md      # PDF export CLI notes
  ├── architecture_collections_multirepo.md
  ├── maintenance/              # Maintenance plans and notes
  ├── template_project/         # Starter template (single project)
  ├── template_collection/      # Starter template (multi-project hub)
  └── manuals/                  # StreamTeX manuals (runnable demo projects)
      ├── stx_manual_intro/      # Phase 1 intro course (lazy-loading demo)
      ├── stx_manual_advanced/   # Phase 1 advanced + multi-source blocks
      ├── stx_manuals_collection/# Phase 2 collection hub (modern design)
      └── stx_manuals_shared-blocks/ # Cross-project shared block library
.claude/
  ├── commands/                 # Slash commands (all discoverable)
  │   ├── Designer: new-project, new-collection, new-block, new-slide,
  │   │   migrate-html, export-html, preview-block, style-audit,
  │   │   audit-slide, fix-slide, refactor-styles, upgrade-project
  │   └── Developer: run-tests, lint, deploy
  ├── designer/                 # Designer reference knowledge
  │   ├── skills/               # visual-design-rules, style-conventions, quick-reference
  │   └── agents/               # slide-designer, slide-reviewer
  └── developer/                # Developer reference knowledge
      └── skills/               # architecture, testing-patterns
```

## Running & Testing
```bash
uv sync                                                # Install all dependencies (creates .venv)

# Run individual projects
uv run streamlit run projects/<your_project>/book.py
uv run streamlit run documentation/manuals/stx_manual_intro/book.py

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
- HTML export (self-contained, dual rendering pipeline)
- Block helpers with DI pattern

**Demo projects**: `documentation/manuals/stx_manual_intro`, `documentation/manuals/stx_manual_advanced`

### Phase 2: Collections & Hub
- Multi-project collections via st_collection()
- TOML-based project configuration (CollectionConfig)
- Modern collection home page with st_book()
- Project discovery cards with navigation
- Dark mode support with gradient styling

**Demo project**: `documentation/manuals/stx_manuals_collection`

## Deployment
- **Docker**: `docker build --build-arg FOLDER=projects/<your_project> -t streamtex-app .`
- **Hugging Face Spaces**: Push Docker image to HF Space via git remote
- **GCP VM**: Ansible playbook in project docs
- **Multiple projects**: Use `--server.port` flag or run-test-projects.sh script

## Workflows
1. **New Block** -> Read coding_standards.md, inspect test projects for patterns (`/new-block`)
2. **New Slide** -> Read designer skills (visual-design-rules, style-conventions) (`/new-slide`)
3. **New Project** -> Copy template_project, update custom/styles.py (`/new-project`)
4. **New Collection** -> Copy template_collection, configure collection.toml (`/new-collection`)
5. **HTML Migration** -> Read html-migration rules, reconstruct visuals (`/migrate-html`)
6. **HTML Export** -> Configure ExportConfig, audit widgets (`/export-html`)
7. **Large Block Count** -> Use LazyBlockRegistry for enterprise-scale
8. **Testing** -> Run `uv run pytest tests/ -v` after library changes (`/run-tests`)
9. **Linting** -> Run `uv run ruff check streamtex/` (`/lint`)
