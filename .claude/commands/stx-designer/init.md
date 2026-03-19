# /stx-designer:init — Create a new StreamTeX project

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS] <description>`

**Options** (parsed before the description text):
- `--<template-name>` — Use a specific project template (e.g. `--presentation`, `--collection`, `--course`). Default: `project`
- `--help` — Show the stx-designer cheatsheet (see Help section below)

**Description**: Free-form natural language text describing the desired project.

If `$ARGUMENTS` is empty or only `--help`, show the Help section.

### Examples

```
/stx-designer:init Docker course for beginners, 8 slides, dark style
/stx-designer:init --presentation AI4SE conference talk, 12 slides, blue/violet palette
/stx-designer:init --collection my teaching hub with 3 sub-projects
/stx-designer:init --course Python fundamentals, 6 chapters with exercises
/stx-designer:init --help
```

## Required readings BEFORE generation

1. `.claude/references/coding_standards.md` — coding rules (single source of truth)
2. `.claude/references/streamtex_cheatsheet_en.md` — syntax reference
3. `.claude/designer/skills/block-blueprints.md` — 12 block templates
4. `.claude/designer/agents/project-architect.md` — architecture agent
5. `.claude/designer/skills/style-conventions.md` — style naming rules
6. The **template file** matching the chosen template (see Template resolution below)
7. Existing `book.py` (if the project has already been scaffolded)

### Documentation lookup (recommended)

Before generating blocks, search for real examples in the StreamTeX manuals:

1. **Check if manuals exist**: Look for `../../streamtex-docs/manuals/` (or `../streamtex-docs/manuals/`).
2. **If found** — search for blocks matching the topic you're about to create:
   - Use glob: `../../streamtex-docs/manuals/stx_manual_*/blocks/**/bck_*<keyword>*.py`
   - Read matching blocks to study their `build()` function, `BlockStyles` patterns, and `show_code()` examples
   - Use these real examples as reference for structure, style naming, and API usage
   - Manual index: intro (text, grids, lists, images), advanced (export, PDF, diagrams, overlays), ai (AI images), deploy (Docker, CI), developer (architecture, testing)
3. **If NOT found** — rely on cheatsheet and block-blueprints (no action needed)

### Presentation-specific readings

If the project type is **presentation** (or `--presentation` template), also read:
- `.claude/designer/skills/slide-design-rules.md` — L1/L2/L3 grid system
- `.claude/designer/presentation/skills/presentation-design-rules.md` (if present — live projection rules)

## Template resolution

Templates are defined in `.claude/designer/templates/<name>.md`. Each template specifies:
- Default structure (block list with blueprint mappings)
- Default features (pagination, TOC, banner, marker)
- Default audience and text sizing
- Reference files to copy or adapt

**Available templates**:

| Template | File | Description |
|----------|------|-------------|
| `project` (default) | `templates/project.md` | Standard StreamTeX project (screen) |
| `presentation` | `templates/presentation.md` | Live projection (auditorium, large fonts) |
| `collection` | `templates/collection.md` | Multi-project hub |
| `course` | `templates/course.md` | Pedagogical course with chapters |

If the template file does not exist, fall back to `project.md`.

## Workflow

### Step 1: Analyze the request

Extract from `<description>` + template defaults:

- **Type**: presentation | documentation | collection (from template or description)
- **Number of sections/slides**: N (from description or template default)
- **Visual theme**: dark | light | custom
- **Features**: TOC, pagination, banner, export, interactivity
- **Target audience**: auditorium (`s.Large` min) | screen (`s.large`)
- **Color palette**: from description or template default

If information is missing, use the template's defaults. If no template defaults exist, use:
- Type: presentation, Theme: dark, Pagination: yes, Audience: screen
- TOC: `numbering=NumberingMode.SIDEBAR_ONLY, sidebar_max_level=2`
- Sidebar: `initial_sidebar_state="expanded"`

### Step 2: Propose a plan

Adopt the **Project Architect** role (`.claude/designer/agents/project-architect.md`)
and propose to the user:

1. **List of N blocks** with names, associated blueprints, and descriptions
2. **book.py structure** (pagination, TOC, banner, marker)
3. **Proposed color palette**
4. **Enabled features**

Use the output format defined in `project-architect.md`.

**Ask for confirmation before generating.** Never generate without explicit approval.

### Step 3: Generate files

For each block:

1. Create `blocks/bck_<name>.py` with:
   - Descriptive docstring of the block's content
   - Standard imports conforming to `coding_standards.md`:
     ```python
     from streamtex import *
     from streamtex.styles import Style as ns
     from streamtex.enums import Tags as t, ListTypes as lt
     from custom.styles import Styles as s
     ```
   - `BlockStyles` class with styles adapted to the theme and target audience
   - `bs = BlockStyles` alias
   - `def build()` implementing the chosen blueprint's structure
   - Structured placeholder content (no Lorem Ipsum):
     - Descriptive titles matching the actual subject
     - Bullet points with `"[TODO: description of expected content]"`
     - Image placeholders with comments `# TODO: add image`
   - `toc_lvl` on the main title for the table of contents

2. Update `book.py`:
   - Import `blocks` (registry)
   - Configure `st.set_page_config(initial_sidebar_state="expanded")`
   - Configure `TOCConfig(numbering=NumberingMode.SIDEBAR_ONLY, sidebar_max_level=2, search=True)`
   - Configure `st_book()` with the list of blocks in order
   - Enable chosen features (pagination, TOC, banner, marker)
   - Add default `exports=[...]` config with `ExportMode.NEVER` (HTML + PDF), so users can enable auto-export later by changing `NEVER` to `ALWAYS`

3. Adapt `custom/styles.py`:
   - Define the chosen color palette
   - Create project-level styles (titles, containers, colors)

4. Adapt `custom/themes.py` if the theme is not the default

5. Update `.streamlit/config.toml` if necessary (dark/light theme)

### Step 4: Validate

- Verify that all blocks have a `build()` function
- Verify that `book.py` references all generated blocks
- Verify style consistency (no referenced style left undefined)
- Display a summary of generated files:

```
Generated files:
  book.py                          (updated)
  custom/styles.py                 (updated)
  blocks/bck_title.py              (created)
  blocks/bck_intro.py              (created)
  ...
  blocks/bck_conclusion.py         (created)

Next steps:
  1. Fill in block content (replace "[TODO: ...]" placeholders)
  2. Add images to static/images/
  3. Test: stx run
  4. Use /stx-designer:audit to check compliance
```

## Generation rules

- All blocks follow the `BlockStyles` + `build()` pattern
- Style names are in English (`style-conventions.md`)
- Text sizes respect the target audience:
  - Auditorium: `s.Large` (48pt) minimum for body text
  - Screen: `s.large` (32pt) for body text
- Each block has a `toc_lvl` for the table of contents
- Content is structured placeholder (no Lorem Ipsum)
- Block filenames use semantic names: `bck_title.py`, `bck_intro.py`, etc. (no numbered prefixes)
- Maximum 15 blocks per project (otherwise, suggest a collection)
- Always include a title block (Blueprint 1) and a conclusion block (Blueprint 10)
- No raw HTML/CSS — use only `stx.*` functions
- No hardcoded black/white — use the style system
- Use the most specific `stx.*` component for each content type: `st_list()` for lists (never `st_write("- item")`), `st_grid()` for layouts, `st_image()` for images, `st_code()` for code blocks
- If the project is already scaffolded (`book.py` exists), adapt rather than recreate

## Constraints

- Follow ALL rules in CLAUDE.md
- Read the template MD file before proposing a plan
- Ask for confirmation before generating

---

## Help — stx-designer Cheatsheet

```
╔══════════════════════════════════════════════════════════════╗
║                    stx-designer Commands                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  /stx-designer:init [--template] <desc>                      ║
║    Create a new project from a natural language description.  ║
║    Templates: project (default), presentation, collection,   ║
║               course                                         ║
║                                                              ║
║  /stx-designer:update [--upgrade|--migrate|--export] <desc>  ║
║    Modify an existing project: add blocks, change palette,   ║
║    migrate HTML, export, upgrade structure.                   ║
║                                                              ║
║  /stx-designer:audit [--all|--target <name>] <desc>          ║
║    Check project quality: structure, styles, design rules.   ║
║    Targets: block name, "styles", "book", or --all.          ║
║    Add "presentation" in desc for projection rules.          ║
║                                                              ║
║  /stx-designer:fix [--all|--target <name>] <desc>            ║
║    Auto-fix issues found by audit.                           ║
║    Same targeting as audit.                                  ║
║                                                              ║
║  /stx-designer:tool <tool-name> <desc>                       ║
║    Run a specialized tool.                                   ║
║    Tools: survey-convert, list                               ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Lifecycle:  init → update → audit → fix → update → ...     ║
║  All commands accept --help to show this cheatsheet.         ║
╚══════════════════════════════════════════════════════════════╝
```
