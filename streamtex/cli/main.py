"""Entry point for the stx CLI.

This module is referenced by pyproject.toml [project.scripts]:
    stx = "streamtex.cli.main:app"
"""

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


def app() -> None:
    """Launch the StreamTeX CLI."""
    _check_uv_version()

    try:
        import click  # noqa: F401
        import rich  # noqa: F401
    except ImportError:
        print(
            "Error: the stx CLI requires optional dependencies.\n"
            "Install them with:\n\n"
            "    uv add \"streamtex[cli]\"          # if using uv\n"
            "    pip install \"streamtex[cli]\"      # if using pip\n\n"
            "Or install click and rich directly:\n\n"
            "    uv add click rich jinja2           # if using uv\n"
            "    pip install click rich jinja2       # if using pip",
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
