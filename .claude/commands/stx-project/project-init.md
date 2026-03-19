# /stx-project:project-init — Initialize a complete StreamTeX project

Arguments: $ARGUMENTS (natural language description of the desired project)

## Trigger

The user describes a project in natural language. Examples:

- `"Docker course for beginners, 8 slides, dark presentation style"`
- `"technical REST API documentation, 12 sections, with code examples"`
- `"research project portfolio, 5 projects, collection mode"`

## Required readings BEFORE generation

1. `.claude/references/coding_standards.md`
2. `.claude/references/streamtex_cheatsheet_en.md`
3. `.claude/designer/skills/visual-design-rules.md`
4. `.claude/designer/skills/style-conventions.md`
5. `.claude/designer/skills/block-blueprints.md`
6. `.claude/designer/agents/project-architect.md`
7. Existing `book.py` (if the project has already been scaffolded)

## Workflow

### Step 1: Analyze the request

Extract from the user's description:

- **Type**: presentation | documentation | collection
- **Number of sections/slides**: N
- **Visual theme**: dark | light | custom
- **Features**: TOC, pagination, banner, export, interactivity
- **Target audience**: auditorium (large text, `s.Large` min) | screen (normal text, `s.large`)

If information is missing, use default values:
- Type: presentation
- Theme: dark
- TOC: `numbering=NumberingMode.SIDEBAR_ONLY, sidebar_max_level=2` (numbering in sidebar only, up to level 2)
- Sidebar: `initial_sidebar_state="expanded"` (always open by default)
- Pagination: yes
- Audience: screen

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
   - Imports conforming to `coding_standards.md`:
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
- No raw HTML/CSS — use only `stx.*` functions
- No hardcoded black/white — use the style system

## Constraints

- Follow ALL rules in CLAUDE.md
- Maximum 15 blocks per project (otherwise, suggest a collection)
- Always include a title block (Blueprint 1) and a conclusion block (Blueprint 10)
- If the project is already scaffolded (`book.py` exists), adapt rather than recreate
