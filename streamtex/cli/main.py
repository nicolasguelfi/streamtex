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
            "    uv add streamtex[cli]\n\n"
            "Or install click and rich directly:\n\n"
            "    uv add click rich jinja2",
            file=sys.stderr,
        )
        sys.exit(1)

    from .commands import cli

    cli()
