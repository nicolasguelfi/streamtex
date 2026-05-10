"""Click commands: ``stx patterns ...``.

Thin adapter on top of :mod:`streamtex.patterns`. Translates ``PatternError``
subclasses into ``click.ClickException`` and formats output via Rich.
"""

from __future__ import annotations

import json
import logging
from functools import wraps
from pathlib import Path

import click

from streamtex.patterns import (
    DriftError,
    PatternError,
    SourceNotFoundError,
    ValidationError,
)
from streamtex.patterns.installer import (
    DEFAULT_TARGET_REL,
    build_install_plan,
    execute_install,
    remove_pattern,
)
from streamtex.patterns.manifest import load_meta, sha256_file
from streamtex.patterns.preset import (
    list_presets as _list_presets,
)
from streamtex.patterns.preset import (
    resolve_preset,
)
from streamtex.patterns.resolver import resolve_source
from streamtex.patterns.updater import apply_update, compute_drift
from streamtex.patterns.validator import validate_all, validate_file

from .console import get_console
from .workspace_cmd import find_workspace_root

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _handle_errors(func):
    """Decorator: convert ``PatternError`` to ``click.ClickException``."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SourceNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc
        except DriftError as exc:
            raise click.ClickException(str(exc)) from exc
        except ValidationError as exc:
            raise click.ClickException(
                f"validation failed for {exc.name}: "
                + "; ".join(exc.issues)
            ) from exc
        except PatternError as exc:
            raise click.ClickException(str(exc)) from exc
        except NotImplementedError as exc:
            raise click.ClickException(str(exc)) from exc

    return wrapper


def _resolve_target(target: str | None) -> Path:
    """Return absolute target dir for installed patterns."""
    if target:
        return Path(target).expanduser().resolve()
    return (Path.cwd() / DEFAULT_TARGET_REL).resolve()


def _resolve_project_dir() -> Path:
    """Return the current project directory (cwd)."""
    return Path.cwd().resolve()


def _resolve_workspace_root() -> Path | None:
    ws = find_workspace_root()
    return Path(ws).resolve() if ws else None


def _resolve(source_override: str | None):
    return resolve_source(
        _resolve_project_dir(),
        cli_override=source_override,
        workspace_root=_resolve_workspace_root(),
    )


def _split_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(x.strip() for x in value.split(",") if x.strip())


# ---------------------------------------------------------------------------
# Group
# ---------------------------------------------------------------------------

@click.group(name="patterns")
def patterns() -> None:
    """Manage StreamTeX design patterns (install, update, validate, ...)."""


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

@patterns.command(name="list")
@click.option(
    "--remote/--local", "remote", default=False,
    help="List patterns from the source repo (--remote) or installed (--local).",
)
@click.option("--source", "source_override", default=None, help="Override patterns source.")
@click.option("--preset", default=None, help="Filter by preset (with --remote).")
@click.option("--tag", default=None, help="Filter by tag.")
@click.option(
    "--format", "fmt", type=click.Choice(["table", "json", "names"]),
    default="table",
)
@_handle_errors
def list_cmd(remote: bool, source_override: str | None, preset: str | None,
             tag: str | None, fmt: str) -> None:
    """List patterns available locally or remotely."""
    console = get_console()

    if remote:
        resolved = _resolve(source_override)
        if preset:
            rp = resolve_preset(resolved.path, preset)
            entries = [
                {"name": p.stem, "from": str(p.relative_to(resolved.path))}
                for p in rp.pattern_files
            ]
        else:
            from streamtex.patterns.installer import _all_patterns
            entries = [
                {"name": p.stem, "from": str(p.relative_to(resolved.path))}
                for p in _all_patterns(resolved.path)
            ]
        title = f"Remote patterns ({resolved.path.name})"
    else:
        target = _resolve_target(None)
        meta = load_meta(target)
        entries = [
            {"name": r.name, "from": r.from_} for r in meta.patterns
        ]
        title = f"Installed patterns ({target})"

    if tag:
        # tag filter requires reading frontmatter; cheap pass for --remote only.
        filtered = []
        from streamtex.patterns.manifest import (
            parse_frontmatter,
            split_frontmatter,
        )
        for entry in entries:
            file_path = (
                resolved.path / entry["from"] if remote
                else _resolve_target(None) / f"{entry['name']}.md"
            )
            try:
                yaml, _ = split_frontmatter(file_path.read_text(encoding="utf-8"))
                fm = parse_frontmatter(yaml)
            except Exception:
                continue
            if tag in fm.tags:
                filtered.append(entry)
        entries = filtered

    if fmt == "json":
        click.echo(json.dumps(entries, indent=2))
        return
    if fmt == "names":
        for e in entries:
            click.echo(e["name"])
        return

    from rich.table import Table
    table = Table(title=title)
    table.add_column("Name", style="cyan")
    table.add_column("From")
    for e in entries:
        table.add_row(e["name"], e["from"])
    console.print(table)
    console.print(f"  [dim]{len(entries)} pattern(s)[/dim]")


# ---------------------------------------------------------------------------
# presets
# ---------------------------------------------------------------------------

@patterns.command(name="presets")
@click.option("--source", "source_override", default=None)
@click.option(
    "--format", "fmt", type=click.Choice(["table", "json", "names"]),
    default="table",
)
@_handle_errors
def presets_cmd(source_override: str | None, fmt: str) -> None:
    """List presets available in the patterns source."""
    resolved = _resolve(source_override)
    presets_list = _list_presets(resolved.path)

    if fmt == "json":
        click.echo(json.dumps(
            [
                {
                    "name": p.name,
                    "description": p.description,
                    "extends": p.extends,
                    "include": list(p.include),
                    "exclude": list(p.exclude),
                }
                for p in presets_list
            ],
            indent=2,
        ))
        return
    if fmt == "names":
        for p in presets_list:
            click.echo(p.name)
        return

    from rich.table import Table
    table = Table(title=f"Presets in {resolved.path.name}")
    table.add_column("Name", style="cyan")
    table.add_column("Extends")
    table.add_column("Description")
    for p in presets_list:
        table.add_row(p.name, p.extends or "—", p.description)
    get_console().print(table)


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

@patterns.command(name="install")
@click.argument("patterns_args", nargs=-1)
@click.option("--preset", default=None, help="Install a preset.")
@click.option("--pattern", "pattern_csv", default=None,
              help="Install specific patterns (comma-separated).")
@click.option("--all", "install_all", is_flag=True, help="Install all patterns.")
@click.option("--exclude", default=None, help="Exclude patterns (comma-separated).")
@click.option("--mode", type=click.Choice(["copy", "symlink"]), default="copy")
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None,
              help=f"Target directory (default: {DEFAULT_TARGET_REL}).")
@click.option("--force", is_flag=True, help="Overwrite locally modified patterns.")
@click.option("--dry-run", is_flag=True, help="Show plan without writing.")
@_handle_errors
def install_cmd(patterns_args: tuple[str, ...], preset: str | None,
                pattern_csv: str | None, install_all: bool,
                exclude: str | None, mode: str, source_override: str | None,
                target: str | None, force: bool, dry_run: bool) -> None:
    """Install patterns into the project."""
    console = get_console()
    resolved = _resolve(source_override)
    target_path = _resolve_target(target)

    individual = tuple(patterns_args) + _split_csv(pattern_csv)

    plan = build_install_plan(
        target=target_path,
        source=resolved.path,
        preset=preset,
        individual_patterns=individual,
        install_all=install_all,
        exclude=_split_csv(exclude),
        mode=mode,
        force=force,
    )

    if dry_run:
        console.print(
            f"[bold]Dry-run install[/bold] -> {target_path}\n"
            f"  source: {resolved.path}\n"
            f"  preset: {preset or '—'}  mode: {mode}  "
            f"force: {force}  initial: {plan.is_initial}"
        )
        for src in plan.selected_files:
            console.print(f"  + {src.relative_to(resolved.path)}")
        console.print(f"[dim]{len(plan.selected_files)} file(s) selected[/dim]")
        return

    result = execute_install(plan, raw_source=resolved.raw_value or str(resolved.path))
    console.print(f"[green]Installed {len(result.installed)} pattern(s)[/green]")
    if result.overwritten:
        console.print(
            f"[yellow]Overwrote {len(result.overwritten)} existing file(s)"
            "[/yellow]"
        )
    console.print(f"  target: {result.target}")
    if result.meta_path:
        console.print(f"  meta:   {result.meta_path}")


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

@patterns.command(name="update")
@click.argument("names", nargs=-1)
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None)
@click.option("--force", is_flag=True)
@click.option("--dry-run", is_flag=True)
@_handle_errors
def update_cmd(names: tuple[str, ...], source_override: str | None,
               target: str | None, force: bool, dry_run: bool) -> None:
    """Update installed patterns from the source."""
    resolved = _resolve(source_override)
    target_path = _resolve_target(target)
    reports, applied = apply_update(
        target_path, resolved.path,
        force=force, only=tuple(names), dry_run=dry_run,
    )
    console = get_console()
    if dry_run:
        console.print("[bold]Dry-run update[/bold]")
    if not applied:
        console.print("[bold green]Up to date.[/bold green]")
    else:
        console.print(
            f"[green]Updated {len(applied)} pattern(s):[/green] "
            + ", ".join(applied)
        )
    for r in reports:
        if r.status.value not in ("clean", "upstream_ahead"):
            console.print(f"  [yellow]{r.name}: {r.status.value}[/yellow]")


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

@patterns.command(name="sync")
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None)
@click.option("--force", is_flag=True)
@click.option("--dry-run", is_flag=True)
@_handle_errors
def sync_cmd(source_override: str | None, target: str | None,
             force: bool, dry_run: bool) -> None:
    """Idempotent: install missing + update existing patterns."""
    resolved = _resolve(source_override)
    target_path = _resolve_target(target)
    meta = load_meta(target_path)
    preset = meta.preset

    if preset is None:
        # No preset stored: just run update.
        apply_update(target_path, resolved.path, force=force, dry_run=dry_run)
        return

    # Compute missing files
    rp = resolve_preset(resolved.path, preset)
    have = {r.name for r in meta.patterns}
    missing = [p for p in rp.pattern_files if p.stem not in have]

    if missing:
        plan = build_install_plan(
            target=target_path,
            source=resolved.path,
            individual_patterns=tuple(p.stem for p in missing),
            mode=meta.mode,
            force=force,
        )
        if not dry_run:
            execute_install(plan, raw_source=meta.source)

    apply_update(target_path, resolved.path, force=force, dry_run=dry_run)
    get_console().print("[green]Sync complete.[/green]")


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------

@patterns.command(name="remove")
@click.argument("name")
@click.option("--target", default=None)
@click.option("--dry-run", is_flag=True)
@_handle_errors
def remove_cmd(name: str, target: str | None, dry_run: bool) -> None:
    """Remove an installed pattern."""
    target_path = _resolve_target(target)
    remove_pattern(target_path, name, dry_run=dry_run)
    msg = "would remove" if dry_run else "removed"
    get_console().print(f"[green]{msg} {name}[/green]")


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@patterns.command(name="status")
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
@_handle_errors
def status_cmd(source_override: str | None, target: str | None, fmt: str) -> None:
    """Compare installed patterns against the source."""
    resolved = _resolve(source_override)
    target_path = _resolve_target(target)
    reports = compute_drift(target_path, resolved.path)

    if fmt == "json":
        click.echo(json.dumps([
            {
                "name": r.name,
                "status": r.status.value,
                "local_sha": r.local_sha,
                "installed_sha": r.installed_sha,
                "source_sha": r.source_sha,
            }
            for r in reports
        ], indent=2))
        return

    from rich.table import Table
    table = Table(title=f"Patterns status ({target_path})")
    table.add_column("Name", style="cyan")
    table.add_column("Status")
    table.add_column("Local")
    table.add_column("Source")
    for r in reports:
        table.add_row(
            r.name, r.status.value,
            (r.local_sha or "—")[:8],
            (r.source_sha or "—")[:8],
        )
    get_console().print(table)


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------

@patterns.command(name="diff")
@click.argument("name")
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None)
@_handle_errors
def diff_cmd(name: str, source_override: str | None, target: str | None) -> None:
    """Show unified diff between installed pattern and source."""
    import difflib

    resolved = _resolve(source_override)
    target_path = _resolve_target(target)
    meta = load_meta(target_path)
    rec = next((r for r in meta.patterns if r.name == name), None)
    if rec is None:
        raise click.ClickException(f"pattern {name!r} not tracked")

    local = (target_path / f"{name}.md").read_text(encoding="utf-8").splitlines(keepends=True)
    src_path = resolved.path / rec.from_
    remote = src_path.read_text(encoding="utf-8").splitlines(keepends=True) \
        if src_path.is_file() else []
    diff = difflib.unified_diff(
        remote, local,
        fromfile=f"source/{rec.from_}",
        tofile=f"target/{name}.md",
    )
    out = "".join(diff)
    click.echo(out if out else f"# {name}: identical")


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

@patterns.command(name="validate")
@click.argument("name", required=False)
@click.option("--all", "validate_all_flag", is_flag=True)
@click.option("--remote", is_flag=True, help="Validate the source repo instead of installed copy.")
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None)
@click.option("--verbose", is_flag=True)
@_handle_errors
def validate_cmd(name: str | None, validate_all_flag: bool, remote: bool,
                 source_override: str | None, target: str | None,
                 verbose: bool) -> None:
    """Validate pattern files against the A2 spec."""
    console = get_console()

    if remote:
        resolved = _resolve(source_override)
        from streamtex.patterns.installer import _all_patterns
        files = _all_patterns(resolved.path)
        scan_dir = resolved.path
    else:
        target_path = _resolve_target(target)
        files = sorted(p for p in target_path.glob("*.md") if not p.name.startswith("_"))
        scan_dir = target_path

    if name and not validate_all_flag:
        files = [p for p in files if p.stem == name]
        if not files:
            raise click.ClickException(f"pattern {name!r} not found in {scan_dir}")

    reports = [validate_file(p) for p in files]

    from rich.table import Table
    table = Table(title="Validation report")
    table.add_column("Name", style="cyan")
    table.add_column("Status")
    table.add_column("Issues", justify="right")
    table.add_column("Warnings", justify="right")
    for r in reports:
        status = "[green]OK[/green]" if r.ok else "[red]FAIL[/red]"
        table.add_row(r.name, status, str(len(r.issues)), str(len(r.warnings)))
    console.print(table)

    if verbose:
        for r in reports:
            if r.issues or r.warnings:
                console.print(f"\n[bold]{r.name}[/bold] ({r.file})")
                for i in r.issues:
                    console.print(f"  [red]issue:[/red] {i}")
                for w in r.warnings:
                    console.print(f"  [yellow]warn:[/yellow] {w}")

    failed = [r for r in reports if not r.ok]
    if failed:
        raise click.ClickException(
            f"{len(failed)} pattern(s) failed validation"
        )

    # silence unused
    _ = validate_all


# ---------------------------------------------------------------------------
# promote (stub-ish — minimal copy + meta refresh)
# ---------------------------------------------------------------------------

@patterns.command(name="promote")
@click.argument("name")
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None)
@click.option("--message", default=None, help="Commit message override.")
@click.option("--no-commit", is_flag=True, help="Skip git commit.")
@click.option("--allow-dirty", is_flag=True)
@_handle_errors
def promote_cmd(name: str, source_override: str | None, target: str | None,
                message: str | None, no_commit: bool, allow_dirty: bool) -> None:
    """Promote a locally modified pattern back into the source repo."""
    import shutil
    import subprocess

    console = get_console()
    resolved = _resolve(source_override)
    target_path = _resolve_target(target)
    meta = load_meta(target_path)
    rec = next((r for r in meta.patterns if r.name == name), None)
    if rec is None:
        raise click.ClickException(f"pattern {name!r} not tracked")

    local = target_path / f"{name}.md"
    if not local.is_file():
        raise click.ClickException(f"local pattern file missing: {local}")

    src_path = resolved.path / rec.from_
    local_sha = sha256_file(local)
    if src_path.is_file() and sha256_file(src_path) == local_sha:
        console.print("[yellow]No changes to promote (local == source).[/yellow]")
        return

    # Validate before promoting
    report = validate_file(local)
    if report.issues:
        raise ValidationError(name, list(report.issues))

    # Refuse if source is dirty unless allowed
    if not allow_dirty and (resolved.path / ".git").exists():
        try:
            res = subprocess.run(
                ["git", "-C", str(resolved.path), "status", "--porcelain"],
                capture_output=True, text=True, timeout=10,
            )
            if res.returncode == 0 and res.stdout.strip():
                raise click.ClickException(
                    f"source repo {resolved.path} is dirty; "
                    "commit/stash or pass --allow-dirty"
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    src_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(local, src_path)
    rec.installed_sha = local_sha
    rec.sha = local_sha
    from streamtex.patterns.manifest import save_meta as _save_meta
    _save_meta(target_path, meta)

    if not no_commit and (resolved.path / ".git").exists():
        msg = message or f"patterns: promote {name}"
        try:
            subprocess.run(
                ["git", "-C", str(resolved.path), "add", str(src_path.relative_to(resolved.path))],
                check=True, timeout=10,
            )
            subprocess.run(
                ["git", "-C", str(resolved.path), "commit", "-m", msg],
                check=True, timeout=10,
            )
            console.print(f"[green]Promoted and committed: {name}[/green]")
            console.print(
                f"  Don't forget: cd {resolved.path} && git push"
            )
            return
        except subprocess.CalledProcessError as exc:
            raise click.ClickException(f"git commit failed: {exc}") from exc

    console.print(f"[green]Promoted (file copied): {name}[/green]")


# ---------------------------------------------------------------------------
# init (scaffolder)
# ---------------------------------------------------------------------------

_PATTERN_TEMPLATE = """\
---
name: {name}
type: pattern
description: {description}
tags: [{tags}]
extrapolable: {extrapolable}
since: {since}
---

# {title}

TODO: short narrative summary.

## Visual

TODO: ASCII / image preview.

## Structure

- TODO

## Styling rules

| Element | Property | Value |
|---|---|---|
| TODO | TODO | TODO |

## Code skeleton

```python
# TODO: minimal Python code skeleton.
```

## When to use

- TODO

## When NOT to use

- TODO
"""


@patterns.command(name="init")
@click.argument("name")
@click.option("--scope", required=True,
              help="Scope: core | slides | docs | projects/<id>")
@click.option("--source", "source_override", default=None)
@click.option("--description", default="TODO: one-line description")
@click.option("--extrapolable/--no-extrapolable", default=True)
@click.option("--tags", default="")
@_handle_errors
def init_cmd(name: str, scope: str, source_override: str | None,
             description: str, extrapolable: bool, tags: str) -> None:
    """Scaffold a new pattern file in the source repo."""
    from datetime import date

    resolved = _resolve(source_override)
    target_file = resolved.path / scope / f"{name}.md"
    if target_file.exists():
        raise click.ClickException(f"pattern already exists: {target_file}")

    body = _PATTERN_TEMPLATE.format(
        name=name,
        description=description,
        tags=", ".join(t.strip() for t in tags.split(",") if t.strip()),
        extrapolable="true" if extrapolable else "false",
        since=date.today().isoformat(),
        title=name.replace("_", " ").title(),
    )
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(body, encoding="utf-8")
    get_console().print(f"[green]Created {target_file}[/green]")
