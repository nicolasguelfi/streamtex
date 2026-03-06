# Coherence Check Rules

Reference file for `/coherence:audit`. Defines 12 check categories.

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
| `streamtex-claude/shared/commands/stx-guide.md` | `streamtex/.claude/commands/`, `streamtex-docs/.claude/commands/`, `projects/*/.claude/commands/` |

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

**Source**: `streamtex-claude/shared/commands/stx-guide.md`

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

---

## Check 10: Language Consistency — English (scope: all)

**Goal**: All ecosystem content must be written in English, except explicitly exempted files.

**Scope**: All text content across the ecosystem.

**Files to check**:

| Category | Paths | What to check |
|----------|-------|---------------|
| Library code | `streamtex/streamtex/**/*.py` | Docstrings, comments, string literals in error messages |
| Manual blocks | `streamtex-docs/manuals/**/blocks/**/*.py` | `st_write()` text, `show_explanation()`, `show_details()`, `show_code()` descriptions, docstrings, comments |
| Manual book.py | `streamtex-docs/manuals/**/book.py` | TOC entries, banner text, section titles |
| Claude profiles | `streamtex-claude/profiles/**/*.md` | All markdown content |
| Claude commands | `streamtex-claude/profiles/**/commands/**/*.md` | Command descriptions and instructions |
| Claude skills | `streamtex-claude/profiles/**/skills/**/*.md` | Skill content |
| Claude agents | `streamtex-claude/profiles/**/agents/**/*.md` | Agent prompts and instructions |
| Shared references | `streamtex-claude/shared/references/*.md` | Cheatsheet, coding standards |
| Project templates | `streamtex-docs/templates/**/*.py` | Same rules as manual blocks |
| README files | `*/README.md` | Full content |
| CLAUDE.md files | `*/CLAUDE.md`, `projects/*/CLAUDE.md` | Full content |

**Explicit exceptions** (allowed in French or other languages):
- `streamtex-claude/shared/commands/stx-guide.md` — French by design (user-facing guide)
- Manual content that demonstrates multilingual features (e.g., i18n examples)
- Inline code identifiers (variable/function names are language-neutral)

**Rules**:
- ERROR if a Claude profile/command/skill/agent file contains non-English prose
- WARNING if a manual block contains non-English text in `st_write()`, `show_explanation()`, or `show_details()`
- WARNING if docstrings or comments in library code are not in English
- WARNING if a `CLAUDE.md` or `README.md` contains non-English prose
- INFO: report total files scanned and language status

**How to check**: For each file, sample text passages (docstrings, markdown paragraphs, `st_write()` string arguments). Flag content containing common non-English patterns:
- French indicators: words like `le`, `la`, `les`, `un`, `une`, `des`, `est`, `sont`, `avec`, `pour`, `dans`, `cette`, `nous`, `vous` in prose context
- Look for accented characters typical of French (`é`, `è`, `ê`, `ë`, `à`, `ù`, `ç`, `ô`, `î`) in non-code text
- Ignore: code identifiers, URLs, file paths, proper nouns

---

## Check 11: Claude Artifact API Validation (scope: profiles, all)

**Goal**: All Python code examples in Claude artifacts (skills, agents, commands) use correct, current StreamTeX API.

**Why this check is critical**: Users generate most of their project code via Claude artifacts (`/designer:block-new`, `/project:project-init`, agents). If these artifacts contain incorrect API usage, every generated project inherits the bugs.

**Scope**: All `.md` files containing Python code blocks in:
- `streamtex-claude/profiles/**/skills/**/*.md`
- `streamtex-claude/profiles/**/agents/**/*.md`
- `streamtex-claude/profiles/**/commands/**/*.md`
- `streamtex-claude/shared/commands/*.md`

**Method**:
1. Extract all fenced Python code blocks (` ```python ... ``` `) from each `.md` file
2. For each code block, check the rules below against the actual library API
3. To verify the actual API, introspect the library:
   - `from streamtex.enums import ListTypes; dir(ListTypes)` → valid enum members
   - `from streamtex.enums import Tags; dir(Tags)` → valid tag names
   - `from streamtex import *; inspect.signature(st_list)` → valid parameters
   - `from streamtex import *; inspect.signature(st_image)` → valid parameters
   - (repeat for all `st_*` functions used in code blocks)

**Rules**:

### Enum validation
- ERROR if code uses `lt.ul` or `lt.ol` (correct: `lt.unordered`, `lt.ordered`)
- ERROR if code uses any `lt.<name>` where `<name>` is not in `dir(ListTypes)`
- ERROR if code uses any `t.<name>` where `<name>` is not in `dir(Tags)`

### Function signature validation
- ERROR if code passes a keyword argument that does not exist in the function signature
  - Example: `st_list(..., items=[...])` — `items` is not a parameter of `st_list()`
  - Example: `st_image(..., caption="...")` — `caption` is not a parameter of `st_image()`
- ERROR if code uses a function as a regular call when it is a context manager
  - Example: `st_list(style, items=[...])` should be `with st_list(...) as l:` + `l.item()`
- WARNING if code passes positional arguments in the wrong order vs. the signature

### st_grid validation
- ERROR if `cols` receives a Python list (e.g., `st_grid([1, 1])`) — must be `int` or `str`
- WARNING if code uses fixed columns without responsive pattern (same as coding standards rule)

### Cross-reference with cheatsheet
- WARNING if an artifact shows a pattern that contradicts the cheatsheet
- WARNING if an artifact uses a deprecated parameter (e.g., `banner_color` instead of `banner=BannerConfig(...)`)

**How to check** (automated introspection):
```bash
uv run python -c "
from streamtex.enums import ListTypes, Tags
print('ListTypes:', [x for x in dir(ListTypes) if not x.startswith('_')])
print('Tags:', [x for x in dir(Tags) if not x.startswith('_')])
"
uv run python -c "
import inspect
from streamtex import st_list, st_image, st_grid, st_write, st_code, st_space, st_block, st_overlay
for fn in [st_list, st_image, st_grid, st_write, st_code, st_space, st_block, st_overlay]:
    print(f'{fn.__name__}: {inspect.signature(fn)}')
"
```
Then for each code block, parse function calls and verify parameter names and enum values against the introspected API.

---

## Check 12: Test Coverage Sync (scope: library, tests, all)

**Goal**: Tests stay up-to-date when the library API changes. A modified or new public function should have corresponding test coverage, and existing tests should not use stale signatures.

**Why this check is critical**: Library changes (new parameters, renamed functions, modified behavior) can silently invalidate existing tests. Tests that pass but test the wrong thing (e.g., missing a new required parameter) give a false sense of safety.

**Source files**:
- `streamtex/streamtex/__init__.py` — public exports
- `streamtex/streamtex/*.py` — module source files (function signatures, classes)

**Target files**:
- `streamtex/tests/test_*.py` — all test files

### Sub-check 12a: Test file coverage

**Method**: For each source module `streamtex/<module>.py`, check if a corresponding `tests/test_<module>.py` exists.

**Rules**:
- WARNING if a source module with public functions has no corresponding test file
- INFO: report module → test file mapping and coverage ratio

**Known exceptions** (modules not expected to have dedicated test files):
- `__init__.py`, `constants.py`, `enums.py`, `utils.py` (tested indirectly)
- Modules with only re-exports or trivial wrappers

### Sub-check 12b: Signature drift

**Method**: For each public function in `__init__.py`, introspect its current signature. Then grep all `test_*.py` files for calls to that function. Compare keyword arguments used in tests against the actual signature.

**Rules**:
- ERROR if a test calls a function with a keyword argument that no longer exists in the signature
- WARNING if a function gained a new parameter (not default-only) and no test exercises it
- WARNING if a function's parameter was renamed but tests still use the old name
- INFO: report total public functions checked and how many have test coverage

**How to check** (automated introspection):
```bash
uv run python -c "
import inspect, importlib
import streamtex
# Get all public exports
exports = [name for name in dir(streamtex) if not name.startswith('_')]
for name in sorted(exports):
    obj = getattr(streamtex, name)
    if callable(obj) and not isinstance(obj, type):
        sig = inspect.signature(obj)
        print(f'{name}: {sig}')
"
```
Then for each test file, parse function calls and compare keyword arguments against introspected signatures.

### Sub-check 12c: Deprecated API in tests

**Method**: Scan all `test_*.py` files for usage of deprecated patterns.

**Rules**:
- WARNING if a test imports a name that is no longer exported from `__init__.py`
- WARNING if a test uses a deprecated parameter (same list as Check 11 cross-reference)
- WARNING if a test mocks a function path that has been moved or renamed

### Sub-check 12d: New features without tests

**Method**: Compare recent git changes in `streamtex/*.py` against `tests/test_*.py`. For functions modified or added since the last release tag, check if corresponding tests exist.

**Rules**:
- WARNING if a new public function (added since last release) has zero test assertions
- WARNING if a function with modified signature (since last release) has no test exercising the new/changed parameters
- INFO: report functions changed since last release and their test status

**How to check**:
```bash
# List functions changed since last release tag
git diff $(git describe --tags --abbrev=0)..HEAD --name-only -- 'streamtex/*.py' | sort
# Then introspect each changed module for new/modified function signatures
```
