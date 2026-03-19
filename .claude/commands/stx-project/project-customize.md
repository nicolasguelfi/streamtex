# /stx-project:project-customize — Customize a StreamTeX project

Arguments: $ARGUMENTS (natural language description of desired changes)

## Trigger

The user describes the desired customization changes. Examples:

- `"switch to light theme with green palette"`
- `"add a TOC sidebar with numbering"`
- `"enable HTML export and banner mode"`
- `"adapt for auditorium projection (large text)"`
- `"change palette to blue and orange, add pagination"`

## Required readings

1. `book.py` — current project configuration
2. `custom/styles.py` — current palette and styles
3. `custom/themes.py` — current theme (if file exists)
4. `.streamlit/config.toml` — current Streamlit configuration
5. `.claude/references/coding_standards.md`
6. `.claude/designer/skills/style-conventions.md`

## Customization domains

### 1. Theme and colors

**Affected files**: `custom/styles.py`, `custom/themes.py`, `.streamlit/config.toml`

- Color palette: `primary`, `accent`, `highlight`, `success`, `muted`
- Streamlit theme: dark / light (in `.streamlit/config.toml`)
- Block background colors (via `Style.create()`)
- Accent colors for titles, links, bullets

### 2. Typography

**Affected files**: `custom/styles.py`, all blocks

- Font sizes: screen (`s.large` body) vs auditorium (`s.Large` body)
- Title hierarchy: `s.huge` > `s.Large` > `s.large`
- Bullet style in lists
- Custom font (if requested)

### 3. Navigation

**Affected files**: `book.py`

- **TOC**: on/off, mode `numbering=NumberingMode.SIDEBAR_ONLY` (default), `sidebar_max_level=2` (default)
- **Sidebar**: `initial_sidebar_state="expanded"` (always open by default)
- **Pagination**: on/off (paginate=True/False in st_book)
- **Marker**: on/off, navigation keys (PageUp/PageDown by default)
- **Banner**: on/off, configuration (title, logo, color)

### 4. Features

**Affected files**: `book.py`, `custom/styles.py`

- **HTML export**: on/off (ExportConfig in book.py)
- **Inspector**: on/off (live debug mode)
- **Zoom**: on/off, default value
- **Collection mode**: convert project to collection (add collection.toml)

## Workflow

### Step 1: Read the current configuration

Read the project files to understand the current state:
- Which theme is used?
- Which features are enabled?
- Which color palette?
- Which target audience?

### Step 2: Identify requested changes

Parse the user's description and determine:
- Which domains are affected (theme, typography, navigation, features)
- Which files need to be modified
- Are there any conflicts with the current configuration?

### Step 3: Propose modifications

Display a clear summary of the proposed changes:

```
Proposed changes:

1. custom/styles.py
   - primary : #1a1a2e -> #2d5016 (dark green)
   - accent  : #e94560 -> #4caf50 (green)
   + highlight : #81c784 (light green) [new]

2. .streamlit/config.toml
   - base = "dark" -> base = "light"

3. book.py
   + toc_config = TOCConfig(numbering=NumberingMode.SIDEBAR_ONLY, sidebar_max_level=2, search=True)
   + initial_sidebar_state="expanded"
   + paginate = True

Files affected: 3
Blocks to update: 0
```

**Ask for confirmation before applying.**

### Step 4: Apply modifications

Modify files in order:
1. `custom/styles.py` (palette, project-level styles)
2. `custom/themes.py` (theme if necessary)
3. `.streamlit/config.toml` (Streamlit theme)
4. `book.py` (navigation, features)
5. Individual blocks (only if font sizes change)

### Step 5: Validate

- Verify that no referenced style is missing
- Verify consistency between Streamlit theme and custom styles
- Display a summary of applied modifications

```
Applied modifications:
  custom/styles.py       — palette updated (3 colors)
  .streamlit/config.toml — theme switched to light
  book.py                — TOC + pagination enabled

Test: stx run
```

## Rules

- NEVER delete existing content in blocks
- Only modify blocks for font sizes (target audience change)
- Always use `Style.create()` for colors, never raw CSS
- Always propose a diff before applying
- If the change affects all blocks (e.g. audience change), warn the user about the number of files affected

## Constraints

- Follow ALL rules in CLAUDE.md
- No hardcoded black/white — use the style system
- No raw HTML/CSS
- Style names in English only
