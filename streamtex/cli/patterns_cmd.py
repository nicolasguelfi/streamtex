"""Click commands: ``stx patterns ...``.

Thin adapter on top of :mod:`streamtex.patterns`. Translates ``PatternError``
subclasses into ``click.ClickException`` and formats output via Rich.
"""

from __future__ import annotations

import json
import logging
import os
from functools import wraps
from pathlib import Path

import click

from streamtex.patterns import (
    DriftError,
    MetaError,
    PatternError,
    SourceNotFoundError,
    ValidationError,
)
from streamtex.patterns.installer import (
    DEFAULT_PATTERNS_REPO_URL,
    DEFAULT_TARGET_REL,
    build_install_plan,
    clone_patterns_source,
    execute_install,
    remove_pattern,
    resolve_selection,
)
from streamtex.patterns.installer import (
    _all_patterns as _all_patterns,  # noqa: F401 — re-export used by tests/picker
)
from streamtex.patterns.manifest import PatternSelection, load_meta, sha256_file
from streamtex.patterns.picker import (
    InteractiveAborted,
    collect_pattern_catalog,
    select_patterns_compositely,
    select_patterns_interactively,
)
from streamtex.patterns.preset import (
    list_presets as _list_presets,
)
from streamtex.patterns.preset import (
    resolve_preset,
)
from streamtex.patterns.project_toml import (
    read_project_selection,
    write_project_selection,
    write_project_source,
)
from streamtex.patterns.resolver import (
    TraceStatus,
    resolve_source,
    trace_source,
)
from streamtex.patterns.updater import apply_update, compute_drift
from streamtex.patterns.validator import validate_all, validate_file

from .console import get_console
from .workspace_cmd import find_workspace_root, load_stx_toml

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_interactive() -> bool:
    """True iff we can open a TUI. Extracted so tests can monkeypatch it.

    CliRunner replaces sys.stdin with a non-tty stream, so we route the
    check through this helper rather than calling ``sys.stdin.isatty()``
    inline.
    """
    import sys

    return sys.stdin.isatty()


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


def _read_initial_selection(
    target_path: Path, project_dir: Path,
) -> PatternSelection | None:
    """Return the currently-persisted selection (TOML wins over meta).

    Used to pre-fill the composite picker so users see "what's currently
    declared for this project" and can iterate from there rather than
    starting empty.
    """
    sel = read_project_selection(project_dir)
    if sel is not None:
        return sel
    try:
        meta = load_meta(target_path)
        return meta.selection
    except MetaError:
        return None


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
@click.option("--preset", "preset_names", multiple=True,
              help="Install a preset (may be repeated for multiple presets).")
@click.option("--pattern", "pattern_csv", default=None,
              help="Install specific patterns (comma-separated).")
@click.option("--all", "install_all", is_flag=True,
              help="Install every pattern in the source.")
@click.option("--exclude", default=None,
              help="Exclude patterns (comma-separated). Subtracted from the "
                   "resolved set in every mode, including --all.")
@click.option("--mode", type=click.Choice(["copy", "symlink"]), default="copy")
@click.option("--source", "source_override", default=None)
@click.option("--target", default=None,
              help=f"Target directory (default: {DEFAULT_TARGET_REL}).")
@click.option("--force", is_flag=True, help="Overwrite locally modified patterns.")
@click.option("--dry-run", is_flag=True, help="Show plan without writing.")
@click.option("--tag", default=None,
              help="(Interactive mode) only show patterns whose tags include this value.")
@_handle_errors
def install_cmd(patterns_args: tuple[str, ...], preset_names: tuple[str, ...],
                pattern_csv: str | None, install_all: bool,
                exclude: str | None, mode: str, source_override: str | None,
                target: str | None, force: bool, dry_run: bool,
                tag: str | None) -> None:
    """Install patterns into the project.

    Composable declarative selectors (all may be combined except --all):
      * --preset NAME           — repeat for multiple presets
      * --pattern A,B,C         — explicit list (also accepts positional NAMES)
      * --exclude X,Y           — subtract from the resolved set
      * --all                   — every pattern in the source (excludes still apply)

    Interactive fallback (no selector given, TTY only):
      * default                 — menu-driven composite picker
      * --tag VALUE             — flat picker narrowed by tag

    Non-TTY contexts (CI, scripts) refuse the interactive fallback.
    """
    console = get_console()
    resolved = _resolve(source_override)
    target_path = _resolve_target(target)

    individual = tuple(patterns_args) + _split_csv(pattern_csv)
    exclude_list = _split_csv(exclude)

    # --all is exclusive with --preset and --pattern (but not with --exclude).
    if install_all and (preset_names or individual):
        raise click.ClickException(
            "--all is exclusive with --preset / --pattern (use --exclude to "
            "subtract specific patterns from --all).",
        )

    # --- Interactive mode trigger ----------------------------------------
    nothing_chosen = not preset_names and not individual and not install_all
    composite_selection: PatternSelection | None = None
    if nothing_chosen:
        if not _is_interactive():
            raise click.ClickException(
                "no selector given and stdin is not a terminal. "
                "Pass --preset, --pattern, or --all (or run interactively).",
            )

        catalog = collect_pattern_catalog(resolved.path)
        if not catalog:
            raise click.ClickException(
                f"no patterns found in source {resolved.path}",
            )

        # The --tag flag is a narrowing convenience that only the flat
        # picker honours; pick the picker accordingly.
        if tag:
            preselected: set[str] = set()
            try:
                existing_meta = load_meta(target_path)
                preselected = {r.name for r in existing_meta.patterns}
            except MetaError:
                pass
            try:
                picked = select_patterns_interactively(
                    catalog, preselected=preselected, tag_filter=tag,
                )
            except InteractiveAborted as exc:
                raise click.ClickException(
                    f"interactive install aborted: {exc}",
                ) from exc
            individual = tuple(picked)
            console.print(
                f"  [dim]picked {len(individual)} pattern(s) "
                f"interactively (tag={tag!r})[/dim]"
            )
        else:
            # Default interactive mode: composite menu-driven picker.
            initial = _read_initial_selection(target_path, _resolve_project_dir())
            try:
                composite_selection = select_patterns_compositely(
                    catalog, resolved.path, initial=initial,
                )
            except InteractiveAborted as exc:
                raise click.ClickException(
                    f"interactive install aborted: {exc}",
                ) from exc
            # Resolve composite → individual list for build_install_plan;
            # the canonical v3 selection is persisted via selection_override.
            individual = resolve_selection(composite_selection, resolved.path)
            console.print(
                f"  [dim]picked {composite_selection.effective_mode} "
                f"selection → {len(individual)} pattern(s)[/dim]"
            )
    else:
        # Declarative path: build the composite from flags so multiple
        # --preset, individual lists, and --exclude can all be combined
        # in one install. The single-preset shortcut (one --preset only,
        # no individuals, no excludes) still goes through the legacy
        # build_install_plan branch below for backwards compatibility
        # of the per-flag selection it records in meta.
        cli_uses_composite = (
            len(preset_names) > 1
            or (preset_names and individual)
            or (preset_names and exclude_list)
            or (install_all and exclude_list)
        )
        if cli_uses_composite:
            if install_all:
                composite_selection = PatternSelection(
                    all_flag=True, excludes=exclude_list,
                )
            else:
                composite_selection = PatternSelection(
                    presets=preset_names,
                    individuals=individual,
                    excludes=exclude_list,
                )
            individual = resolve_selection(composite_selection, resolved.path)

    # Single-flag preset shortcut still uses the legacy plan branch so
    # downstream tests/back-compat behaviour is unchanged.
    legacy_preset = preset_names[0] if (
        len(preset_names) == 1 and composite_selection is None
    ) else None

    plan = build_install_plan(
        target=target_path,
        source=resolved.path,
        preset=legacy_preset,
        individual_patterns=individual,
        install_all=install_all and composite_selection is None,
        exclude=exclude_list if composite_selection is None else (),
        mode=mode,
        force=force,
        selection_override=composite_selection,
    )

    if dry_run:
        console.print(
            f"[bold]Dry-run install[/bold] -> {target_path}\n"
            f"  source: {resolved.path}\n"
            f"  preset(s): {', '.join(preset_names) or '—'}  mode: {mode}  "
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

    # Persist user intent into the project's TOML so sync can restore the
    # selection on a fresh clone. Best-effort: skip silently when --target
    # points outside the current project, or when no project dir is around.
    if plan.selection is not None:
        project_dir = _resolve_project_dir()
        try:
            target_in_project = target_path.is_relative_to(project_dir)
        except (AttributeError, ValueError):
            target_in_project = str(target_path).startswith(str(project_dir))
        if target_in_project:
            try:
                toml_path = write_project_selection(
                    project_dir,
                    plan.selection,
                    source=resolved.raw_value,
                )
                console.print(f"  intent: {toml_path}")
            except Exception as exc:
                logger.warning("failed to persist selection to project TOML: %s", exc)


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
    """Idempotent: install missing + update existing patterns.

    Honours the user's recorded intent in precedence order:
      1. ``stx.toml [patterns.selection]`` (or shortcuts) — source of truth.
      2. ``.patterns-meta.json`` ``selection`` field (schema v2+).
      3. ``.patterns-meta.json`` ``preset`` field (v1, migrated in-memory).
      4. No intent → just refresh what's already on disk.
    """
    console = get_console()
    resolved = _resolve(source_override)
    target_path = _resolve_target(target)
    project_dir = _resolve_project_dir()

    # --- Determine effective intent ---------------------------------------
    selection = read_project_selection(project_dir)

    try:
        meta = load_meta(target_path)
    except MetaError:
        meta = None

    if selection is None and meta is not None:
        selection = meta.selection
    if selection is None and meta is not None and meta.preset:
        selection = PatternSelection.from_legacy(
            mode="preset", items=(meta.preset,),
        )

    # --- No intent → plain update ----------------------------------------
    if selection is None or selection.is_empty():
        if meta is None:
            console.print(
                "[yellow]Nothing to sync: no .patterns-meta.json and no "
                "[patterns] intent in stx.toml/pyproject.toml.[/yellow]"
            )
            return
        apply_update(target_path, resolved.path, force=force, dry_run=dry_run)
        console.print("[green]Sync complete (no recorded selection).[/green]")
        return

    # --- Resolve composite selection → target name set -------------------
    target_names = resolve_selection(selection, resolved.path)
    have = {r.name for r in meta.patterns} if meta else set()
    missing = [n for n in target_names if n not in have]

    if missing:
        plan = build_install_plan(
            target=target_path,
            source=resolved.path,
            individual_patterns=tuple(missing),
            mode=meta.mode if meta else "copy",
            force=force,
            record_selection=False,
        )
        if not dry_run:
            execute_install(
                plan,
                raw_source=meta.source if meta else resolved.raw_value,
            )
        console.print(
            f"  installed {len(missing)} missing pattern(s) from intent "
            f"({selection.mode})"
        )

    if meta is not None or missing:
        # apply_update needs meta on disk; missing install just wrote one.
        apply_update(target_path, resolved.path, force=force, dry_run=dry_run)

    console.print("[green]Sync complete.[/green]")


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


# ---------------------------------------------------------------------------
# source subgroup — inspect / clone / link / set the patterns source path
# ---------------------------------------------------------------------------

@patterns.group(name="source")
def source_group() -> None:
    """Inspect or configure where ``stx patterns`` resolves its source repo."""


_STATUS_COLOR = {
    TraceStatus.MATCHED: "green",
    TraceStatus.UNREACHED: "dim",
    TraceStatus.SKIPPED: "dim",
    TraceStatus.NOT_FOUND: "yellow",
    TraceStatus.INVALID: "red",
}


@source_group.command(name="show")
@click.option(
    "--source", "source_override", default=None,
    help="Probe resolution as if --source were passed (does not write).",
)
@_handle_errors
def source_show_cmd(source_override: str | None) -> None:
    """Print the R4 resolution chain — what was tried, what matched.

    Useful to debug "patterns: no usable source found" without running an
    actual install/list command.
    """
    console = get_console()
    project_dir = _resolve_project_dir()
    workspace = _resolve_workspace_root()
    entries, resolved = trace_source(
        project_dir,
        cli_override=source_override,
        workspace_root=workspace,
    )

    from rich.table import Table
    table = Table(
        title=f"Patterns source — R4 resolution from {project_dir}",
    )
    table.add_column("Level", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Candidate / Reason")
    for e in entries:
        color = _STATUS_COLOR.get(e.status, "")
        status = (
            f"[{color}]{e.status.value}[/{color}]" if color else e.status.value
        )
        candidate = e.candidate or "(none)"
        detail = f" — {e.detail}" if e.detail else ""
        table.add_row(
            f"L{e.level.value} {e.level.name.lower()}",
            status,
            f"{candidate}{detail}",
        )
    console.print(table)

    if resolved:
        console.print(
            f"\n[bold green]Resolved[/bold green] → {resolved.path}"
            f"  [dim](level: {resolved.level.name.lower()})[/dim]"
        )
        if resolved.raw_value:
            console.print(f"  raw value:   {resolved.raw_value}")
        if resolved.declared_at:
            console.print(f"  declared at: {resolved.declared_at}")
    else:
        console.print(
            "\n[bold red]No source resolved.[/bold red]\n"
            "  Next steps:\n"
            "    [cyan]stx patterns source clone[/cyan]"
            "          fetch the official repo into this workspace\n"
            "    [cyan]stx patterns source link PATH[/cyan]"
            "    point to an existing local clone\n"
            "    [cyan]stx patterns source set PATH[/cyan]"
            "     record a custom path in stx.toml"
        )


def _default_patterns_url(workspace_root: Path | None) -> str:
    """Return the URL to clone, preferring the workspace's declaration."""
    if workspace_root is None:
        return DEFAULT_PATTERNS_REPO_URL
    try:
        config = load_stx_toml(str(workspace_root))
    except click.ClickException:
        return DEFAULT_PATTERNS_REPO_URL
    repos = config.get("repos", {})
    entry = repos.get("streamtex-patterns")
    if isinstance(entry, dict) and entry.get("url"):
        return str(entry["url"])
    return DEFAULT_PATTERNS_REPO_URL


def _is_empty_dir(path: Path) -> bool:
    """True iff *path* is a directory with no entries (not even hidden)."""
    return path.is_dir() and not any(path.iterdir())


@source_group.command(name="clone")
@click.option("--url", default=None,
              help="Git URL to clone (default: workspace [repos.streamtex-patterns].url, "
                   "else the official repo).")
@click.option("--branch", default=None, help="Branch or tag to check out.")
@click.option("--target", default=None,
              help="Where to clone (default: <workspace>/streamtex-patterns).")
@click.option("--force", is_flag=True,
              help="Allow cloning over a non-empty existing directory (it is removed first).")
@_handle_errors
def source_clone_cmd(url: str | None, branch: str | None,
                     target: str | None, force: bool) -> None:
    """Clone the patterns source repo into the workspace (R4 level 4)."""
    console = get_console()
    workspace = _resolve_workspace_root()

    if target:
        target_path = Path(target).expanduser().resolve()
    elif workspace is not None:
        target_path = (workspace / "streamtex-patterns").resolve()
    else:
        raise click.ClickException(
            "no workspace detected and no --target specified — "
            "pass --target PATH or run inside a stx workspace."
        )

    effective_url = url or _default_patterns_url(workspace)
    console.print(f"[cyan]Cloning[/cyan] {effective_url} → {target_path}")

    clone_patterns_source(
        effective_url, target_path, branch=branch, force=force,
    )

    console.print("[green]Cloned successfully.[/green]")
    console.print(
        "  Run [cyan]stx patterns source show[/cyan] to confirm the new "
        "resolution, then [cyan]stx patterns install[/cyan]."
    )


@source_group.command(name="link")
@click.argument("path")
@click.option("--force", is_flag=True,
              help="Replace an existing <workspace>/streamtex-patterns symlink or directory.")
@_handle_errors
def source_link_cmd(path: str, force: bool) -> None:
    """Symlink ``<workspace>/streamtex-patterns`` to an existing local clone.

    Use this when you already have a streamtex-patterns checkout on disk
    that you want several workspaces to share, or when iterating on pattern
    files (edits show up live in every consuming project).
    """
    console = get_console()
    workspace = _resolve_workspace_root()
    if workspace is None:
        raise click.ClickException(
            "no workspace detected — run inside a stx workspace, or use "
            "`stx patterns source set PATH` to record a custom path instead."
        )

    src = Path(path).expanduser().resolve()
    if not src.is_dir():
        raise click.ClickException(f"target {src} is not a directory.")
    if not (src / "manifest.toml").is_file():
        raise click.ClickException(
            f"{src} is not a valid patterns source (no manifest.toml).",
        )

    dst = (workspace / "streamtex-patterns").resolve()
    if dst.exists() or dst.is_symlink():
        if not force:
            raise click.ClickException(
                f"{dst} already exists; pass --force to replace it."
            )
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            import shutil
            shutil.rmtree(dst)

    try:
        os.symlink(src, dst)
    except OSError as exc:
        raise click.ClickException(f"symlink failed: {exc}") from exc

    console.print(f"[green]Linked[/green] {dst} → {src}")
    console.print(
        "  Run [cyan]stx patterns source show[/cyan] to confirm the new "
        "resolution."
    )


@source_group.command(name="set")
@click.argument("path")
@click.option("--scope", type=click.Choice(["project", "workspace"]),
              default="project",
              help="Write [patterns].source in the current project (default) or workspace stx.toml.")
@click.option("--allow-missing", is_flag=True,
              help="Skip the manifest.toml validation (record the path even if invalid today).")
@_handle_errors
def source_set_cmd(path: str, scope: str, allow_missing: bool) -> None:
    """Record ``[patterns].source = PATH`` in stx.toml without cloning anything."""
    console = get_console()

    raw = path  # keep what the user typed (relative or absolute)
    abs_path = Path(path).expanduser().resolve()
    if not allow_missing:
        if not abs_path.is_dir():
            raise click.ClickException(
                f"{abs_path} is not a directory; pass --allow-missing to record it anyway."
            )
        if not (abs_path / "manifest.toml").is_file():
            raise click.ClickException(
                f"{abs_path} has no manifest.toml; pass --allow-missing to record it anyway."
            )

    if scope == "workspace":
        target_dir = _resolve_workspace_root()
        if target_dir is None:
            raise click.ClickException(
                "no workspace detected — cannot set --scope workspace."
            )
    else:
        target_dir = _resolve_project_dir()

    toml_path = write_project_source(target_dir, raw)
    console.print(
        f"[green]Wrote[/green] [patterns].source = {raw!r} → {toml_path}"
    )
    console.print(
        "  Run [cyan]stx patterns source show[/cyan] to confirm the new "
        "resolution."
    )
