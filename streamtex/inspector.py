"""Block Inspector — inline editor panel for StreamTeX blocks.

Provides a discrete edit button per block and a fixed right panel
showing all related files (Python, Mermaid, JSON, etc.) with an editor.

Disabled by default; opt-in via ``InspectorConfig(enabled=True)``.
"""

import ast
import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

import streamlit as st

# ---------------------------------------------------------------------------
# Session state keys
# ---------------------------------------------------------------------------

_STX_INSPECTOR_OPEN = "_stx_inspector_open"
_STX_INSPECTOR_BLOCK = "_stx_inspector_block"
_STX_INSPECTOR_AUTH = "_stx_inspector_auth"
_STX_INSPECTOR_WIDTH = "_stx_inspector_width"
_STX_INSPECTOR_MODE = "_stx_insp_mode"
_STX_INSPECTOR_PROJECT_ROOT = "_stx_insp_proj_root"
_STX_INSPECTOR_PROJECT_FILES = "_stx_insp_proj_files"

_EXCLUDED_DIRS = {
    ".venv", "__pycache__", ".git", ".claude", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".streamlit",
    ".tox", "dist", "build",
}

# Width presets for the inspector sidebar.
# CSS min-width overrides Streamlit's hardcoded 600px clamp because
# per the CSS spec, min-width takes precedence over width.
_WIDTH_PRESETS = {
    "Default": "",        # Streamlit native (up to 600px)
    "Medium": "700px",
    "Large": "900px",
    "XL": "1100px",
}

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class InspectorConfig:
    """Configuration for the Block Inspector feature.

    Attributes:
        enabled: Whether the inspector is active (default False).
        password: Optional password gate. If set, user must authenticate.
        panel_width: CSS width of the right panel (default ``"35vw"``).
        backup: Create ``.bak`` files before saving (default True).
    """

    enabled: bool = False
    password: Optional[str] = None
    panel_width: str = "35vw"
    backup: bool = True


# ---------------------------------------------------------------------------
# File categories
# ---------------------------------------------------------------------------


@dataclass
class FileCategory:
    """Describes a family of editable files.

    Attributes:
        name: Display name shown in UI tabs (e.g. "Python").
        extensions: Set of file extensions including the dot (e.g. ``{".py"}``).
        ace_mode: Language mode for the ``streamlit-ace`` editor.
        validator: Optional callable ``(content: str) -> str | None``.
                   Returns an error message on failure, ``None`` on success.
    """

    name: str
    extensions: set
    ace_mode: str = "text"
    validator: Optional[Callable[[str], Optional[str]]] = None


# ---------------------------------------------------------------------------
# Built-in validators
# ---------------------------------------------------------------------------


def _validate_python(content: str) -> Optional[str]:
    """Check Python syntax with ``ast.parse``."""
    try:
        ast.parse(content)
        return None
    except SyntaxError as e:
        return f"Syntax error at line {e.lineno}: {e.msg}"


def _validate_json(content: str) -> Optional[str]:
    """Check JSON syntax with ``json.loads``."""
    try:
        json.loads(content)
        return None
    except json.JSONDecodeError as e:
        return f"JSON error at line {e.lineno}: {e.msg}"


# ---------------------------------------------------------------------------
# Category registry
# ---------------------------------------------------------------------------


class FileCategoryRegistry:
    """Extensible registry mapping file extensions to categories.

    Pre-registers Python, Diagrams, Data, and Texts categories.
    Unknown extensions fall back to a generic "Text" category.
    """

    def __init__(self):
        self._categories: List[FileCategory] = []
        self._ext_map: Dict[str, FileCategory] = {}
        self._fallback = FileCategory(name="Text", extensions=set(), ace_mode="text")

        # Pre-register default categories
        self.register(FileCategory(
            name="Python",
            extensions={".py"},
            ace_mode="python",
            validator=_validate_python,
        ))
        self.register(FileCategory(
            name="Diagrams",
            extensions={".mmd", ".tex", ".puml", ".dot"},
            ace_mode="text",
        ))
        self.register(FileCategory(
            name="Data",
            extensions={".json", ".csv", ".toml", ".yaml", ".yml"},
            ace_mode="json",
            validator=_validate_json,
        ))
        self.register(FileCategory(
            name="Texts",
            extensions={".txt", ".md", ".bib", ".ris"},
            ace_mode="markdown",
        ))

    def register(self, category: FileCategory) -> None:
        """Register a new file category (or override existing extensions)."""
        self._categories.append(category)
        for ext in category.extensions:
            self._ext_map[ext] = category

    def detect(self, file_path: str) -> FileCategory:
        """Return the category matching *file_path*'s extension.

        Falls back to a generic "Text" category for unknown extensions.
        """
        ext = os.path.splitext(file_path)[1].lower()
        return self._ext_map.get(ext, self._fallback)

    @property
    def categories(self) -> List[FileCategory]:
        """Return all registered categories (in registration order)."""
        return list(self._categories)


# ---------------------------------------------------------------------------
# Source file descriptor
# ---------------------------------------------------------------------------


@dataclass
class SourceFile:
    """A file associated with a block, discovered for editing.

    Attributes:
        path: Absolute path to the file on disk.
        category: The matched ``FileCategory``.
        label: Short display name (e.g. "bck_intro.py", "diagram.mmd").
    """

    path: str
    category: FileCategory
    label: str = ""

    def __post_init__(self):
        if not self.label:
            self.label = os.path.basename(self.path)


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def _find_project_root(start_path: str) -> Optional[str]:
    """Walk up the directory tree from *start_path* looking for ``book.py``.

    Returns the directory containing ``book.py``, or ``None``.
    """
    current = Path(start_path)
    if current.is_file():
        current = current.parent
    for _ in range(20):  # safety cap
        if (current / "book.py").is_file():
            return str(current)
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def discover_sources(module, category_registry: FileCategoryRegistry) -> List[SourceFile]:
    """Discover editable source files associated with a block *module*.

    Discovery logic:
    1. Main file (``module.__file__``)
    2. Atomic sub-blocks: AST scan for ``load_atomic_block("name", __file__)``
    3. Static references: string literals ending in known extensions
    4. Styles file: ``custom/styles.py`` relative to project root
    5. Optional ``__sources__`` attribute on module
    """
    sources: List[SourceFile] = []
    seen: set = set()

    # Collect all known extensions from the registry
    known_exts = set()
    for cat in category_registry.categories:
        known_exts.update(cat.extensions)

    main_file = getattr(module, "__file__", None)
    if not main_file or not os.path.isfile(main_file):
        return sources

    def _add(path: str):
        abs_path = os.path.abspath(path)
        if abs_path not in seen and os.path.isfile(abs_path):
            seen.add(abs_path)
            cat = category_registry.detect(abs_path)
            sources.append(SourceFile(path=abs_path, category=cat))

    # 1. Main file
    _add(main_file)

    # Parse main file AST for further discovery
    try:
        with open(main_file, "r", encoding="utf-8") as f:
            source_code = f.read()
        tree = ast.parse(source_code)
    except (SyntaxError, OSError):
        return sources

    main_dir = os.path.dirname(main_file)

    # 2. Atomic sub-blocks: look for load_atomic_block("name", __file__) calls
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "load_atomic_block"
                and len(node.args) >= 1
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            block_name = node.args[0].value
            atomic_path = os.path.join(main_dir, "_atomic", f"{block_name}.py")
            _add(atomic_path)
        elif (isinstance(node, ast.Call)
              and isinstance(node.func, ast.Name)
              and node.func.id == "load_atomic_block"
              and len(node.args) >= 1
              and isinstance(node.args[0], ast.Constant)
              and isinstance(node.args[0].value, str)):
            block_name = node.args[0].value
            atomic_path = os.path.join(main_dir, "_atomic", f"{block_name}.py")
            _add(atomic_path)

    # 3. Static references: string literals ending in known extensions
    #    Also scan atomic files we just discovered
    py_files_to_scan = [main_file] + [
        s.path for s in sources if s.path.endswith(".py") and s.path != main_file
    ]
    for py_path in py_files_to_scan:
        try:
            with open(py_path, "r", encoding="utf-8") as f:
                py_tree = ast.parse(f.read()) if py_path != main_file else tree
        except (SyntaxError, OSError):
            continue

        py_dir = os.path.dirname(py_path)
        for node in ast.walk(py_tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                ext = os.path.splitext(val)[1].lower()
                if ext in known_exts and not val.startswith(("http://", "https://")):
                    # Try relative to the .py file's directory
                    candidate = os.path.join(py_dir, val)
                    if os.path.isfile(candidate):
                        _add(candidate)
                        continue
                    # Try via resolve_static
                    resolved_ok = False
                    try:
                        from .blocks import resolve_static
                        resolved = resolve_static(val)
                        if resolved != val and os.path.isfile(resolved):
                            _add(resolved)
                            resolved_ok = True
                    except Exception:
                        pass
                    # Fallback: recursive search in {project_root}/static/
                    if not resolved_ok:
                        project_root = _find_project_root(py_path)
                        if project_root:
                            static_dir = os.path.join(project_root, "static")
                            basename = os.path.basename(val)
                            if os.path.isdir(static_dir):
                                for dp, _, fns in os.walk(static_dir):
                                    if basename in fns:
                                        _add(os.path.join(dp, basename))
                                        break

    # 4. Styles file: look for "from custom.styles import"
    for node in ast.walk(tree):
        if isinstance(node, (ast.ImportFrom,)):
            if node.module and "custom.styles" in node.module:
                project_root = _find_project_root(main_file)
                if project_root:
                    styles_path = os.path.join(project_root, "custom", "styles.py")
                    _add(styles_path)
                break

    # 5. Optional __sources__ attribute
    extra_sources = getattr(module, "__sources__", None)
    if extra_sources and isinstance(extra_sources, (list, tuple)):
        for src in extra_sources:
            if isinstance(src, str):
                if os.path.isabs(src):
                    _add(src)
                else:
                    _add(os.path.join(main_dir, src))

    return sources


# ---------------------------------------------------------------------------
# Project-wide file scanning
# ---------------------------------------------------------------------------

# Extensions recognised when scanning the whole project tree.
_PROJECT_EXTENSIONS = {
    ".py", ".mmd", ".tex", ".puml", ".dot",
    ".json", ".csv", ".toml", ".yaml", ".yml",
    ".txt", ".md", ".bib", ".ris",
}


def _scan_project_files(
    project_root: str,
    category_registry: FileCategoryRegistry,
) -> List[SourceFile]:
    """Walk *project_root* and collect editable files with known extensions.

    Prunes directories listed in ``_EXCLUDED_DIRS``.
    Each ``SourceFile.label`` is the path relative to *project_root*.
    """
    results: List[SourceFile] = []
    root = os.path.abspath(project_root)

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in-place (modifying dirnames)
        dirnames[:] = [
            d for d in dirnames if d not in _EXCLUDED_DIRS
        ]
        dirnames.sort()

        for fn in sorted(filenames):
            ext = os.path.splitext(fn)[1].lower()
            if ext not in _PROJECT_EXTENSIONS:
                continue
            abs_path = os.path.join(dirpath, fn)
            rel_path = os.path.relpath(abs_path, root)
            cat = category_registry.detect(abs_path)
            results.append(SourceFile(path=abs_path, category=cat, label=rel_path))

    return results


def _get_cached_project_files(
    project_root: str,
    category_registry: FileCategoryRegistry,
) -> List[SourceFile]:
    """Return project files, rescanning only when *project_root* changes."""
    cached_root = st.session_state.get(_STX_INSPECTOR_PROJECT_ROOT)
    if cached_root == project_root:
        cached = st.session_state.get(_STX_INSPECTOR_PROJECT_FILES)
        if cached is not None:
            return cached

    files = _scan_project_files(project_root, category_registry)
    st.session_state[_STX_INSPECTOR_PROJECT_ROOT] = project_root
    st.session_state[_STX_INSPECTOR_PROJECT_FILES] = files
    return files


# ---------------------------------------------------------------------------
# Editor widget
# ---------------------------------------------------------------------------


def _render_editor(content: str, language: str, key: str, height: int = 450) -> str:
    """Render a code editor using ``streamlit-ace`` or fall back to ``st.text_area``.

    Returns the current editor content (which may differ from *content*
    if the user has made edits).
    """
    try:
        from streamlit_ace import st_ace
        result = st_ace(
            value=content,
            language=language,
            theme="monokai",
            key=key,
            height=height,
            auto_update=True,
        )
        return result if result is not None else content
    except ImportError:
        result = st.text_area(
            "",
            value=content,
            height=height,
            key=key,
            label_visibility="collapsed",
        )
        return result if result is not None else content


# ---------------------------------------------------------------------------
# Edit button — global CSS + per-block marker
# ---------------------------------------------------------------------------

_STX_EDIT_MARKER_CLASS = "stx-edit-marker"


def inject_inspector_css() -> None:
    """Inject the **single** global CSS for all inspector edit buttons.

    Called once in ``st_book`` when the inspector is enabled.
    This replaces per-button CSS injection (N calls → 1 call).

    Sidebar width is handled separately by :func:`_inject_sidebar_width_css`,
    which is called from the panel renderer so it can react to the user's
    width-preset selection.
    """
    css = f"""
    <style>
        /* --- Edit button positioning (✎) --- */
        div:has(> .element-container > .stHtml > span.{_STX_EDIT_MARKER_CLASS}) {{
            position: relative;
        }}
        div:has(> .element-container > .stHtml > span.{_STX_EDIT_MARKER_CLASS}) [data-testid="stButton"] {{
            position: absolute;
            top: 4px;
            right: 4px;
            z-index: 50;
            opacity: 0.15;
            transition: opacity 0.2s;
        }}
        div:has(> .element-container > .stHtml > span.{_STX_EDIT_MARKER_CLASS}) [data-testid="stButton"]:hover {{
            opacity: 0.8;
        }}
        div:has(> .element-container > .stHtml > span.{_STX_EDIT_MARKER_CLASS}) [data-testid="stButton"] button {{
            padding: 2px 8px;
            min-height: 0;
            font-size: 1.1rem;
            line-height: 1.2;
        }}
        /* Keep ace editor responsive inside sidebar */
        [data-testid="stSidebar"] iframe {{
            width: 100% !important;
        }}
    </style>
    """
    st.html(css)


def _inject_sidebar_width_css(min_width: str) -> None:
    """Inject CSS to widen the sidebar beyond Streamlit's 600px cap.

    Streamlit's frontend ``clampSidebarWidth()`` hard-caps the sidebar
    ``width`` inline style to 600px.  Per the CSS spec, ``min-width``
    takes precedence over ``width``, so setting ``min-width`` with
    ``!important`` reliably overrides the JS-applied inline width
    without any JavaScript hacks.
    """
    if not min_width:
        return
    st.html(f"""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"] {{
            min-width: {min_width} !important;
            max-width: none !important;
        }}
    </style>
    """)


def render_edit_button(module_name: str, config: InspectorConfig) -> None:
    """Render a discrete ``✎`` button in the top-right corner of a block.

    Only emits a lightweight marker ``<span>`` + ``st.button``.
    The CSS is injected once by :func:`inject_inspector_css`.
    """
    if not config.enabled:
        return

    with st.container():
        st.html(f'<span class="{_STX_EDIT_MARKER_CLASS}" style="display:none;"></span>')

        def _on_click():
            st.session_state[_STX_INSPECTOR_OPEN] = True
            st.session_state[_STX_INSPECTOR_BLOCK] = module_name

        st.button(
            "✎",
            key=f"_stx_edit_{module_name}",
            on_click=_on_click,
            help="Open Block Inspector",
        )


# ---------------------------------------------------------------------------
# Inspector panel — rendered inside st.sidebar (native behaviour)
# ---------------------------------------------------------------------------


def _close_inspector():
    """on_click callback — closes the inspector panel."""
    st.session_state[_STX_INSPECTOR_OPEN] = False


def _auth_inspector(password_key: str, expected: str):
    """on_click callback — checks password and authenticates."""
    pwd = st.session_state.get(password_key, "")
    if pwd == expected:
        st.session_state[_STX_INSPECTOR_AUTH] = True


_STX_INSPECTOR_PENDING = "_stx_inspector_pending"


def _apply_edits(file_path: str, editor_key: str):
    """on_click callback — stage the current editor content for saving.

    Reads the last-applied value from the ``st_ace`` widget (transferred
    to session state via Cmd+Enter or the ace APPLY button) and stores it
    in a *pending* dict.  Multiple files can be staged before a single
    :func:`_save_and_reload` writes them all to disk.
    """
    content = st.session_state.get(editor_key)
    if content is None:
        return
    pending = st.session_state.setdefault(_STX_INSPECTOR_PENDING, {})
    pending[file_path] = content


def _save_and_reload(file_path: str, editor_key: str, backup: bool):
    """on_click callback — write all pending + current file to disk.

    1. Writes every file in the *pending* dict to disk.
    2. Also writes the **current** file from its editor session-state key
       (in case the user edited and applied via Cmd+Enter but did not
       click *Apply edits*).
    3. Invalidates block-registry caches and the paginated page cache
       so the next rerun picks up the new code.
    """
    pending = st.session_state.pop(_STX_INSPECTOR_PENDING, {})

    # Include the current file from session state (convenience shortcut
    # so the user can skip "Apply edits" for single-file edits).
    current_content = st.session_state.get(editor_key)
    if current_content is not None:
        pending[file_path] = current_content

    if not pending:
        return

    for fp, content in pending.items():
        if backup:
            try:
                shutil.copy2(fp, fp + ".bak")
            except OSError:
                pass
        try:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError:
            continue

    _invalidate_module_cache()
    st.session_state.pop(_STX_INSPECTOR_PROJECT_FILES, None)
    # NOTE: we do NOT clear "_stx_page_cache" here.  The page cache
    # stores TOC/marker/search metadata — not block output.  Clearing
    # it forces _build_page_cache to re-execute ALL blocks in a hidden
    # container, which causes StreamlitDuplicateElementKey errors when
    # the current page's block is then rendered a second time (blocks
    # with hardcoded widget keys like st.selectbox(key=...) crash).
    # The registry invalidation above is sufficient: the next access
    # to any block module re-imports it from the updated file on disk.
    st.session_state["_stx_inspector_needs_rerun"] = True


def _cancel_edits(file_path: str):
    """on_click callback — discard pending changes for *file_path*."""
    pending = st.session_state.get(_STX_INSPECTOR_PENDING, {})
    pending.pop(file_path, None)


def _invalidate_module_cache() -> None:
    """Clear block registry caches so modules are reloaded from disk.

    Both ``ProjectBlockRegistry`` and ``LazyBlockRegistry`` cache loaded
    modules.  After a file is saved, their caches must be cleared so that
    the next ``blocks.bck_xxx`` access re-imports the module from the
    updated file on disk.
    """
    from .blocks import LazyBlockRegistry, ProjectBlockRegistry

    ProjectBlockRegistry.invalidate_all()
    LazyBlockRegistry.invalidate_all()


def render_inspector_panel(
    sources: List[SourceFile],
    config: InspectorConfig,
    category_registry: FileCategoryRegistry,
    placeholder=None,
    project_root: Optional[str] = None,
) -> None:
    """Render the inspector panel inside a **pre-reserved sidebar placeholder**.

    The *placeholder* is an ``st.empty()`` created early in ``st_book``
    (before TOC, markers, search).  Using ``placeholder.container()``
    ensures the inspector content is **stable** across reruns — it
    does not get displaced by TOC rebuilds or search JS injections.

    Falls back to ``with st.sidebar:`` if no placeholder is provided.

    When *project_root* is provided, a mode selector lets the user
    switch between "Block files" (discovered sources) and "Project"
    (all editable files under the project root).
    """
    if not st.session_state.get(_STX_INSPECTOR_OPEN, False):
        return

    ctx = placeholder.container() if placeholder is not None else st.sidebar
    with ctx:
        st.divider()

        # --- Password gate ---
        if config.password is not None and not st.session_state.get(_STX_INSPECTOR_AUTH, False):
            st.markdown("**Block Inspector** — Authentication Required")
            pwd_key = "_stx_insp_pwd"
            st.text_input("Password", type="password", key=pwd_key)
            col_auth, col_close = st.columns([3, 1])
            with col_auth:
                st.button(
                    "Authenticate", key="_stx_insp_auth_btn",
                    on_click=_auth_inspector, args=(pwd_key, config.password),
                )
            with col_close:
                st.button("Close", key="_stx_insp_close_auth", on_click=_close_inspector)
            return

        # --- Header: title + width selector ---
        block_name = st.session_state.get(_STX_INSPECTOR_BLOCK, "")
        st.markdown(f"**Inspector:** `{block_name}`")

        width_labels = [*_WIDTH_PRESETS]
        current_label = st.session_state.get(_STX_INSPECTOR_WIDTH, "Large")
        current_idx = width_labels.index(current_label) if current_label in width_labels else 2
        selected_width = st.segmented_control(
            "Panel width",
            width_labels,
            default=width_labels[current_idx],
            key="_stx_insp_width_ctrl",
            label_visibility="collapsed",
        )
        if selected_width and selected_width != current_label:
            st.session_state[_STX_INSPECTOR_WIDTH] = selected_width
        # Apply the chosen width via CSS min-width
        effective_label = selected_width or current_label
        _inject_sidebar_width_css(_WIDTH_PRESETS.get(effective_label, ""))

        # --- Mode selector (Block files / Project) ---
        mode_options = ["Block files"]
        if project_root:
            mode_options.append("Project")

        if len(mode_options) > 1:
            current_mode = st.session_state.get(_STX_INSPECTOR_MODE, "Block files")
            if current_mode not in mode_options:
                current_mode = "Block files"
            selected_mode = st.segmented_control(
                "Browse mode",
                mode_options,
                default=current_mode,
                key="_stx_insp_mode_ctrl",
                label_visibility="collapsed",
            )
            active_mode = selected_mode or current_mode
            if active_mode != current_mode:
                st.session_state[_STX_INSPECTOR_MODE] = active_mode
        else:
            active_mode = "Block files"

        # --- Text filter (both modes) ---
        filter_text = st.text_input(
            "Filter files",
            key="_stx_insp_filter",
            placeholder="Type to filter...",
            label_visibility="collapsed",
        )

        # --- Project mode ---
        if active_mode == "Project" and project_root:
            all_files = _get_cached_project_files(project_root, category_registry)
            if filter_text:
                ft_lower = filter_text.lower()
                all_files = [f for f in all_files if ft_lower in f.label.lower()]
            if not all_files:
                st.info("No matching files found.")
                return
            labels = [f.label for f in all_files]
            selected_label = st.selectbox(
                "Project file", labels, key="_stx_insp_proj_sel",
                label_visibility="collapsed",
            )
            idx = labels.index(selected_label) if selected_label in labels else 0
            _render_file_editor(all_files[idx], config)
            return

        # --- Block files mode (existing behaviour) ---
        if not sources:
            st.info("No source files found for this block.")
            return

        # Apply text filter to block sources
        if filter_text:
            ft_lower = filter_text.lower()
            sources = [s for s in sources if ft_lower in s.label.lower()]
            if not sources:
                st.info("No matching files found.")
                return

        # --- Group sources by category ---
        cat_sources: Dict[str, List[SourceFile]] = {}
        for src in sources:
            cat_name = src.category.name
            cat_sources.setdefault(cat_name, []).append(src)

        # --- Category tabs ---
        tab_names = [*cat_sources]
        if len(tab_names) == 1:
            _render_category_files(cat_sources[tab_names[0]], config, tab_names[0])
        else:
            tabs = st.tabs(tab_names)
            for tab, tab_name in zip(tabs, tab_names):
                with tab:
                    _render_category_files(cat_sources[tab_name], config, tab_name)


def _render_category_files(
    files: List[SourceFile],
    config: InspectorConfig,
    category_name: str,
) -> None:
    """Render file selector + editor + save/cancel for a list of files."""
    if len(files) == 1:
        _render_file_editor(files[0], config)
    else:
        labels = [f.label for f in files]
        sel_key = f"_stx_insp_sel_{category_name}"
        selected_label = st.selectbox(
            "File", labels, key=sel_key, label_visibility="collapsed",
        )
        idx = labels.index(selected_label) if selected_label in labels else 0
        _render_file_editor(files[idx], config)


@st.fragment
def _render_file_editor(source: SourceFile, config: InspectorConfig) -> None:
    """Render the editor for a single source file (as a Streamlit fragment).

    Using ``@st.fragment`` isolates the editor from the main app:
    keystrokes only rerun this fragment, not the full page, so the
    sidebar width stays stable and the main content is not re-rendered.

    Layout::

        path/to/file.py
        [Apply edits] [Save & Reload] [Cancel] [Close]
        ┌──────────────────────────────────────────────┐
        │  ace editor (auto_update=True)                │
        └──────────────────────────────────────────────┘

    Workflow:

    1. Edit code in the ace editor (content synced automatically).
    2. Click **Apply edits** to *stage* the file (optional — useful when
       editing multiple files before saving).
    3. Click **Save & Reload** to write staged + current file to disk
       and trigger a full re-render (``st.rerun(scope="app")``).
    """
    file_path = source.path

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            disk_content = f.read()
    except OSError as e:
        st.error(f"Cannot read {source.label}: {e}")
        return

    st.caption(source.path)

    path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
    editor_key = f"_stx_insp_editor_{path_hash}"

    # --- Full-rerun triggers (set by on_click callbacks) ---
    # st.rerun() cannot be called inside callbacks, so callbacks set
    # flags in session state and we call st.rerun(scope="app") here
    # (in the fragment body, where it IS allowed).
    if st.session_state.pop("_stx_inspector_needs_rerun", False):
        st.rerun(scope="app")
    if not st.session_state.get(_STX_INSPECTOR_OPEN, True):
        st.rerun(scope="app")

    # --- Pending indicator ---
    pending = st.session_state.get(_STX_INSPECTOR_PENDING, {})
    if file_path in pending:
        st.success("Changes applied — pending save")

    # --- Toolbar: Apply | Save & Reload | Cancel | Close ---
    col_apply, col_save, col_cancel, col_close = st.columns(4)
    with col_apply:
        st.button(
            "Apply edits", key=f"_stx_insp_apply_{path_hash}",
            on_click=_apply_edits, args=(file_path, editor_key),
        )
    with col_save:
        st.button(
            "Save & Reload", key=f"_stx_insp_save_{path_hash}", type="primary",
            on_click=_save_and_reload,
            args=(file_path, editor_key, config.backup),
        )
    with col_cancel:
        st.button(
            "Cancel", key=f"_stx_insp_cancel_{path_hash}",
            on_click=_cancel_edits, args=(file_path,),
        )
    with col_close:
        st.button(
            "Close", key=f"_stx_insp_close_{path_hash}",
            on_click=_close_inspector,
        )

    # --- Editor ---
    edited = _render_editor(
        disk_content,
        language=source.category.ace_mode,
        key=editor_key,
    )

    # Validation
    if source.category.validator and edited != disk_content:
        error = source.category.validator(edited)
        if error:
            st.warning(f"Validation: {error}")
