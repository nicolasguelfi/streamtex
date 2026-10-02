"""stx validate — aggregate validation across all reuse-architecture artifacts.

Exit codes (PLAN §7.5):
* 0 — no issues
* 1 — warnings only (becomes 2 with --strict)
* 2 — errors found
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import click

from ._shared import _find_project_dir
from .console import get_console


def _print_issues(console, label: str, issues) -> tuple[int, int]:
    """Print issues grouped by severity; return (error_count, warning_count)."""
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    if errors:
        console.print(f"  [red]{label}: FAIL[/red]")
        for issue in errors:
            console.print(f"    [red][{issue.code}][/red] {issue.message}")
    elif warnings:
        console.print(f"  [yellow]{label}: WARN[/yellow]")
    else:
        console.print(f"  [green]{label}: OK[/green]")
    for issue in warnings:
        console.print(f"    [yellow][{issue.code}][/yellow] {issue.message}")
    return len(errors), len(warnings)


def _declares_claude_mode(stx_toml: Path) -> bool:
    """True when stx.toml has a [claude] table with a ``mode`` key (valid or not)."""
    import tomllib

    try:
        with open(stx_toml, "rb") as f:
            return "mode" in tomllib.load(f).get("claude", {})
    except (OSError, tomllib.TOMLDecodeError):
        return False


@click.command("validate")
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Promote warnings to errors (exit 2 instead of 1 when only warnings).",
)
@click.option(
    "--build", "build", is_flag=True, default=False,
    help="Also run the real build() of every block of every book.py (headless, no browser): "
         "exceptions, media that resolve to nothing, large inlined media, empty styled blocks.",
)
@click.option(
    "--book", "books", multiple=True, type=click.Path(exists=True, dir_okay=False),
    help="With --build: check only this book.py (repeatable). Default: every book.py found.",
)
@click.option("--timeout", default=180, show_default=True, help="With --build: seconds per book.")
def validate(strict: bool, build: bool, books: tuple[str, ...], timeout: int) -> None:
    """Run pack + component + design system + kit validation on the current project.

    Also runs the project rules declared in stx.toml ([[validate.rules]]) and,
    with --build, the real build() of every block.
    """
    from streamtex.core import discovery, validation

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)

    total_errors = 0
    total_warnings = 0

    # 1) Packs
    console.print("[bold]Packs[/bold]")
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            console.print(f"  [yellow]{pack_obj.name}: not installed[/yellow]")
            continue
        mod = importlib.import_module(pack_obj.entry_point_module)
        pack_root = Path(mod.__file__).resolve().parent  # type: ignore[arg-type]
        issues = validation.validate_pack(pack_root)
        e, w = _print_issues(console, pack_obj.name, issues)
        total_errors += e
        total_warnings += w

    # 2) Components
    console.print("[bold]Components[/bold]")
    artifacts = discovery.discover_components(packs)
    for art in artifacts:
        if art.module is None:
            continue
        issues = validation.validate_component(art.module)
        e, w = _print_issues(console, f"{art.pack_name}:{art.name}", issues)
        total_errors += e
        total_warnings += w

    # 3) Design systems
    console.print("[bold]Design systems[/bold]")
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            continue
        try:
            mod = importlib.import_module(pack_obj.entry_point_module)
        except Exception:  # noqa: BLE001
            continue
        ds_dir = Path(mod.__file__).resolve().parent / "design_systems"  # type: ignore[arg-type]
        if not ds_dir.is_dir():
            continue
        for sub in sorted(ds_dir.iterdir()):
            if not (sub.is_dir() and (sub / "__init__.py").is_file()):
                continue
            ds_mod_name = f"{pack_obj.entry_point_module}.design_systems.{sub.name}"
            try:
                ds_mod = importlib.import_module(ds_mod_name)
            except Exception as exc:  # noqa: BLE001
                total_errors += 1
                console.print(f"  [red]{pack_obj.name}:{sub.name}: import error: {exc}[/red]")
                continue
            issues = validation.validate_design_system(ds_mod)
            e, w = _print_issues(console, f"{pack_obj.name}:{sub.name}", issues)
            total_errors += e
            total_warnings += w

    # 4) Kits
    console.print("[bold]Kits[/bold]")
    for pack_obj in packs:
        if pack_obj.entry_point_module is None:
            continue
        try:
            mod = importlib.import_module(pack_obj.entry_point_module)
        except Exception:  # noqa: BLE001
            continue
        kits_dir = Path(mod.__file__).resolve().parent / "kits"  # type: ignore[arg-type]
        if not kits_dir.is_dir():
            continue
        for kit_path in sorted(kits_dir.glob("*.toml")):
            issues = validation.validate_kit(kit_path)
            e, w = _print_issues(console, f"{pack_obj.name}:{kit_path.stem}", issues)
            total_errors += e
            total_warnings += w

    # 5) Claude declaration (project mode, #71) — printed only when declared
    from .claude_project import is_project_mode, validate_declaration

    if stx_toml.is_file() and (is_project_mode(str(project_dir)) or _declares_claude_mode(stx_toml)):
        console.print("[bold]Claude[/bold]")
        try:
            from .claude_cmd import find_claude_repo
            from .workspace_cmd import load_stx_toml

            claude_repo = find_claude_repo(str(project_dir), load_stx_toml(str(project_dir)))
        except click.ClickException:
            claude_repo = None
        problems = validate_declaration(str(project_dir), claude_repo)
        if problems:
            console.print("  [red]\\[claude]: FAIL[/red]")
            for msg in problems:
                console.print(f"    [red]\\[claude][/red] {msg}")
            total_errors += len(problems)
        elif claude_repo is None:
            console.print("  [yellow]\\[claude]: WARN[/yellow] streamtex-claude not found — profile not checked")
            total_warnings += 1
        else:
            console.print("  [green]\\[claude]: OK[/green]")

    # 6) Project rules declared in stx.toml (L12)
    from .project_rules import check_rules, load_rules

    rules = load_rules(project_dir)
    if rules:
        console.print(f"[bold]Project rules[/bold] ({len(rules)})")
        violations = check_rules(project_dir, rules)
        by_rule: dict[str, list] = {}
        for v in violations:
            by_rule.setdefault(v.rule, []).append(v)
        for rule in rules:
            rid = str(rule.get("id") or "")
            vs = [v for k, lst in by_rule.items() for v in lst if k == rid] if rid else []
            if not vs:
                console.print(f"  [green]{rid or 'rule'}: OK[/green]")
                continue
            color = "red" if vs[0].severity == "error" else "yellow"
            console.print(f"  [{color}]{rid}: {len(vs)} violation(s)[/{color}] — {vs[0].message}")
            for v in vs[:10]:
                console.print(f"    {v.where}")
            if len(vs) > 10:
                console.print(f"    ... and {len(vs) - 10} more")
        for v in violations:
            if v.severity == "error":
                total_errors += 1
            else:
                total_warnings += 1

    # 6b) Local copies of public st_* functions — information only (L15)
    from .project_rules import local_copies_of_public_api

    copies = local_copies_of_public_api(project_dir)
    if copies:
        console.print("[bold]Library functions defined locally[/bold] (information)")
        for path, line, name in copies[:20]:
            console.print(f"  [dim]i[/dim] {path}:{line} defines {name}, which streamtex provides — "
                          "keep it if it is a deliberate specialisation")
        if len(copies) > 20:
            console.print(f"  ... and {len(copies) - 20} more")

    # 7) Real build of every block (L11, L16)
    if build:
        from .build_check import discover_books, empty_styled_blocks, run_book

        targets = [Path(b).resolve() for b in books] or discover_books(project_dir)
        console.print(f"[bold]Build[/bold] ({len(targets)} book(s), real build() of every block)")
        for book in targets:
            r = run_book(book, timeout=timeout)
            rel = os.path.relpath(r.book, project_dir)
            if r.book_error:
                console.print(f"  [red]{rel}: FAIL[/red] — {r.book_error}")
                total_errors += 1
                continue
            label = f"{rel}: {r.blocks} block(s)"
            if not (r.errors or r.missing_media or r.inlined_media):
                console.print(f"  [green]{label} OK[/green]")
                continue
            color = "red" if r.errors else "yellow"
            console.print(f"  [{color}]{label}[/{color}]")
            for block, etype, msg, *_trace in r.errors:
                console.print(f"    [red]error[/red] {block}: {etype}: {msg}")
            for block, uri in r.missing_media:
                console.print(f"    [yellow]empty frame[/yellow] {block}: media not found: {uri}")
            for block, uri, size in r.inlined_media:
                console.print(f"    [yellow]inlined {size // 1024} KB[/yellow] {block}: {uri} — serve it "
                              "(configure_image_path + set_static_sources)")
            total_errors += len(r.errors)
            total_warnings += len(r.missing_media) + len(r.inlined_media)
        empties = empty_styled_blocks(project_dir)
        if empties:
            console.print("  [yellow]empty styled st_block (renders nothing in the app):[/yellow]")
            for path, line in empties[:20]:
                console.print(f"    {path}:{line}")
            total_warnings += len(empties)

    # Summary + exit code (PLAN §7.5: 0 = OK, 1 = warnings, 2 = errors)
    if total_errors:
        console.print(
            f"[red]`stx validate` found {total_errors} error(s) "
            f"and {total_warnings} warning(s).[/red]"
        )
        sys.exit(2)
    if total_warnings:
        if strict:
            console.print(
                f"[red]`stx validate --strict` failed: "
                f"{total_warnings} warning(s) promoted to errors.[/red]"
            )
            sys.exit(2)
        console.print(
            f"[yellow]`stx validate` completed with {total_warnings} warning(s).[/yellow]"
        )
        sys.exit(1)
    console.print("[green]All artifacts validate cleanly.[/green]")
