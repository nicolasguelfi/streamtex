"""Click command hierarchy for the stx CLI."""

import click

from streamtex import __version__

from .bib_cmd import generate_stubs
from .shortcuts import run_lint, run_test
from .workspace_cmd import init, status


@click.group()
@click.version_option(version=__version__, prog_name="stx")
def cli():
    """StreamTeX CLI — manage workspaces, run tests, and more."""


# --- Top-level shortcuts ---------------------------------------------------

@cli.command()
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def test(verbose, extra_args):
    """Run the test suite (shortcut for pytest)."""
    run_test(verbose=verbose, extra_args=extra_args)


@cli.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def lint(extra_args):
    """Run the linter (shortcut for ruff check)."""
    run_lint(extra_args=extra_args)


# --- Workspace subgroup ----------------------------------------------------

@cli.group()
def workspace():
    """Manage StreamTeX workspaces."""


workspace.add_command(init)
workspace.add_command(status)


# --- Bibliography subgroup -------------------------------------------------

@cli.group()
def bib():
    """Bibliography utilities."""


bib.add_command(generate_stubs)
