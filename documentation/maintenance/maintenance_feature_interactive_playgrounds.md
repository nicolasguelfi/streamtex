# Interactive Playgrounds — Feasibility Analysis

**Date**: 2026-02-22
**Status**: Shelved (analysis complete, implementation deferred)

## Objective

Replace static `show_code()` examples in StreamTeX manuals with interactive editable playgrounds where users can:

1. See an editable code window for each example
2. See the live rendering/visualization below
3. Edit the code and see changes reflected immediately
4. Have code stored in independent files with backup/reset capability

## Current State

### Inspector Feature (Feb 21-22, 2026)

The recently added Block Inspector provides:

- File editing in sidebar via `streamlit-ace` (optional dep)
- Hot-reload via `ProjectBlockRegistry.invalidate_all()` / `LazyBlockRegistry.invalidate_all()`
- Backup system (`.bak` files before save)
- `@st.fragment` isolation (keystrokes only rerun the editor fragment)
- Password-optional auth gate
- Two browse modes: "Block files" (per-block) and "Project" (all files)

### Manual Code Examples

- **332 code examples** across **84 blocks** in two manuals (intro + advanced)
- 100% inline via `textwrap.dedent()` — no external files
- Systematic pattern: `show_explanation()` → `show_code()` → live demo
- ~30% of examples: displayed code differs from executed code (widget key prefixes, default values)
- **245 examples** (~74%): pure rendering (text, styles, grids, containers)
- **87 examples** (~26%): interactive widgets (forms, buttons, selectboxes)

### Code Example Distribution by Language

| Language | Count | Examples |
|----------|-------|----------|
| Python   | ~240  | Block code, API examples |
| Bash     | ~45   | Installation, Docker commands |
| Text     | ~25   | Configuration, sample data |
| Dockerfile | ~8  | Deployment examples |
| TOML     | ~5    | Config files |
| Other    | ~9    | HTML, SQL, etc. |

## Technical Challenges

| Problem | Difficulty | Impact |
|---------|-----------|--------|
| **User code execution** (`exec()`) | Medium | Core mechanism — works with Streamlit but fragile |
| **Unique widget keys** | High | Duplicate `st.button(key="x")` → `DuplicateWidgetKey` crash |
| **Rerun isolation** | Medium | Each editor must be a `@st.fragment` to avoid full page rerun |
| **Execution context** | Medium | Code needs all StreamTeX imports + project styles |
| **Migration of 332 examples** | High (volume) | Extract each snippet to independent file |
| **Displayed code != executed code** | Medium | ~30% of examples have differences (keys, values) |
| **Security** | Low | `exec()` is risky in prod, but this is a local documentation tool |
| **Error handling** | Low | User code will have errors — need graceful display |

## Proposals Evaluated

### Proposal A: `st_playground()` — Lightweight `exec()`-based Component

**Principle**: New StreamTeX component combining editor + preview + dynamic execution.

```
┌─────────────────────────────────────────┐
│  Editor (streamlit-ace)                 │
│  ┌─────────────────────────────────────┐│
│  │ st_write(s.large, "Hello!")         ││
│  │ st_space("v", 1)                   ││
│  │ st_write(s.bold, "World")          ││
│  └─────────────────────────────────────┘│
│  [Run]  [Reset]                         │
├─────────────────────────────────────────┤
│  Preview                                │
│  ┌─────────────────────────────────────┐│
│  │ Hello!                              ││
│  │                                     ││
│  │ World                               ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

- Snippet files in `snippets/<block_name>/01_example.py`
- Each snippet = just executable code (no `class BlockStyles`, no `build()`)
- `.original` reference file for reset
- `@st.fragment` wrapped for isolation
- Prepared namespace with all StreamTeX imports + project styles
- "Run" button (no auto-exec to avoid crashes while typing)

**Pros**: Lightweight, direct UX, reuses `streamlit-ace`
**Cons**: `exec()` crash risks, widget key conflicts, no IDE support in web editor

### Proposal B: Inspector Extension — "Inline Inspector"

**Principle**: Each code example becomes a mini-inspector embedded in content. Each snippet is a full `.py` file with `build()`.

- Each snippet = complete Python file with imports + `build()`
- Disk save via existing inspector mechanism (`.bak` backup)
- Hot-reload via `importlib.util.spec_from_file_location`
- `st.rerun()` after save

**Pros**: Reuses existing infrastructure, full Python files (IDE/lint support), no `exec()`
**Cons**: Heavy boilerplate per snippet, `st.rerun()` reloads entire page, 332 micro-files

### Proposal C (Recommended): Hybrid — "Snippet Runner"

**Principle**: Combine the best of both. Snippets are minimal `.py` files (just code), execution uses a template wrapper injecting context.

**Snippet file** (`snippets/text_basics/01_plain_text.py`):
```python
st_write(s.large, "Hello, StreamTeX!")
st_space("v", 1)
st_write(s.bold + s.Large, "Styled text")
```

**Block usage**:
```python
# Before:
show_code(textwrap.dedent("""\
    st_write(s.large, "Hello, StreamTeX!")
"""))
# manual demo below...

# After:
show_playground("text_basics/01_plain_text.py")
```

**File organization**:
```
stx_manual_intro/
├── blocks/
│   ├── _atomic/
│   │   └── bck_text_basics.py      # calls show_playground(...)
│   └── helpers.py                   # defines show_playground()
├── snippets/                        # NEW
│   ├── _originals/                  # reference copies (never modified)
│   │   └── text_basics/
│   │       ├── 01_plain_text.py
│   │       └── 02_styled_text.py
│   └── text_basics/                 # working copies (editable by user)
│       ├── 01_plain_text.py
│       └── 02_styled_text.py
├── custom/
│   └── styles.py
└── book.py
```

**Execution mechanism**:

```python
# In streamtex/playground.py

@st.fragment
def st_playground(snippet_path, *, context=None, original_path=None, height=300):
    """Interactive editor + preview for a code snippet."""
    code = Path(snippet_path).read_text()

    col_edit, col_ctrl = st.columns([0.9, 0.1])
    with col_edit:
        edited = _render_editor(code, "python", key=f"pg_{hash}")
    with col_ctrl:
        run = st.button("Run", key=f"run_{hash}")
        if original_path and st.button("Reset", key=f"reset_{hash}"):
            shutil.copy2(original_path, snippet_path)
            st.rerun(scope="fragment")

    if run or edited != code:
        Path(snippet_path).write_text(edited)

    with st.container(border=True):
        try:
            exec(edited, _build_namespace(context))
        except Exception as e:
            st.error(f"Error: {e}")


def _build_namespace(extra=None):
    """Build execution namespace with all StreamTeX imports."""
    import streamtex as stx
    ns = {
        "st": st, "stx": stx,
        "st_write": stx.st_write, "st_block": stx.st_block,
        "st_span": stx.st_span, "st_grid": stx.st_grid,
        "st_space": stx.st_space, "st_br": stx.st_br,
        "st_list": stx.st_list, "st_image": stx.st_image,
        "st_code": stx.st_code, "Style": stx.Style,
        "t": stx.Tags,
        **(extra or {}),
    }
    return ns
```

**Pros**:
- Minimal snippets (just the relevant code, no boilerplate)
- Independent files (versionable, diffable, greppable)
- Backup via `_originals/` (reset = simple copy)
- Fragment isolation (keystrokes = local rerun only)
- Displayed code = executed code (no more divergence)
- Incremental migration (both patterns coexist)
- Reusable in any StreamTeX project

**Cons**:
- `exec()` still required (mitigated by fragment + try/except)
- Migration of 332 snippets = significant effort (largely automatable)
- Snippets with interactive widgets need key prefixing mechanism

## Interactive Widgets Problem

~26% of examples (87/332) create Streamlit widgets (`st.button`, `st.form`, `st.selectbox`). In an `exec()` context:

- Keys must be unique across the entire page
- If user duplicates a widget without changing its key → crash

**Possible solutions**:

1. **Auto-prefixing**: `exec()` wrapper that monkey-patches `st.button`, `st.form`, etc. to add key prefix. Feasible but fragile.
2. **Restriction (recommended for v1)**: Playgrounds only support pure rendering code. Examples with widgets keep `show_code()` + separate demo.
3. **Isolated container**: Use `st.container(key=unique)` as implicit namespace. Not yet supported by Streamlit natively.

## Migration Plan (if implemented)

| Phase | Scope | Effort |
|-------|-------|--------|
| **Phase 0** | Create `streamtex/playground.py` + `show_playground()` in block_helpers | New module |
| **Phase 1** | Migrate 5-10 simple examples (text, styles) to validate approach | Pilot |
| **Phase 2** | Script to auto-extract `textwrap.dedent()` → snippet files | Automation |
| **Phase 3** | Migrate ~245 pure rendering examples | Volume |
| **Phase 4** | Evaluate if 87 widget examples can be migrated (key prefixing) | Optional |

## Recommendation

**Proposal C (Hybrid)** is the most viable:

- Reuses existing infrastructure (`streamlit-ace`, `@st.fragment`, backup pattern)
- Minimal snippets are easy to maintain
- Migration can be incremental (both patterns coexist)
- `_originals/` system protects documentation
- `st_playground()` component is reusable across any StreamTeX project

Main risk is `exec()`, mitigated by context (local tool, no public exposure) and isolation via `@st.fragment` + `try/except`.
