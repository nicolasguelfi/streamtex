"""Interactive pattern picker for ``stx patterns install`` (TUI).

Three responsibilities:

1. :func:`collect_pattern_catalog` walks a patterns source repo and
   returns one :class:`CatalogEntry` per pattern (name + scope + parsed
   frontmatter). Pure I/O, no UI.

2. :func:`select_patterns_interactively` — the legacy *flat* picker:
   single multi-select of patterns grouped by scope. Returns a list of
   pattern names. Kept for callers that want a plain individual-only
   pick.

3. :func:`select_patterns_compositely` — the *menu-driven* picker. Builds
   a composite v3 :class:`PatternSelection` (presets + individuals +
   excludes + all) through a persistent menu loop. The user can add
   presets in any number, add individual patterns on top, remove items
   from the resolved set (which become excludes), toggle the "all"
   mode, inspect a summary, and confirm or cancel.

Both picker functions raise :class:`InteractiveAborted` on Esc/Ctrl-C or
empty confirmation.
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass
from pathlib import Path

from .installer import _all_patterns, resolve_selection
from .manifest import (
    ManifestError,
    PatternSelection,
    parse_frontmatter,
    split_frontmatter,
)
from .preset import Preset, list_presets, resolve_preset

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CatalogEntry:
    """One row of the patterns catalog."""

    name: str
    scope: str
    description: str
    tags: tuple[str, ...]
    path: Path
    extrapolable: bool
    since: str


def _scope_of(path: Path, source: Path) -> str:
    """Return e.g. 'core', 'slides', or 'projects/ai4se6d' for a pattern path."""
    rel = path.resolve().relative_to(source.resolve())
    parts = rel.parts
    if len(parts) >= 2 and parts[0] == "projects":
        return f"projects/{parts[1]}"
    return parts[0] if parts else "?"


def collect_pattern_catalog(source: Path) -> list[CatalogEntry]:
    """Walk *source*, parse each pattern's frontmatter, return sorted entries.

    Patterns whose frontmatter fails to parse are skipped with a warning
    (the picker should never crash because one file is malformed).
    """
    source = Path(source).resolve()
    entries: list[CatalogEntry] = []
    for path in _all_patterns(source):
        try:
            text = path.read_text(encoding="utf-8")
            yaml, _ = split_frontmatter(text)
            fm = parse_frontmatter(yaml)
        except (OSError, ManifestError) as exc:
            logger.warning("skipping %s: %s", path, exc)
            continue
        entries.append(
            CatalogEntry(
                name=path.stem,
                scope=_scope_of(path, source),
                description=fm.description,
                tags=fm.tags,
                path=path,
                extrapolable=fm.extrapolable,
                since=fm.since,
            )
        )
    entries.sort(key=lambda e: (e.scope, e.name))
    return entries


def filter_by_tag(
    catalog: list[CatalogEntry], tag: str | None,
) -> list[CatalogEntry]:
    """Return entries whose tags contain *tag* (case-insensitive). Pass-through if None."""
    if not tag:
        return list(catalog)
    needle = tag.lower()
    return [e for e in catalog if any(t.lower() == needle for t in e.tags)]


# ---------------------------------------------------------------------------
# Interactive picker
# ---------------------------------------------------------------------------

class InteractiveAborted(Exception):
    """Raised when the user cancels the picker (Ctrl-C / Esc / empty result)."""


def select_patterns_interactively(
    catalog: list[CatalogEntry],
    *,
    preselected: set[str] | frozenset[str] = frozenset(),
    tag_filter: str | None = None,
) -> list[str]:
    """Show a multi-select TUI grouped by scope; return the chosen names.

    Args:
        catalog: All patterns available in the source (use
            :func:`collect_pattern_catalog`).
        preselected: Names that should start checked (typically: what's
            already installed in the project).
        tag_filter: Only show patterns whose tags include this value.

    Raises:
        InteractiveAborted: if the user cancels or makes an empty selection.
    """
    # Lazy import — questionary lives in the optional `[cli]` extra. Doing
    # the import at call time keeps the package importable in environments
    # that don't need the picker.
    try:
        import questionary
        from questionary import Choice, Separator
    except ImportError as exc:
        raise RuntimeError(
            "questionary is required for the interactive picker. "
            "Install it with: uv add 'streamtex[cli]'  (or pip install ...)"
        ) from exc

    visible = filter_by_tag(catalog, tag_filter)
    if not visible:
        hint = f" matching tag {tag_filter!r}" if tag_filter else ""
        raise InteractiveAborted(f"no patterns available{hint}.")

    # Build choices grouped by scope. Separators between scopes anchor the
    # eye; entries within a scope keep alphabetic order set by collect_pattern_catalog.
    choices: list = []
    current_scope: str | None = None
    for e in visible:
        if e.scope != current_scope:
            choices.append(Separator(f"── {e.scope} ──"))
            current_scope = e.scope
        title = _format_choice_title(e)
        choices.append(
            Choice(title=title, value=e.name, checked=e.name in preselected),
        )

    message = (
        "Select patterns to install "
        "(↑/↓ navigate, space toggles, enter confirms, ctrl-c cancels)"
    )
    if tag_filter:
        message += f"  [tag filter: {tag_filter}]"

    answer = questionary.checkbox(message, choices=choices).ask()
    if answer is None:
        raise InteractiveAborted("cancelled by user.")
    if not answer:
        raise InteractiveAborted("empty selection.")
    return list(answer)


def _format_choice_title(entry: CatalogEntry) -> str:
    """Render one catalog entry as a single picker row."""
    # Keep it dense — questionary truncates very long titles on narrow terminals.
    tag_str = f"  [{', '.join(entry.tags)}]" if entry.tags else ""
    desc = entry.description
    # Cap description so the row stays readable on ~120 cols.
    if len(desc) > 80:
        desc = desc[:77] + "…"
    return f"{entry.name:<30} {desc}{tag_str}"


# ---------------------------------------------------------------------------
# Composite picker (menu-driven state machine, UX 2E)
# ---------------------------------------------------------------------------

# Menu action identifiers — strings, not Enum, because questionary returns
# the `value=` of the chosen Choice verbatim.
_ACTION_ADD_PRESET = "add_preset"
_ACTION_ADD_INDIVIDUAL = "add_individual"
_ACTION_REMOVE = "remove"
_ACTION_TOGGLE_ALL = "toggle_all"
_ACTION_SUMMARY = "summary"
_ACTION_DONE = "done"
_ACTION_CANCEL = "cancel"


def _try_resolve(selection: PatternSelection, source: Path) -> tuple[str, ...]:
    """Resolve a selection but degrade to ``()`` on error.

    During the menu loop the user might temporarily have a half-built
    selection that references a not-yet-installed pattern. We don't want
    a stray PatternError to abort the picker — we show 0 patterns and let
    them keep editing.
    """
    try:
        return resolve_selection(selection, source)
    except Exception as exc:
        logger.debug("intermediate resolve failed: %s", exc)
        return ()


def _state_header(selection: PatternSelection, resolved: tuple[str, ...]) -> str:
    """One-line summary printed above the action menu each iteration."""
    parts: list[str] = []
    if selection.all_flag:
        parts.append("ALL")
    if selection.presets:
        parts.append(f"presets: {', '.join(selection.presets)}")
    if selection.individuals:
        parts.append(f"individuals: {len(selection.individuals)}")
    if selection.excludes:
        parts.append(f"excludes: {len(selection.excludes)}")
    if not parts:
        parts.append("(empty)")
    return f"Current selection — {' | '.join(parts)}  →  {len(resolved)} pattern(s) resolved"


def select_patterns_compositely(
    catalog: list[CatalogEntry],
    source: Path,
    *,
    initial: PatternSelection | None = None,
) -> PatternSelection:
    """Menu-driven picker — build a composite v3 selection step by step.

    Args:
        catalog: All patterns available in the source (see
            :func:`collect_pattern_catalog`). Used by Add-individual /
            Remove actions to populate sub-prompts.
        source: Path to the patterns source repo (passed to
            :func:`resolve_selection` and :func:`resolve_preset`).
        initial: Starting selection (typically the project's current
            persisted intent, or empty). Mutations build on top.

    Returns:
        The final :class:`PatternSelection` once the user chooses Done.

    Raises:
        InteractiveAborted: on cancel or empty-confirmed Done.
        RuntimeError: if ``questionary`` is not installed.
    """
    try:
        import questionary
    except ImportError as exc:
        raise RuntimeError(
            "questionary is required for the interactive picker. "
            "Install it with: uv add 'streamtex[cli]'"
        ) from exc

    presets = list_presets(source)
    working: PatternSelection = initial or PatternSelection()

    while True:
        resolved = _try_resolve(working, source)
        header = _state_header(working, resolved)
        questionary.print(header, style="bold")

        action = questionary.select(
            "What next?",
            choices=[
                questionary.Choice(
                    title="Add preset(s)",
                    value=_ACTION_ADD_PRESET,
                ),
                questionary.Choice(
                    title="Add individual pattern(s)",
                    value=_ACTION_ADD_INDIVIDUAL,
                ),
                questionary.Choice(
                    title="Remove pattern(s) from current selection",
                    value=_ACTION_REMOVE,
                    disabled="(nothing to remove)" if not resolved else None,
                ),
                questionary.Choice(
                    title=(
                        "Disable 'all patterns' mode" if working.all_flag
                        else "Use 'all patterns' (every pattern in the source)"
                    ),
                    value=_ACTION_TOGGLE_ALL,
                ),
                questionary.Choice(
                    title="Show summary",
                    value=_ACTION_SUMMARY,
                ),
                questionary.Separator("──────"),
                questionary.Choice(
                    title="Done — install this selection",
                    value=_ACTION_DONE,
                ),
                questionary.Choice(
                    title="Cancel",
                    value=_ACTION_CANCEL,
                ),
            ],
        ).ask()

        if action is None or action == _ACTION_CANCEL:
            raise InteractiveAborted("cancelled by user.")
        if action == _ACTION_DONE:
            if working.is_empty():
                confirm = questionary.confirm(
                    "Selection is empty — really cancel?", default=False,
                ).ask()
                if confirm:
                    raise InteractiveAborted("empty selection.")
                continue
            return working

        if action == _ACTION_ADD_PRESET:
            working = _action_add_presets(working, presets, source)
        elif action == _ACTION_ADD_INDIVIDUAL:
            working = _action_add_individuals(working, catalog, resolved)
        elif action == _ACTION_REMOVE:
            working = _action_remove(working, resolved)
        elif action == _ACTION_TOGGLE_ALL:
            working = _action_toggle_all(working)
        elif action == _ACTION_SUMMARY:
            _action_show_summary(working, source, presets, catalog)


# ---------------------------------------------------------------------------
# Individual menu actions (each returns a new PatternSelection)
# ---------------------------------------------------------------------------

def _action_add_presets(
    working: PatternSelection,
    presets: list[Preset],
    source: Path,
) -> PatternSelection:
    """Multi-select among presets not yet in ``working.presets``."""
    import questionary

    available = [p for p in presets if p.name not in working.presets]
    if not available:
        questionary.print("All presets are already selected.", style="fg:ansiyellow")
        return working

    choices = []
    for p in available:
        # Try to count how many patterns the preset resolves to.
        try:
            rp = resolve_preset(source, p.name)
            count = len(rp.pattern_files)
        except Exception:
            count = -1
        suffix = f"  ({count} patterns)" if count >= 0 else ""
        title = f"{p.name:<12} {p.description}{suffix}"
        choices.append(questionary.Choice(title=title, value=p.name))

    chosen = questionary.checkbox(
        "Add presets (space to toggle, enter to confirm):",
        choices=choices,
    ).ask()
    if not chosen:
        return working

    new_presets = tuple(list(working.presets) + list(chosen))
    return dataclasses.replace(
        working,
        presets=new_presets,
        # Adding a preset implies you don't want literal-all mode anymore.
        all_flag=False,
    )


def _action_add_individuals(
    working: PatternSelection,
    catalog: list[CatalogEntry],
    currently_resolved: tuple[str, ...],
) -> PatternSelection:
    """Multi-select among patterns not currently in the resolved set."""
    import questionary

    covered = set(currently_resolved)
    # Also exclude patterns already in the individuals list (idempotence).
    covered |= set(working.individuals)

    candidates = [e for e in catalog if e.name not in covered]
    if not candidates:
        questionary.print(
            "Every pattern is already in the current selection.",
            style="fg:ansiyellow",
        )
        return working

    choices = []
    current_scope: str | None = None
    for e in candidates:
        if e.scope != current_scope:
            choices.append(questionary.Separator(f"── {e.scope} ──"))
            current_scope = e.scope
        choices.append(
            questionary.Choice(title=_format_choice_title(e), value=e.name),
        )

    chosen = questionary.checkbox(
        "Add individual patterns (space toggles, enter confirms):",
        choices=choices,
    ).ask()
    if not chosen:
        return working

    # If a chosen pattern was in excludes, remove it from excludes (cancels
    # out the negative).
    new_excludes = tuple(x for x in working.excludes if x not in set(chosen))
    new_individuals = tuple(list(working.individuals) + list(chosen))
    return dataclasses.replace(
        working,
        individuals=new_individuals,
        excludes=new_excludes,
        all_flag=False,
    )


def _action_remove(
    working: PatternSelection,
    currently_resolved: tuple[str, ...],
) -> PatternSelection:
    """Multi-select among currently-resolved patterns; checked = REMOVE.

    The user's intent is "drop these from the install". For each checked
    name, we either remove it from ``individuals`` (if it was added that
    way) or add it to ``excludes`` (if it came from a preset / from --all).
    """
    import questionary

    if not currently_resolved:
        return working

    choices = [
        questionary.Choice(title=name, value=name)
        for name in currently_resolved
    ]
    chosen = questionary.checkbox(
        "Pick patterns to REMOVE from the current selection:",
        choices=choices,
    ).ask()
    if not chosen:
        return working

    to_drop = set(chosen)
    new_individuals = tuple(x for x in working.individuals if x not in to_drop)
    dropped_via_individuals = set(working.individuals) & to_drop
    excludes_to_add = to_drop - dropped_via_individuals
    new_excludes = tuple(sorted(set(working.excludes) | excludes_to_add))
    return dataclasses.replace(
        working,
        individuals=new_individuals,
        excludes=new_excludes,
    )


def _action_toggle_all(working: PatternSelection) -> PatternSelection:
    """Flip the ``all_flag``; warn if it would lose presets/individuals."""
    import questionary

    if working.all_flag:
        return dataclasses.replace(working, all_flag=False)

    if working.presets or working.individuals:
        confirm = questionary.confirm(
            "Switching to 'all' mode will discard your current presets and "
            "individuals (excludes are kept). Continue?",
            default=False,
        ).ask()
        if not confirm:
            return working

    return dataclasses.replace(
        working,
        all_flag=True,
        presets=(),
        individuals=(),
    )


def _action_show_summary(
    working: PatternSelection,
    source: Path,
    presets: list[Preset],
    catalog: list[CatalogEntry],
) -> None:
    """Print a provenance table of the currently-resolved selection."""
    import questionary

    resolved = _try_resolve(working, source)
    if not resolved:
        questionary.print("Selection resolves to no patterns.", style="fg:ansiyellow")
        return

    # Build a provenance map: name -> "from preset X" / "individual" / "all"
    catalog_by_name = {e.name: e for e in catalog}
    provenance: dict[str, str] = {}
    if working.all_flag:
        for name in resolved:
            provenance[name] = "all"
    for preset in presets:
        if preset.name not in working.presets:
            continue
        try:
            rp = resolve_preset(source, preset.name)
        except Exception:
            continue
        for p in rp.pattern_files:
            if p.stem in resolved and p.stem not in provenance:
                provenance[p.stem] = f"preset:{preset.name}"
    for name in working.individuals:
        if name in resolved and name not in provenance:
            provenance[name] = "individual"
    for name in resolved:
        provenance.setdefault(name, "?")

    questionary.print("", style="")
    questionary.print(
        f"  Resolved selection — {len(resolved)} pattern(s)", style="bold",
    )
    for name in resolved:
        scope = catalog_by_name[name].scope if name in catalog_by_name else "?"
        questionary.print(
            f"    {name:<32}  [{scope}]  ← {provenance[name]}",
        )
    if working.excludes:
        questionary.print("", style="")
        questionary.print(
            f"  Excludes ({len(working.excludes)}):", style="fg:ansired",
        )
        for name in working.excludes:
            questionary.print(f"    {name}")
    questionary.print("", style="")
