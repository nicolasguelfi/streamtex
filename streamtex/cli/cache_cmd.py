"""stx cache warmup — pre-warm the page cache for deployment."""

import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import click

from .console import get_console

# ---------------------------------------------------------------------------
# Headless Streamlit mock
# ---------------------------------------------------------------------------

class _HeadlessDelta:
    """No-op stand-in for any Streamlit object (DeltaGenerator, sidebar, …).

    Supports attribute access, calls, context managers, and iteration so that
    StreamTeX rendering code can execute without a live Streamlit session.
    """

    def __getattr__(self, name):
        return _HeadlessDelta()

    def __call__(self, *args, **kwargs):
        return _HeadlessDelta()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def __iter__(self):
        # Enough items for most st.columns / st.tabs calls.
        return iter([_HeadlessDelta() for _ in range(12)])

    def __bool__(self):
        return False

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __str__(self):
        return ""

    def __contains__(self, item):
        return False

    def __getitem__(self, key):
        return _HeadlessDelta()

    def __len__(self):
        return 0


def _noop_decorator(*args, **kwargs):
    """Identity decorator for st.cache_data / st.cache_resource."""
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return args[0]
    return lambda fn: fn


def _mock_columns(spec=2, *, gap=None, **kwargs):
    n = len(spec) if isinstance(spec, (list, tuple)) else int(spec)
    return [_HeadlessDelta() for _ in range(max(n, 1))]


def _mock_tabs(labels, **kwargs):
    return [_HeadlessDelta() for _ in labels]


# --- Widget mocks that return sensible default values ---------------------

def _mock_selectbox(_label="", options=(), *, index=0, **kw):
    opts = [*options] if options else []
    return opts[index] if opts and 0 <= index < len(opts) else None


def _mock_radio(_label="", options=(), *, index=0, **kw):
    opts = [*options] if options else []
    return opts[index] if opts and 0 <= index < len(opts) else None


def _mock_multiselect(_label="", options=(), *, default=None, **kw):
    return [*default] if default else []


def _mock_checkbox(_label="", value=False, **kw):
    return value


def _mock_toggle(_label="", value=False, **kw):
    return value


def _mock_number_input(_label="", *, value=0, **kw):
    return value


def _mock_slider(_label="", min_value=None, max_value=None, value=None, **kw):
    return value if value is not None else (min_value or 0)


def _mock_text_input(_label="", value="", **kw):
    return value


def _mock_text_area(_label="", value="", **kw):
    return value


def _mock_color_picker(_label="", value="#000000", **kw):
    return value


def _mock_date_input(_label="", value=None, **kw):
    return value


def _mock_time_input(_label="", value=None, **kw):
    return value


@contextmanager
def _headless_streamlit():
    """Monkey-patch the ``streamlit`` module for headless execution.

    Patches are applied to the *already-imported* module object so that every
    ``import streamlit as st`` reference picks up the mocks.
    """
    import streamlit as st

    _saved: dict = {}
    _mock = _HeadlessDelta()

    # Attributes that should become silent no-ops / mock objects.
    _NOOP_ATTRS = [
        "html", "empty", "container", "markdown", "write", "title",
        "header", "subheader", "caption", "text", "divider", "code",
        "file_uploader",
        "button", "download_button", "link_button",
        "image", "audio", "video",
        "dataframe", "table", "metric", "json",
        "line_chart", "bar_chart", "area_chart", "scatter_chart",
        "plotly_chart", "graphviz_chart", "pydeck_chart", "map",
        "spinner", "progress", "status", "toast", "balloons", "snow",
        "error", "warning", "info", "success", "exception",
        "set_page_config", "get_option", "query_params",
        "form", "form_submit_button", "expander",
    ]

    for attr in _NOOP_ATTRS:
        if hasattr(st, attr):
            _saved[attr] = getattr(st, attr)
            setattr(st, attr, _mock)

    # Widgets that return default values (must NOT return _HeadlessDelta).
    _WIDGET_MOCKS = {
        "selectbox": _mock_selectbox,
        "radio": _mock_radio,
        "multiselect": _mock_multiselect,
        "checkbox": _mock_checkbox,
        "toggle": _mock_toggle,
        "number_input": _mock_number_input,
        "slider": _mock_slider,
        "text_input": _mock_text_input,
        "text_area": _mock_text_area,
        "color_picker": _mock_color_picker,
        "date_input": _mock_date_input,
        "time_input": _mock_time_input,
    }
    for attr, fn in _WIDGET_MOCKS.items():
        if hasattr(st, attr):
            _saved[attr] = getattr(st, attr)
            setattr(st, attr, fn)

    # session_state must be a real dict.
    _saved["session_state"] = st.session_state
    st.session_state = {}

    # sidebar needs to be a mock (attribute, not function).
    _saved["sidebar"] = st.sidebar
    st.sidebar = _mock

    # Decorators must be identity functions (applied at import time).
    for deco in ("cache_data", "cache_resource"):
        if hasattr(st, deco):
            _saved[deco] = getattr(st, deco)
            setattr(st, deco, _noop_decorator)

    # st.columns / st.tabs need to return lists of correct length.
    _saved["columns"] = st.columns
    st.columns = _mock_columns
    _saved["tabs"] = st.tabs
    st.tabs = _mock_tabs

    # components.html — no-op.
    _components_saved = None
    try:
        import streamlit.components.v1 as components
        _components_saved = components.html
        components.html = lambda *a, **kw: None
    except ImportError:
        pass

    try:
        yield
    finally:
        for attr, val in _saved.items():
            setattr(st, attr, val)
        if _components_saved is not None:
            import streamlit.components.v1 as components
            components.html = _components_saved


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------

@click.command("warmup")
@click.argument("path", default=".", type=click.Path(exists=True))
def warmup(path):
    """Pre-warm the page cache for faster first load.

    Executes the project's book.py in headless mode (no Streamlit server)
    to build the TOC / markers / search-index cache and persist it to disk.

    Run this during Docker build so the first visitor loads instantly.

    \b
    Example (Dockerfile):
        RUN cd /app/${FOLDER} && uv run stx cache warmup .
    """
    console = get_console()
    project_dir = os.path.abspath(path)
    book_py = os.path.join(project_dir, "book.py")

    if not os.path.isfile(book_py):
        console.print(f"[red]Error:[/] {book_py} not found.")
        raise SystemExit(1)

    console.print(f"[bold]Cache warmup[/] for [cyan]{project_dir}[/]")

    # Add project dir to sys.path so ``import setup`` / ``import blocks`` work.
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    # Save and restore cwd (book.py may change it).
    original_cwd = os.getcwd()
    os.chdir(project_dir)

    with _headless_streamlit():
        # Enable warmup mode in streamtex.book
        from streamtex import book as _book_mod
        _book_mod._warmup_mode = True

        t0 = time.time()
        try:
            # Execute book.py — it will import setup, blocks, call st_book()
            # which detects _warmup_mode and only builds + saves the cache.
            code = Path(book_py).read_text(encoding="utf-8")
            exec(compile(code, book_py, "exec"),  # noqa: S102
                 {"__name__": "__main__", "__file__": book_py})
        except SystemExit:
            pass  # st.set_page_config may call sys.exit in some edge cases
        finally:
            _book_mod._warmup_mode = False
            os.chdir(original_cwd)

    elapsed = time.time() - t0

    # Check if the cache file was created.
    cache_file = os.path.join(project_dir, ".stx_cache", "page_cache.json")
    if os.path.isfile(cache_file):
        size_kb = os.path.getsize(cache_file) / 1024
        console.print(
            f"[green]Done[/] in {elapsed:.1f}s — "
            f"cache saved to [cyan].stx_cache/page_cache.json[/] ({size_kb:.0f} KB)"
        )
    else:
        console.print(
            f"[yellow]Warning:[/] warmup completed in {elapsed:.1f}s "
            f"but no cache file was created. "
            f"Is paginate=True set in st_book()?"
        )
