"""Entry point for the stx CLI.

This module is referenced by pyproject.toml [project.scripts]:
    stx = "streamtex.cli.main:app"
"""

import sys


def app() -> None:
    """Launch the StreamTeX CLI."""
    try:
        import click  # noqa: F401
        import rich  # noqa: F401
    except ImportError:
        print(
            "Error: the stx CLI requires optional dependencies.\n"
            "Install them with:\n\n"
            "    uv add \"streamtex[cli]\"\n\n"
            "Or install click and rich directly:\n\n"
            "    uv add click rich jinja2",
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
                "StreamTeX requires Python 3.11+. Check with: python3 --version\n"
                "To fix: uv tool install \"streamtex[cli]\" -U --python 3.12",
                file=sys.stderr,
            )
        sys.exit(1)

    cli()
