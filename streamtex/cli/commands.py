"""Click command hierarchy for the stx CLI."""

from importlib.metadata import version

import click

__version__ = version("streamtex")

from .bib_cmd import generate_stubs
from .cache_cmd import warmup as cache_warmup
from .claude_cmd import check_cmd as claude_check
from .claude_cmd import diff_cmd as claude_diff
from .claude_cmd import install as claude_install
from .claude_cmd import list_cmd as claude_list
from .claude_cmd import update_cmd as claude_update
from .deploy_cmd import configure_domain_cmd as deploy_configure_domain
from .deploy_cmd import docker as deploy_docker
from .deploy_cmd import env_sync_cmd as deploy_env_sync
from .deploy_cmd import hetzner_cmd as deploy_hetzner
from .deploy_cmd import huggingface_cmd as deploy_huggingface
from .deploy_cmd import install_coolify_cmd as deploy_install_coolify
from .deploy_cmd import preflight as deploy_preflight
from .deploy_cmd import provision_cmd as deploy_provision
from .deploy_cmd import render_cmd as deploy_render
from .deploy_cmd import secure_cmd as deploy_secure
from .deploy_cmd import setup_cmd as deploy_setup
from .deploy_cmd import status_cmd as deploy_status
from .deploy_cmd import update_cmd as deploy_update
from .install_cmd import install as stx_install
from .project_cmd import new as project_new
from .project_cmd import validate as project_validate
from .publish_cmd import check_cmd as publish_check
from .publish_cmd import pypi_cmd as publish_pypi
from .run_cmd import run as stx_run
from .shortcuts import run_lint, run_test
from .status_cmd import status as workspace_status
from .upgrade_cmd import upgrade as project_upgrade
from .workspace_cmd import update as workspace_update


@click.group()
@click.version_option(version=__version__, prog_name="stx")
def cli():
    """StreamTeX CLI — manage workspaces, run tests, and more."""


# --- Top-level commands ----------------------------------------------------

cli.add_command(stx_install)
cli.add_command(stx_run)
cli.add_command(workspace_update, name="update")
cli.add_command(workspace_status, name="status")


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
project.add_command(project_upgrade)


# --- Deploy subgroup -------------------------------------------------------

@cli.group()
def deploy():
    """Deploy StreamTeX projects."""


deploy.add_command(deploy_preflight)
deploy.add_command(deploy_docker)
deploy.add_command(deploy_render)
deploy.add_command(deploy_huggingface)
deploy.add_command(deploy_status)
deploy.add_command(deploy_env_sync)
deploy.add_command(deploy_setup)
deploy.add_command(deploy_hetzner)
deploy.add_command(deploy_update)
deploy.add_command(deploy_provision)
deploy.add_command(deploy_secure)
deploy.add_command(deploy_install_coolify)
deploy.add_command(deploy_configure_domain)


# --- Publish subgroup ------------------------------------------------------

@cli.group()
def publish():
    """Publish StreamTeX to PyPI."""


publish.add_command(publish_check)
publish.add_command(publish_pypi)


# --- Cache subgroup -------------------------------------------------------

@cli.group()
def cache():
    """Manage the page cache."""


cache.add_command(cache_warmup)
