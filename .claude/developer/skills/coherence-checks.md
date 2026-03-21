# Coherence Check Rules

Reference file for `/stx-coherence:audit`. Defines 22 check categories.

---

## Check 1: API Coverage (scope: library, all)

**Goal**: Every public export in the library should be documented in at least one manual.

**Source**: `streamtex/streamtex/__init__.py` — extract all names from import statements.
**Target**: `streamtex-docs/manuals/**/blocks/**/*.py` — grep for usage of each export.

**Rules**:
- WARNING if an exported function/class appears in ZERO block files
- INFO if an export appears in blocks but has no `show_code()` example
- SKIP internal names (prefixed with `_`), type aliases, and re-exports of enums

**Presentation exports to verify**: `PresentationConfig`, `set_presentation_config`, `get_presentation_config`, `st_presentation_footer`, `add_presentation_options`

**Known exceptions** (not expected in blocks):
- Low-level exports: `export_append`, `export_push_wrapper`, `export_pop_wrapper`, `generate_export_html`, `reset_export_buffer`, `is_export_active`
- Config internals: `get_block_helper_config`, `get_bib_config`, `get_gsheet_config`, `get_link_config`, `get_bib_registry`, `reset_bib_registry`, `get_ai_image_config`, `get_slide_break_config`, `get_presentation_config`
- Display/layout internals: `PageLayout`, `ViewMode`, `SlideBreakDisplayConfig`, `ProfileConfig`, `AssetMode`
- Parser internals: `parse_bibtex_string`, `parse_ris_string`, `register_bib_parser`
- Utility re-exports: `generate_bib_stubs`, `export_bibtex`, `load_css`, `exec_static`, `resolve_content`, `inject_link_preview_scaffold`, `add_wrap_all_option`, `add_slide_break_options`
- Error/result types: `AIImageError`, `AIImageResult`, `BibParseError`, `GSheetError`
- AI image internals: `is_cached`, `list_providers`
- Registry internals: `FileCategoryRegistry`
- Style internals: `StreamTeX_Styles`

---

## Check 2: Cheatsheet & Coding Standards Sync (scope: library, all)

**Goal**: The cheatsheet and coding standards reflect the current library API.

**Source files**:
- `streamtex/streamtex/__init__.py` (exports)
- Key module files: `write.py`, `code.py`, `book.py`, `grid.py`, `list.py`, `container.py`, `block_helpers.py`, `presentation.py`

**Target files**:
- `streamtex-claude/shared/references/streamtex_cheatsheet_en.md`
- `streamtex-claude/shared/references/coding_standards.md`

**Rules**:
- WARNING if a function's signature (new parameter) is not reflected in the cheatsheet
- ERROR if the coding standards recommend a pattern that contradicts current library behavior
- WARNING if the cheatsheet documents a function that no longer exists in `__init__.py`
- WARNING if `presentation.py` signatures (`PresentationConfig`, `set_presentation_config`, `get_presentation_config`, `st_presentation_footer`, `add_presentation_options`) are missing from the cheatsheet

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
| `streamtex-claude/profiles/project/commands/stx-designer/*.md` | `projects/*/.claude/commands/stx-designer/` |
| `streamtex-claude/profiles/project/designer/agents/*.md` | `projects/*/.claude/designer/agents/` |
| `streamtex-claude/profiles/project/designer/skills/*.md` | `projects/*/.claude/designer/skills/` |
| `streamtex-claude/profiles/project/designer/templates/*.md` | `projects/*/.claude/designer/templates/` |
| `streamtex-claude/profiles/project/designer/tools/*.md` | `projects/*/.claude/designer/tools/` |
| `streamtex-claude/profiles/documentation/designer/agents/*.md` | `streamtex-docs/.claude/designer/agents/` |
| `streamtex-claude/shared/commands/stx-guide.md` | `streamtex/.claude/commands/`, `streamtex-docs/.claude/commands/`, `projects/*/.claude/commands/` |

**Method**: First verify source existence, then read both files, compare content. If different, report as ERROR.

**Rules**:
- ERROR if a source file declared in a manifest `[shared]` section does not exist in `shared/references/` or `shared/commands/` (source existence guard)
- ERROR if file content differs between source and copy
- WARNING if a source file exists but has no copy in an expected location
- INFO: report total files checked and sync status
- INFO: report any files found in `.claude/custom/` (user customizations detected)
- WARNING if a file in `.claude/custom/references/` has the same name as a file in `.claude/references/` (potential shadow/conflict)
- WARNING if a file in `.claude/custom/skills/` has the same name as a file in `.claude/developer/skills/` or `.claude/designer/skills/` (potential shadow/conflict)

---

## Check 5: Version Alignment (scope: library, all)

**Goal**: Library version is consistent across all locations and satisfies all dependency constraints.

**Source files**:
- `streamtex/pyproject.toml` → `[project] version`
- `streamtex/streamtex/__init__.py` → `__version__`
- `streamtex/CHANGELOG.md` → latest `## [X.Y.Z]` entry

**Targets**: All `pyproject.toml` files in `streamtex-docs/`, `projects/*/`

**Rules**:
- ERROR if `pyproject.toml` version differs from `__init__.py` `__version__`
- ERROR if CHANGELOG.md latest entry version differs from `pyproject.toml` version
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
- WARNING if topic "presentation" is missing from the topics table or does not document PresentationConfig
- WARNING if CLI templates documented in stx-guide do not match `AVAILABLE_TEMPLATES` in `install_cmd.py`
- WARNING if presets documented in stx-guide do not match `PRESET_ORDER` in `workspace_cmd.py`
- WARNING if the distinction between CLI templates and stx-designer templates is not documented
- WARNING if `/stx-issue:*` commands are missing from the stx-guide topics table or Section 4e
- WARNING if `/stx-issue:bug`, `/stx-issue:feature`, `/stx-issue:question`, `/stx-issue:docs`, `/stx-issue:comment`, `/stx-issue:list` are missing from the quick reference table (Section 6)
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
- `streamtex-claude/cursor/*.md` — Internal planning documents (not user-facing)
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

**Why this check is critical**: Users generate most of their project code via Claude artifacts (`/stx-designer:update`, `/stx-designer:init`, agents). If these artifacts contain incorrect API usage, every generated project inherits the bugs.

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
- WARNING if `test_presentation.py` does not exist (presentation module must have dedicated tests)
- INFO: report module → test file mapping and coverage ratio

**Known exceptions** (modules not expected to have dedicated test files):
- `__init__.py`, `constants.py`, `enums.py`, `utils.py` (tested indirectly)
- `block_helpers.py` — covered indirectly by `test_export_guard.py`
- `search.py` — covered indirectly by `test_book_search_markers.py`
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

---

## Check 13: Manual Blocks → Library API Existence (scope: docs, all)

**Goal**: Every `st_*` / `stx.*` function call in manual block **rendered code** must exist in the current library API. This is the reverse of Check 1.

**Why this check is critical**: Manuals are the user-facing documentation. If a block calls a function that was renamed, removed, or restructured in the library, the manual will crash at runtime — or worse, silently show nothing.

**Scope**: `streamtex-docs/manuals/**/blocks/**/*.py`

**What to check**: Rendered code ONLY — skip example strings inside `show_code()`, `show_explanation()`, `show_details()`.

**Method**:
1. Build the list of all valid exports: read `streamtex/streamtex/__init__.py`, extract all names
2. For each block file, extract all `st_*` and `stx.*` function calls at **block indentation level** (outside triple-quoted strings)
3. Verify each call exists in the exports list

**How to distinguish rendered vs example code**:
- Code **inside** `show_code("""...""")`, `show_explanation("""...""")`, `show_details("""...""")` string arguments → SKIP (example only, shown to user)
- Code **inside** `show_code(file="...")` → SKIP (example loaded from file)
- `st_*()` calls at block indentation level (inside `def build():`) → CHECK (executed at runtime)
- Calls inside `with st_block(...)`, `with st_grid(...)`, `with st_list(...)` → CHECK

**Rules**:
- ERROR if a rendered `st_*()` call references a function not in `__init__.py` exports
- ERROR if a rendered call uses `stx.<name>` where `<name>` is not an attribute of the `streamtex` module
- WARNING if a block imports a submodule path that no longer exists (e.g., `from streamtex.foo import bar`)
- INFO: report total rendered calls checked, how many are valid, how many blocks scanned

**How to check** (automated introspection):
```bash
uv run python -c "
import streamtex
exports = [n for n in dir(streamtex) if not n.startswith('_')]
print('\n'.join(sorted(exports)))
"
```
Then for each block, parse rendered `st_*()` calls and verify against the exports list.

---

## Check 14: Manual Examples Signature Coherence (scope: docs, all)

**Goal**: Function call signatures used in manual `show_code()` examples must match the current library function signatures (parameter names, parameter existence).

**Why this check is critical**: Users copy-paste code from `show_code()` examples. If an example uses a parameter that was renamed or removed, the user's code breaks. This erodes trust in the documentation.

**Scope**: `streamtex-docs/manuals/**/blocks/**/*.py` — specifically the content inside `show_code()` string arguments.

**Method**:
1. Introspect the library to get current signatures for all major `st_*` functions
2. For each block file, extract code from `show_code("""...""")` string arguments
3. Parse `st_*()` function calls within those strings
4. Compare keyword arguments against the actual function signature

**Rules**:
- ERROR if an example uses a keyword argument that does not exist in the function signature
  - Example: `st_image(caption="...")` but `st_image` has no `caption` parameter
  - Example: `st_list(items=[...])` but `st_list` has no `items` parameter
- ERROR if an example calls a function that no longer exists in the library
- WARNING if an example uses a deprecated parameter (even if still accepted for backward compat)
- WARNING if an example shows a context manager usage for a non-context-manager function, or vice versa
  - Example: `with st_write(...)` — `st_write` is NOT a context manager
  - Example: `st_list(style, items=[...])` — `st_list` IS a context manager
- WARNING if an example shows positional arguments in the wrong order vs the signature
- INFO: report total examples checked, total `st_*` calls in examples, issues found

**How to check** (automated introspection):
```bash
uv run python -c "
import inspect
from streamtex import st_list, st_image, st_grid, st_write, st_code, st_space, st_block, st_span
from streamtex import st_book, st_collection, st_markdown, st_mermaid, st_plantuml, st_tikz, st_latex
from streamtex import st_ai_image, st_ai_image_widget, st_slide_break, st_br, st_overlay
from streamtex import show_code, show_explanation, show_details, show_code_inline
for fn in [st_list, st_image, st_grid, st_write, st_code, st_space, st_block, st_span,
           st_book, st_collection, st_markdown, st_mermaid, st_plantuml, st_tikz, st_latex,
           st_ai_image, st_ai_image_widget, st_slide_break, st_br, st_overlay,
           show_code, show_explanation, show_details, show_code_inline]:
    print(f'{fn.__name__}: {inspect.signature(fn)}')
"
```
Then for each `show_code()` string, parse function calls and verify keyword arguments.

**Interaction with Check 11**: Check 11 validates code in Claude artifacts (skills, agents, commands). Check 14 validates code in manual `show_code()` examples. Together they cover all user-facing code examples in the ecosystem.

---

## Check 15: Manual Enum & Constant Coherence (scope: docs, all)

**Goal**: All enum members, class attributes, and constant values referenced in manual blocks (both rendered and examples) must exist in the current library.

**Why this check is critical**: Enums and constants are frequently refactored (renamed, reorganized, deprecated). A block using `ListTypes.ul` when the correct member is `ListTypes.unordered` will crash silently or raise an AttributeError at runtime.

**Scope**: `streamtex-docs/manuals/**/blocks/**/*.py` (both rendered code and `show_code()` examples)

**Method**:
1. Introspect the library to get valid members for all key enums and classes
2. For each block file, extract all attribute accesses on known types
3. Verify each attribute exists

**Enums and classes to validate**:

| Import | Variable | Valid members (introspect to get full list) |
|--------|----------|---------------------------------------------|
| `from streamtex.enums import ListTypes` | `lt` | `unordered`, `ordered`, `custom`, ... |
| `from streamtex.enums import Tags` | `t` | `div`, `span`, `p`, `h1`-`h6`, ... |
| `from streamtex import PdfMode` | — | `CONTINUOUS`, `PAGINATED` |
| `from streamtex import PdfConfig` | — | `mode`, `format`, `landscape`, `scale`, `margins`, ... |
| `from streamtex import ExportConfig` | — | Constructor parameters |
| `from streamtex import BannerConfig` | — | Constructor parameters |
| `from streamtex import AIImageConfig` | — | Constructor parameters |
| `from streamtex import PresentationConfig` | — | Constructor parameters (`title`, `aspect_ratio`, `footer`, `center_content`, `hide_streamlit_header`, `enforce_ratio`) |
| `from custom.styles import Styles` | `s` | Project-specific (skip — not library) |

**Rules**:
- ERROR if code accesses `lt.<member>` where `<member>` is not in `dir(ListTypes)`
- ERROR if code accesses `t.<member>` where `<member>` is not in `dir(Tags)`
- ERROR if code accesses `PdfMode.<member>` where `<member>` is not a valid variant
- ERROR if code constructs `PdfConfig(...)` or `ExportConfig(...)` with invalid keyword arguments
- WARNING if code uses an enum member that exists but is deprecated
- INFO: report total enum/constant references checked and validation results

**How to check** (automated introspection):
```bash
uv run python -c "
from streamtex.enums import ListTypes, Tags
from streamtex import PdfMode, PdfConfig, ExportConfig, BannerConfig
import inspect
for cls in [ListTypes, Tags, PdfMode]:
    members = [x for x in dir(cls) if not x.startswith('_')]
    print(f'{cls.__name__}: {members}')
for cls in [PdfConfig, ExportConfig, BannerConfig]:
    print(f'{cls.__name__}: {inspect.signature(cls)}')
"
```

---

## Check 16: Static File Existence (scope: docs, blocks, all)

**Goal**: Every file referenced by a rendered call in manual blocks must exist on disk.

**Scope**: `streamtex-docs/manuals/**/blocks/**/*.py`

**What to check**: Scan block files for runtime file references (NOT inside `show_code()` strings — those are examples). Specifically:

1. **Images**: `st_image(uri="<path>")` where `<path>` is NOT a URL (`https://` or `http://`). Resolve against the manual's `static/images/` directory (or the path set by `configure_image_path()`).
2. **show_code(file="<path>")**: Resolve against the manual's `static/` directory.
3. **open() calls**: e.g., `open(text_path)` where path is built with `os.path.join(_static_dir, ...)`. Verify the target file exists.
4. **st_audio() / st_video()**: Local file paths (not URLs). Resolve against `static/`.
5. **Repo-level files**: Blocks reading files from `_repo_root` or similar variables. Verify the file exists at the repo root.

**How to distinguish example vs rendered code**:
- Code inside `show_code("""...""")` string arguments → SKIP (example only)
- Code inside `show_code(file="...")` → CHECK the `file=` path (it's loaded at runtime)
- Bare `st_image()`, `open()`, `st_audio()`, `st_video()` calls at block indentation level → CHECK

**Resolution rules**:
- Each manual has its own `static/` directory at `manuals/<manual_name>/static/`
- `configure_image_path("app/static/images")` → files served by Streamlit at `static/images/<file>`
- `set_static_sources([...])` in `book.py` adds additional search paths
- `resolve_static("path")` uses the block registry's static sources

**Rules**:
- ERROR if a rendered `st_image(uri=)` references a local file that does not exist
- ERROR if a `show_code(file=)` references a file that does not exist
- ERROR if an `open()` call references a file that does not exist
- WARNING if `st_audio()` or `st_video()` references a missing local file
- WARNING if a repo-level file reference (Dockerfile, CI config, etc.) does not exist
- INFO: report total static references checked and how many are valid

---

## Check 17: CHANGELOG Freshness (scope: library, all)

**Goal**: The CHANGELOG.md accurately reflects the current library version and recent changes.

**Source**: `streamtex/CHANGELOG.md` + `streamtex/pyproject.toml` (version)

**Rules**:
- ERROR if the library version in `pyproject.toml` has no matching `## [X.Y.Z]` entry in CHANGELOG.md
- WARNING if the latest CHANGELOG entry has no `### Added`, `### Changed`, `### Fixed`, or `### Removed` subsection
- WARNING if CHANGELOG entries are not in reverse chronological order
- INFO: report current library version and latest CHANGELOG version

---

## Check 18: Manifest File Existence (scope: profiles, all)

**Goal**: Every file declared in a profile's `manifest.toml` must physically exist at the path resolved by `install.py`'s `CATEGORY_PATHS` mapping.

**Why this check is critical**: The CI (`validate.yml`) catches this on push, but catching it locally before pushing avoids broken CI runs. A manifest that declares files which don't exist means `install.py` will silently skip them, and users won't get the expected commands/skills/agents.

**Scope**: `streamtex-claude/profiles/*/manifest.toml`

**Method**:
1. For each profile directory in `streamtex-claude/profiles/`:
   - Read `manifest.toml`
   - For each category (`[commands]`, `[skills]`, `[agents]`, `[templates]`, `[tools]`):
     - Resolve the subdirectory using `CATEGORY_PATHS` mapping:
       - `commands.<subdir>` → `commands/<subdir>/`
       - `skills.designer` → `designer/skills/`
       - `skills.developer` → `developer/skills/`
       - `agents.designer` → `designer/agents/`
       - `templates.designer` → `designer/templates/`
       - `tools.designer` → `designer/tools/`
     - For each file in the list, verify `profiles/<profile>/<resolved_path>/<file>` exists
   - For `[shared]`:
     - `references` → verify each file exists in `shared/references/`
     - `commands` → verify each file exists in `shared/commands/`

**Rules**:
- ERROR if a declared file does not exist at the resolved path
- ERROR if a `[shared]` reference file does not exist in `shared/references/` or `shared/commands/`
- WARNING if a profile has no `manifest.toml`
- INFO: report total files declared vs found per profile

**Example of what this catches**:
- `documentation/manifest.toml` declares `stx-designer = ["init.md", ...]` but `documentation/commands/stx-designer/` does not exist → 5 ERRORS
- `project/manifest.toml` declares `shared.references = ["presentation_cheatsheet_en.md"]` but `shared/references/presentation_cheatsheet_en.md` is missing → 1 ERROR

---

## Check 19: CLI Template Registry Sync (scope: profiles, all)

**Goal**: The CLI template registry, the `click.Choice` validator, the template directories on disk, and the documentation are all synchronized.

**Why this check is critical**: A template can be added to `AVAILABLE_TEMPLATES` but forgotten in `click.Choice` (users get a rejection error), or a template directory can be created but never registered (users can't use it). The documentation may also list incorrect templates, confusing users.

**Source files**:
- `streamtex/streamtex/cli/install_cmd.py` → `AVAILABLE_TEMPLATES` list
- `streamtex/streamtex/cli/project_cmd.py` → `click.Choice([...])` in `--template` option
- `streamtex-docs/templates/` → directories matching `template_*/`
- `streamtex-claude/shared/commands/stx-guide.md` → CLI template references
- `streamtex/README.md` → template references in Quick Start section

**Method**:
1. Extract `AVAILABLE_TEMPLATES` from `install_cmd.py` (parse the Python list literal)
2. Extract the `click.Choice` list from `project_cmd.py` (parse the list in `type=click.Choice([...])`)
3. List directories matching `streamtex-docs/templates/template_*/`, extract names (strip `template_` prefix)
4. Extract template names mentioned in stx-guide.md CLI sections (look for `--template` references with `[...|...|...]` syntax)
5. Extract template names mentioned in README.md (look for `--template` in code blocks)

**Rules**:
- ERROR if `AVAILABLE_TEMPLATES` differs from the `click.Choice` list (these MUST be identical)
- ERROR if a directory `template_<name>` exists in `streamtex-docs/templates/` but `<name>` is not in `AVAILABLE_TEMPLATES`
- ERROR if a name is in `AVAILABLE_TEMPLATES` but no `template_<name>` directory exists
- WARNING if stx-guide.md CLI template list differs from `AVAILABLE_TEMPLATES`
- WARNING if README.md template list differs from `AVAILABLE_TEMPLATES`
- INFO: report all 4 sets and their alignment status

**Important distinction** (do NOT flag as errors):
- stx-designer templates (`/stx-designer:init --template`) are Claude AI blueprints stored in `profiles/project/designer/templates/`. These are a DIFFERENT system from CLI templates and should NOT be compared to `AVAILABLE_TEMPLATES`.
- Only flag mismatches for CLI template references (identified by `stx project new --template` or `stx install --template` context).

---

## Check 20: GitHub Issue Template & Command Sync (scope: profiles, all)

**Goal**: All three StreamTeX repositories have consistent GitHub issue templates, and the shared `stx-issue/` command directory exists with all 6 command files.

**Why this check is critical**: Issue templates ensure a consistent experience for users creating issues via the web or via `/stx-issue:*`. Missing templates in one repo but not others creates confusion. Missing command files cause silent installation failures.

**Source files**:
- `streamtex/.github/ISSUE_TEMPLATE/` → bug_report.md, feature_request.md, question.md, docs.md
- `streamtex-docs/.github/ISSUE_TEMPLATE/` → same 4 files
- `streamtex-claude/.github/ISSUE_TEMPLATE/` → same 4 files
- `streamtex-claude/shared/commands/stx-issue/` → 6 files: bug.md, feature.md, question.md, docs.md, comment.md, list.md
- `streamtex-claude/profiles/*/manifest.toml` → `[shared] commands` must include `"stx-issue"`

**Method**:
1. For each repo (streamtex, streamtex-docs, streamtex-claude):
   - Verify `.github/ISSUE_TEMPLATE/` directory exists
   - Verify all 4 template files exist: `bug_report.md`, `feature_request.md`, `question.md`, `docs.md`
   - Verify templates have correct YAML frontmatter (name, about, labels)
2. Verify `shared/commands/stx-issue/` contains all 6 files: `bug.md`, `feature.md`, `question.md`, `docs.md`, `comment.md`, `list.md`
3. Verify all profiles include `"stx-issue"` in their `[shared] commands` list
4. Verify stx-guide.md references `/stx-issue:*` in topics table and Section 6
5. Verify NO profile still has `stx-project = ["issue.md"]` or `commands/stx-project/issue.md`

**Rules**:
- ERROR if a repo is missing `.github/ISSUE_TEMPLATE/` directory
- ERROR if any of the 4 template files is missing from a repo
- ERROR if `shared/commands/stx-issue/` is missing any of the 6 command files
- ERROR if a profile does not include `"stx-issue"` in `[shared] commands`
- ERROR if any profile still has `commands/stx-project/issue.md` (orphan from old structure)
- WARNING if issue templates differ between repos (content should be consistent)
- WARNING if stx-guide.md does not reference `/stx-issue:*`
- INFO: report template existence status across all repos and profiles

---

## Check 21: Command Namespace stx- Prefix Convention (scope: profiles, all)

**What**: All command namespace directories and their references must use the `stx-` prefix convention. No bare namespace directories (e.g. `developer/`, `project/`, `designer/`) should exist under `commands/`.

**Why**: Consistent `stx-` prefix avoids user confusion — if `/stx-designer:init` exists, users expect `/stx-project:issue`, not `/project:issue`.

**Source files**:
- `streamtex-claude/profiles/*/commands/` → directory names
- `streamtex-claude/profiles/*/manifest.toml` → `[commands]` keys
- All `.md`, `.j2`, `.py` files across the 3 repos → slash command references

**Method**:
1. Scan all `profiles/*/commands/` directories — every subdirectory name must start with `stx-`
2. Scan all `manifest.toml` `[commands]` keys — every key must start with `stx-`
3. Grep all 3 repos for bare namespace patterns: `/project:`, `/designer:`, `/developer:`, `/migration:`, `/coherence:`, `/presentation:` (without `stx-` prefix)
4. Grep for old path references: `commands/project/`, `commands/developer/`, `commands/designer/`, `commands/migration/`, `commands/coherence/`, `commands/presentation/`

**Rules**:
- ERROR if a command directory under `commands/` does not start with `stx-`
- ERROR if a manifest `[commands]` key does not start with `stx-`
- ERROR if any file contains a bare namespace slash command reference (e.g. `/developer:test-run` instead of `/stx-developer:test-run`)
- WARNING if any file contains a bare namespace path reference (e.g. `commands/project/` instead of `commands/stx-project/`)
- INFO: report all namespace directories found and their prefix status

---

## Check 22: Release & Deploy Pipeline Coherence (scope: library, all)

**Goal**: The release pipeline (git tag → PyPI → lock file → Render deploy → GitHub Release) is fully consistent. Every step must be completed and synchronized.

**Why this check is critical**: Missing any step in the release pipeline causes silent failures: Render installs the wrong version from PyPI, GitHub shows an outdated "Latest" badge, lock files reference non-existent versions, or users install an old version. This check was added after a session where multiple pipeline steps were skipped, causing hours of debugging.

**Source files**:
- `streamtex/pyproject.toml` → `[project] version`
- `streamtex/streamtex/__init__.py` → `__version__`
- `streamtex/CHANGELOG.md` → latest `## [X.Y.Z]` entry
- Git tags: `git tag --sort=-creatordate | head -1`
- PyPI: `curl -s https://pypi.org/pypi/streamtex/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"`
- `streamtex-docs/uv.lock` → `name = "streamtex"` version
- GitHub Releases: `gh release list -R nicolasguelfi/streamtex --limit 1`
- Render deploy: `gh run list -R nicolasguelfi/streamtex-docs --workflow=render-deploy.yml --limit=1 --json conclusion`

**Method**:
1. Read the library version from `pyproject.toml` and `__init__.py` — they MUST match
2. Read the latest CHANGELOG entry version — MUST match library version
3. Read the latest git tag — MUST match library version (format: `vX.Y.Z`)
4. Query PyPI for the latest published version — MUST match library version
5. Read `streamtex-docs/uv.lock` streamtex version — MUST match PyPI version
6. Query GitHub Releases for the latest release — MUST match library version
7. Query the last Render deploy workflow run — MUST be `success`

**Rules**:
- ERROR if `pyproject.toml` version ≠ `__init__.py` `__version__`
- ERROR if CHANGELOG latest entry ≠ library version
- ERROR if latest git tag ≠ `v{library_version}`
- ERROR if PyPI latest version ≠ library version (library not published)
- ERROR if `streamtex-docs/uv.lock` streamtex version ≠ PyPI latest (lock file stale)
- ERROR if no GitHub Release exists for the library version
- WARNING if the latest Render deploy workflow run is `failure`
- WARNING if the GitHub Release for the library version is not marked as "Latest"
- INFO: report the complete pipeline state (version, tag, PyPI, lock, release, deploy)

**How to check** (automated):
```bash
# Library version
LIB_VER=$(grep 'version =' streamtex/pyproject.toml | head -1 | sed 's/.*"\(.*\)".*/\1/')
INIT_VER=$(grep '__version__' streamtex/streamtex/__init__.py | sed 's/.*"\(.*\)".*/\1/')
CHANGELOG_VER=$(grep '^## \[' streamtex/CHANGELOG.md | head -1 | sed 's/.*\[\(.*\)\].*/\1/')
GIT_TAG=$(cd streamtex && git tag --sort=-creatordate | head -1)
PYPI_VER=$(curl -s https://pypi.org/pypi/streamtex/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])")
LOCK_VER=$(grep -A1 'name = "streamtex"' streamtex-docs/uv.lock | grep version | head -1 | sed 's/.*"\(.*\)".*/\1/')
GH_RELEASE=$(gh release list -R nicolasguelfi/streamtex --limit 1 --json tagName,isLatest -q '.[0].tagName')
RENDER_STATUS=$(gh run list -R nicolasguelfi/streamtex-docs --workflow=render-deploy.yml --limit=1 --json conclusion -q '.[0].conclusion')

echo "pyproject.toml: $LIB_VER"
echo "__init__.py:    $INIT_VER"
echo "CHANGELOG:      $CHANGELOG_VER"
echo "Git tag:        $GIT_TAG"
echo "PyPI:           $PYPI_VER"
echo "Lock file:      $LOCK_VER"
echo "GitHub Release: $GH_RELEASE"
echo "Render deploy:  $RENDER_STATUS"
```

**Release pipeline checklist** (correct order):
1. Bump version in `pyproject.toml` + `__init__.py` + `CHANGELOG.md`
2. Commit + push to GitHub
3. `uv build && uv publish --token $PYPI_TOKEN`
4. `git tag vX.Y.Z && git push origin vX.Y.Z`
5. `gh release create vX.Y.Z --title "..." --notes "..." --latest`
6. Update `streamtex-docs/uv.lock`: `uv lock --upgrade-package streamtex`
7. Commit + push streamtex-docs
8. `gh workflow run render-deploy.yml -R nicolasguelfi/streamtex-docs`
9. Verify deploy success
