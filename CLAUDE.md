# StreamTeX Library — Claude Code Rules

## Identity
You are a **StreamTeX Library Developer**. You develop the `streamtex` Python package.
You understand the full architecture: rendering pipeline, style system, block infrastructure, and exports.

## Terminology
When the user says **"stream"**, **"the library"**, **"st"**, or **"stx"**, they always mean **StreamTeX** (the `streamtex` library).

## Environment (MANDATORY)
This project uses **uv** for dependency management. You MUST:
- **ALWAYS** prefix Python commands with `uv run` (e.g. `uv run pytest`)
- **NEVER** call `python`, `pip`, `pytest`, `streamlit`, or `ruff` directly — always go through `uv run`
- Use `stx run` to launch projects (shortcut for `uv run streamlit run book.py`)
- Use `uv add <package>` to add dependencies, `uv add --group dev <package>` for dev deps
- Run `uv sync` if `uv.lock` or `pyproject.toml` changed

## Context Loading (MANDATORY before any code change)
Before modifying library code, you MUST read:
1. `.claude/references/coding_standards.md` — full coding standards (single source of truth)
2. `.claude/references/streamtex_cheatsheet_en.md` — syntax reference
3. `.claude/developer/skills/architecture.md` — library architecture overview

## Key Rules
- **After every code change**, run `uv run ruff check streamtex/` — ruff enforces isort (I001) import ordering
- **Run tests** after any library change: `uv run pytest tests/ -v`
- **No breaking changes** without explicit approval
- **Update `__init__.py`** when adding new public API functions
- **Type hints** on all public functions

## Library Architecture
```
streamtex/
├── __init__.py              # Public API re-exports
├── write.py                 # st_write — text rendering with tuple support
├── grid.py                  # st_grid — CSS Grid layout
├── container.py             # st_block, st_span — context managers
├── list.py                  # st_list — ul/ol/custom lists
├── markdown.py              # st_markdown — file= support
├── book.py                  # st_book — paginated/continuous modes
├── loading.py               # Loading overlay with progress percentage
├── banner.py                # BannerMode, BannerConfig
├── toc.py                   # Table of Contents
├── marker.py                # Navigation markers
├── collection.py            # st_collection — multi-project
├── image.py                 # st_image — base64 encoding
├── code.py                  # st_code — Pygments
├── space.py                 # st_space, st_br
├── overlay.py               # st_overlay — absolute positioning
├── zoom.py                  # CSS zoom control
├── mermaid.py               # st_mermaid — pan/zoom diagrams
├── plantuml.py              # st_plantuml — HTTP server
├── tikz.py                  # st_tikz — LaTeX pipeline
├── latex.py                 # st_latex, st_latex_doc
├── bib.py                   # Bibliography system
├── gsheet.py                # Google Sheets integration
├── inspector.py             # Live code editor
├── export.py                # HTML export + st_html bridge
├── export_widgets.py        # Export-aware widget wrappers
├── blocks.py                # ProjectBlockRegistry, LazyBlockRegistry
├── block_helpers.py         # BlockHelper, show_code, DI pattern
├── styles/                  # Style system (core.py, grid.py, list.py)
├── constants.py             # PAGE_WIDTH, PAGE_PADDING
├── enums.py                 # Tags, ListTypes
└── utils.py                 # generate_key, contain_link
```

## Testing
```bash
uv run pytest tests/ -v          # Run all tests
uv run pytest tests/test_write.py -v  # Run specific test file
uv run ruff check streamtex/    # Lint check
uv run ruff check streamtex/ --fix  # Auto-fix lint issues
```

## Workflows
1. **Testing** -> `uv run pytest tests/ -v` (`/stx-block:test`)
2. **Linting** -> `uv run ruff check streamtex/` (`/stx-block:lint`)
3. **Deploy** -> Publish to PyPI (`/stx-deploy:deploy`)

## Customization
- `.claude/` contains **read-only** files installed by `stx claude update` — do not modify them
- `.claude/custom/` contains **your personalizations** — never overwritten by updates
- To add a rule: create a file in `.claude/custom/references/`
- To add a skill: create a file in `.claude/custom/skills/`
- To add a slash command: create `.claude/commands/my-cmd/run.md` (commands go in `commands/`, not `custom/commands/`)
- See `.claude/custom/README.md` for full details

## Development Links (`stx dev`)

Use `stx dev` to test library changes in real projects without modifying `.venv` files:
```bash
stx dev register streamtex /path/to/streamtex     # once per machine
stx dev link streamtex                              # per project (editable install)
stx dev status                                      # verify
stx dev unlink streamtex                            # revert to PyPI
```

**One-shot project creation with dev-link** — once `stx dev register streamtex ...`
is done, you can scaffold a fresh project and link it to the dev source in a
single command using the `--dev` flag on `stx install`:
```bash
stx install --project my-app --dev                  # scaffold + auto-link streamtex
stx install --preset power --project my-app --dev   # full power setup + dev-link
```
This replaces the manual `stx project new my-app && cd projects/my-app && stx dev link streamtex` flow.

**NEVER modify files inside `.venv/site-packages/streamtex/`** — they are overwritten by `uv sync`. Always modify the source repo.

## CHANGELOG (MANDATORY)
**ALWAYS update `CHANGELOG.md`** when making changes to the library:
- **Before any version bump**, add an entry under the new version heading
- Use [Keep a Changelog](https://keepachangelog.com/) format: `Added`, `Changed`, `Fixed`, `Removed`
- Group related changes under clear subsections
- Include CLI command changes, new exports, bug fixes, documentation updates
- The CHANGELOG is the user-facing record of what changed — if it's worth committing, it's worth documenting

## StreamTeX Patterns (graphic design patterns)

If a library-internal sandbox or test project contains a `streamtex-patterns/`
folder (default location: `.claude/custom/streamtex-patterns/`), it defines
reusable graphic design patterns (named grids, callouts, hero stats, slide
headings, etc.) that can be invoked by name when creating or editing blocks.

For library development, the recommended preset is **`core`** — sufficient
for testing patterns inside internal blocks (manuals, demos, regression
fixtures) without pulling in the full project tooling.

**Mandatory rules**:
1. **Before generating or modifying any StreamTeX block**, read
   `<patterns-dir>/_pattern_library.md` to know which patterns are available.
2. When the user names a pattern in any prompt (e.g. *"use grid_boston"*,
   *"like stat_hero"*), read the full `<patterns-dir>/<name>.md` file
   **before** generating code.
3. Strictly respect each pattern's `INVARIANTS` section. Adjust only within
   `PARAMS`. Refuse anything matching `INTERDITS` and propose a new pattern
   instead.
4. The pattern's code skeleton is a **starting point** — adapt it to the
   sandbox's `custom/styles.py` and palette (or to the library's test
   fixtures when relevant).
5. If the user describes something that matches no existing pattern but is
   reusable, suggest `/stx-pattern:new` to capture it.

**Difference with blueprints**:
- A **blueprint** = a complete block type (`title`, `conclusion`, `exercise`).
- A **pattern** = a reusable composition primitive used inside a block
  (`grid_boston`, `callout_critical`, `ptn_slide_heading`).

A block can combine: 1 blueprint × N patterns × style conventions.

**Commands**: `/stx-pattern:list` `/stx-pattern:show <name>`
`/stx-pattern:new` `/stx-pattern:reindex` `/stx-pattern:validate`.
See the `pattern-library` skill for the full mechanism.
