# streamtex — Claude Code Rules

## Identity
You are a **StreamTeX Expert**. You NEVER write standard Streamlit code for content rendering.
You ALWAYS use the `streamtex` library (`stx.*` functions) instead of raw `st.*` calls.

## Terminology
When the user says **"stream"**, **"the library"**, **"st"**, or **"stx"**, they always mean **StreamTeX**.

## Environment (MANDATORY)
This project uses **uv** for dependency management. You MUST:
- **ALWAYS** prefix Python commands with `uv run` (e.g. `uv run pytest`)
- **NEVER** call `python`, `pip`, `pytest`, `streamlit`, or `ruff` directly — always go through `uv run`
- Use `stx run` to launch projects (shortcut for `uv run streamlit run book.py`)
- Use `uv add <package>` to add dependencies, `uv add --group dev <package>` for dev deps
- Run `uv sync` if `uv.lock` or `pyproject.toml` changed

## Context Loading (MANDATORY before any code generation)
Before writing any block code, you MUST read:
1. `.claude/references/coding_standards.md` — full coding standards (single source of truth)
2. `.claude/references/streamtex_cheatsheet_en.md` — syntax reference
3. `book.py` — to understand how blocks are wired

## Coding Standards
See `.claude/references/coding_standards.md` for the full reference. Key rules:

- **stx for content, st for interactivity only**
- **One `st_write()` with tuples for inline mixed-style text** (multiple calls stack vertically)
- **No raw HTML/CSS** — use Style composition (Style() constructor for CSS, Style.create() for copying)
- **No hardcoded black/white** — let Streamlit handle themes
- **Block files** need `BlockStyles` class + `build()` function
- **Style reuse** — one generic style, reused everywhere
- **After every code change**, run `uv run ruff check` before committing

## Key Components

### Core Rendering
- `st_write(style, text|tuple)` — Text rendering with inline mixed-style support
- `st_grid(cols, grid_style, cell_styles)` — CSS Grid layout with responsive columns
- `st_block(style)`, `st_span(style)` — Container context managers
- `st_list(list_type)` — List rendering with ul/ol/custom support
- `st_markdown(style, file=)` — Markdown rendering (Streamlit native engine)

### Organization & Navigation
- `st_book(blocks, paginate=True|False, view_modes=[ViewMode.PAGINATED, ViewMode.CONTINUOUS])` — Book orchestration with paginated/continuous modes; `view_modes` restricts which modes are available (single-mode hides the radio button)
- `st_collection(config)` — Multi-project collection system

### Styling
- `Style(css_string, style_id)` — Create style from CSS
- `Style.create(existing, new_id)` — Copy an existing style
- Style composition: `Style + Style`, `Style + string`, `Style - string`

### Media & Visual
- `st_image(style, uri=)` — Image handling with base64 encoding
- `st_code(style, code=, language=)` — Code blocks with Pygments
- `st_space(dir, amount)`, `st_br()` — Spacing
- `st_mermaid(style, code)` — Mermaid diagrams
- `st_plantuml(style, code)` — PlantUML diagrams
- `st_tikz(style, code)` — TikZ diagrams via LaTeX pipeline
- `st_latex(content, *, style=)` — LaTeX math rendering

### Block Infrastructure
- `ProjectBlockRegistry` — Lazy-loading block registry
- `BlockHelper`, `show_code`, `show_explanation`, `show_details` — Block helpers with DI

## Running the App
```bash
stx run
```

## Project Structure
```
streamtex/
├── book.py                 # Entry point
├── blocks/                 # Block files (bck_*.py)
│   ├── __init__.py         # ProjectBlockRegistry
│   └── helpers.py          # Block helper config
├── custom/
│   ├── styles.py           # Project styles
│   └── themes.py           # Theme overrides
├── static/images/          # Static assets
└── .streamlit/config.toml  # Streamlit config
```

## Documentation Lookup (when answering user questions)

When the user asks a question about StreamTeX usage, patterns, or features:

1. **Check if manuals exist**: look for `../../streamtex-docs/manuals/` (relative to this project).
   Also try `../streamtex-docs/manuals/` (if project is directly in the workspace root).
2. **If found** — search the relevant manual blocks for examples and patterns:
   - `stx_manual_intro/blocks/` — fundamentals (text, grids, lists, images, containers, styles)
   - `stx_manual_advanced/blocks/` — advanced features (export, PDF, bibliography, diagrams, overlays, banners)
   - `stx_manual_ai/blocks/` — AI image generation, Claude profiles, prompt patterns
   - `stx_manual_deploy/blocks/` — deployment (Docker, Render, CI/CD)
   - `stx_manual_developer/blocks/` — library internals (architecture, testing, block system, CLI)
   - Block files are `bck_*.py` — the `def build()` function contains live examples with `show_code()`, `show_explanation()`, and `show_details()`.
3. **If NOT found** — the user's workspace doesn't include the documentation repo. Tell them:
   > The StreamTeX documentation manuals are not available in your workspace.
   > To access them (rich examples, tutorials, and patterns), upgrade your workspace:
   > ```
   > stx install --preset standard
   > stx update
   > ```
   > This will clone the `streamtex-docs` repo with 6 manuals and 114+ example blocks.

Always prefer showing real examples from manual blocks over generating code from scratch.

## Customization
- `.claude/` contains **read-only** files installed by `stx claude update` — do not modify them
- `.claude/custom/` contains **your personalizations** — never overwritten by updates
- To add a rule: create a file in `.claude/custom/references/`
- To add a skill: create a file in `.claude/custom/skills/`
- To add a slash command: create `.claude/commands/my-cmd/run.md` (commands go in `commands/`, not `custom/commands/`)
- See `.claude/custom/README.md` for full details

## Workflows — stx-block Commands

The `stx-block` commands cover the full project lifecycle:

1. **Create project** -> `/stx-block:init <description>` (templates: project, presentation, collection, course)
2. **Add content** -> `/stx-block:update add a new block about X` or `/stx-block:update add 3 slides on Y`
3. **Customize** -> `/stx-block:update change palette to blue/violet` or `/stx-block:customize`
4. **Migrate HTML** -> `/stx-block:update --migrate convert intro.html`
5. **Audit quality** -> `/stx-block:audit --all` or `/stx-block:audit --target bck_intro`
6. **Fix issues** -> `/stx-block:fix --all` or `/stx-block:fix --target bck_intro`
7. **Specialized tools** -> `/stx-block:tool survey-convert`
8. **Help** -> `/stx-block:init --help` (cheatsheet for all commands)
9. **Testing** -> `uv run pytest tests/ -v` (`/stx-block:test`)
10. **Linting** -> `uv run ruff check` (`/stx-block:lint`)

## Workflows — stx-ce Compound Document Engineering

The `stx-ce` commands provide a structured methodology for document production:

```
COLLECT -> ASSESS -> PLAN -> PRODUCE -> REVIEW -> FIX -> COMPOUND -> INTEGRATE
```

1. **Inventory sources** -> `/stx-ce:collect ~/my-sources/` (scan files, classify, evaluate importability)
2. **Define objectives** -> `/stx-ce:assess` (auto-detects pathway: import/improve/create)
3. **Plan production** -> `/stx-ce:plan` (auto) or `/stx-ce:plan --interactive` (4-step collaborative)
4. **Execute plan** -> `/stx-ce:produce` (orchestrates stx-block + stx-import commands)
5. **Review document** -> `/stx-ce:review` (5 perspectives: audience, pedagogy, visual, style, editorial)
6. **Fix findings** -> `/stx-ce:fix` (correct automatable issues, verify, trace — iterable with review)
7. **Capitalize** -> `/stx-ce:compound` (3 axes: production learnings, ecosystem feedback, dev governance)
8. **Integrate** -> `/stx-ce:integrate` (route solutions to lib issues, skill updates, or custom rules)
9. **Full cycle** -> `/stx-ce:go "description"` (autonomous with 4 validation gates)

CE artifacts are stored in `docs/` (collect/, assess/, plans/, reviews/, solutions/).
See `.claude/references/ce_cheatsheet_en.md` for the full reference.

## Design Guidelines

Projects can adopt a design guideline for consistent visual design:
- **Available**: `.claude/designer/guidelines/_index.md` — catalog of built-in guidelines
- **Project config**: `custom/design-guideline.md` — set default + block overrides
- **Block annotation**: `# @guideline: <name>` in block files (most specific wins)
- **Combination**: `# @guideline: A + B` — A has priority, B complements
- **Built-in**: `maximize-viewport`, `minimalist-visual`, `academic-structured`, `dense-informative`

## StreamTeX Patterns (graphic design patterns)

If the project contains a `streamtex-patterns/` folder (default location:
`.claude/custom/streamtex-patterns/`), it defines reusable graphic design
patterns (named grids, callouts, hero stats, slide headings, etc.) that
the user can invoke by name when creating or editing blocks.

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
   project's `custom/styles.py` and palette.
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
