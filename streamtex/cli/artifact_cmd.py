"""stx artifact — list / show / validate for the generic artifact engine.

A single uniform CLI for all manifest-0.2 artifact categories (palette,
ai_prompt, archetype, guideline, skill, agent, asset, integration). Per-kind
formatting lives in the per-category render helpers below.

See `streamtex.core.artifacts` for the engine API and the RFC at
`documentation/maintenance/design-packs/RFC-extended-artifacts.md`.
"""

from __future__ import annotations

import click

from streamtex.core.artifacts import (
    ArtifactKind,
    discover_artifacts,
    resolve_artifact,
    validate_artifact,
)

from .console import get_console

_KIND_CHOICES = [k.value for k in ArtifactKind]


def _parse_kind(value: str | None) -> ArtifactKind | None:
    if value is None:
        return None
    try:
        return ArtifactKind(value)
    except ValueError as exc:
        raise click.BadParameter(
            f"unknown artifact kind {value!r} ; supported: {', '.join(_KIND_CHOICES)}"
        ) from exc


def _kinds_to_scan(kind: ArtifactKind | None) -> list[ArtifactKind]:
    return [kind] if kind else list(ArtifactKind)


@click.group()
def artifact() -> None:
    """Manage extended pack artifacts (manifest 0.2 — palettes, prompts, …)."""


@artifact.command("list")
@click.option(
    "--kind",
    "kind_str",
    type=click.Choice(_KIND_CHOICES),
    default=None,
    help="Filter by artifact category. Default: all categories.",
)
@click.option("--pack", "pack_filter", default=None, help="Filter by pack name.")
def list_cmd(kind_str: str | None, pack_filter: str | None) -> None:
    """Enumerate artifacts across installed packs."""
    console = get_console()
    kind = _parse_kind(kind_str)
    total = 0
    for k in _kinds_to_scan(kind):
        found = discover_artifacts(k, pack=pack_filter)
        if not found:
            continue
        total += len(found)
        console.print(f"[bold]{k.value}[/bold] ({len(found)})")
        for art in found:
            console.print(f"  {art.pack}:{art.name}  [dim]({art.path})[/dim]")
    if total == 0:
        scope = f"kind={kind.value}" if kind else "any kind"
        pack_scope = f" pack={pack_filter}" if pack_filter else ""
        console.print(f"[dim]No artifacts found ({scope}{pack_scope}).[/dim]")


@artifact.command("show")
@click.argument("name")
@click.option(
    "--kind",
    "kind_str",
    type=click.Choice(_KIND_CHOICES),
    required=True,
    help="Artifact category.",
)
@click.option("--pack", "pack_filter", default=None, help="Disambiguate by pack name.")
def show_cmd(name: str, kind_str: str, pack_filter: str | None) -> None:
    """Show one artifact's content (formatted per kind)."""
    console = get_console()
    kind = ArtifactKind(kind_str)
    try:
        discovered = resolve_artifact(
            name, kind, prefer=[pack_filter] if pack_filter else None
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"[bold]{discovered.pack}:{discovered.name}[/bold]  ({kind.value})")
    console.print(f"[dim]{discovered.path}[/dim]")
    console.print()

    if kind == ArtifactKind.PALETTE:
        _render_palette(discovered, console)
    elif kind == ArtifactKind.AI_PROMPT:
        _render_ai_prompt(discovered, console)
    else:
        # Fallback: dump path + first lines for categories not yet rendered.
        try:
            if discovered.path.is_file():
                console.print(discovered.path.read_text()[:2000])
            else:
                for child in sorted(discovered.path.iterdir())[:20]:
                    console.print(f"  {child.name}")
        except Exception as exc:
            console.print(f"[red]Could not preview: {exc}[/red]")


@artifact.command("validate")
@click.argument("name", required=False)
@click.option(
    "--kind",
    "kind_str",
    type=click.Choice(_KIND_CHOICES),
    default=None,
    help="Filter by artifact category. Default: all categories.",
)
@click.option("--pack", "pack_filter", default=None, help="Filter by pack name.")
def validate_cmd(name: str | None, kind_str: str | None, pack_filter: str | None) -> None:
    """Validate one (NAME + --kind) or all matching artifacts.

    Exit code 0 if no errors ; 1 otherwise.
    """
    console = get_console()
    kind = _parse_kind(kind_str)
    targets = []
    for k in _kinds_to_scan(kind):
        for art in discover_artifacts(k, pack=pack_filter):
            if name is None or art.name == name:
                targets.append((k, art))

    if not targets:
        console.print("[yellow]No artifacts matched the filters.[/yellow]")
        return

    total_errors = 0
    for k, art in targets:
        issues = validate_artifact(art.path, k)
        errors = [i for i in issues if i.is_error()]
        warnings = [i for i in issues if i.severity == "warning"]
        status = "[green]OK[/green]" if not errors else f"[red]{len(errors)} error(s)[/red]"
        warn_tag = f" [yellow]({len(warnings)} warn)[/yellow]" if warnings else ""
        console.print(f"{art.pack}:{art.name}  ({k.value})  {status}{warn_tag}")
        for issue in errors + warnings:
            tag_color = "red" if issue.severity == "error" else "yellow"
            console.print(f"  [{tag_color}][{issue.code}][/{tag_color}] {issue.message}")
        total_errors += len(errors)

    if total_errors:
        raise click.ClickException(
            f"{total_errors} validation error(s) across {len(targets)} artifact(s)."
        )


# ---------------------------------------------------------------------------
# Per-kind renderers
# ---------------------------------------------------------------------------


def _render_palette(discovered, console) -> None:
    from streamtex.core.artifacts.palette import load_palette_from_path

    palette = load_palette_from_path(discovered.path, pack=discovered.pack)
    console.print(f"version: {palette.version}")
    console.print(f"colors ({len(palette.colors)}):")
    for token, color in palette.colors.items():
        role = f" — {color.role}" if color.role else ""
        console.print(f"  {token:<16}  {color.hex}{role}")
    if palette.dimensions:
        console.print(f"dimensions ({len(palette.dimensions)}):")
        for dim, target in palette.dimensions.items():
            console.print(f"  {dim:<16} → {target}")


def _render_ai_prompt(discovered, console) -> None:
    from streamtex.core.artifacts.ai_prompt import load_ai_prompt_from_path

    prompt = load_ai_prompt_from_path(discovered.path, pack=discovered.pack)
    console.print(f"orientations: {', '.join(sorted(prompt.suffixes)) or '(none)'}")
    console.print()
    console.print("[bold]prefix[/bold]:")
    console.print(prompt.prefix)
    console.print()
    for orient in sorted(prompt.suffixes):
        console.print(f"[bold]suffix-{orient}[/bold]:")
        console.print(prompt.suffixes[orient])
        console.print()
