"""Project upgrade command: stx project upgrade."""

import os
import shutil
import subprocess
from importlib.metadata import version as pkg_version

import click

from .console import get_console
from .migrations import check_compatibility, detect_project_version, get_pending_migrations
from .migrations.registry import _version_tuple, write_version_marker


def _get_installed_version() -> str:
    """Return the installed streamtex version."""
    return pkg_version("streamtex")


@click.command("upgrade")
@click.argument("path", default=".")
@click.option("--check", "check_only", is_flag=True, help="Check compatibility only, don't apply changes.")
@click.option("--dry-run", is_flag=True, help="Show what would change without applying.")
@click.option("--skip-sync", is_flag=True, help="Skip uv sync after upgrade.")
@click.option("--skip-claude", is_flag=True, help="Skip Claude profile update.")
def upgrade(path, check_only, dry_run, skip_sync, skip_claude):
    """Upgrade a StreamTeX project to the current library version.

    Detects the project's current version, checks for compatibility issues,
    applies structural migrations, and re-syncs dependencies.

    \b
    Examples:
      stx project upgrade                # upgrade current directory
      stx project upgrade --check        # check only, don't modify
      stx project upgrade --dry-run      # preview changes
      stx project upgrade projects/demo  # upgrade a specific project
    """
    console = get_console()
    project_path = os.path.abspath(path)

    # Validate project
    if not os.path.isfile(os.path.join(project_path, "pyproject.toml")):
        raise click.ClickException(
            f"No pyproject.toml found in {project_path}. Is this a StreamTeX project?"
        )

    # Step counter
    total_steps = 5 if not check_only else 2
    if skip_sync:
        total_steps -= 1
    if skip_claude:
        total_steps -= 1
    step = 0

    def _step(label: str) -> None:
        nonlocal step
        step += 1
        console.print(f"\n[bold cyan][{step}/{total_steps}][/bold cyan] {label}")

    # --- Step 1: Detect versions ---
    _step("Detecting versions ...")
    current_ver = detect_project_version(project_path)
    installed_ver = _get_installed_version()
    console.print(f"  Project: [yellow]{current_ver}[/yellow]")
    console.print(f"  Installed: [green]{installed_ver}[/green]")

    if _version_tuple(current_ver) >= _version_tuple(installed_ver):
        console.print("\n[bold green]Project is already up to date.[/bold green]")
        return

    # --- Step 2: Compatibility check ---
    _step("Checking compatibility ...")
    issues = check_compatibility(project_path, current_ver, installed_ver)

    if issues:
        from rich.table import Table

        table = Table(title="Compatibility Issues")
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right")
        table.add_column("Severity")
        table.add_column("Code")
        table.add_column("Message")

        for issue in issues:
            rel_file = os.path.relpath(issue.file, project_path)
            sev_style = "[red]error[/red]" if issue.severity == "error" else "[yellow]warning[/yellow]"
            table.add_row(rel_file, str(issue.line), sev_style, issue.code, issue.message)

        console.print(table)

        if any(i.suggestion for i in issues):
            console.print("\n[bold]Suggestions:[/bold]")
            for issue in issues:
                if issue.suggestion:
                    rel_file = os.path.relpath(issue.file, project_path)
                    console.print(f"  {rel_file}:{issue.line} -> {issue.suggestion}")

        errors = [i for i in issues if i.severity == "error"]
        if errors:
            console.print(
                f"\n[red]{len(errors)} error(s) found.[/red] "
                "Fix these before upgrading, or use [bold]/stx-migrate[/bold] for assisted fixes."
            )
            if check_only:
                raise SystemExit(1)
    else:
        console.print("  [green]No compatibility issues found.[/green]")

    if check_only:
        console.print("\n[bold]Check complete.[/bold] Run without --check to apply migrations.")
        return

    # --- Step 3: Apply migrations ---
    _step("Applying migrations ...")
    pending = get_pending_migrations(current_ver, installed_ver)

    if not pending:
        console.print("  [green]No structural migrations needed.[/green]")
    else:
        for migration in pending:
            if migration.check(project_path):
                result = migration.apply(project_path, dry_run=dry_run)
                prefix = "[dim](dry-run)[/dim] " if dry_run else ""
                if result.applied:
                    console.print(f"  {prefix}[green]v{result.version}[/green]: {result.description}")
                    for change in result.changes:
                        console.print(f"    - {change}")
                else:
                    console.print(f"  {prefix}[yellow]v{result.version}[/yellow]: skipped ({result.skipped_reason})")
            else:
                console.print(f"  [dim]v{migration.version}: already applied[/dim]")

    # --- Step 4: Update Claude profile ---
    if not skip_claude:
        _step("Updating Claude profile ...")
        if dry_run:
            console.print("  [dim](dry-run) Would update Claude profile[/dim]")
        else:
            try:
                from .claude_cmd import find_claude_repo, install_profile, read_installed_profile
                from .workspace_cmd import find_workspace_root, load_stx_toml

                ws_root = find_workspace_root(project_path)
                if ws_root:
                    config = load_stx_toml(ws_root)
                    claude_repo = find_claude_repo(ws_root, config)
                    profile = read_installed_profile(project_path) or "project"
                    installed = install_profile(claude_repo, profile, project_path)
                    console.print(f"  [green]Profile '{profile}':[/green] {len(installed)} files")
                else:
                    console.print("  [yellow]Not in a workspace — skipped.[/yellow]")
            except click.ClickException:
                console.print("  [yellow]Claude repo not available — skipped.[/yellow]")

    # --- Step 5: Re-sync dependencies ---
    if not skip_sync:
        _step("Syncing dependencies ...")
        if dry_run:
            console.print("  [dim](dry-run) Would run uv sync[/dim]")
        else:
            uv = shutil.which("uv")
            if uv:
                # Upgrade streamtex in lock first
                subprocess.run(
                    [uv, "lock", "--upgrade-package", "streamtex"],
                    cwd=project_path,
                    capture_output=True, text=True, timeout=120,
                )
                result = subprocess.run(
                    [uv, "sync"],
                    cwd=project_path,
                    capture_output=True, text=True, timeout=120,
                )
                if result.returncode == 0:
                    console.print("  [green]uv sync: ok[/green]")
                else:
                    console.print(f"  [yellow]uv sync: {result.stderr.strip()}[/yellow]")
            else:
                console.print("  [yellow]uv not found — skipped.[/yellow]")

    # --- Write version marker ---
    if not dry_run:
        write_version_marker(project_path, installed_ver)
        console.print(f"\n[bold green]Upgrade complete![/bold green] ({current_ver} -> {installed_ver})")
        console.print("\n  Review changes with: [bold]git diff[/bold]")
        console.print("  Validate project: [bold]stx project validate[/bold]")
    else:
        console.print("\n[bold]Dry run complete.[/bold] Run without --dry-run to apply changes.")
