# Style Consistency Checker Agent

## Role

Reviews the document's technical coherence -- CSS styles, StreamTeX conventions, block structure validity, and book.py configuration. This agent ensures the project is well-formed, follows StreamTeX conventions, and has no structural or technical issues that would cause runtime errors or maintenance problems.

## Before Starting

Read these files:
1. .claude/designer/skills/style-conventions.md
2. .claude/references/streamtex_cheatsheet_en.md
3. The project's book.py
4. The project's blocks/ directory listing

## Methodology

1. **Check all blocks follow canonical structure**:
   - Each block file has a `BlockStyles` class with CSS definitions
   - Each block file has a `build()` function as entry point
   - BlockStyles class uses `@dataclass` or class variables properly
   - Build function signature matches expected pattern
   - Imports are correct (`from streamtex import *`)
2. **Verify style naming conventions**:
   - Style names in English, descriptive, using snake_case
   - No duplicate style names across blocks (unless intentional override)
   - Style names match their purpose (e.g., `title_container`, not `div1`)
   - CSS class names follow project conventions
3. **Check CSS consistency**:
   - Same visual properties used consistently for same purposes across blocks
   - No conflicting styles (same class name, different definitions)
   - No orphaned styles (defined but never used)
   - No inline styles that should be in BlockStyles
   - CSS units consistent (rem vs px vs em -- pick one system)
4. **Verify book.py configuration**:
   - All block files in blocks/ are registered in book.py
   - Block order matches intended navigation flow
   - Part/section grouping is correct
   - Features (sidebar, navigation, etc.) properly configured
   - No import errors (all referenced blocks exist)
5. **Check blocks.csv / __init__.py registry coherence**:
   - If blocks.csv exists: all entries match actual files
   - __init__.py exports match actual block modules
   - No missing or extra entries
6. **Detect anti-patterns**:
   - Inline styles that should be in BlockStyles
   - Duplicated style definitions across blocks (should be shared)
   - Hard-coded colors/sizes that should use variables
   - `textwrap.dedent()` wrapping `show_explanation`/`show_details`/`show_code`/`st_write` (these auto-dedent)
   - Missing error handling in data-loading blocks

## Output Format

```markdown
# Style Consistency Check Report

**Project**: <project name>
**Date**: YYYY-MM-DD
**Blocks checked**: N
**Issues found**: N (critical: N, major: N, minor: N, suggestions: N)

## Block Structure Audit

| Block | BlockStyles | build() | Imports | Status |
|-------|-------------|---------|---------|--------|
| bck_1_1_intro | OK | OK | OK | Pass |
| bck_1_2_concepts | Missing | OK | OK | FAIL - no BlockStyles class |
| bck_2_1_api | OK | Wrong signature | OK | FAIL - build(config) should be build() |
| ... | ... | ... | ... | ... |

## Style Naming Audit

| Issue | Block | Style Name | Recommendation |
|-------|-------|------------|----------------|
| Non-descriptive | bck_1_2 | `s1`, `s2` | Rename to `header_section`, `content_section` |
| Duplicate name | bck_1_3, bck_2_1 | `card_style` | Different definitions -- rename one or extract shared |
| Wrong language | bck_3_1 | `titre_principal` | Rename to `main_title` (English convention) |

## CSS Consistency Audit

| Property | Variations | Blocks | Recommendation |
|----------|------------|--------|----------------|
| Primary color | #1a73e8, #1976d2, blue | 3, 5, 8 | Standardize to #1a73e8 |
| Border radius | 8px, 0.5rem, 10px | 2, 4, 7 | Standardize to 8px |
| Font family | system-ui, sans-serif | 1, 6 | Standardize to system-ui |

## book.py Configuration

| Check | Status | Details |
|-------|--------|---------|
| All blocks registered | Warning | bck_3_2_extra.py not in book.py |
| Import validity | OK | All imports resolve |
| Block order | OK | Matches document plan |
| Feature config | OK | Sidebar and navigation enabled |

## Anti-Patterns Detected

| # | Severity | Block | Anti-Pattern | Fix |
|---|----------|-------|-------------|-----|
| 1 | MAJOR | bck_2_1 | textwrap.dedent() wrapping st_write() | Remove dedent -- st_write auto-dedents |
| 2 | MAJOR | bck_1_3 | Inline style="color: red" in HTML | Move to BlockStyles |
| 3 | MINOR | bck_3_1 | Hard-coded #1a73e8 in 5 places | Extract to style variable |
| 4 | SUGGESTION | bck_1_1, bck_1_2 | Identical card_style in both | Extract to shared styles module |

## Findings Summary

| # | Severity | Block/File | Technical Issue | Convention Violated | Suggested Fix |
|---|----------|-----------|-----------------|---------------------|---------------|
| 1 | CRITICAL | bck_2_1 | build() takes unexpected parameter | Block structure convention | Change to `def build():` |
| 2 | MAJOR | bck_1_2 | No BlockStyles class | Block structure convention | Add BlockStyles dataclass |
| ... | ... | ... | ... | ... | ... |

## Top 3 Priorities

1. <most impactful technical fix>
2. <second most impactful>
3. <third most impactful>
```
