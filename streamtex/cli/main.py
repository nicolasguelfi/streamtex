"""Entry point for the stx CLI.

This module is referenced by pyproject.toml [project.scripts]:
    stx = "streamtex.cli.main:app"
"""

import os
import sys

# Minimum uv version required for Python 3.13 managed installs.
_MIN_UV_VERSION = "0.7.0"


def _check_uv_version() -> None:
    """Warn (not fatal) if uv is too old to manage Python 3.13."""
    import shutil
    import subprocess

    uv = shutil.which("uv")
    if not uv:
        print(
            "Note: uv is not installed. Some stx commands (install, update, publish) require it.\n"
            "Install uv:  curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            "More info:   https://docs.astral.sh/uv/getting-started/installation/\n",
            file=sys.stderr,
        )
        return
    try:
        result = subprocess.run(
            [uv, "--version"], capture_output=True, text=True, timeout=5,
        )
        # output like "uv 0.6.12 (abcdef 2025-01-01)"
        version_str = result.stdout.strip().split()[1] if result.stdout else ""
        parts = [int(x) for x in version_str.split(".")[:3]]
        min_parts = [int(x) for x in _MIN_UV_VERSION.split(".")[:3]]
        if parts < min_parts:
            print(
                f"Warning: uv {version_str} is outdated (minimum {_MIN_UV_VERSION}).\n"
                "Some features may not work. Update with:  brew upgrade uv\n",
                file=sys.stderr,
            )
    except Exception:
        pass  # best-effort check, never block the CLI


def _find_global_stx() -> str | None:
    """Find the global ``stx`` executable outside the current virtualenv.

    When streamtex is installed as a project dependency (without the ``[cli]``
    extra), a ``.venv/bin/stx`` shim is created that lacks click/rich.  This
    function locates the *real* ``stx`` — typically the one installed via
    ``uv tool install streamtex[cli]`` in ``~/.local/bin`` — so that the shim
    can transparently delegate to it.
    """
    venv = os.environ.get("VIRTUAL_ENV", "")
    if not venv:
        return None  # not in a venv — nothing to delegate to

    # Walk PATH, skipping entries inside the active venv
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if directory.startswith(venv):
            continue
        candidate = os.path.join(directory, "stx")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    # Fallback: standard uv tool location
    candidate = os.path.join(os.path.expanduser("~"), ".local", "bin", "stx")
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        return candidate

    return None


def app() -> None:
    """Launch the StreamTeX CLI."""
    _check_uv_version()

    try:
        import click  # noqa: F401
        import rich  # noqa: F401
    except ImportError:
        # CLI deps not installed — try to delegate to the global stx tool
        global_stx = _find_global_stx()
        if global_stx:
            import subprocess

            raise SystemExit(
                subprocess.run([global_stx, *sys.argv[1:]]).returncode
            )
        # No global stx found — show install instructions
        print(
            "Error: the stx CLI requires optional dependencies.\n"
            "Install them with:\n\n"
            "    uv add \"streamtex[cli]\"          # if using uv\n"
            "    pip install \"streamtex[cli]\"      # if using pip\n\n"
            "Or install click and rich directly:\n\n"
            "    uv add click rich                  # if using uv\n"
            "    pip install click rich              # if using pip",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        from .commands import cli
    except Exception as exc:
        print(f"Error: failed to load stx CLI: {exc}", file=sys.stderr)
        if "tomllib" in str(exc) or "tomli" in str(exc):
            print(
                "\nThis usually means your Python version is too old.\n"
                "StreamTeX requires Python >= 3.11. Check with: python3 --version\n"
                'To fix: uv tool install "streamtex[cli]" -U --python 3.13',
                file=sys.stderr,
            )
        sys.exit(1)

    cli()
