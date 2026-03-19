# /stx-designer:audit — Verify project quality

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS] <description>`

**Options** (parsed before the description text):
- `--all` — Audit the entire project (all blocks, styles, book.py)
- `--target <name>` — Audit a specific element: block name (e.g. `bck_intro`), `styles`, `book`
- `--help` — Show the stx-designer cheatsheet (see init.md Help section)

**Description**: Free-form text providing additional context or directives.
- Include "presentation" or "projection" to apply live projection rules
- Include "migration" to apply post-migration checks
- Include specific concerns (e.g. "check font sizes", "verify color contrast")

If no `--all` or `--target` is given AND no target is detectable from the description,
ask the user what they want to audit.

### Examples

```
/stx-designer:audit --all
/stx-designer:audit --all check presentation compliance
/stx-designer:audit --target bck_text_styles
/stx-designer:audit --target bck_text_styles verify projection readability
/stx-designer:audit --target styles check for dark mode compatibility
/stx-designer:audit --target book verify TOC and navigation config
/stx-designer:audit --all check migration quality
```

## Required readings

Always read before auditing:
1. `.claude/references/coding_standards.md` — coding rules
2. `.claude/designer/skills/style-conventions.md` — style naming rules

### Documentation reference (recommended)

When auditing, consult real manual blocks as the gold standard for correct patterns:

1. **Check if manuals exist**: Look for `../../streamtex-docs/manuals/` (or `../streamtex-docs/manuals/`).
2. **If found** — when an audit finding is ambiguous, compare the audited code against similar manual blocks to determine the correct pattern. This is especially useful for:
   - API usage validation (correct function signatures, valid parameters)
   - Style patterns (how `BlockStyles` should be structured)
   - Block structure (canonical `build()` organization)
3. **If NOT found** — rely on cheatsheet and coding_standards.md (no action needed)

### Rule set selection

The audit applies different rule sets based on context:

| Context | Rules to load | Source |
|---------|--------------|--------|
| **Base** (always) | Structure, imports, style conventions | `coding_standards.md` |
| **Visual design** (blocks) | Font sizes, layout, spacing, themes | `visual-design-rules.md` |
| **Slide design** (blocks) | L1/L2/L3 grid, telegraphic text | `slide-design-rules.md` |
| **Presentation** (desc contains "presentation"/"projection") | 48pt min, keywords only, no helpers | `presentation-design-rules.md` |
| **Migration** (desc contains "migration") | Color fidelity, HTML structure | Migration rules |
| **Styles** (target = "styles") | Naming, reuse, dark mode compat | `style-conventions.md` |

### Auto-detection of presentation profile

If `.claude/designer/presentation/` exists OR `.claude/.stx-profile` contains "presentation",
automatically include presentation rules (no need for the user to specify "presentation" in desc).

## Audit targets

### Block audit (`--target <block_name>` or `--all`)

For each block file, check:

#### Structure (CRITICAL)
- [ ] Has mandatory imports (`streamtex`, `styles`, `enums`, `custom.styles`)
- [ ] Has `BlockStyles` class (or `BStyles`) with `bs` alias
- [ ] Has `build()` function
- [ ] No raw HTML strings (`<div`, `<span`, `<style`, `unsafe_allow_html`)
- [ ] No raw CSS strings outside of `Style()` or `ns()` constructors
- [ ] Uses `stx.*` functions, not raw `st.*` for content
- [ ] No simulated lists — any enumeration of 2+ items must use `st_list()` with `l.item()`, not successive `st_write()` with dashes/bullets (`"- item"`, `"• item"`, `"1. item"`), nor `\n`-separated bullet text in a single `st_write()`

#### Visual design (ERROR)
- [ ] `build()` wraps content in `with st_block(s.center_txt):`
- [ ] Main heading uses `tag=t.div, toc_lvl="1"`
- [ ] Body text uses appropriate font size for audience
- [ ] Multi-line text blocks use `"""\..."""` (auto-dedented)
- [ ] No string concatenation in `st_write()` calls
- [ ] `st_space("v", 2)` between sections, `st_space("v", 1)` within
- [ ] Section structure follows canonical order

#### Presentation-specific (CRITICAL — only when presentation rules apply)
- [ ] Body text uses `s.Large` (48pt) or above
- [ ] Section titles use `s.Huge` (96pt) or `s.huge` (80pt)
- [ ] No bullet exceeds 7 words, no section has more than 3 bullets
- [ ] No `muted`/`subtle` color on body text
- [ ] No image below 400px width
- [ ] `st_space(size=3)` minimum between sections
- [ ] No helper boxes (`show_explanation`, `show_details`, `show_code`)

#### Assets (WARNING)
- [ ] All `uri=` values in `st_image()` point to existing files
- [ ] Image naming follows convention
- [ ] No missing or broken references

#### TOC (WARNING)
- [ ] Heading hierarchy is consistent (no level jumps > 1)
- [ ] All major sections have `toc_lvl` entries

#### Marker visibility (ERROR)
- [ ] Block contains at least one `st_write(...)` with `toc_lvl="1"` — required for sidebar and floating bar navigation (via `auto_marker_on_toc`). A block without any `toc_lvl` heading is invisible in all navigation panels.
- [ ] If using `st_ai_image_widget()`, confirm no invalid kwargs are passed (`editable` is NOT a valid parameter — the widget is inherently interactive)

### Style audit (`--target styles`)

Check `custom/styles.py` and all `BlockStyles` classes:

- [ ] No duplicate style definitions
- [ ] No hardcoded black/white (should be theme-controlled)
- [ ] English-only style names
- [ ] No unused styles in `BlockStyles`
- [ ] Dark mode compatibility
- [ ] Style reuse opportunities (repeated compositions)

### Book audit (`--target book`)

Check `book.py` configuration:

- [ ] All blocks referenced in `st_book()` exist as files
- [ ] No orphaned block files (exist but not in `st_book()`)
- [ ] TOC config is present and valid
- [ ] Sidebar state is set
- [ ] Features are consistent (e.g., marker requires pagination)

## Output format

```
# Audit Report: <target>

## Summary
- CRITICAL: N issues
- ERROR: N issues
- WARNING: N issues
- PASS: N checks

## CRITICAL Issues
### [C1] <rule name>
- **File**: <path>:<line>
- **Found**: <what's wrong>
- **Expected**: <what it should be>
- **Fix**: <specific fix instruction>

## ERROR Issues
### [E1] ...

## WARNING Issues
### [W1] ...

## Passed Checks
- [x] <check name>

## Recommendation
Use `/stx-designer:fix --target <target>` to auto-fix issues.
```

## Constraints

- Report only — do NOT modify any files
- Be specific with line numbers and fix suggestions
- Severity levels: CRITICAL (must fix, broken), ERROR (should fix), WARNING (should consider)
