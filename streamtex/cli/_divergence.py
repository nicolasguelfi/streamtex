"""Warn (and optionally prompt) when the global ``stx`` binary and the
current project's venv have a different ``streamtex`` version installed.

Introspection commands (``pack list``, ``component list``, ``kit list``,
``ds list``, ``pack validate``) read entry points from the Python process
that runs them. The global ``stx`` binary lives in the tool venv
(``uv tool install``); commands in a project see the project venv only when
launched via ``uv run stx``. Without this check, a developer running
``stx component list`` while their project venv pulls a different streamtex
version sees a silently truncated (or wrong) listing.

No environment variables are used to control this behaviour (project policy:
env vars are reserved for secrets / system / subprocess IPC, never for
config switches). Suppression is entirely in-process:

  * when the running interpreter IS the project venv, there is nothing to
    warn about — we return silently;
  * differences that are only a PEP 440 local/dev suffix (e.g. ``0.7.18``
    vs ``0.7.18+local``) are treated as aligned;
  * the interactive prompt offers a "never" choice that records a persistent
    dismissal in ``.stx_cache/`` (per project, per version pair).
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import click

from .console import get_console

_CACHE_TTL_SECONDS = 60 * 60  # 1 hour
_CACHE_FILENAME = "divergence.json"
_FOREVER_PREFIX = "never:"
_VERSION_RE = re.compile(r"""__version__\s*=\s*['"]([^'"]+)['"]""")


def _public_version(version: str) -> str:
    """Strip the PEP 440 local segment (everything after ``+``).

    ``uv tool install -e`` often yields a local-tagged version
    (``0.7.18+g1a2b3c``) for the same release the project pins from PyPI
    (``0.7.18``). Those are the same upstream code; only a genuine base
    difference (``0.7.17`` vs ``0.7.18``) is worth a warning.
    """
    return version.split("+", 1)[0]


def _tool_version() -> str:
    """Version of streamtex as installed in the venv currently running stx."""
    from streamtex import __version__

    return __version__


def _project_streamtex_init(project_dir: Path) -> Path | None:
    """Return the path to streamtex/__init__.py inside the project's venv,
    or None if the project venv doesn't ship streamtex yet."""
    venv = project_dir / ".venv"
    if not venv.is_dir():
        return None
    # POSIX layout: .venv/lib/pythonX.Y/site-packages/streamtex/__init__.py
    for lib_root in (venv / "lib", venv / "Lib"):
        if not lib_root.is_dir():
            continue
        for py_dir in lib_root.glob("python*"):
            candidate = py_dir / "site-packages" / "streamtex" / "__init__.py"
            if candidate.is_file():
                return candidate
        # Windows layout: .venv/Lib/site-packages/...
        candidate = lib_root / "site-packages" / "streamtex" / "__init__.py"
        if candidate.is_file():
            return candidate
    return None


def _project_version(project_dir: Path) -> str | None:
    """Read streamtex.__version__ from the project venv without importing it.

    Importing would either crash (incompatible Python) or pollute the running
    process; a regex against ``__init__.py`` is enough.
    """
    init_py = _project_streamtex_init(project_dir)
    if init_py is None:
        return None
    try:
        text = init_py.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _VERSION_RE.search(text)
    return m.group(1) if m else None


def _cache_path(project_dir: Path) -> Path:
    return project_dir / ".stx_cache" / _CACHE_FILENAME


def _load_cache(project_dir: Path) -> dict:
    p = _cache_path(project_dir)
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(project_dir: Path, data: dict) -> None:
    p = _cache_path(project_dir)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        # Cache is best-effort; never crash the CLI because we couldn't write.
        pass


def _recently_warned(project_dir: Path, key: str, *, now: float | None = None) -> bool:
    data = _load_cache(project_dir)
    ts = data.get(key)
    if not isinstance(ts, (int, float)):
        return False
    return ((now or time.time()) - ts) < _CACHE_TTL_SECONDS


def _mark_warned(project_dir: Path, key: str, *, now: float | None = None) -> None:
    data = _load_cache(project_dir)
    data[key] = now if now is not None else time.time()
    _save_cache(project_dir, data)


def _dismissed_forever(project_dir: Path, key: str) -> bool:
    return _load_cache(project_dir).get(_FOREVER_PREFIX + key) is True


def _mark_forever(project_dir: Path, key: str) -> None:
    data = _load_cache(project_dir)
    data[_FOREVER_PREFIX + key] = True
    _save_cache(project_dir, data)


def _running_in_project_venv(project_dir: Path) -> bool:
    """True when the interpreter executing this CLI lives inside the project's
    own .venv — i.e. we were launched via ``uv run stx`` (or an activated
    venv). In that case introspection already targets the project, so there is
    no divergence to surface. Replaces the old STX_DELEGATED env flag with an
    objective check."""
    try:
        exe = Path(sys.executable).resolve()
        venv = (project_dir / ".venv").resolve()
    except OSError:
        return False
    return exe.is_relative_to(venv)


def _find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from cwd looking for a directory that holds both pyproject.toml
    and stx.toml. Returns None when called from a workspace-level path."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "stx.toml").is_file():
            return candidate
    return None


def maybe_warn_divergence(command_name: str) -> None:
    """Surface a tool/project streamtex divergence before a venv-sensitive
    command runs. No-ops when there's nothing to warn about.
    """
    project_dir = _find_project_root()
    if project_dir is None:
        return  # Workspace-level invocation — no project venv to compare.

    if _running_in_project_venv(project_dir):
        return  # Already in the project venv (e.g. `uv run stx`); moot.

    project_version = _project_version(project_dir)
    if project_version is None:
        return  # Project venv not built yet or streamtex not installed there.

    tool_version = _tool_version()
    if _public_version(project_version) == _public_version(tool_version):
        return  # Same upstream release (local/dev suffix aside); benign.

    cache_key = f"{command_name}|{tool_version}|{project_version}"
    if _dismissed_forever(project_dir, cache_key):
        return  # User chose "never" for this exact divergence.
    if _recently_warned(project_dir, cache_key):
        return

    console = get_console()
    console.print(
        "\n[yellow bold]⚠ streamtex version divergence[/yellow bold]\n"
        f"  • global [cyan]stx[/cyan]                : streamtex "
        f"[bold]{tool_version}[/bold] (tool venv)\n"
        f"  • project [cyan]{project_dir.name}[/cyan]: streamtex "
        f"[bold]{project_version}[/bold] (./.venv)\n"
        "\n"
        f"  [cyan]stx {command_name}[/cyan] introspects the tool venv, so the\n"
        f"  output reflects streamtex [bold]{tool_version}[/bold] — possibly\n"
        "  missing packs/components installed in the project venv.\n"
        "\n"
        "  Fixes:\n"
        f"    [cyan]uv run stx {command_name}[/cyan]   "
        "(use the project venv for this command)\n"
        "    [cyan]stx dev link streamtex[/cyan]            "
        "(align project on tool's local source)\n"
    )
    _mark_warned(project_dir, cache_key)

    if sys.stdin.isatty() and sys.stdout.isatty():
        # y = proceed once, n = abort, v = never warn again for this pair.
        choice = click.prompt(
            f"Continue running `stx {command_name}` with the tool venv? "
            "[y]es / [n]o / ne[v]er",
            type=click.Choice(["y", "n", "v"], case_sensitive=False),
            default="y",
            show_choices=False,
        ).lower()
        if choice == "n":
            raise click.Abort()
        if choice == "v":
            _mark_forever(project_dir, cache_key)
    # Non-TTY: warning emitted, proceed without blocking the caller.
