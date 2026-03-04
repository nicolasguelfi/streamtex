# Coherence Check Rules

Reference file for `/coherence:audit`. Defines 9 check categories.

---

## Check 1: API Coverage (scope: library, all)

**Goal**: Every public export in the library should be documented in at least one manual.

**Source**: `streamtex/streamtex/__init__.py` — extract all names from import statements.
**Target**: `streamtex-docs/manuals/**/blocks/**/*.py` — grep for usage of each export.

**Rules**:
- WARNING if an exported function/class appears in ZERO block files
- INFO if an export appears in blocks but has no `show_code()` example
- SKIP internal names (prefixed with `_`), type aliases, and re-exports of enums

**Known exceptions** (not expected in blocks):
- Low-level exports: `export_append`, `export_push_wrapper`, `export_pop_wrapper`, `generate_export_html`, `reset_export_buffer`, `is_export_active`
- Config internals: `get_block_helper_config`, `get_bib_config`, `get_gsheet_config`, `get_link_config`, `get_bib_registry`, `reset_bib_registry`
- Parser internals: `parse_bibtex_string`, `parse_ris_string`, `register_bib_parser`
- Utility re-exports: `generate_bib_stubs`, `export_bibtex`

---

## Check 2: Cheatsheet & Coding Standards Sync (scope: library, all)

**Goal**: The cheatsheet and coding standards reflect the current library API.

**Source files**:
- `streamtex/streamtex/__init__.py` (exports)
- Key module files: `write.py`, `code.py`, `book.py`, `grid.py`, `list.py`, `container.py`, `block_helpers.py`

**Target files**:
- `streamtex-claude/shared/references/streamtex_cheatsheet_en.md`
- `streamtex-claude/shared/references/coding_standards.md`

**Rules**:
- WARNING if a function's signature (new parameter) is not reflected in the cheatsheet
- ERROR if the coding standards recommend a pattern that contradicts current library behavior
- WARNING if the cheatsheet documents a function that no longer exists in `__init__.py`

**How to check signatures**: For each major function, read the `def` line in the source module. Compare parameter names with those listed in the cheatsheet.

---

## Check 3: Cross-Manual Block Consistency (scope: docs, blocks, all)

**Goal**: All manual blocks use consistent, up-to-date patterns.

**Scope**: `streamtex-docs/manuals/**/blocks/**/*.py`

**Rules**:
- WARNING if a block uses `textwrap.dedent(` in code (now auto-dedented)
- WARNING if a block has `import textwrap` but doesn't use it in code
- WARNING if a block uses an old API pattern (e.g., deprecated parameter name)
- WARNING if a `show_code()` example inside a block shows `import textwrap` as part of the example code (inside triple-quoted strings)
- INFO if import styles differ between blocks in the same manual (e.g., some use `from streamtex import *`, others explicit imports)

---

## Check 4: Profile File Sync (scope: profiles, all)

**Goal**: All copies of shared profile files are identical to their source of truth.

**Source of truth** → **Copies to check**:

| Source | Copies |
|--------|--------|
| `streamtex-claude/shared/references/coding_standards.md` | `streamtex/.claude/references/`, `streamtex-docs/.claude/references/`, `streamtex-docs/references/`, `projects/*/.claude/references/` |
| `streamtex-claude/shared/references/streamtex_cheatsheet_en.md` | Same locations as above |
| `streamtex-claude/profiles/project/commands/designer/*.md` | `projects/*/.claude/commands/designer/` |
| `streamtex-claude/profiles/project/designer/agents/*.md` | `projects/*/.claude/designer/agents/` |
| `streamtex-claude/profiles/project/designer/skills/*.md` | `projects/*/.claude/designer/skills/` |
| `streamtex-claude/profiles/documentation/commands/designer/*.md` | `streamtex-docs/.claude/commands/designer/` |
| `streamtex-claude/profiles/documentation/designer/agents/*.md` | `streamtex-docs/.claude/designer/agents/` |

**Method**: Read both files, compare content. If different, report as ERROR.

**Rules**:
- ERROR if file content differs between source and copy
- WARNING if a source file exists but has no copy in an expected location
- INFO: report total files checked and sync status

---

## Check 5: Version Alignment (scope: all)

**Goal**: Library version satisfies all dependency constraints.

**Source**: `streamtex/pyproject.toml` → `[project] version`
**Targets**: All `pyproject.toml` files in `streamtex-docs/`, `projects/*/`

**Rules**:
- WARNING if library version doesn't satisfy a `streamtex>=X.Y.Z` constraint
- INFO: report current library version and all constraints found

---

## Check 6: Block Structure Compliance (scope: docs, blocks, all)

**Goal**: All blocks follow canonical structure.

**Scope**: `streamtex-docs/manuals/**/blocks/bck_*.py` + `streamtex-docs/templates/**/blocks/bck_*.py`

**Rules**:
- WARNING if block lacks `class BlockStyles`
- WARNING if block lacks `def build()` function
- WARNING if block lacks `bs = BlockStyles` alias
- WARNING if block has `build()` not wrapped in `with st_block(...):`
- INFO if block doesn't use `show_code()` or `show_explanation()` (may be intentional)

---

## Check 7: Template Freshness (scope: blocks, all)

**Goal**: Project template reflects latest practices.

**Source**: `streamtex-docs/templates/template_project/`
**Compare with**: Latest patterns in `streamtex-docs/manuals/stx_manual_intro/blocks/`

**Rules**:
- WARNING if template has obsolete imports
- WARNING if template pyproject.toml is missing ruff ignore rules
- WARNING if template pyproject.toml is missing `[tool.pyright] extraPaths`
- INFO: report template version vs latest manual patterns

---

## Check 8: stx-guide Knowledge Base Sync (scope: profiles, all)

**Goal**: The global `stx-guide.md` skill accurately reflects the current ecosystem state.

**Source**: `~/.claude/commands/stx-guide.md`

**Cross-reference with**:
- All `manifest.toml` files in `streamtex-claude/profiles/*/` — command categories and counts
- `streamtex-claude/profiles/*/commands/*/` — actual command files
- `streamtex/streamtex/__init__.py` — public API (gotchas section)
- `streamtex-docs/manuals/` — manual list and ports

**Rules**:
- WARNING if a command category listed in a manifest.toml is missing from Section 4.2b table
- WARNING if the command count in Section 4.2b doesn't match the manifest
- WARNING if a profile listed by `install.py --list` is missing from stx-guide
- WARNING if a manual in `streamtex-docs/manuals/` is missing from Section 2 layout
- WARNING if a gotcha in Section 5 references deprecated behavior
- INFO: report stx-guide line count and last-known sync date

---

## Check 9: README Links for PyPI (scope: library, all)

**Goal**: README.md uses only absolute URLs so links work on PyPI, GitHub, and locally.

**Source**: `streamtex/README.md`

**Rules**:
- WARNING if any markdown link uses a relative path (e.g., `[text](FILE.md)` instead of `[text](https://github.com/nicolasguelfi/streamtex/blob/main/FILE.md)`)
- PyPI renders README.md but does NOT resolve relative links — they become broken
- `stx publish check` also detects this (check "README links")
- INFO: report total links found and how many are absolute vs relative

**How to check**: Regex `\[([^\]]+)\]\((?!https?://|#)([^)]+)\)` finds relative links.
