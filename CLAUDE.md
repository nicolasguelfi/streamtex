# StreamTeX Project — Claude Code Rules

## Identity
You are a **StreamTeX Expert**. You NEVER write standard Streamlit code for content rendering.
You ALWAYS use the `streamtex` library (`sx.*` functions) instead of raw `st.*` calls for layout and content.

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
- **No raw HTML/CSS** — use Style composition
- **No hardcoded black/white** — let Streamlit handle themes
- **Block files** need `BlockStyles` class + `build()` function
- **Style reuse** — one generic style, reused everywhere

## Key Files to Know
- `streamtex/styles/` — Core style system (modular package)
- `streamtex/__init__.py` — Public API surface (re-exports)
- `streamtex/book.py` — Book orchestration (st_book, st_include, st_toc)
- `streamtex/zoom.py` — Zoom controls and page scaling
- `streamtex/write.py` — Text rendering (st_write)
- `streamtex/grid.py` — CSS Grid layout (st_grid)
- `streamtex/container.py` — st_block, st_span context managers
- `streamtex/list.py` — List rendering (st_list)
- `streamtex/toc.py` — Table of Contents registry
- `streamtex/image.py` — Image handling with base64
- `streamtex/overlay.py` — Absolute positioning layers
- `streamtex/image_utils.py` — Base64, MIME, URL detection
- `streamtex/link_preview.py` — Hover link preview scaffold

## Repository Layout
```
streamtex/              # Library source (Python package)
projects/               # User projects (each is a self-contained StreamTeX app)
tests/test_project/     # Integration test project (also serves as a feature showcase)
documentation/          # Coding standards, cheatsheets, and template_project
```
- `documentation/template_project/` — starter template for new projects
- `tests/test_project/` — comprehensive example with all StreamTeX features demonstrated

## Running & Testing
```bash
uv sync                                                # Install all dependencies (creates .venv)
uv run streamlit run projects/<your_project>/book.py   # Run a project
uv run streamlit run tests/test_project/book.py        # Run the test project
uv run pytest tests/ -v                                # Run unit tests
```

## Deployment
- **Docker**: `docker build --build-arg FOLDER=projects/<your_project> -t streamtex-app .`
- **Hugging Face Spaces**: Push Docker image to HF Space via git remote
- **GCP VM**: Ansible playbook in project docs

## Workflows
1. **New Feature** -> Read coding_standards.md, inspect `tests/test_project/` or `documentation/template_project/` for patterns
2. **HTML Migration** -> Read migration + color-fidelity rules, follow the generic workflow
3. **Visual Reconstruction** -> Analyze visual hierarchy, reconstruct with st_grid and st_block
4. **Testing** -> Run `pytest tests/ -v` after any library changes
