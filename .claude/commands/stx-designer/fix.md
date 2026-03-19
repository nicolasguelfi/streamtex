# /stx-designer:fix — Auto-fix project issues

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS] <description>`

**Options** (parsed before the description text):
- `--all` — Fix all issues in the entire project
- `--target <name>` — Fix a specific element: block name (e.g. `bck_intro`), `styles`, `book`
- `--help` — Show the stx-designer cheatsheet (see init.md Help section)

**Description**: Free-form text providing additional context or directives.
- Include "presentation" or "projection" to apply live projection fixes
- Include specific concerns (e.g. "fix font sizes only", "fix colors")

If no `--all` or `--target` is given AND no target is detectable from the description,
ask the user what they want to fix.

### Examples

```
/stx-designer:fix --all
/stx-designer:fix --all apply presentation rules
/stx-designer:fix --target bck_text_styles
/stx-designer:fix --target bck_text_styles fix projection readability
/stx-designer:fix --target styles refactor duplicates
```

## Documentation reference (recommended)

Before fixing, check if real manual blocks are available for reference:

1. **Check if manuals exist**: Look for `../../streamtex-docs/manuals/` (or `../streamtex-docs/manuals/`).
2. **If found** — when applying fixes, consult similar manual blocks to ensure the fix follows the correct pattern. Search with: `../../streamtex-docs/manuals/stx_manual_*/blocks/**/bck_*<keyword>*.py`
3. **If NOT found** — rely on cheatsheet and coding_standards.md

## Workflow

### Step 1: Implicit audit

Before fixing, run an implicit audit (following `/stx-designer:audit` logic)
to identify all issues. DO NOT show the full audit report — just summarize
the findings.

### Step 2: Propose fixes

Present a summary of what will be changed:

```
Issues found: 3 CRITICAL, 5 ERROR, 2 WARNING

Proposed fixes:
  1. [C1] bck_text_styles.py:15 — s.medium → s.Large (body font too small for projection)
  2. [C2] bck_text_styles.py:23 — "Long sentence about..." → "Key concept: short phrase"
  3. [E1] bck_text_styles.py:8 — Missing BlockStyles.question role
  ...

Files to modify: 2
```

**Ask for confirmation before applying.**

### Step 3: Apply fixes

Apply fixes in order of severity (CRITICAL first), following the fix catalog below.

### Step 4: Verify

After applying:
1. Check that no syntax errors were introduced (imports, indentation)
2. Run a quick re-audit to confirm issues are resolved
3. Report all changes made with before/after comparisons

## Fix catalog

### Block fixes

#### Font size corrections
| Found | Fix (screen) | Fix (presentation) |
|-------|-------------|-------------------|
| `s.medium` on body | `s.large` | `s.Large` |
| `s.big` on body | `s.large` | `s.Large` |
| `s.large` on titles | `s.huge` | `s.Huge` |
| `s.Large` on main titles | `s.huge` | `s.Huge` |

#### Text style corrections
| Found | Fix |
|-------|-----|
| Full sentences as bullets | Reduce to 5-7 word keyword phrases |
| Paragraphs in slides | Convert to 3 keyword bullets max |
| `muted`/`subtle` on body text | Remove or use `accent`/`primary` |
| Multiple `st_write` for inline text | Merge into ONE `st_write` with tuples |

#### Structure corrections
| Found | Fix |
|-------|-----|
| Missing `BlockStyles` class | Add with `heading` and `sub` roles |
| Missing `bs` alias | Add `bs = BlockStyles` |
| Missing `build()` | Wrap content in `def build():` |
| Raw HTML strings | Convert to `Style()` composition |
| Raw `st.*` for content | Replace with `stx.*` equivalents |

#### Spacing corrections (presentation)
| Found | Fix |
|-------|-----|
| `st_space(size=1)` between sections | `st_space(size=3)` or `st_space(size=4)` |
| `st_space(size=2)` between sections | `st_space(size=3)` minimum |

#### Helper box removal (presentation only)
| Found | Fix |
|-------|-----|
| `show_explanation(...)` | `st_write(bs.body, ...)` |
| `show_details(...)` | Remove or convert to keyword bullets |
| `show_code(...)` | Remove (not for presentation slides) |

#### Image fixes
| Found | Fix |
|-------|-----|
| Image `width` < 400px (presentation) | Increase to 600px+ |
| Missing image placeholder | Add placeholder with generation prompt comment |

### Style fixes (`--target styles`)

| Found | Fix |
|-------|-----|
| Duplicate style definitions | Remove duplicates, keep one |
| Inline CSS in blocks | Extract to `custom/styles.py` |
| Non-English style names | Rename to English equivalents |
| Hardcoded black/white | Remove or use theme-aware alternatives |
| Unused styles in `BlockStyles` | Remove unused entries |

### Book fixes (`--target book`)

| Found | Fix |
|-------|-----|
| Orphaned blocks (not in `st_book()`) | Warn user, suggest adding or removing |
| Missing TOC config | Add default `TOCConfig` |
| Missing sidebar state | Add `initial_sidebar_state="expanded"` |

## Constraints

- Follow ALL rules in CLAUDE.md
- Only modify what violates the rules — preserve existing content and structure
- Always propose changes before applying (ask for confirmation)
- After fixing, display a before/after summary
