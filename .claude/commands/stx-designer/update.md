# /stx-designer:update — Modify an existing StreamTeX project

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS] <description>`

**Options** (parsed before the description text):
- `--upgrade` — Upgrade project boilerplate to latest template structure
- `--migrate` — Migrate HTML content to StreamTeX blocks
- `--export` — Prepare or generate HTML export
- `--help` — Show the stx-designer cheatsheet (see init.md Help section)

**Description**: Free-form natural language text describing the desired changes.

If `$ARGUMENTS` is empty, ask the user what they want to modify.

### Examples

```
/stx-designer:update add a comparison block about VM vs Containers
/stx-designer:update add 3 new slides about security best practices
/stx-designer:update change the color palette to blue and orange
/stx-designer:update switch to light theme and enable HTML export
/stx-designer:update adapt for auditorium projection (large fonts)
/stx-designer:update remove bck_old_topic and reorder blocks
/stx-designer:update generate a course on Python in 6 chapters
/stx-designer:update --upgrade
/stx-designer:update --migrate convert intro.html to StreamTeX
/stx-designer:update --export prepare HTML export
```

## Required readings

1. `book.py` — current project configuration
2. `custom/styles.py` — current palette and styles
3. `blocks/__init__.py` — current block registry
4. `.claude/references/coding_standards.md` — coding rules
5. `.claude/designer/skills/style-conventions.md` — style naming rules

### Additional readings based on detected mode

| Mode | Additional readings |
|------|-------------------|
| Add block/slide | `block-blueprints.md`, `streamtex_cheatsheet_en.md` |
| Add slide (presentation) | `slide-design-rules.md`, `presentation-design-rules.md` (if present) |
| Change styles | `style-conventions.md`, `custom/themes.py` (if exists) |
| Upgrade | Template files in `designer/templates/` |
| Migrate HTML | Migration rules (see Migrate mode below) |
| Export HTML | `streamtex_cheatsheet_en.md` Section "Export" |
| Generate course | `block-blueprints.md`, `project-architect.md` |

### Documentation lookup (recommended for Add, Migrate, Course modes)

Before generating blocks, search for real examples in the StreamTeX manuals:

1. **Check if manuals exist**: Look for `../../streamtex-docs/manuals/` (or `../streamtex-docs/manuals/`).
2. **If found** — search for blocks matching the topic or component you're about to use:
   - Use glob: `../../streamtex-docs/manuals/stx_manual_*/blocks/**/bck_*<keyword>*.py`
   - Read matching blocks to study their `build()` function, `BlockStyles` patterns, and real API usage
   - **Prioritize real examples over generating from scratch** — manual blocks are the gold standard
   - Manual index: intro (text, grids, lists, images), advanced (export, PDF, diagrams, overlays), ai (AI images), deploy (Docker, CI), developer (architecture, testing)
3. **If NOT found** — rely on cheatsheet and block-blueprints (no action needed)

## Mode detection

Analyze `<description>` to determine the operation mode:

| Keywords in description | Mode | Action |
|------------------------|------|--------|
| "add", "new block", "new slide", "create" | **Add** | Create new block(s) |
| "change", "switch", "modify", "palette", "theme", "font" | **Customize** | Modify project settings |
| "remove", "delete", "reorder", "move" | **Restructure** | Reorganize blocks |
| "generate course", "chapters", "sequence" | **Course** | Generate multi-block course |
| `--upgrade` flag | **Upgrade** | Update boilerplate files |
| `--migrate` flag | **Migrate** | Convert HTML to StreamTeX |
| `--export` flag | **Export** | Prepare HTML export |

If the mode is ambiguous, state what you detected and ask for confirmation.

---

## Mode: Add (new blocks/slides)

### Workflow

1. **Read context**: Read `book.py` and existing blocks to understand the project
2. **Check blueprints**: Read `.claude/designer/skills/block-blueprints.md` and match the request to a blueprint:
   - "title slide" → Blueprint 1
   - "comparison X vs Y" → Blueprint 4
   - "code demo" → Blueprint 6
   - "steps / process" → Blueprint 7
   - "conclusion" → Blueprint 10
   - (See full mapping in `block-blueprints.md`)
3. **Determine naming**: Assign `bck_<name>.py` using a semantic name (no numbered prefix)
4. **Create the block file** in `blocks/` with:
   - Standard imports, `BlockStyles` class, `bs` alias, `build()` function
   - Content adapted to the user's description using the blueprint structure
   - **MANDATORY: At least one `st_write(...)` with `toc_lvl="1"` as the first significant heading.** Without this, the block will be invisible in the sidebar and floating navigation bar (markers are auto-generated from TOC level-1 entries via `auto_marker_on_toc`). Even if the user does not explicitly ask for a title, always include one.
   - **MANDATORY: Use the most specific `stx.*` component for each content type.** In particular, any enumeration of 2+ items MUST use `st_list()` with `l.item()` — never simulate lists with successive `st_write()` calls, markdown dashes (`"- item"`), or unicode bullets (`"• item"`). See `coding_standards.md` section 6 for BAD/GOOD patterns.
   - When the user requests an **interactive AI image** (or "image AI editable/modifiable"), use `st_ai_image_widget(...)`. The widget is inherently interactive — the user can modify the prompt and regenerate the image without any additional parameter.
5. **Show wiring instructions**: Tell the user how to add the block to `book.py`:
   ```python
   import blocks
   st_book([..., blocks.bck_new_block_name], toc_config=toc)
   ```
6. **Validate**: Check that all referenced styles exist and all image URIs point to existing files

### Presentation-aware generation

If the project has presentation skills (`.claude/designer/presentation/` exists or profile is `presentation`):
- Use `s.Large` (48pt) for body text instead of `s.large` (32pt)
- Apply L1/L2/L3 grid structure from `slide-design-rules.md`
- Keyword-driven text (3-7 words/bullet, max 3-5 bullets)
- No helper boxes (`show_explanation`, `show_details`, `show_code`)

---

## Mode: Customize (modify settings)

### Workflow

1. **Read current state**: `book.py`, `custom/styles.py`, `custom/themes.py`, `.streamlit/config.toml`
2. **Identify changes**: Parse the description for customization domains:
   - **Theme/colors**: palette, dark/light, accent colors
   - **Typography**: font sizes, audience change (screen ↔ auditorium)
   - **Navigation**: TOC, pagination, banner, marker
   - **Features**: export, inspector, zoom, collection mode
3. **Propose a diff**: Show what will change, which files, how many blocks affected
4. **Ask for confirmation** before applying
5. **Apply changes** in order: styles.py → themes.py → config.toml → book.py → blocks (if font sizes change)
6. **Validate**: Check style consistency

### Rules
- NEVER delete existing content in blocks
- Only modify blocks for font sizes (target audience change)
- Always propose a diff before applying

---

## Mode: Restructure (remove/reorder)

### Workflow

1. **Read `book.py`** to list current blocks and their order
2. **Parse the request**: Which blocks to remove, add, or reorder
3. **Propose the new structure**: Show before/after block list
4. **Ask for confirmation**
5. **Apply**: Update `book.py` block list. If removing, warn about orphaned files but do NOT delete block files (the user can do that manually)

---

## Mode: Course (generate multi-block sequence)

### Workflow

1. **Adopt Project Architect role** (`.claude/designer/agents/project-architect.md`)
2. **Analyze the course description**: Extract topic, number of chapters, audience
3. **Propose the structure**: List of blocks with blueprints, following pedagogical progression:
   - Context and objectives → Fundamental concepts → Practical demos → Exercises → Conclusion
4. **Ask for confirmation**
5. **Generate all blocks** following the `init` generation rules
6. **Update `book.py`** with the new block list

---

## Mode: Upgrade (`--upgrade`)

### Workflow

1. Read template files to understand the latest project structure
2. Compare the target project's boilerplate files against the template:
   - `blocks/__init__.py`, `blocks/helpers.py`
   - `setup.py`, `.streamlit/config.toml`
   - `pyproject.toml` (ruff config, pyright config)
3. Report differences and apply updates where safe
4. Do NOT modify `custom/styles.py`, `custom/themes.py`, or block content files

---

## Mode: Migrate (`--migrate`)

### Workflow

1. **Read migration rules** (if they exist in the project):
   - HTML migration rules for color fidelity, structure mapping
2. **Read the source HTML**: From the path provided in `<description>`, or ask the user
3. **Analyze**: Filter noise (class names), identify defaults (black/white = theme), audit colors
4. **Generate the StreamTeX block** with:
   - `BlockStyles` class with color-mapping summary
   - `build()` function using `stx.*` components only
   - One `st_write()` with tuples for inline mixed-style text
   - `st_grid()` for tables, `st_list()` for lists
5. **Second-pass verification**: Re-read source HTML, check color fidelity, fix mismatches
6. **Batch mode**: If description mentions multiple files or `--all`, process each sequentially

---

## Mode: Export (`--export`)

### Workflow

1. **Check export readiness**: Verify `book.py` has an `exports=[...]` list in `st_book()`. If missing, add default configs with `ExportMode.NEVER`.
2. **Configure exports**: Help the user set up `ExportConfig` entries:
   - `format`: `"html"` or `"pdf"`
   - `mode`: `ExportMode.ALWAYS` (auto-export after render), `ExportMode.MANUAL` (sidebar panel), `ExportMode.NEVER` (disabled)
   - `output_dir`, `filename`, `timestamp` (adds `-YYMMDD-HHMMSS` suffix)
   - `pdf`: optional `PdfConfig(format="A4", landscape=True, ...)` for PDF exports
3. **Audit export-aware widgets**: Scan all `bck_*.py` for bare `st.*` widget calls that should be `stx.*`
4. **Check image assets**: Verify all `st_image(uri=...)` references exist
5. **Report issues** and suggest fixes

---

## Constraints

- Follow ALL rules in CLAUDE.md
- No raw HTML/CSS — use only `stx.*` functions
- No hardcoded black/white — use the style system
- Style names in English only
- Always propose changes before applying (ask for confirmation)
