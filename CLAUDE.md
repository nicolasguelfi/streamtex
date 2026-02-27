# StreamTeX Project — Claude Code Rules

## Identity
You are a **StreamTeX Expert**. You NEVER write standard Streamlit code for content rendering.
You ALWAYS use the `streamtex` library (`stx.*` functions) instead of raw `st.*` calls for layout and content.

## Terminology
When the user says **"stream"**, **"la librairie"**, **"st"**, or **"stx"**, they always mean **StreamTeX** (the `streamtex` library).

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
- **After every code change**, run `uv run ruff check streamtex/` before committing — ruff enforces isort (I001) import ordering which is the most common CI failure

## Key Components

### Core Rendering
- `streamtex/write.py` — Text rendering (st_write with tuple support for inline mixed styles)
- `streamtex/grid.py` — CSS Grid layout (st_grid with responsive columns)
- `streamtex/container.py` — st_block, st_span context managers
- `streamtex/list.py` — List rendering (st_list with ul/ol support, align="center" for centered lists)
- `streamtex/export.py` — st_html: raw HTML bridge (inline or iframe with auto font injection)

### Organization & Navigation
- `streamtex/book.py` — Book orchestration (st_book with paginated/continuous modes, page_width: int default 90)
- `streamtex/banner.py` — Configurable paginated navigation banners (BannerMode, BannerConfig, presets: full/compact/hidden)
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
- `streamtex/zoom.py` — Width% and Zoom% sidebar inputs, pure CSS (no JavaScript)

### Diagram Rendering
- `streamtex/mermaid.py` — Mermaid diagrams (st_mermaid with pan/zoom, fit modes: contain/width/none)
- `streamtex/plantuml.py` — PlantUML diagrams via HTTP server (st_plantuml with pan/zoom)
- `streamtex/tikz.py` — TikZ diagrams via LaTeX pipeline (st_tikz, pan/zoom when height is explicit)

### Bibliography
- `streamtex/bib.py` — Bibliography system (BibEntry, BibConfig, BibFormat, CitationStyle, BibRegistry, cite, st_cite, st_bibliography, st_refs, load_bib/bibtex/json/ris/csl_json, parse_bibtex_string, parse_ris_string, export_bibtex, generate_bib_stubs)

### Google Sheets
- `streamtex/gsheet.py` — Google Sheets integration (GSheetConfig, GSheetSource, GSheetError, AuthMode, load_gsheet, load_gsheet_df, set_gsheet_config, get_gsheet_config)

### Block Inspector
- `streamtex/inspector.py` — Live code editor in sidebar (InspectorConfig, FileCategoryRegistry, SourceFile, discover_sources, render_edit_button, render_inspector_panel)

### Export
- `streamtex/export.py` — HTML export system (ExportConfig, HtmlExportBuffer, st_export context manager, st_html raw HTML bridge)
- `streamtex/export_widgets.py` — Export-aware widget wrappers (st_dataframe, st_table, st_metric, st_json, st_graphviz, charts, st_audio, st_video)

### Block Infrastructure
- `streamtex/blocks.py` — ProjectBlockRegistry, LazyBlockRegistry, load_atomic_block, static resolution API (set_static_sources, get_static_sources, resolve_static), BlockNotFoundError, BlockImportError
- `streamtex/block_helpers.py` — BlockHelper, show_code, show_code_inline, show_explanation, show_details (3 usage modes: functions, config injection via BlockHelperConfig, OOP inheritance)

### Utilities & Internal
- `streamtex/constants.py` — Configurable defaults (PAGE_WIDTH="100%", PAGE_PADDING="36pt") — overridable per project via st_book(page_width=...)
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
      ├── stx_manual_deploy/     # Deployment guide (Docker, Cloud, CI/CD)
      ├── stx_manuals_collection/# Phase 2 collection hub (modern design)
      └── stx_manuals_shared-blocks/ # Cross-project shared block library
.claude/
  ├── commands/                 # Slash commands (domain-action naming, grouped by category)
  │   ├── designer/             # slide-audit, slide-fix, slide-new, block-new, block-preview,
  │   │                         # style-audit, style-refactor, presentation-audit, presentation-fix,
  │   │                         # survey-convert
  │   ├── developer/            # test-run, lint, deploy
  │   ├── migration/            # conversion-audit, html-convert-batch, html-convert-block,
  │   │                         # html-export, html-migrate
  │   └── project/              # project-new, collection-new, project-upgrade, course-generate
  ├── designer/                 # Designer reference knowledge
  │   ├── skills/               # visual-design-rules, style-conventions, quick-reference
  │   ├── agents/               # slide-designer, slide-reviewer
  │   └── ros_designer_default/ # Presentation design role (live projection 10-20m)
  │       ├── skills/           # presentation-design-rules
  │       └── agents/           # presentation-designer
  └── developer/                # Developer reference knowledge
      └── skills/               # architecture, testing-patterns
```

## Running & Testing
```bash
uv sync                                                # Install all dependencies (creates .venv)

# Run individual projects
uv run streamlit run projects/<your_project>/book.py
uv run streamlit run documentation/manuals/stx_manual_intro/book.py
uv run streamlit run documentation/manuals/stx_manual_deploy/book.py

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
See `deploy/README.md` for the full deployment guide and `documentation/manuals/stx_manual_deploy/` for the interactive manual.
- **Docker local**: `docker build --build-arg FOLDER=projects/<your_project> -t streamtex-app .`
- **Docker Compose**: `docker compose up --build` (3 demo projects on ports 8501-8503)
- **Streamlit Cloud**: `./deploy/gen-requirements.sh > requirements.txt` then connect on share.streamlit.io
- **Hugging Face Spaces**: `./deploy/huggingface.sh <HF_SPACE_URL> [PROJECT_FOLDER]`
- **Render.com**: `./deploy/render.sh [PROJECT_FOLDER]` (render.yaml at repo root)
- **GCP VM + Ansible**: `ansible-playbook -i deploy/ansible/inventory.ini deploy/ansible/deploy.yml`
- **CI/CD**: `.github/workflows/ci.yml` (tests + Docker build on push)
- **Multiple projects**: Use `--server.port` flag or run-test-projects.sh script
- **Preflight checks**: `./deploy/preflight.sh [PROJECT_FOLDER]` (run before any deployment)

## Workflows
1. **New Block** -> Read coding_standards.md, inspect test projects for patterns (`/designer:block-new`)
2. **New Slide** -> Read designer skills (visual-design-rules, style-conventions) (`/designer:slide-new`)
3. **New Project** -> Copy template_project, update custom/styles.py (`/project:project-new`)
4. **New Collection** -> Copy template_collection, configure collection.toml (`/project:collection-new`)
5. **HTML Migration** -> Read html-migration rules, reconstruct visuals (`/migration:html-migrate`)
6. **HTML Export** -> Configure ExportConfig, audit widgets (`/migration:html-export`)
7. **Large Block Count** -> Use LazyBlockRegistry for enterprise-scale
8. **Testing** -> Run `uv run pytest tests/ -v` after library changes (`/developer:test-run`)
9. **Linting** -> Run `uv run ruff check streamtex/` (`/developer:lint`)
10. **Presentation Audit** -> Check block for live projection compliance (`/designer:presentation-audit`)
11. **Presentation Fix** -> Auto-fix presentation design violations (`/designer:presentation-fix`)
