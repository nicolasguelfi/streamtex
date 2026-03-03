"""Click command hierarchy for the stx CLI."""

import click

from streamtex import __version__

from .bib_cmd import generate_stubs
from .claude_cmd import check_cmd as claude_check
from .claude_cmd import diff_cmd as claude_diff
from .claude_cmd import install as claude_install
from .claude_cmd import list_cmd as claude_list
from .claude_cmd import update_cmd as claude_update
from .deploy_cmd import docker as deploy_docker
from .deploy_cmd import huggingface_cmd as deploy_huggingface
from .deploy_cmd import preflight as deploy_preflight
from .deploy_cmd import render_cmd as deploy_render
from .deploy_cmd import status_cmd as deploy_status
from .project_cmd import new as project_new
from .project_cmd import validate as project_validate
from .publish_cmd import check_cmd as publish_check
from .publish_cmd import pypi_cmd as publish_pypi
from .shortcuts import run_lint, run_test
from .workspace_cmd import clone, init, link, status, sync


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
workspace.add_command(clone)
workspace.add_command(link)
workspace.add_command(status)
workspace.add_command(sync)


# --- Claude subgroup -------------------------------------------------------

@cli.group()
def claude():
    """Manage Claude AI profiles."""


claude.add_command(claude_install)
claude.add_command(claude_list)
claude.add_command(claude_update)
claude.add_command(claude_diff)
claude.add_command(claude_check)


# --- Bibliography subgroup -------------------------------------------------

@cli.group()
def bib():
    """Bibliography utilities."""


bib.add_command(generate_stubs)


# --- Project subgroup ------------------------------------------------------

@cli.group()
def project():
    """Create and validate StreamTeX projects."""


project.add_command(project_new)
project.add_command(project_validate)


# --- Deploy subgroup -------------------------------------------------------

@cli.group()
def deploy():
    """Deploy StreamTeX projects."""


deploy.add_command(deploy_preflight)
deploy.add_command(deploy_docker)
deploy.add_command(deploy_render)
deploy.add_command(deploy_huggingface)
deploy.add_command(deploy_status)


# --- Publish subgroup ------------------------------------------------------

@cli.group()
def publish():
    """Publish StreamTeX to PyPI."""


publish.add_command(publish_check)
publish.add_command(publish_pypi)
