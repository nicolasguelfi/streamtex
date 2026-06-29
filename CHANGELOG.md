# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.19] — 2026-06-29

### Fixed

- **`st_book` cache build crash on Streamlit ≥ 1.58** — `_isolate_widget_keys`
  called `.copy()` on `ScriptRunContext.widget_user_keys_this_run` /
  `widget_ids_this_run`, which Streamlit 1.58 changed from a plain `set` to a
  `ThreadSafeSet` (no `.copy()`), raising `AttributeError: 'ThreadSafeSet'
  object has no attribute 'copy'` on every paginated render. Snapshot/restore
  is now version-agnostic (`_snapshot_widget_keys` / `_restore_widget_keys`):
  it uses `.snapshot()` on a `ThreadSafeSet`, `set()` on a plain set, and
  restores in place (`.check_and_add` / `.update`) so the thread-safe
  container type is preserved. Verified end-to-end against Streamlit 1.58.

## [0.7.18] — 2026-06-29

### Fixed

- **`stx pack add --dev` for monorepo packs** — the command conflated a
  local pack's *manifest directory* (`_pack_manifest.toml`, in the inner
  package module) with its *distribution root* (`pyproject.toml` /
  `setup.py`, what `uv` installs). Pointing at the repo root failed
  manifest validation (`PV001`), while pointing at the package module
  recorded a uv source `uv sync` could not build. `add` now resolves both
  anchors independently (`_resolve_local_pack_layout`): it validates the
  manifest wherever it lives and always records the buildable distribution
  root as the editable source. Either input path (repo root or package
  module) now yields a working editable install. Regression tests added.

## [0.7.17] — 2026-05-26 — generic artifact engine (manifest 0.2)

### Added

- **`streamtex.core.artifacts` subpackage** — generic engine for extended
  pack artifacts under the additive `[pack.data]` section of manifest
  format **0.2**. Eight categories supported:
  - `palette` — JSON canonical, Python view at import (composable Style atoms)
  - `ai_prompt` — prefix + per-orientation suffixes for AI image generation
  - `archetype` — markdown + YAML frontmatter, reusable visual scene patterns
  - `guideline` — markdown + YAML frontmatter, opposable R-rules
  - `skill` / `agent` — pack-scoped Claude Code skill/agent (install hook
    to `.claude/custom/<subdir>/<pack_slug>__<name>.md`)
  - `asset` — `_manifest.toml` + binary files with license tracking
  - `integration` — open-contract recipe per third-party framework
- Per-category modules (`palette.py`, `ai_prompt.py`, …) each ship a
  TypedDict / dataclass view, a dedicated validator (`PAV*` / `APV*` /
  `ARV*` / `GLV*` / `SKV*` / `AGV*` / `ASV*` / `INV*` codes), and a
  typed loader.
- `streamtex/cli/artifact_cmd.py` — new CLI surface
  `stx artifact list|show|validate|install [--kind <k>] [--pack <p>]`.
- Lifecycle hook for skills/agents: `install_claude_artifact()` copies
  pack-shipped Claude artifacts into `<project>/.claude/custom/` with a
  namespaced filename. Confirmation prompt by default at the CLI;
  `--yes` to skip.
- `contracts.PackManifest` gains optional `PackDataSection` (TypedDict).
- Reference example: `streamtex-pack-gse v2.0.0` ships 17 artifacts
  across 6 of the 8 categories.

### Notes

- Format **0.2** is additive. Existing format-0.1 packs (pack-design
  v0.3.0, pack-manuals v0.2.0) work unchanged. A 0.2 pack with no
  `[pack.data]` section is identical to a 0.1 pack.
- Supersedes the now-removed `streamtex-shared/graphic-designs/gse/`
  legacy file-copy system.

## [0.7.16] — 2026-05-25 — optional `FontsBundle` Protocol + `stx --help` quick-start

### Added

- **`FontsBundle` Protocol** in `streamtex.core.contracts` — declares the
  shape a design system MAY expose for typography (`body_family`,
  `heading_family`, `code_family` as composable `Style` objects). Kept as
  an **optional** bundle (not in `REQUIRED_BUNDLES`) so existing third-party
  design systems remain conforming without modification. The three slots are
  intentionally kept distinct (body vs heading vs code) so downstream
  documents can diverge typography per role without touching the pack.
  Referenced by `streamtex-pack-design 0.3.0` which adds a `_Fonts` bundle
  on all three of its design systems.
- Optional-bundles docstring next to `REQUIRED_BUNDLES` updated to mention
  `fonts` in the optional set.

### Changed

- **`stx --help` shows a quick-start header** — the top-level CLI docstring
  now surfaces the streamtex.org link, the three commands a new user needs
  (`stx install .`, `stx project new <name>`, `stx run`), and a pointer to
  the `/stx-guide` slash command in Claude Code. Replaces the previous
  one-liner that gave no entry point for first-time users. Test:
  `test_cli_help_shows_quickstart`.

## [0.7.15] — 2026-05-25 — `stx sync` + deterministic `stx update --locked`

### Added

- **New top-level command `stx sync`** — project-level dependency sync.
  Wraps `uv sync --locked` (deterministic, idempotent) for any directory
  containing a `pyproject.toml`. Walks up from the cwd to find the
  project root; `stx sync <path>` targets a specific directory.
- **`stx sync --upgrade-deps`** removes `--locked` so `uv sync` may
  refresh `uv.lock` from `pyproject.toml`. Use when pyproject changes
  intentionally.
- **`stx update --upgrade-deps`** flag: opt back into the legacy
  behaviour (`uv lock --upgrade-package streamtex` + plain `uv sync`).
  Required when bumping streamtex after a new PyPI release.

### Changed

- **`stx update` now uses `uv sync --locked` by default.** Routine
  updates no longer rewrite `uv.lock` — they fail loudly when the lock
  diverges from `pyproject.toml`, with a hint pointing to
  `--upgrade-deps`. Eliminates silent lock flip-flop between editable
  and PyPI modes.
- The `--no-sources` fallback (used when a local editable source is
  missing) still rewrites the lock; `_restore_uv_lock_if_only_dirty`
  brings it back to the committed state after sync.

## [0.7.14] — 2026-05-24 — `stx claude update` redesign

### Changed

- **`stx claude update` now removes orphan files by default.** Files
  installed previously but no longer declared by any `streamtex-claude`
  manifest are removed automatically. Empty parent directories left
  behind are cleaned up too.
- **A confirmation prompt is shown** before any destructive action
  (orphan removal, modified-file overwrite). The recap lists every
  affected path so user-added files in `.claude/commands/` can be spotted
  and the operation cancelled if needed.
- **`--force` semantics unchanged**: still required to overwrite
  locally-modified files (with auto-backup to `.claude/.backup/`).
  Without `--force`, modified files are preserved.
- Protected paths (NEVER touched, even at `--force --yes`):
  `.claude/custom/`, `.claude/.backup/`, `.claude/.stx-profile`.

### Added

- **`-y` / `--yes` flag** to bypass the confirmation prompt (for CI /
  scripted updates). Combine with `--force` for full auto mode:
  `stx claude update --force --yes`.

### Removed

- **`--prune` flag**. Pruning is now the default behaviour; the flag was
  opt-in for one local release cycle and never reached PyPI, so no
  external script depends on it.

## [0.7.13] — 2026-05-21 — Navigation refactor Phase 4c: scroll-spy hears the real scroll container

### Fixed

- **Sidebar highlight was frozen in live continuous mode.** The
  cross-context scroll-spy (`stx_scroll_spy.js`) installed a plain `window`
  scroll listener, but in live Streamlit the page scrolls inside `.stMain`
  (a scrollable `<section>`), whose scroll events never reach a `window`
  listener — so the highlight never updated while scrolling (companion
  §6.15, the scroll-container gap, found alongside the export off-by-one).
  The listener now runs in the **capture phase**, which receives scroll
  events from any descendant scroller — covering `window` (static export)
  and `.stMain` (live) uniformly. Validated by a new deterministic e2e
  scenario (S10): scrolling a nested `overflow:auto` container now moves the
  active entry (frozen before the fix).

## [0.7.12] — 2026-05-21 — Navigation refactor Phase 4b: scroll-spy closest-to-line

### Fixed

- **Sidebar highlight lagged one entry behind in the static HTML export**
  (and any window-scroll context). The cross-context scroll-spy
  (`stx_scroll_spy.js`) chose the active entry as *"the heading with the
  largest top still ≤ TOP_OFFSET"* (the most recently scrolled-past
  heading). But the floating widget parks the **marker** at its scroll
  offset while the sidebar tracks **heading** anchors that sit just below
  their marker — landing just past the 120 px line — so the rule selected
  the **previous** heading (companion issues 6.3 / 6.9). `findClosestAnchor`
  now picks the heading **closest** to the reading line, which tracks the
  displayed section without the off-by-one. Trade-off: while free-scrolling
  a tall section the highlight may advance to the next heading slightly
  early. Validated by a new deterministic e2e scenario (S9) that injects the
  real scroll-spy into a controlled DOM and asserts closest-to-line
  selection.

### Known (separate issue, not addressed here)

- In **live** Streamlit the scroll container is `.stMain`, but scroll-spy
  listens on `window` scroll — so its recompute does not fire there, leaving
  the live continuous-mode sidebar highlight static. This is the
  scroll-container resolver gap (companion §6.15) and is tracked separately.

## [0.7.11] — 2026-05-21 — Navigation refactor Phase 4a: single active sidebar entry

### Fixed

- **Sidebar group-highlight** (paginated mode): a page with multiple
  headings (H1 + H2…) or multiple markers used to light **every**
  same-page entry in the TOC / Markers sidebar simultaneously, because the
  builder applied `color:var(--stx-link-active-color)` to all entries whose
  `page_idx == current_page` (companion issue 6.13 — the central UX
  complaint behind the 0.6.36→0.6.41 series). `_build_paginated_sidebar`
  now applies the active colour to **only the first** current-page entry in
  each tab; the remaining same-page entries keep their in-page anchor link
  without the active colour. Tactical, server-side only — no scroll-spy
  changes, so it cannot reintroduce the reverted frozen-highlight bug.
  Verified by the real-browser harness (scenario S6 flipped to passing).

## [0.7.10] — 2026-05-21 — Navigation refactor Phase 2: coalesce dropped page navigations

### Fixed

- **Double-press / double-click navigation no longer gets stuck one page
  short** (paginated mode). The paginated `navigateToPage` re-entry guard
  used to *silently drop* any navigation that arrived while a Streamlit
  rerun was already in flight (`if (navigating) return;` — companion issue
  6.2). A fast double `PageDown`/`ArrowRight` or a double-click on the
  floating ▶ arrow therefore advanced only one page while the widget
  counter had already moved to +2. The guard now **coalesces** the surplus
  request (`_stxPendingPage`) and applies it once the rerun lands, so a
  rapid double-press advances two pages and the counter stays consistent
  with the rendered page. Verified by the Phase-0 real-browser harness
  (scenarios S3/S4 flipped from `xfail` to passing). No public API change.

## [0.7.9] — 2026-05-21 — Navigation refactor Phase 0: real-browser regression harness

### Added

- **Real-browser navigation e2e harness** (`tests/e2e/test_nav_active_state.py`,
  `tests/e2e/_nav_harness.py`, fixture `tests/e2e/fixtures/nav_active_app/`).
  Phase 0 of the navigation-subsystem refactor
  (`documentation/maintenance/navigation_system/navigation-refactor-plan-v01.md`).
  Drives Chromium against a paginated, search-enabled deck and asserts on
  DOM/CSS state (the five invariants in the plan), since the reverted
  0.6.36→0.6.40 series proved headless probes do not reproduce the
  frozen-highlight / counter-desync bugs. Test-only; no library code changed.
- Three acceptance scenarios reproduce the open bugs as `xfail(strict=True)`
  so they flip to hard failures the moment a later phase fixes them:
  S3 (double PageDown drops the 2nd nav + counter desync),
  S4 (double-click ▶ same), S6 (multi-heading page lights the whole group).
  Scenarios S1/S2/S7 + a smoke check guard the consistent baseline.
- Harness runs headless by default (fast smoke) and headed under
  `STX_E2E_HEADED=1` (the real gate); `STX_NAV_E2E_DECK=/abs/deck` points it
  at an external deck (e.g. the draft bench) for manual verification. Requires
  `STX_USE_MARKER_RUNTIME=1` (set automatically by the launcher).

## [0.7.8] — 2026-05-21 — Visual-review foundation: `stx screenshot`, `st_hover_tooltip`, auto-Chromium

### Added

- **`st_hover_tooltip`** — new public widget: an inline icon that reveals a
  panel on CSS `:hover`, enabling the "telegraphic slide + detail-on-hover"
  technique (keywords on the slide, explanations one hover away). Palette-
  neutral by design (override colours/background via `*_style` / `bg_color`);
  routes through `st_html` so it is export/PDF-aware. Supports `position`
  (`left`/`center`/`right`) and `direction` (`up`/`down`) so the panel always
  opens on the side opposite the icon and stays on-slide, plus `max_height`
  with an internal scrollbar. Promoted from the proven ai4se6d/FC presentation
  widget. New module `streamtex/hover_tooltip.py`; tests in
  `tests/test_hover_tooltip.py`.
- **`stx screenshot`** — render a StreamTeX project to PNG images via headless
  Chromium (Playwright). Captures one PNG per slide (`.stx-block`) plus a
  full-page render, with a `manifest.json` index, into `docs/_screens/` by
  default. Intended to feed automated vision review (the CE PROTOTYPE visual
  gate) so unreadable fonts, content overflow, or empty viewports are caught
  before asking the user to validate. Requires the `pdf` extra + Chromium
  (`playwright install chromium`). New module
  `streamtex/cli/screenshot_cmd.py` exposing the reusable
  `capture_screenshots()` helper; E2E coverage in
  `tests/e2e/test_screenshot_cmd.py`.

### Changed

- **`stx install` now downloads Chromium automatically** (final step, all
  presets) so `stx screenshot` and PDF export work out of the box, instead of
  only printing a hint. Cross-platform, idempotent, and non-fatal on failure
  (prints the manual command and continues). Set `STX_SKIP_BROWSER_INSTALL=1`
  to opt out (CI / offline / hermetic environments).
- **`stx status`** now reports whether the Chromium browser is downloaded
  (Environment section), detected from the `ms-playwright` cache.

### Notes (ecosystem)

- The pack ecosystem migrated on 2026-05-20 to a single monorepo
  `nicolasguelfi/streamtex-packs`. Pip names follow the convention
  `streamtex-pack-{name}`. Python module names are **preserved**
  (`streamtex_design`, `streamtex_manuals`) so no impact on the
  streamtex library — `import streamtex` and all downstream code
  paths are unchanged. The legacy `nicolasguelfi/streamtex-design`
  repo is archived. The previously local-only `streamtex-manuals`
  is now formalized as `streamtex-pack-manuals` in the monorepo.
  Full migration plan: `streamtex/documentation/maintenance/pack_monorepo/PLAN.md`.

## [0.7.7] — 2026-05-20 — Fix: missing scale_curves.toml in wheel

### Fixed

- **Packaging**: `streamtex/styles/scale_curves.toml` is now included
  in the wheel (`[tool.setuptools.package-data]` extended with
  `"streamtex.styles" = ["*.toml"]`). Before this fix every fresh
  install of 0.7.6 was broken — `import streamtex` raised
  `FileNotFoundError` at `streamtex/styles/scale.py:48`.
- **Import diagnostics**: the stderr redirect in
  `streamtex/__init__.py` (used to silence Streamlit's "No runtime
  found" warnings during the import cascade) no longer swallows
  tracebacks. Any exception raised during the redirect window now
  flushes the buffered stderr to the real stderr before re-raising,
  instead of failing with a silent `exit 1`. This is what hid the
  packaging bug above.

## [0.7.6] — 2026-05-20 — Indexed font scale: relative architecture

### Changed

- `scale_curves.toml` rewritten to v0.2 **relative** schema: one
  `base_pt_desktop` value (default 18) + 29 adimensional ratios per
  curve. Changing the base re-scales every palier, every breakpoint,
  every curve proportionally. The v0.1 absolute-pt format (87 ints per
  curve) is gone.
- `ScaleConfig` gains 4 optional override fields: `base_pt_desktop`,
  `base_idx`, `tablet_scale`, `mobile_scale`. Per-document fine-tuning
  no longer requires constructing custom 29-value lists.
- Tablet/mobile pt values are now derived (`tablet = desktop × 0.85`,
  `mobile = desktop × 0.70`) instead of hand-tuned per palier. Most
  tablet/mobile pt values shift by ±1-3pt as a result.
- All 4 named curves (`word_processor`, `geometric`, `body_centric`,
  `bell`) now share the SAME base palier (idx_7 = `base_pt_desktop`).
  Previously each curve had its own absolute scale. `GEOMETRIC` and
  `BELL` therefore render at smaller default pt values than in 0.7.5
  — switch via `ScaleConfig(base_pt_desktop=X)` to compensate if you
  relied on the previous larger geometric scale.
- Tailwind aliases **rebased on the BASE palier**:
  `s.text_base = idx_7 = 18pt` (was `idx_4 = 12pt`). Smaller aliases
  (`text_xs/sm`) now resolve to paliers ≥ 14pt = 18.67px on desktop,
  respecting the ≥18px content floor automatically. Larger aliases
  shift by +3 palier indices to keep the visual spread.
- `default.css` regenerated with the new derivation; desktop palier
  pt values unchanged from 0.7.5 (round-trip exact), tablet/mobile
  shift ±1-3pt.

### Migration

- Code using `s.text_xs` / `s.text_sm` / `s.text_base` for body copy
  now renders at floor-respecting sizes automatically. Blocks that
  used `s.text_base` expecting 12pt → now get 18pt; verify any layout
  that depended on the previous smaller size.
- Code using `s.scale[N]` or `s.idx_N` (direct palier access) is
  unaffected on the default WORD_PROCESSOR curve (round-trip exact);
  GEOMETRIC / BELL curves shift due to the harmonized base.
- Custom curve overrides previously passed `list[int]` of 29 pt
  values; they now accept `list[float]` of ratios. A backward-
  compat shim auto-detects integer lists ≥ 6 and treats them as
  legacy pt-list (deprecation warning logged, auto-normalized to
  ratios).

### Added

- `streamtex/scripts/migrate_curves_to_relative.py` — one-shot
  migration helper that converts a v0.1 TOML to v0.2.
- 9 new tests in `test_scale.py::TestRelativeArchitectureV02`
  covering base override, breakpoint scale override, alias re-
  anchoring, curve-base harmonization, ratio validation.
- `_BASE_PT_DESKTOP_DEFAULT`, `_BASE_IDX_DEFAULT`,
  `_TABLET_SCALE_DEFAULT`, `_MOBILE_SCALE_DEFAULT` module constants
  exposed from `streamtex.styles.scale` for introspection.

## [0.7.5] — 2026-05-20 — Indexed responsive font scale

### Added

- Indexed responsive font scale: 29-palier scale with 4 named curves
  (`word_processor`, `geometric`, `body_centric`, `bell`). Three access
  modes: attribute (`s.idx_N`), subscript (`s.scale[N]`), Tailwind alias
  (`s.text_xs` … `s.text_9xl`).
- New API: `ScaleConfig` dataclass + `ScaleCurve` enum +
  `compute_scale()` + `emit_scale_css()` exported from `streamtex`.
- Per-document configuration via `st_book(scale=ScaleConfig(...))` —
  inline `<style>` block injected after `default.css` load.
- Data-driven curves stored in `streamtex/styles/scale_curves.toml`;
  editable without code changes.
- Out-of-range subscript indices clamped (no exceptions) with debug
  logging — `s.scale[-5]` → `s.scale[0]`, `s.scale[100]` → `s.scale[28]`.

### Changed

- `default.css` extended with 87 new CSS custom properties
  (`--stx-scale-0..28` × 3 breakpoints) inside a BEGIN/END marker block
  generated from `scale_curves.toml`.
- No existing tokens or CSS variables removed; full backwards compatibility
  for `s.tiny`/`s.medium`/`s.LARGE`/… and `s.pt4`/`s.pt196` scales.

## [0.7.4] — 2026-05-19 — Pack Engineering availability (docs-only)

Documents the availability of the **Pack Engineering (PE)** module that
shipped in `streamtex-claude` 0.3.0. No library code changes — this release
exists so the streamtex library's own `.claude/references/` cheatsheet and
README stay in sync with the broader ecosystem.

### Changed

- `README.md` — "AI-Powered Features" section updated to reference
  `stx-pe` (7 commands) alongside `stx-block` and `stx-ce`. New
  "Pack Engineering (`/stx-pe`)" subsection. `pack-orchestrator` added
  to the AI Agents table.
- The local `.claude/references/streamtex_cheatsheet_en.md` and
  `.claude/references/pe_cheatsheet_en.md` files are synced from the
  `streamtex-claude` 0.3.0 source via `stx claude update`. They are
  gitignored by design (`.claude/*` is managed by the profile
  installer, not by git).

### About the PE module

PE is a Claude-driven orchestrated lifecycle for extracting, forking,
refining, auditing, adopting, and publishing reuse packs across N
projects. It drives the deterministic `stx component / pack / kit / validate`
CLI commands (which already exist in `streamtex 0.7.x`) and adds the
AI-assisted analysis, design, and retrofit phases that those commands
cannot perform deterministically.

The module itself ships in **streamtex-claude 0.3.0** as a project-profile
sub-directory (`profiles/project/pack-engineering/`) and is installed by
`stx claude install project <target>`. No `streamtex` library changes
are required to use PE.

## [0.7.3] — 2026-05-19 (L5 — TOCConfig.numerate_titles removed)

Final piece of the Q10 legacy purge: the `numerate_titles` field on
`TOCConfig` is removed in favour of the `numbering` field
(`NumberingMode.{BOTH,SIDEBAR_ONLY,MAIN_ONLY,NONE}`). The field had
been documented as legacy since the `numbering` field was introduced
but kept for backward compatibility; pre-distribution legacy mandate
applies. Full test suite still green (2112 passed, 1 skipped).

### Removed
- `TOCConfig.numerate_titles` field — replaced by `numbering`
  (`NumberingMode.BOTH` is now the default; `NumberingMode.NONE`
  replaces the legacy `numerate_titles=False`).
- The two-branch fallback in `TOCConfig.effective_numbering` is
  reduced to `return self.numbering`.

### Changed
- `tests/test_toc.py` — 4 tests migrated from `numerate_titles=` to
  `numbering=NumberingMode.X`. The class `TestNumberingMode` renames
  `test_numerate_false_gives_none` → `test_numbering_none` and
  `test_numbering_overrides_numerate_titles` → `test_numbering_sidebar_only`.
  `test_defaults` now asserts `numbering == NumberingMode.BOTH`.

## [0.7.2] — 2026-05-19 (Q10 — Library legacy API removal)

Pre-distribution legacy purge: removes deprecated functions, params, and
flags that had been kept for backward compatibility with versions prior
to 0.7. All have clear replacements (cited below). Full test suite
green (2112 passed, 1 skipped).

### Removed
- **`st_ai_image()` and `st_ai_image_widget()`** — both deprecated
  since v0.4. Replacement: `st_image(prompt=..., editable=True,
  name=...)` for declarative AI image rendering and
  `st_image(editable=True)` with the editor panel's AI tab for
  interactive generation. The whole `streamtex/ai_image.py` module
  is deleted along with `tests/test_ai_image.py`. The
  `streamtex.__init__` no longer re-exports these symbols.
- **`monties_color` parameter** of `st_book()` — was a deprecated
  alias for `banner_color`/`banner=`. Removed from the signature and
  the resolution branch in `book.py`. The `TestBackwardCompatibility`
  class in `test_banner.py` (carrying the `test_monties_color_*`
  case) is renamed to `TestBannerColorResolution` and trimmed
  accordingly.
- **`*args` and `**_legacy_kwargs` "transparent forwarding"** to
  `block.build()` in `st_book()`. The signature now accepts only the
  explicit `block_args=(...)` and `block_kwargs={...}` paths. Passing
  unknown kwargs directly to `st_book()` now raises `TypeError`
  immediately (was a `DeprecationWarning` deferred to the next major).
  `test_book_integration.py::test_legacy_unknown_kwarg_emits_deprecation_warning`
  is replaced by `test_unknown_kwarg_raises_typeerror`; the two
  legacy-forwarding tests
  (`test_legacy_kwargs_still_forwarded_for_backward_compat`,
  `test_block_kwargs_overrides_legacy_kwargs`) are consolidated into
  the clean-path `test_block_kwargs_only_path_works`.
- **`--no-patterns` CLI flag** on `stx install` — was a hidden
  deprecated alias for `--no-design-pack` with a yellow warning.
  Removed; the `install_cmd.py` branch that printed the deprecation
  notice is gone.
- **Stale "MIG-2 → MIG-5 coexistence" comment** in
  `streamtex/cli/pack_cmd.py` module docstring — the legacy
  `stx patterns *` CLI group it referred to was removed entirely in
  earlier 0.7.x patches.

### Provider error messages updated
- `streamtex/ai/providers/{google,fal,openai}.py` — API-key error
  messages no longer mention `st_ai_image()`; now reference
  `st_image()`.

### Deferred (not in this release)
- `numerate_titles` field on `TOCConfig` — still used by tests and
  the `streamtex-quick-reference.md` skill. Removing it requires a
  caller migration to `numbering=NumberingMode.X` first.

## [0.7.1] — 2026-05-19 (Legacy purge — Render removed)

Pre-distribution cleanup pass: removes the `Render` deployment platform
that had been replaced by `Hetzner/Coolify` per
`feedback_hetzner_only.md`. The patches in 0.7.0 had kept Render as a
co-existing alternative; this release makes the production stance
explicit and reduces the deploy surface.

### Removed
- `stx deploy render` CLI command (`render_cmd`) + 6 supporting helpers:
  `generate_render_service`, `generate_render_yaml`,
  `parse_render_yaml_services`, `render_service_url`,
  `check_render_status`, env-sync's `render_yaml` branch.
- `stx deploy env-sync` CLI command (was Render-API only) and its
  helpers (`_read_render_cli_config`, `_parse_render_yaml_env_vars`,
  `_render_api_get/put/post`, `_resolve_render_service_ids`).
- `stx deploy status render` mode — `PLATFORM` choice now restricted to
  `huggingface | coolify`.
- ~20 tests covering the removed Render code paths.

### Migration
- For deployment, use `stx deploy hetzner` / `stx deploy update` /
  `stx deploy status coolify` (or `stx deploy huggingface` for
  HuggingFace Spaces).
- The mapping is 1:1: `stx deploy render` → `stx deploy hetzner`,
  `stx deploy env-sync` → manage env vars via Coolify UI / API.

### Rationale
- The Render code path had been informally deprecated since the
  Hetzner/Coolify migration but was kept as "co-existing alternative".
  No StreamTeX project is deployed on Render today, no PyPI release of
  streamtex was distributed before this consolidation, so this is a
  clean strict-pruning of unused code.

## [0.7.0] — 2026-05-19 (Wave 4 — Reuse architecture milestone)

Consolidation milestone (PLAN Q15 / D15). Bundles the structural changes
shipped across 0.6.42 → 0.6.45 (Waves 1-2) and signals to consumers that
the pattern-flow is gone and the pack-based reuse architecture is the
new contract. Per `feedback_no_minor_bump.md` (now amended): the
`0.7.x` track was reserved for this consolidation; from `0.7.0` onward
patch-only releases on the `0.7.x` track until the next consolidation.

### Added (cumulative — see 0.6.42 / 0.6.43 / 0.6.44 / 0.6.45 below)
- `streamtex.core.*` — contracts (`DesignSystemProtocol`, `ComponentMeta`,
  `KitManifest`, `PackManifest`, `StxTomlPackEntry`, `ReuseArchitectureError`),
  validation (CV/DV/KV/PV/BV codes), and discovery
  (`discover_packs`, `get_primary_local_pack`, `get_bundle_attr`).
- New CLI groups: `stx pack`, `stx component`, `stx ds`, `stx kit`,
  `stx validate` (Q9 MIG-2 → MIG-6).
- `stx project new --kit <pack>:<kit_name>` + `--pack`, `--pack-name`,
  `--no-mypack` (Q7 / Q8 MIG-3). Generates `stx.toml`, scaffolds the
  primary local pack `mypack/`, installs it editable.
- `stx install` auto-adds the `streamtex-design` pack to projects on
  preset `standard`/`power`/`developer` (Q9 MIG-4); new `--no-design-pack`
  (`--no-patterns` retained as deprecated alias).
- Top-level re-exports (PLAN §5.0): `DesignSystemProtocol`,
  `ComponentMeta`, `ReuseArchitectureError`.
- `tests/test_integration_multipack.py::test_invariants_1_to_5` — the
  multi-pack E2E matrix demonstrating D5 (PLAN §11.4).

### BREAKING (0.6.45 — already shipped)
- `stx patterns *` removed (replaced by `stx pack/component/ds/kit/validate`).
- `streamtex.patterns` module removed (`streamtex.core.*` is the new
  contracts layer).

### Notes
- `streamtex-design` v0.1.0 is the reference pack
  (`github.com/nicolasguelfi/streamtex-design`).
- `streamtex-claude` v0.2.0 ships the new `reuse-architecture` skill
  and the `stx-pack/component/ds/kit/validate/new` shared commands.
- `streamtex-docs` `docs-patterns.streamtex.org` now serves
  `stx_manual_reuse` (Wave 3 Phase 6.5 — same Coolify slot, env var
  `FOLDER` patched).
- Full suite at this tag: 2113 passing.

## [0.6.45] — 2026-05-19 (Wave 2 MIG-6 — atomic suppression of legacy patterns)

### BREAKING (removed)
- `stx patterns *` command group removed in full. Replaced by `stx pack`,
  `stx component`, `stx ds`, `stx kit`, `stx validate` (introduced in
  Wave 1 MIG-2). Per PLAN §29.8 / Q9.
- `streamtex.patterns` Python module deleted (10 files / 2973 lines):
  `__init__.py`, `index.py`, `installer.py`, `manifest.py`, `picker.py`,
  `preset.py`, `project_toml.py`, `resolver.py`, `updater.py`,
  `validator.py`.
- `streamtex/cli/patterns_cmd.py` (1173 lines) removed.
- `streamtex/cli/install_cmd.py`: `_maybe_offer_patterns` helper removed.
  The new replacement `_add_default_design_pack` (MIG-4) is the active
  code path.
- 6 test files removed (2201 lines):
  `tests/test_patterns_smoke.py`, `test_patterns_meta_v3.py`,
  `test_patterns_picker.py`, `test_patterns_composite.py`,
  `test_patterns_source_cmd.py`, `test_install_patterns_offer.py`.
- README.md "Design Patterns (`stx patterns`)" section rewritten as
  "Reuse architecture (`stx pack`/`component`/`ds`/`kit`)".

### Notes
- MIG-5 checkpoint SHA: `ccabd695ad0151096eccdf1466a7a0e18f08ffde`.
- Q14 orphan checks (PLAN §29.8): `grep "patterns-meta"`,
  `grep "from streamtex.patterns"` both return 0 occurrences across
  `streamtex/` and `tests/` (verified at MIG-6 commit time).
- 4 conceptual patterns (exception hierarchy, composite v3 QCM,
  `extends` mechanism, TraceEntry audit) were extracted and ported to
  `streamtex/core/*` in Wave 1 MIG-1 before deletion (see PLAN §28).
- Full suite: 2111 passed (down from 2223 in 0.6.44, −112 patterns tests
  removed; no production code uncovered).

### MIG-5 checkpoint

Audit run at SHA `ccabd695ad0151096eccdf1466a7a0e18f08ffde` (post-MIG-4).
`grep -rln "from streamtex\.patterns\|import streamtex\.patterns" streamtex/
tests/` yields **8 files** (PLAN §29.7 expected 7):

- `streamtex/cli/patterns_cmd.py` (multiple imports — to be deleted in MIG-6)
- `streamtex/cli/install_cmd.py` (**deviation**: dormant `_maybe_offer_patterns`
  preserved with its inner imports so `test_install_patterns_offer.py` keeps
  importing cleanly; the install flow no longer calls it. Removed atomically
  in MIG-6.)
- `tests/test_patterns_smoke.py`
- `tests/test_patterns_meta_v3.py`
- `tests/test_patterns_picker.py`
- `tests/test_patterns_composite.py`
- `tests/test_patterns_source_cmd.py`
- `tests/test_install_patterns_offer.py`

No unexpected consumer was introduced. MIG-5 go.

## [0.6.44] — 2026-05-19 (Wave 2 MIG-4 — `stx install` switches to design pack)

### Added
- `stx install` now auto-adds the official `streamtex-design` pack to the
  project's `stx.toml` after creation, for presets `standard`, `power`,
  and `developer` (PLAN §29.6 / Q9). New helper
  `_add_default_design_pack(ws_root, project, preset, console)`.
- `--no-design-pack` flag on `stx install` to opt out.

### Changed
- `--no-patterns` is now a deprecated alias for `--no-design-pack`
  (kept for retro-compat; prints a yellow warning when used). The legacy
  `_maybe_offer_patterns` is no longer invoked from the install flow but
  remains in the file (dormant, removed atomically in MIG-6 alongside
  its dedicated test file).
- 8 new tests in `tests/test_install_design_pack.py`. Full suite: 2223 passed.

## [0.6.43] — 2026-05-19 (Wave 2 MIG-3 — `stx project new` modernised)

### Added
- `stx project new` accepts the new reuse-architecture flags
  (PLAN §7.1 / Q7 + Q8): `--kit <pack>:<kit_name>`,
  `--pack <ref>` (repeatable), `--pack-name <name>` (default `mypack`),
  `--no-mypack`.
- `stx project new` now generates `stx.toml` at the project root
  (PLAN §6.1) and scaffolds the local primary pack (`<pack_name>/`)
  with its `pyproject.toml`, `_pack_manifest.toml`, and the four
  subdirectories (`components/`, `design_systems/`, `cli_templates/`,
  `kits/`). After `uv sync` the pack is installed in editable mode
  (`uv pip install -e ./<pack_name>`).
- Project validation: 4 new checks (11-14) — `stx.toml` parsability,
  primary pack directory + manifest, primary pack importability,
  exactly-one-primary uniqueness.
- New helpers in `streamtex/cli/project_cmd.py`:
  `generate_stx_toml`, `generate_mypack_pyproject_toml`,
  `generate_mypack_manifest`, `scaffold_mypack`, `_resolve_kit`,
  `_split_kit_ref`.
- Legacy `--template <X>` is preserved as an alias to
  `--kit streamtex_design:<X>-default` (or `slides-modern-dark` for
  `--template slides`) — falls back to the rich template path when the
  kit cannot be resolved.
- 10 new tests in `tests/test_cli_project.py`. Full suite: 2215 passed.

## [0.6.42] — 2026-05-19 (Wave 1 — reuse architecture foundations)

### Added
- `streamtex.core.*` — reuse architecture contracts, validation, discovery
  (MIG-1 per PLAN.md §29.3). Implements `DesignSystemProtocol`,
  `ComponentMeta`, `KitManifest`, `PackManifest`, `StxTomlPackEntry` plus
  the bundle Protocols (Colors/Titles/Callouts/StatHero/CardGrid/
  ComparisonTable/Takeaways/Body/Citation/InlineEmphasis/Lists).
  Validation API: `validate_component` (CV001-CV011),
  `validate_design_system` (DV001-DV006), `validate_kit` (KV001-KV005),
  `validate_pack` (PV001-PV010), `validate_bundles_required` (BV001-BV002).
  Discovery surfaces the 5 pack lifecycle states (§5.6bis) and includes
  `get_primary_local_pack` (Q7), `get_bundle_attr` (Q2). Exception
  hierarchy: `ReuseArchitectureError` + 5 subclasses.
- Top-level re-exports (PLAN §5.0 convention hybride):
  `DesignSystemProtocol`, `ComponentMeta`, `ReuseArchitectureError`.
- New CLI groups (`stx pack/component/ds/kit/validate`) shipped alongside
  the legacy `stx patterns *` (MIG-2 per §29.4). Includes
  `stx pack add --dev <path>` (Q17), the four-branch
  `stx component promote` routing helper (Q12), and
  `stx pack list --trace`.
- Shared CLI helpers `streamtex/cli/_toml_helpers.py` and
  `streamtex/cli/_stx_toml.py`.
- 62 new tests (31 core + 31 CLI). Full suite: 2205 passed.

### Unchanged (legacy preserved for MIG-6 in Wave 2)
- `streamtex.patterns.*` (2971 lines) and `streamtex/cli/patterns_cmd.py`
  (1173 lines) continue to function unchanged. Atomic removal scheduled
  for Wave 2 MIG-6.

### Fixed
- **Composite picker: empty checkbox submission no longer silently
  cancels an add.** The classic questionary trap — pressing ENTER
  without first using SPACE to toggle items — used to return the user
  silently to the main menu with no preset / no pattern added, leaving
  them confused (the report was *"the picker did not even propose
  preset contents"* — in reality the picker did, but the empty
  submission discarded everything). Two complementary mitigations:
  * Every multi-select prompt now prints a dim help line just above the
    checkbox: `(↑↓ navigate · SPACE to toggle · ENTER to confirm · ESC to cancel)`.
  * `Add preset(s)` and `Add individual pattern(s)` use a new
    `_checkbox_with_empty_retry()` helper: on an empty submission, a
    yellow warning explains the SPACE step and the prompt is re-opened
    once. A second empty submission returns to the menu (no infinite
    loop). ESC / Ctrl-C still propagates as a genuine cancel without
    going through the retry path.
  * `Customize a preset` and `Remove` keep their existing semantics
    (empty submission there is legitimate — "drop everything from this
    preset" or "I changed my mind, remove nothing") and only get the
    help line, not the retry.
  (`streamtex/patterns/picker.py`)
- **Invisible JS-bus iframes no longer render as visible light bars.**
  StreamTeX injects JavaScript into the parent document via
  `st.iframe(js, height=1)` from 10+ call sites (loading overlay,
  marker navigation, banner, paginated nav, search refresh, bib
  hover-preview, Chrome banner, password keyboard capture). Streamlit's
  default iframe chrome (light background + border) made each 1px host
  appear as a thin horizontal line — particularly noticeable in dark
  themes. Added a single CSS rule in `streamtex/static/default.css`
  that collapses `iframe[height="1"]` to `height: 0` and uses
  `visibility: hidden` (not `display: none`, which would prevent
  the JS from loading). (`streamtex/static/default.css`)
- **`generate_book_py()` no longer passes `title="{name}"` to `st_book`.**
  That kwarg is not part of `st_book`'s API; under the legacy forwarding
  it was sent verbatim to every `block.build()` and crashed any block
  whose signature didn't accept it (i.e. every scaffolded block). The
  page title is already set via `st.set_page_config(page_title=...)`
  earlier in the generated file, so this argument was redundant on top
  of being broken. (`streamtex/cli/project_cmd.py`)
- **`stx install`: skip cloning repos that are dev-linked.** Step 2
  ("Clone missing repos") now calls `resolve_repo_path()` to detect
  repos registered via `stx dev register` and skips `git clone` for
  them, matching the existing behaviour of `stx update`. Avoids
  creating redundant `<workspace>/streamtex-claude/` and
  `<workspace>/streamtex-docs/` clones when a global dev link is
  active. (`streamtex/cli/install_cmd.py`)
- **`stx project new --template` / `stx install --template`: honor
  dev-linked `streamtex-docs`.** `_copy_rich_template()` now resolves
  the docs repo through `resolve_repo_path()` instead of hardcoding
  `<workspace>/streamtex-docs/templates/…`, so rich templates work
  when docs is dev-linked rather than cloned into the workspace.
  (`streamtex/cli/project_cmd.py`)
- **`stx install`: don't offer to clone `streamtex-docs` if it is
  dev-linked.** `_maybe_clone_docs_for_template()` checks
  `resolve_repo_path()` before testing the workspace path and reports
  the dev link as satisfying the template requirement.
  (`streamtex/cli/install_cmd.py`)
- **`stx status`: read library version from the dev-linked source.**
  `_get_source_version()` now resolves the library repo through
  `resolve_repo_path()` so the displayed source version reflects the
  dev-linked checkout when one is registered.
  (`streamtex/cli/status_cmd.py`)
- **Scaffolded `blocks/__init__.py` now passes the parent directory to
  `ProjectBlockRegistry`, not `__file__`.** Root cause of the "StreamTeX
  Initializing…" loading loop seen on freshly-scaffolded projects:
  `ProjectBlockRegistry(__file__)` made `self.blocks_dir` a file path,
  `Path.glob("bck_*.py")` silently returned empty, the manifest stayed
  empty, `_paginated_book` early-returned on `total == 0` without
  removing the loading overlay. Generator now emits
  `ProjectBlockRegistry(Path(__file__).parent)` (matches the docstring
  and the `streamtex-docs` template). (`streamtex/cli/project_cmd.py`)
- **`ProjectBlockRegistry.__init__` now validates that the path is a
  directory.** Passing a file (or non-existent path) now raises a clear
  `ValueError` with the correct usage hint, instead of silently
  producing an empty registry. Catches the bug above at the lib level
  for any user writing `blocks/__init__.py` by hand. (`streamtex/blocks.py`)
- **`_paginated_book` removes the loading overlay before the
  `total == 0` early-return.** Defensive cleanup so a legitimately
  empty book (or any other path that produces `total == 0`) no longer
  leaves the "Initializing…" overlay stuck on screen.
  (`streamtex/book.py`)
- **`ProjectBlockRegistry` implements the Python sequence protocol
  (`__len__` / `__iter__` / `__getitem__`).** Fixes `TypeError: object
  of type 'ProjectBlockRegistry' has no len()` raised by
  `st_book(registry, ...)` — the form produced by `generate_book_py()`
  for new projects. Per-block lazy loading is preserved: `__len__`
  reads the manifest without importing anything, and `__iter__` yields
  blocks one at a time so `st_book` only imports the blocks it
  actually renders. Blocks are ordered alphabetically by name (use the
  convention `bck_NN_xxx.py` for explicit ordering).
  (`streamtex/blocks.py`)

### Changed
- **Composite picker: per-preset 'Customize?' after add + Remove choices
  grouped by provenance.** Closes a discoverability gap in the v3
  picker: when the user added a preset, its contents were absorbed
  silently and the only way to drop one of its patterns was to navigate
  to the separate Remove action — non-obvious. Now:
  * After multi-selecting presets, the picker asks
    *"Customize '<preset>'? [y/N]"* once per newly-added preset (default
    No). Saying Yes opens a checkbox of that preset's patterns with all
    currently-kept items pre-checked; unchecked patterns are added to
    `working.excludes`. Excludes remain global by design (consistent
    with declarative `--exclude` and with how a single excluded pattern
    affects every preset that brings it).
  * The Remove action now groups choices by provenance with one
    `── preset:<name> ──` / `── individual ──` / `── all ──` separator
    per group, so the user can see where each pattern comes from when
    deciding what to drop.
  New helper `_compute_provenance(working, resolved, source)` returns
  the per-pattern provenance label and is reused by both flows.
  (`streamtex/patterns/picker.py`)
- **`SourceNotFoundError` now points at the new tooling.** The error
  message includes the per-level R4 trace and ends with a hint listing
  `stx patterns source clone | link | set | show` so users know how to
  resolve the situation without grepping the source. The resolver no
  longer collects ad-hoc strings; it delegates to `trace_source()`.
  (`streamtex/patterns/resolver.py`)
- **`stx install --dev`: auto-link the registered streamtex source into a
  new project's venv.** When creating a project with `--project NAME`,
  passing `--dev` runs the equivalent of `stx dev link streamtex` inside
  the freshly-scaffolded project: writes `[tool.uv.sources]` to its
  `pyproject.toml` and re-syncs uv so the project uses the dev-source
  immediately, no manual follow-up needed. No-op (with a hint) when
  `streamtex` is not registered globally via `stx dev register`.
  (`streamtex/cli/install_cmd.py`)

### Added
- **`.patterns-meta.json` schema v3 — composite selection.** The
  ``selection`` field generalises from a single mode+items pair into
  four composable parts: ``presets[]`` (taken in full), ``individuals[]``
  (added on top), ``excludes[]`` (subtracted from the resolved set),
  and an ``all`` flag (everything in the source, still subject to
  excludes). v1 and v2 selections migrate silently in-memory on load;
  v1/v2 shapes are also still accepted on read in ``stx.toml`` for
  hand-edited files. Bumps ``__version_schema__`` to 3,
  ``SUPPORTED_SCHEMA_VERSIONS`` to ``(1, 2, 3)``. The legacy ``mode`` /
  ``items`` attributes are gone from ``PatternSelection``; a derived
  ``effective_mode`` property classifies a selection as
  ``empty``/``preset``/``individual``/``all``/``composite``.
  (`streamtex/patterns/__init__.py`, `streamtex/patterns/manifest.py`,
  `streamtex/patterns/installer.py`, `streamtex/patterns/project_toml.py`)
- **`stx patterns install` — composite menu-driven picker.** When no
  selector flag is passed in a TTY, the interactive mode now opens a
  persistent menu loop instead of a single multi-select:
  *Add preset(s)* / *Add individual pattern(s)* / *Remove pattern(s)
  from current selection* / *Toggle 'all' mode* / *Show summary* /
  *Done* / *Cancel*. Each action mutates a working ``PatternSelection``
  v3, with a header line showing the current composition and the
  resolved pattern count. The flat picker (one screen, multi-select
  grouped by scope) is still available via ``--tag VALUE``.
  (`streamtex/patterns/picker.py`, `streamtex/cli/patterns_cmd.py`)
- **Composable declarative CLI.** ``--preset`` is now repeatable
  (``--preset slides --preset docs``); ``--preset`` + ``--pattern``
  + ``--exclude`` may be combined freely; ``--all`` is exclusive with
  ``--preset/--pattern`` but still accepts ``--exclude``. The composite
  selection is built from flags and persisted to
  ``stx.toml [patterns.selection]`` in canonical v3 form.
  (`streamtex/cli/patterns_cmd.py`)
- **``resolve_selection(selection, source)`` helper.** Pure function
  that resolves a v3 selection against a source repo into a sorted
  tuple of pattern names. Algorithm: ``all_flag`` ⇒ every pattern;
  else union of ``patterns(preset)`` for each preset + ``individuals``;
  always subtract ``excludes``. Used by ``install``, ``sync``, and the
  picker's summary view. (`streamtex/patterns/installer.py`)
- **`stx install --project NAME`: opt-in design-patterns prompt at the
  end of project creation.** Two-stage, both default to NO; the whole
  helper is skipped silently in non-TTY contexts so CI/scripts remain
  reproducible. (1) If no patterns source is resolvable for the new
  project, ask whether to clone `streamtex-patterns` into the workspace
  (URL inherits from `[repos.streamtex-patterns].url` if declared, else
  the official repo). (2) Then, if a source is reachable, ask whether to
  open the interactive picker; selected patterns are installed into
  `<project>/.claude/custom/streamtex-patterns/` and the choice is
  persisted as `[patterns.selection]` in the project `stx.toml`. New
  flag `--no-patterns` short-circuits both stages. Clone/install
  failures degrade to a warning — they never break `stx install`.
  (`streamtex/cli/install_cmd.py`)
- **Reusable `clone_patterns_source(url, target, branch=None, force=False)`.**
  Extracted from `stx patterns source clone` so the opt-in prompt above
  and the explicit subcommand share one validated implementation
  (git presence check, empty-dir handling, manifest verification,
  subprocess timeout). (`streamtex/patterns/installer.py`)
- **`stx patterns install` — interactive multi-select picker when no
  selector is passed.** Running `stx patterns install` (no `--preset`,
  no `--pattern`, no `--all`) in a TTY now opens a `questionary`
  checkbox grouped by scope (`core`, `slides`, `docs`, `projects/<id>`).
  Already-installed patterns are pre-checked, so a re-run shows current
  state and lets you toggle. Empty selection or Ctrl-C aborts cleanly.
  New flag `--tag VALUE` narrows the picker to patterns whose frontmatter
  tags include `VALUE` (case-insensitive). Non-TTY contexts (CI, scripts)
  refuse with a clear error pointing at the explicit flags — no hidden
  install ever happens. (`streamtex/patterns/picker.py`,
  `streamtex/cli/patterns_cmd.py`)
- **`collect_pattern_catalog()` + `filter_by_tag()` helpers.** Walk a
  source repo and return one `CatalogEntry(name, scope, description,
  tags, path, extrapolable, since)` per pattern, skipping malformed
  files with a warning so the picker never crashes on bad input.
  (`streamtex/patterns/picker.py`)
- **`st_book(..., block_args=(...), block_kwargs={...})`: explicit
  forwarding of args/kwargs to each `block.build()`.** Replaces the
  previous implicit `*args/**kwargs` capture, which silently forwarded
  any unknown kwarg to every block and caused confusing deep
  `TypeError: build() got an unexpected keyword argument ...` cascades
  (e.g. when a scaffolded `book.py` passed `title="..."` to st_book).
  The explicit API gives clear IDE/type-check support and a single
  documented contract; internal helpers (`_paginated_book`,
  `_build_page_cache`, `_warmup_build_cache`) lost their `*args/**kwargs`
  pass-through and now take `block_args`/`block_kwargs` directly.
  (`streamtex/book.py`)
- **New subgroup `stx patterns source` — inspect & configure the patterns
  source path.** Four subcommands replace the previous "edit `stx.toml` by
  hand or guess" workflow:
  - `stx patterns source show` — print the R4 resolution chain (which level
    matched, what each level probed, why others failed) plus next-step
    suggestions when nothing resolves.
  - `stx patterns source clone [--url URL] [--branch B] [--target DIR] [--force]` —
    git-clone the patterns repo into `<workspace>/streamtex-patterns` (or a
    custom target). Default URL is read from `[repos.streamtex-patterns].url`
    in the workspace `stx.toml`, falling back to the official repo. Refuses
    cloning into a non-empty directory without `--force`.
  - `stx patterns source link PATH [--force]` — symlink
    `<workspace>/streamtex-patterns` to an existing local clone (for sharing
    one checkout across many workspaces, or for pattern-author iteration).
  - `stx patterns source set PATH [--scope project|workspace] [--allow-missing]` —
    record `[patterns].source = PATH` in `stx.toml` (or `pyproject.toml`
    under `[tool.patterns]` when no `stx.toml` exists) via `tomlkit`,
    preserving comments and unrelated keys.
  (`streamtex/cli/patterns_cmd.py`, `streamtex/patterns/project_toml.py`)
- **`trace_source()` — structured introspection of the R4 chain.** Returns
  per-level `(status, candidate, detail)` entries without raising; reused
  by `source show` and by `SourceNotFoundError`'s enriched message.
  (`streamtex/patterns/resolver.py`)
- **`.patterns-meta.json` schema v2 — record user install intent.** Adds a
  new `selection` field (`{mode: "preset"|"individual"|"all", items: [...]}`)
  so `stx patterns sync` can restore a hand-picked selection on a fresh
  clone, not just a preset. v1 files load transparently (silent in-memory
  migration; `preset`-only files are upgraded to `selection.mode="preset"`).
  (`streamtex/patterns/__init__.py`, `streamtex/patterns/manifest.py`,
  `streamtex/patterns/installer.py`)
- **`stx patterns` writes user intent to the project TOML.** After every
  successful `stx patterns install`, the chosen preset/pattern list is
  persisted to `<project>/stx.toml` under `[patterns.selection]` (or to
  `[tool.patterns]` in `pyproject.toml` when `stx.toml` is absent). Three
  shortcut forms are accepted on read for hand-edited files:
  `preset = "..."`, `selected = [...]`, `all = true`. The canonical
  sub-table is written back, removing legacy shortcuts. Comments and
  unrelated keys are preserved via `tomlkit`. (new module
  `streamtex/patterns/project_toml.py`, `streamtex/cli/patterns_cmd.py`)
- **`stx patterns sync` honors recorded intent.** Precedence order:
  `stx.toml [patterns.selection]` → `.patterns-meta.json` `selection` →
  legacy `preset` field → fallback to a plain refresh of installed files.
  Missing patterns are installed without overwriting the recorded intent
  (new `build_install_plan(record_selection=False)` flag).
  (`streamtex/cli/patterns_cmd.py`, `streamtex/patterns/installer.py`)
- **CLI extra `[cli]` gains `tomlkit>=0.13` and `questionary>=2.0`.**
  `tomlkit` is used for round-trip-safe edits of `stx.toml`/`pyproject.toml`;
  `questionary` is prepared for the upcoming interactive multi-select
  picker (`stx patterns install` without arguments). (`pyproject.toml`)

### Deprecated
- **Passing extra args/kwargs directly to `st_book` is now deprecated.**
  `st_book(modules, theme="dark")` still forwards `theme` to each
  `block.build()` but emits a `DeprecationWarning`. Use the explicit
  `st_book(modules, block_kwargs={"theme": "dark"})` instead. The
  legacy capture will be removed in a future major release; unknown
  kwargs will then raise `TypeError` at the call site rather than
  crashing deep inside block code. (`streamtex/book.py`)

### Documentation
- **End-to-end install flow documented in three places.** (1) New block
  `bck_install_flow.py` in `streamtex-docs/manuals/stx_manual_patterns/`
  walks through source resolution, interactive picker, declarative flags,
  the opt-in prompt at project creation, and intent persistence for
  `sync`. (2) `bck_cli_overview.py` reorganised into four thematic
  groups (lifecycle / source / catalog / authoring) covering all 15
  subcommands. (3) New "Design Patterns" section in
  `streamtex/README.md` with a 4-step quickstart and a link to the
  manual. (4) `streamtex-patterns/README.md` rewritten around the
  interactive picker, the `source` subgroup, and `[patterns.selection]`.

## [0.6.41] — 2026-05-14

### Reverted
- **Restored navigation/highlight code to the 0.6.34 baseline.** The
  series of scroll-spy / TOC / Markers modifications shipped in
  0.6.36 → 0.6.40 (commits b7de23a, 69e635e, 2233d18, 91d4b99,
  a691168) introduced a regression where double clicking the
  floating-arrow widget or pressing arrow keys twice in quick
  succession left the active-entry highlight permanently missing
  in real browsers — despite headless E2E probes passing. The bug
  could not be reproduced in headless Chromium (the Streamlit
  rerun cycle completes too quickly for the mutation cadence issue
  to surface), so successive forward-only patches accumulated
  without addressing the real failure mode.

  Files reverted to the `727bfba` (0.6.34) state:
  - `streamtex/static/js/stx_scroll_spy.js`
  - `streamtex/book.py` (TOC + Markers sidebar HTML)
  - `tests/test_export_enrich.py` (scroll-spy test assertions)

  CSS active-link colour rule (the `color-mix` brighter-text rule
  added in 0.6.36) removed from `streamtex/static/css/stx_global.css`.

  One-shot E2E probe scripts removed from `tests/e2e/` (those were
  one-off validation runs tied to the reverted behaviour).

### Preserved (intentionally kept from 0.6.35)
- `3e8d6a7` — ordered-list counter rescue (CSS re-emission +
  DOMPurify escape in `marker_runtime.py`).
- `0d07d40` — `.stx-zoom` centering fix (`align-items: stretch`
  + `width: 100%` in `stx_global.css`).

These two addressed real bugs (counter rendering on long decks;
centering loss on wide viewports) and are unrelated to the
highlight regression.

## [0.6.40] — 2026-05-13

### Fixed
- **Highlight still missing after two-click navigation, where 0.6.39
  was insufficient.** User reported that even with the no-clear-on-
  null fix, two consecutive floating-arrow clicks (or arrow-key
  presses) still left the highlight permanently missing.

  Deeper root cause: in paginated mode, the floating-arrow widget
  in `marker.py` calls `_stxMarkerGoToPage` → `navigateToPage` in
  `book.py`, which has a `if (navigating) return` re-entry guard.
  Click #2 is silently dropped while click #1's Streamlit rerun is
  in-flight, but `marker.py` has already advanced its internal
  `currentIdx`. The MutationObserver in `stx_scroll_spy.js` fires
  during the rerun, but the cadence of `childList` events can
  settle (in some browsers / network conditions) WITHOUT a final
  mutation after the page becomes stable — so the last
  `fireRecompute()` call runs against a half-rendered DOM, returns
  `null`, and 0.6.39 correctly does not clear, but no later
  mutation re-triggers a fire against the now-stable DOM either.

  Fix: post-navigation safety net. Every click on the host body
  and every Page/Arrow/Home/End/Space keydown on the host window
  schedules three additional `scheduleRecompute` calls at
  +500/+1500/+3000 ms. Each is throttled and idempotent — if the
  state is already correct (the normal case), the extra fires are
  no-ops. If the MutationObserver cadence settled prematurely,
  these guarantee a recompute against the stable post-rerun DOM.

  Cost: at most three extra `setTimeout` + `setActive` invocations
  per interaction. No new dependencies, no behaviour change for
  scroll-only interactions.

## [0.6.39] — 2026-05-13

### Fixed
- **Highlight disappeared after floating-arrow / keyboard-arrow
  navigation (regression from 0.6.37).** A user reported that after
  clicking a floating navigation arrow or pressing ArrowRight /
  PageDown, the active indicator (bar + brighter text) would
  disappear and not return — and that two rapid clicks made the
  highlight never reappear at all.

  Root cause: 0.6.37 made `setActive()` the sole writer of
  `.stx-nav-active` and called it *unconditionally* on every
  recompute, including when `findClosestAnchor()` returned `null`.
  During a paginated navigation rerun there is a brief window where
  the old page's target headings have been removed but the new
  page's headings are not yet in the DOM — `findClosestAnchor()`
  returns `null` and `setActive(null)` strips every highlight. If
  no further mutation arrives at the right moment (Streamlit can
  settle without emitting a final childList change after a
  paginated rerun in some timing patterns), the highlight stays
  cleared. Two clicks compound the problem because click #2 lands
  mid-rerun from click #1.

  Fix: `fireRecompute()` now only calls `setActive()` when
  `findClosestAnchor()` returns a non-null value. The "same anchor
  → different DOM node after reconciliation" case is still handled
  because `setActive(a)` strips the class from non-matching entries
  as it adds it to the matching one (the original purpose of the
  0.6.37 unconditional-call change). Null results — only ever
  transient in practice — leave the existing highlight in place,
  and the next mutation that produces a valid anchor replaces it.

  Validated with the existing instability / nav-matrix probes plus
  a new `_arrow_burst_probe.py` that fires two consecutive arrow
  clicks 200 ms apart and samples state every 50 ms.

## [0.6.38] — 2026-05-13

### Added
- **Scroll-spy class-strip safety net.** The `MutationObserver` in
  `stx_scroll_spy.js` now also watches `class` attribute mutations
  (in addition to `childList`) and routes them through the same
  throttled `scheduleRecompute` path. This closes the only remaining
  theoretical regression window from 0.6.37: if anything were to
  strip `.stx-nav-active` via a pure attribute mutation with no
  surrounding DOM change, the recompute would still fire and the
  single-writer `setActive()` would re-apply the class within
  ~100 ms. In practice Streamlit reconciles by node replacement
  (childList), so this is belt-and-braces — but it is purely
  additive: the safety net cannot cause class flapping because
  `setActive()` reads current state before writing.
- **Navigation-matrix E2E probe** (`tests/e2e/_nav_matrix_probe.py`)
  exercises 5 paths not covered by `_instability_probe.py`:
  TOC↔Markers tab swap, URL hash navigation (validates the
  `hashchange` listener added in 0.6.37), search-filter activation
  while highlight is set, mid-navigation tab swap (PageDown twice
  then immediate tab switch), and direct class strip via JS
  (regression test for the new safety net). All assertions pass on
  the FC deck at 1920×1080.

### Notes
- Audit of all changes since 0.6.34 was completed. The
  attribute-observation safety net is the only addition; no
  behaviour was modified or removed.

## [0.6.37] — 2026-05-13

### Fixed
- **Active TOC/Markers indicator was unstable across navigation modes.**
  After 0.6.36 made the scroll-spy follow paginated navigation, three
  remaining failure modes surfaced in real use:
  1. After a PageDown / floating-arrow / marker click, the
     `.stx-nav-active` class sometimes stayed on the **previous**
     entry's DOM node for 200-500 ms. Streamlit reconciliation
     reuses the outer `<div data-stx-block>` node but flips its
     inner `<a href>` between a content anchor and the page-nav
     `#stx-goto-N` anchor depending on which page is current —
     so the class persists on a node whose anchor *value* has just
     shifted, while the previous *content-anchor* no longer maps to
     any DOM entry.
  2. The recompute debounce (250 ms after last mutation, 750 ms
     hard cap) could be postponed indefinitely if Streamlit emitted
     a trailing stream of mutations after a rerun (lazy components,
     async images). The user's "highlight never reappears after a
     double-PageDown" bug.
  3. `findClosestAnchor` ranked the hidden `#stx-goto-N` navigation
     buttons alongside real content markers. Those buttons sit at
     a degenerate document-flow position (absolute, `left:-9999px`,
     `top:auto`), so their `getBoundingClientRect().top` polluted
     the closest-anchor pick on certain pages.
  
  Three coordinated fixes in `stx_scroll_spy.js`:
  - `findClosestAnchor` now skips any anchor starting with
    `stx-goto-` — only real content anchors compete.
  - `setActive` is the **sole writer** of `.stx-nav-active` (add +
    remove). On every recompute we call `setActive(findClosestAnchor())`
    unconditionally — never gated on
    `anchor !== currentActiveAnchor`. `setActive(null)` clears every
    active class (with a strict null guard so empty entries stay
    inactive).
  - The previous debounce-with-cap was replaced by a **throttle**:
    `scheduleRecompute` fires at most once every 100 ms and
    **always** fires within 100 ms of any pending signal. So even
    if Streamlit emits mutations continuously for several seconds,
    the active entry converges within 100 ms of the DOM
    stabilising. Validated on the FC deck at 1920×1080: single
    PageDown settles in 150 ms (was 500 ms), double PageDown in
    100 ms (was 500 ms + risk of never), 5-rapid-PageDown burst in
    100 ms after the last keypress.
  
  Test contract updated:
  `test_scroll_spy_recomputes_on_content_change` replaces the
  former `test_scroll_spy_reapplies_class_on_reconciliation` — the
  observer no longer watches `class` attribute mutations because
  the single-source-of-truth `setActive` path handles both add and
  remove on every recompute.

## [0.6.36] — 2026-05-13

### Fixed
- **TOC/Markers sidebar: multiple entries appeared highlighted instead of
  the single active one.** When paginated decks displayed several markers
  or TOC entries pointing to the same Streamlit page, all of them
  received an inline `color:var(--stx-link-active-color)` style — every
  entry on the current page looked identically "highlighted". On top of
  that, the cross-context scroll-spy's 3 px `::before` accent bar (the
  signal for the *single* active entry) was being clipped away in live
  context by the same `overflow:hidden` quirk that 0.6.33 had already
  fixed on the export side. Net visible result: clicking marker N
  highlighted markers N through N+k (k = number of other markers on the
  same page), with no way to identify the truly active one.
  
  Three coordinated fixes, on `fix/single-active-toc-marker-entry`:
  - `book.py` (live, paginated and search-enabled paths for TOC + Markers):
    drop the `style="color:var(--stx-link-active-color)"` from current-page
    anchors. The cross-context scroll-spy is now the **single source of
    truth** for which entry is active.
  - `book.py` (same four paths): wrap the entry content in an inner
    `<span style="display:block; overflow:hidden; text-overflow:ellipsis;
    white-space:nowrap;">` so the outer `[data-stx-block]` no longer
    clips its `::before` bar (mirrors the 0.6.33 export fix).
  - `stx_global.css`: add the brighter active-link colour for live —
    `[data-stx-block].stx-nav-active a { color: color-mix(…65%, white) }`
    — that the export side already had since 0.6.34. The `!important`
    keeps it winning over any Streamlit per-page coloring that might
    reappear in future releases.

- **Scroll-spy didn't follow Streamlit paginated navigation.** The
  cross-context scroll-spy listened for `scroll` events to recompute the
  closest anchor. But Streamlit's paginated mode (PageDown / banner /
  TOC page-link click) tears down the main content and rebuilds it —
  there is no `scroll` event. The previously-active entry stayed
  highlighted forever, even after the user moved to a different slide.
  
  Fix in `stx_scroll_spy.js`: also recompute on `hashchange` (Streamlit
  updates the URL to `#stx-goto-N` on page change), and let the existing
  MutationObserver trigger a debounced recompute whenever the main DOM
  is rebuilt (`childList` mutations). Validated end-to-end on the real
  FC deck at 1920×1080: 10 consecutive PageDowns each correctly move
  the active entry to the new slide's marker (Bloc 2 → "2. Problem
  statement", Bloc 3 → "3 A Historic Moment", …).

## [0.6.35] — 2026-05-13

### Fixed
- **Ordered-list counters rendering as `0.` on long decks (FC "Fifteen
  Propositions" regression).** Two independent issues conspired in
  `inject_marker_runtime` to drop the global stylesheet between reruns:
  - The shipped `stx_global.css` references literal `<style>` /
    `</style>` substrings inside documentation comments. Streamlit's
    `st.html` pipeline runs DOMPurify on the payload, which treats those
    substrings as a forbidden nested style tag and rejects the entire
    injection. We now escape those two tokens with a single invisible
    whitespace before injection — the CSS parser ignores the whitespace
    inside `/* … */` but the DOMPurify tag-open lexer no longer fires.
  - `inject_marker_runtime` was gated by a single `_SESSION_KEY` flag,
    so CSS *and* observer registration both fired only on the first
    rerun. Streamlit reconciliation then removed the resulting `<style>`
    element on every subsequent rerun (no corresponding call from the
    new run), and `counter-reset` / `counter-increment` rules silently
    disappeared. The gate is now split: CSS is re-emitted on every
    `inject_marker_runtime` call (Streamlit reconciles identical
    payloads in place), while the `st.components.v2.component`
    registration still fires once per session — re-registering would
    log `Component … is already registered` warnings. The observer's
    self-installed `window.__stxMarkerObsHandle` survives reconciliation
    of the component host, so single-shot registration remains
    sufficient.
- **Centered titles wrapped in `st_zoom` rendered left-aligned on wide
  viewports.** Pre-existing CSS rule
  `.stx-zoom > [data-testid="stElementContainer"] { width: auto; }` was
  intended to delegate cross-axis sizing to the flex parent (the
  `.stx-grid` rule uses the same pattern). But `.stx-zoom` was missing
  the matching `align-items: stretch`, so when Streamlit's default
  `align-items` on `stVerticalBlock` resolved to a non-stretch value the
  rule collapsed to *shrink-to-fit* and the element ended up narrower
  than its parent. Combined with `text-align: center` on the surrounding
  block, the title then appeared inside a narrower frame anchored at the
  left of its parent — visually centered when the text wrapped to two
  lines, visually left-aligned when the viewport was wide enough to keep
  the text on one line. The previous `inject_marker_runtime` bug
  (CSS-stripped-on-rerun) hid this regression because the rule itself
  disappeared along with the rest of the global stylesheet on every
  rerun; now that the stylesheet survives, the asymmetry between
  `.stx-grid` and `.stx-zoom` is no longer masked. We add the same
  `align-items: stretch !important` to `.stx-zoom` that `.stx-grid`
  already had, and change `width: auto` to `width: 100%` so the
  intent — "child fills the zoom container" — is explicit regardless of
  flex defaults.

### Changed
- **CE lifecycle refonte (cross-repo, see `streamtex-claude` branch `feat/ce-lifecycle-incremental`)**.
  The CE cycle now supports iterative and incremental production: a cycle can
  cover the full document or a single increment (part, section, blocks). A new
  PROTOTYPE phase sits between PLAN and PRODUCE to validate styles by example
  and capture reusable graphic patterns. Project state is driven by a living
  master plan (`docs/master-plan.yaml` pilotage + `docs/master-plan.md`
  contenu détaillé), versioned via paired snapshots in
  `docs/master-plan/archive/`. All user interactions are unified QCMs with a
  recommended default plus `Discutons-en` and `Autre` escapes; the producer
  profile `dialog_level` field (`minimal` / `guided` / `exhaustive`) modulates
  frequency. The pattern catalog now has three explicit levels: draft, local
  (`.claude/custom/streamtex-patterns/`), shared (`streamtex-patterns` repo).
  The library itself is unchanged — all changes are in the Claude profile and
  the documentation manuals. See
  `documentation/maintenance/CE/plan_ce_lifecycle_incremental.md` and
  `documentation/maintenance/CE/scenario_e2e.md`.

## [0.6.34] — 2026-05-13

### Added
- **Static export: brighter cyan text on the active TOC entry.**  The
  3 px ``::before`` bar introduced in 0.6.31 (and unclipped in 0.6.33)
  was correct but too subtle on its own.  The active entry's ``<a>``
  text now uses ``color-mix(in srgb, var(--stx-export-link) 65%,
  white)`` so it shifts visibly lighter than its neighbours — same
  read as the live Streamlit sidebar where the current-page entries
  switch to ``--stx-link-active-color``.  No separate theme variable
  required; the brighter shade is derived at render time from the
  project's ``theme.linkColor``.

  Verified via Playwright: active entry text computes to
  ``srgb(0.52, 0.78, 0.99)`` vs inactive ``rgb(67, 169, 251)`` =
  ``(0.26, 0.66, 0.98)`` — clearly distinct.

  Falls through to ``--stx-export-link`` on browsers without
  ``color-mix()`` (Safari < 16.2 / Chrome < 111).

  Regression test added in
  ``test_export_enrich.py::TestSidebarCssVars::test_active_entry_text_uses_brighter_link_color``.

## [0.6.33] — 2026-05-13

### Fixed
- **Static export: active TOC entry indicator was invisible.**  The
  cyan ``::before`` bar introduced in 0.6.31 and driven by the
  cross-context scroll-spy in 0.6.32 lived at ``left: -8px`` from the
  entry box.  But ``.stx-toc-entry`` itself carried ``overflow:
  hidden`` (for text-ellipsis truncation), and browsers clip
  ``position: absolute`` descendants at the element's overflow box —
  so the bar was entirely clipped away in the static export.  Live
  Streamlit users didn't notice because the live sidebar also
  highlights the current page via ``--stx-link-active-color`` on the
  ``<a>`` (an independent per-page mechanism), which masked the
  invisible bar.

  Fix: move ``overflow: hidden; text-overflow: ellipsis; white-space:
  nowrap`` from ``.stx-toc-entry`` down to the inner ``.stx-toc-entry
  a`` (now ``display: block``).  The entry no longer clips, the
  ``::before`` bar renders correctly, and text-ellipsis still works
  because the ``<a>`` is the element that actually wraps the text.

  Regression test added in
  ``test_export_enrich.py::TestSidebarCssVars::test_toc_entry_does_not_clip_active_indicator``.

## [0.6.32] — 2026-05-13

### Added
- **Cross-context scroll-spy for TOC / Markers navigation.**  A new
  unified JavaScript module (``streamtex/static/js/stx_scroll_spy.js``)
  drives the cyan active-entry indicator across all three contexts the
  reader can encounter:

  1. Live Streamlit + sidebar tab "TOC"
  2. Live Streamlit + sidebar tab "Markers"
  3. Static HTML export sidebar

  All three contexts already share the ``[data-stx-block]`` attribute on
  each navigation entry, which makes a single data-driven module
  possible.  Behaviour:

  - Clicking any entry (any depth, not just L1) marks it active
    immediately and suppresses the scroll handler for 400 ms so the
    smooth-scroll animation doesn't bounce the active state away.
  - On scroll, the entry whose anchor target is closest to (but at or
    above) ~120 px from the viewport top wins.  At the very top of the
    document the first anchor below the line wins.

  Robustness: ``window.__stxScrollSpy`` guard prevents double-mount on
  Streamlit reruns, and a ``MutationObserver`` re-applies the active
  class if Streamlit's reconciliation strips it.

### Changed
- **Renamed CSS class ``.stx-toc-active`` → ``.stx-nav-active``.**  The
  active-entry indicator is no longer TOC-specific — it covers TOC,
  Markers, and export in one rule.  The selector lives in
  ``streamtex/static/css/stx_global.css`` (so live mode gets it via the
  marker-observer injection) and is mirrored in the export sidebar CSS
  for static exports.
- ``_MARKER_NAV_JS.updateUI()`` no longer touches the sidebar's active
  class — scroll-spy now owns this responsibility across all contexts,
  removing the previous coupling between the marker-navigation runtime
  and the sidebar's visual state.

## [0.6.31] — 2026-05-13

### Added
- **Resizable sidebar in the static HTML export.**  A drag handle on
  the sidebar's right edge lets the reader pick any width between
  180px and 50% of the viewport.  The main content's ``margin-left``
  shares the same ``--stx-sidebar-width`` CSS variable, so the content
  area reflows in real time with the same "respiration" effect the
  open/close toggle already produces.  Double-clicking the handle
  resets to the 280px default.  The chosen width is persisted in
  ``localStorage`` and restored on subsequent page loads.

  Accessibility: the handle is keyboard-focusable
  (``role="separator"`` + ``tabindex="0"``) and reacts to
  ``ArrowLeft`` / ``ArrowRight`` (Shift = ×5 step).  Touch + pen
  inputs work via pointer events.  Mobile (≤768px viewport) keeps the
  existing slide-in toggle behaviour and disables resize.

  Implementation: new ``_SIDEBAR_RESIZE_JS`` block wired in
  ``enrich_export_html`` alongside ``_SIDEBAR_TOGGLE_JS``; both share
  the same ``--stx-sidebar-width`` variable so toggling and resizing
  stay in lockstep.

### Changed
- **TOC entries are no longer bolded.**  Previously the L1 level had
  ``font-weight: 600`` and the active entry had ``font-weight: 700``.
  Per user request the entries now render at the default weight; the
  active entry is marked by a subtle left-border (``::before``
  pseudo-element in ``var(--stx-export-link)``) instead of a heavier
  font weight, so the typography stays uniform.

## [0.6.30] — 2026-05-13

### Fixed
- **Static HTML export: TOC entries appeared in white text instead of
  the project's ``linkColor`` (follow-up to 0.6.29).**  0.6.29 aligned
  the sidebar background with the project theme but left the TOC
  entries themselves as ``color: inherit; text-decoration: none`` —
  i.e. plain text in the project's ``textColor``.  On a dark theme
  this produced bold-white labels, while the live Streamlit sidebar
  renders them as underlined hyperlinks in ``linkColor``
  (``#43A9FB`` by default in dark mode).

  ``_SIDEBAR_CSS`` now styles ``.stx-toc-entry a`` as a real hyperlink:
  ``color: var(--stx-export-link, …); text-decoration: underline``.  The
  active-entry marker keeps ``font-weight: 700`` for visual distinction.

  The CSS variable previously named ``--stx-export-link-active`` is
  renamed to ``--stx-export-link`` since it represents the project's
  link colour, not an "active" state.  Internal-only, no public API
  change.

### Changed
- **Commented out the ``[DIAG:LOAD]`` / ``[DIAG:APPLY]`` console logs**
  in ``streamtex/image_editor.py`` and ``streamtex/image.py``.  These
  were diagnostic ``logger.warning`` calls that surfaced in every
  project's console output (one per image-editor mount).  Lines are
  preserved as comments so they can be re-enabled by uncommenting
  during future debugging.

## [0.6.29] — 2026-05-13

### Changed
- **Static HTML export sidebar now follows the project's theme instead
  of the reader's OS preference.**  Previously, ``export_enrich.py``
  baked a light palette into the sidebar CSS with an ``@media
  (prefers-color-scheme: dark)`` block that swapped to a hardcoded dark
  palette (``#1a1a2e`` background, ``#42D0F3`` active link, …) based on
  the reader's operating system.  The live Streamlit app, in contrast,
  picks up the project's ``.streamlit/config.toml`` ``[theme]`` block
  — meaning the static export and the live app could diverge on the
  same machine, and an author's dark-themed project would render light
  on a reader with a Light OS preference.

  ``_SIDEBAR_CSS`` is refactored to resolve every theme-sensitive
  value through CSS custom properties (``var(--stx-export-sidebar-bg)``,
  ``var(--stx-export-sidebar-fg)``, ``var(--stx-export-link-active)``,
  …).  A new ``_build_theme_vars_css()`` emits a ``:root`` block at
  the top of the injected CSS that reads those values via
  ``_get_theme_color`` (already used by ``generate_full_html`` for the
  main content area), so the project's ``.streamlit/config.toml`` is
  now the single source of truth for both live and static rendering.

  Fallbacks for projects that declare only ``base = "dark"`` without
  per-key overrides are encoded in ``_get_theme_color``'s
  ``_dark_defaults``: ``secondaryBackgroundColor = "#1C1E1F"`` (the
  sidebar background) and ``linkColor = "#43A9FB"`` (links) — the
  exact values Streamlit 1.56's frontend computes at runtime.

  No public API change.  Projects that customise ``[theme]``
  ``secondaryBackgroundColor`` / ``textColor`` / ``linkColor`` see their
  values flow into the exported sidebar automatically; projects that
  declare only ``base = "dark"`` get the Streamlit defaults baked in
  rather than the previous hardcoded violet-dark palette.

### Added
- ``tests/test_export_enrich.py`` — 15 tests covering the extended
  dark defaults in ``_get_theme_color``, the ``:root`` block emission
  in ``_build_theme_vars_css``, the ``var()`` usage in ``_SIDEBAR_CSS``
  (with explicit assertions that the previous hardcoded dark palette
  and ``prefers-color-scheme`` overrides are gone), and the full
  ``enrich_export_html`` integration with both light and dark base.

### Notes
- The marker navigation bar (floating bottom bar in paginated mode)
  is intentionally left out of this change — its colours are a separate
  concern that does not affect the sidebar bug reported here.  A
  follow-up can apply the same ``var()`` treatment if desired.

## [0.6.28] — 2026-05-12

### Fixed
- **First list-item invisible on first render after cache clear (pre-existing
  bug, several versions old).**  On the FC-260507-NG-SLIDES "Operational, Not
  Theoretical — The Luxembourg Framework" slide, the first bullet
  ("Supervisory authority — ILR …") showed the bullet character but no
  text on the very first ``streamlit run`` after wiping ``.stx_cache``.
  A browser force-reload made the missing text reappear.

  Root cause was a Streamlit first-paint reconciliation race that
  briefly co-located the list-item ``<span class="stx-marker">`` inside
  the stElementContainer that ultimately hosts the user content.  At
  that transient instant the canonical ``EC > stHtml > span.stx-marker``
  structure was indistinguishable from a real marker cell, so
  ``hideMarkerCell`` correctly stamped ``display: none !important`` on
  it.  Streamlit then reconciled the EC's children to the user's
  ``st_write`` output while also stripping the ``stx-marker-cell`` class
  — leaving an EC that no longer hosted a marker, no longer carried the
  class, yet remained ``display: none``.  Subsequent items were not
  affected because Streamlit's delta rhythm stabilises after the first
  item; the visible effect was strictly first-item-only and strictly
  first-render-only.

  The fix in ``streamtex/static/js/stx_marker_observer.js`` is twofold:

  1. ``hideMarkerCell`` now resolves the cell through the strict
     structural relation ``EC > stHtml > span.stx-marker``, never via
     ``markerSpan.closest(EC_SEL)``.  When the markerSpan is co-located
     with non-marker siblings (mixed stHtml children) or the EC carries
     more than one child element, ``hideMarkerCell`` bails out cleanly;
     the observer fires again as soon as Streamlit moves the marker to
     its proper cell.

  2. A new ``hiddenECs`` ``Set`` tracks every EC ``hideMarkerCell`` has
     stamped, and the new ``auditMarkerCells()`` runs after any batch
     that detached a marker.  It walks the tracking set (not
     ``.stx-marker-cell`` — Streamlit reconciliation may have stripped
     the class) and restores any EC that no longer hosts a marker by
     stripping the lingering class and the inline ``display: none
     !important``.

  Reproduced and pinned by ``tests/e2e/test_first_item_invisible_fc.py``
  against the real FC deck (auto-skipped on machines without the
  project).  All 1976 unit tests pass and the
  ``test_paginated_bleedthrough_fc.py`` e2e still reports zero bleeds,
  confirming no regression on the 0.6.27 fix.

### Added
- ``test_js_hide_marker_cell_has_structural_guards`` in
  ``tests/test_marker_runtime.py`` — pins the parent → grandparent
  resolution and asserts ``.closest()`` is no longer used inside
  ``hideMarkerCell``.
- ``test_js_observer_auto_heals_stranded_marker_cells`` — asserts the
  ``hiddenECs`` tracking + ``auditMarkerCells`` contract.

### Notes
- No public Python API change.  All other invariants from 0.6.21–0.6.27
  (cache-build freeze, paginated bleed-through, attribute-strip
  recovery, KIND_SPECS single source) remain intact.

## [0.6.27] — 2026-05-12

### Fixed
- **Paginated marker bleed-through: stale inline-styles from a previous
  slide survived navigation and skewed the next slide's layout.**  When
  Streamlit paginated navigation unmounted a slide, the marker
  ``<span class="stx-marker">`` was removed from the DOM but the parent
  ``[data-testid="stVerticalBlock"]`` that ``applyMarker`` had decorated
  retained its ``stx-{kind}`` class, ``data-stx-{kind}-uid`` attribute,
  CSS custom properties and inline ``grid-template-columns`` / ``zoom``
  / ``display:flex`` / etc.  If React reused that DOM element for a
  different construct on the next slide, the new slide inherited the
  previous slide's layout — visible on FC-260507-NG-SLIDES as a "mix-up
  between zoom and cells" when the user navigated forward then back
  (screenshots provided by the user).

  The fix introduces ``clearMarker`` in
  ``streamtex/static/js/stx_marker_observer.js`` — the inverse of
  ``applyMarker``.  ``handleBatch`` now consumes ``MutationRecord.
  removedNodes`` in addition to ``addedNodes``, and on every removed
  marker span ``clearMarker`` strips the class, the uid attribute, every
  CSS custom property forwarded from the marker's ``data-stx-*`` attrs,
  and the inline layout properties (``grid-template-columns``, ``zoom``,
  etc.) listed in ``INLINE_PROPS_BY_KIND``.  A "marker with same uid is
  still attached?" guard makes the operation idempotent under React
  move-style reconciliation (remove + re-add in one batch leaves state
  untouched).

  Reproduced and pinned by ``tests/e2e/test_paginated_bleedthrough.py``
  (synthetic 3-slide fixture, fast) and
  ``tests/e2e/test_paginated_bleedthrough_fc.py`` (real-world deck —
  auto-skipped on machines that don't have the FC project at the fixed
  Dropbox path).  Pre-fix the FC test reported bleed on 8 of 9 slides;
  post-fix it reports zero.

### Changed
- **Marker observer refactored around a ``KIND_SPECS`` single source of
  truth.**  Previously, per-kind behavior was scattered in three places
  inside ``stx_marker_observer.js``: ``KIND_TO_CLASS`` (class to add),
  ``INLINE_PROPS_BY_KIND`` (props to strip), and inline ``if (kind ===
  '…') { setInlineImportant(parent, '…', …) }`` branches in
  ``applyMarker`` (props to write).  Three lists to keep synchronised
  meant three drift opportunities — exactly the kind of fragility that
  introduced the bleed-through bug above.

  The refactor lifts all three into a single per-kind ``KIND_SPECS``
  table declaring ``{ cls, inlineStyles(span), booleanModifiers }``.
  ``applyMarker`` writes from the spec; ``clearMarker`` reads the SAME
  spec to discover which property KEYS to strip.  Adding a new kind, or
  a new inline property on an existing kind, only requires editing the
  spec entry — both code paths pick it up automatically, so drift is
  impossible by construction.

  Two contract tests pin the design:
  - ``test_js_observer_uses_kind_specs_single_source_of_truth`` — the
    spec table exists, has every known kind, and both ``spec.cls`` /
    ``spec.inlineStyles`` / ``spec.booleanModifiers`` appear in the
    consumer code.
  - ``test_js_apply_marker_writes_no_inline_style_outside_spec`` —
    scans for ``setInlineImportant(parent, '<literal>', …)`` calls and
    asserts there are zero.  A future refactor that bypasses the spec
    fails this check immediately rather than introducing a silent
    bleed-through regression.

  No public Python API change; no runtime behavior change (the
  ``test_paginated_bleedthrough_fc.py`` e2e still reports 0/9 bleeds).

### Added
- ``test_js_observer_clears_marker_state_on_removal`` in
  ``tests/test_marker_runtime.py`` — asserts ``clearMarker`` is wired
  into the batch handler and reverses every state change.
- ``test_js_observer_uses_kind_specs_single_source_of_truth`` and
  ``test_js_apply_marker_writes_no_inline_style_outside_spec`` — the
  two contract tests described above.

### Notes
- No public Python API change.  The 0.6.26 surgical mutation handling
  is preserved, the 0.6.21–0.6.24 attribute-strip-recovery invariants
  remain exercised by ``test_marker_observer_regression.py``, and the
  cache-build freeze regression test still passes.

## [0.6.26] — 2026-05-12

### Fixed
- **Chrome cache-build freeze on decks of ~40+ blocks (regression introduced
  by the 0.6.21–0.6.24 layout fixes).**  Two root causes addressed.

  1. **`stx_marker_observer.js` — surgical mutation handling.**  The
     `MutationObserver` callback previously schedules a full
     `document.querySelectorAll('span.stx-marker')` walk on every batch of
     mutations, then re-applies every marker.  During the paginated cache
     build of a 60-block deck this produced ~780 000 mutations and ~1 100
     full-document scans, saturating Chrome's main thread for tens of
     seconds (Firefox/Safari coped thanks to lighter MutationObserver +
     more aggressive rAF batching).  The handler now consumes
     `MutationRecord.addedNodes` (for new markers) and the specific
     parent `stVerticalBlock` whose `class` / `style` / `data-stx-*-uid`
     was reconciled (re-applies that marker only), dedup'd via `Set`.
     Bootstrap initial pass is unchanged.  The 0.6.21–0.6.24 invariants
     (attribute-strip recovery, idempotent re-apply) remain exercised by
     `tests/e2e/test_marker_observer_regression.py`.

  2. **`_build_page_cache` — suppress DOM emit during the hidden render.**
     The Tier-3 cache rebuild runs all blocks inside `st.empty().container()`
     that is immediately `.empty()`-cleared once TOC, marker registry,
     search index, and export buffer have been populated server-side.  The
     intermediate DOM still travelled over the WebSocket and was reconciled
     by React (per-instance attribute-selector `<style>` blocks parsed,
     marker spans inserted) before being discarded, blocking the
     `remove_loading_overlay()` iframe at the tail of the run.  A new
     context manager `_suppress_cache_build_dom` monkey-patches the
     DOM-emitting streamlit primitives (`st.html`, `st.markdown`,
     `st.write`, `st.text`, `st.code`, `st.caption`, `st.header`,
     `st.subheader`, `st.title`, `st.divider`) to no-ops for the span of
     the cache-build loop.  `st.container` and `st.iframe` are preserved
     — the former because the with-statement structure of streamtex
     primitives depends on it, the latter because
     `update_loading_progress()` re-emits a progress iframe between
     blocks.  Python-side state (TOC entries, marker registry, search
     index, export buffer) is populated *before* the primitives emit and
     is therefore unaffected.

  Combined measurement on a 60-block synthetic fixture matching the
  FC-260507-NG-SLIDES profile (`tests/e2e/test_cache_build_freeze.py`):
  cold-load cache-build window 60+ s → 0.85 s (≈70 × speed-up); observer
  mutations 782 499 → 409; full-document marker scans 1 088 → 1 (bootstrap
  only); long-task total 57 338 ms → 327 ms.

### Added
- `tests/e2e/test_cache_build_freeze.py` + fixture under
  `tests/e2e/fixtures/cache_build_freeze_app/`: a Playwright regression
  guarding the cold-load wall-clock window and the
  `marker-scan` count on Chromium for a 60-block paginated deck.
- `tests/test_marker_runtime.py::TestStaticAssets::test_js_observer_coalesces_via_animation_frame`
  updated to assert the new `pendingBatch` / `pendingScheduled`
  coalescing tokens (intent unchanged: many mutations must collapse into
  one animation-frame-debounced handler).

### Notes
- No public Python API change; no removal.  The behavioural envelope of
  the 0.6.21–0.6.24 layout fixes is preserved — the existing
  `test_marker_observer_regression.py` Playwright tests continue to pass
  unchanged, ensuring attribute-strip recovery and Streamlit-1.56+
  `display:flex` overrides still survive reconciliation.

## [0.6.25] — 2026-05-12

### Changed
- **Chrome recommendation banner: off by default in `st_book`.**  The
  banner was introduced when streamtex relied on CSS `:has()` selectors,
  which caused a 3–4 s freeze on Chrome cold load and were unsupported in
  Firefox until v121 (2023-12).  The marker-runtime migration (0.6.11 →
  0.6.16) eliminated both issues: `:has()` is no longer used, and the new
  MutationObserver-based path is universally supported.  At this point
  Chrome no longer offers a meaningful advantage for streamtex content,
  so `st_book(chrome_banner=False)` is now the default.  The
  `st_chrome_banner()` helper remains exported for users who want to opt
  back in explicitly.  See `streamtex/browser.py` docstring for the full
  rationale.

## [0.6.24] — 2026-05-12

### Fixed
- **Sidebar settings sliders (zoom / page_width) wiped per-instance
  backgrounds and borders.**  When the user moved a sliders in the
  paginated-mode settings panel, Streamlit's reconciliation stripped our
  `class`, `data-stx-*-uid`, and inline `style` from existing
  `stVerticalBlock` elements *without adding or removing any children*.
  The marker observer was watching `childList` only, so it never saw the
  strip and never re-applied — per-instance CSS rules (which target
  `[data-stx-block-uid="…"]`) no longer matched anything → cells lost
  their backgrounds and borders even though the markers themselves were
  still in the DOM.

  Fix:
  - MutationObserver now also watches `attributes` (filtered to
    `class`, `style`, and each `data-stx-*-uid`).  Any mutation
    schedules a debounced full scan on the next animation frame.
  - `applyMarker` is now fully idempotent: every write (`classList.add`,
    `setProperty`, `setAttribute`) is guarded by a read so that
    re-running on an already-applied marker fires **zero** mutations —
    this is what stops the attribute-watching observer from looping on
    itself.
  - A new helper `setInlineImportant(el, prop, value)` makes the no-op
    guard for `!important` inline styles a one-liner.

## [0.6.23] — 2026-05-12

### Fixed
- **Marker cell stayed visible on Streamlit 1.56+.** The observer used
  `markerSpan.closest('.element-container')` to find the cell containing
  the sentinel, but Streamlit ≥ 1.56 renamed that class to
  `stElementContainer` (only the testid is reliable across versions).  The
  selector now matches both:
  `[data-testid="stElementContainer"], .element-container`.  Symptom: in a
  2-column `.stx-grid`, the invisible marker cell took grid slot #1 and
  shifted every subsequent cell by one (e.g. the FC deck's "Three
  Frameworks" slide rendered GDPR in the top-right slot instead of
  top-left).
- **Marker cell now hidden inline with `!important`** in addition to the
  CSS class — bulletproof against any future cascade surprise.
- **Settings change (sidebar width/zoom) wiped grid layout.**  The observer
  used a one-shot `data-stx-processed` attribute on each marker to avoid
  reprocessing.  Streamlit's reconciliation can replace the parent
  `stVerticalBlock` on rerun *while reusing the marker* — leaving the new
  parent without the `.stx-grid` class or inline layout styles, and the
  observer silently skipping it.  The observer now drops the one-shot gate
  and re-validates on every pass; `applyMarker` is fully idempotent thanks
  to a `parent.classList.contains(cls)` fast-path that only runs the
  expensive work when the parent state was wiped.

## [0.6.22] — 2026-05-12

### Fixed
- **Marker observer: inline-style fallback for layout-critical declarations.**
  Streamlit 1.56+ applies `display: flex; flex-direction: column` on every
  `[data-testid="stVerticalBlock"]` via an inline style (or a `!important`
  rule loaded after our stylesheet, depending on the build), which beat the
  global stylesheet even with `!important`.  The MutationObserver now sets
  the layout-critical properties **directly on the element** with the
  `!important` flag via `element.style.setProperty(prop, value, 'important')`.
  This guarantees correct layout regardless of CSS cascade or stylesheet
  load order:

  | Marker kind | Inline properties applied                                       |
  |-------------|-----------------------------------------------------------------|
  | `grid`      | `display: grid`, `grid-template-columns`, `gap`, `align-items`  |
  | `span`      | `display: flex`, `flex-direction: row`, `white-space: pre`      |
  | `list-item` | `display: flex`, `flex-direction: row`, `align-items: baseline` |
  | `zoom`      | `zoom: <factor>`                                                |

  CSS rules are kept as a safety net for browsers/devtools introspection but
  no longer load-bearing for these four kinds.
- Fixes "Three Frameworks — At a Glance" 3-cell grid rendering vertically
  on the FC presentation deck (verified via `slides/STX_DIAG_GRID/`
  diagnostic harness).

## [0.6.21] — 2026-05-12

### Fixed
- **Layout broken on Streamlit ≥ 1.56** — visible regression on the FC presentation deck's "Three Frameworks — At a Glance" slide (and other multi-grid layouts): the 3 boxes collapsed into a vertical stack regardless of the grid template. Root cause traced through the diagnostic project `slides/STX_DIAG_GRID/` to **stale CSS selectors** in `stx_global.css` that targeted the old Streamlit DOM:
  - `.element-container` (Streamlit ≤ 1.55) is now `[data-testid="stElementContainer"]` (Streamlit ≥ 1.56);
  - Streamlit ≥ 1.56 wraps every cell/container in an additional `[data-testid="stLayoutWrapper"]` parent;
  - Streamlit's default `display: flex; flex-direction: column;` on every `stVerticalBlock` overrides our `display: grid` rule unless we use `!important`.
  - The marker observer was always working correctly (verified empirically: `obs=true`, `handle=true`, all marker `data-stx-processed`, `data-stx-{kind}-uid` set). The chain broke at the CSS-to-DOM mapping.

### Changed
- `streamtex/static/css/stx_global.css` — Phase-4 update for Streamlit 1.56+ DOM:
  - Every `.element-container` selector now also matches `[data-testid="stElementContainer"]` (compat with both old and new Streamlit).
  - Every `> [data-testid="stVerticalBlock"]` cell selector now ALSO matches `> [data-testid="stLayoutWrapper"]` (compat with both wrap structures).
  - Display overrides (`display: grid` on `.stx-grid`, `display: flex` on `.stx-span` / `.stx-list-item`, `grid-template-columns` / `gap` on `.stx-grid`) gain `!important` to beat Streamlit's inline cascade.
  - Inner `stLayoutWrapper > stVerticalBlock` is sized to fill its grid slot so per-instance background/padding styles render correctly inside grid cells.
- **`streamtex/marker_runtime.py:inject_marker_runtime()` migrated from `streamlit.components.v1.html` to `st.components.v2.component(name, js=…, isolate_styles=False)`** — the V2 custom-component API (stable, added in 1.56). With `isolate_styles=False`, the observer JS executes **inline in the host page** (no iframe, no shadow DOM) so it has direct access to `document` without `window.parent` indirection. The component is reconciled by Streamlit across reruns (verified in `slides/STX_DIAG_GRID/`), so the `MutationObserver` stays alive throughout the session.
- **`components.v1.html` is no longer used anywhere in the streamtex codebase.** The deprecation debt accepted in 0.6.20 is now cleared, ahead of the 2026-06-01 removal deadline.
- `tests/test_marker_runtime.py` — `test_js_via_components_html` → `test_js_via_v2_component`. Asserts the V2 component is registered with `isolate_styles=False`, the JS payload is wrapped in `export default function`, the wrapped component callable is invoked once. Mock target: `streamtex.marker_runtime.st.components.v2.component`.

### Notes
- All other 0.6.19 migrations from `components.v1.html` → `st.iframe` (17 other call sites) are preserved as-is. They worked correctly because they don't rely on long-lived `MutationObserver`s; only the marker observer needed the special V2 treatment.
- Verified via `slides/STX_DIAG_GRID/` (the diagnostic mini-project shipped with this PR) that `v2-component` reaches `OBSERVER OK` status on all 4 test slides including the "Three Frameworks" replica.
- Public API unchanged. No env var, no signature change. Users on 0.6.20 simply upgrade.

## [0.6.20] — 2026-05-12

### Fixed
- **Marker observer over-tagging and Chrome freeze** introduced by the 0.6.19 `st.iframe` migration of the observer iframe specifically. Symptoms on the FC presentation deck: at 0.6.19 the "Three Frameworks — At a Glance" slide had 1 grid marker un-processed (visible regression — boxes stacked vertically); at a transient never-shipped variant (disconnect-then-reinstall pattern) the same scene generated **47 `.stx-grid` classes** instead of 3 plus a Chrome cold-load freeze. Root cause not fully understood, but empirically the legacy `streamlit.components.v1.html` works reliably for this specific call site whereas `st.iframe` does not.

### Changed
- `streamtex/marker_runtime.py:inject_marker_runtime()` — reverted to `streamlit.components.v1.html(..., height=0)` for the observer JS injection only. The CSS goes via `st.html("<style>…</style>")` unchanged. The Python-side `session_state` guard is kept (so the observer iframe is emitted once per session; Streamlit treats `components.v1.html` as a persistent custom component whose iframe survives reruns and keeps the `MutationObserver` alive).
- `streamtex/static/js/stx_marker_observer.js` — flag-only `hostWin.__stxMarkerObs` idempotency guard restored.
- `tests/test_marker_runtime.py` — `test_js_via_st_iframe` → `test_js_via_components_html` (asserts the `components.html` call path with `height=0`).

### Notes
- **All other 0.6.19 migrations are preserved**: 17 of the 18 original `components.v1.html` call sites remain on `st.iframe`. Only the marker observer (1 site, in `marker_runtime.py`) keeps `components.v1.html`. The `cli/cache_cmd.py` monkey-patch still patches both APIs.
- **Deprecation debt acknowledged**: `streamlit.components.v1.html` is officially deprecated since Streamlit 1.56 with announced removal after 2026-06-01. This release accepts that debt for one specific call site, deferring the root-cause analysis of why `st.iframe` breaks the marker observer specifically (while working fine for 17 other JS-injection call sites in the same release). Investigation continues under `documentation/maintenance/components.v1_issue/`.
- `streamlit>=1.56.0` floor preserved (still required for the other 17 `st.iframe` call sites).

## [0.6.19] — 2026-05-12

### Changed
- **All `streamlit.components.v1.html` calls migrated to `st.iframe`** (added in Streamlit 1.56; the official replacement per the runtime warning "`st.components.v1.html` will be removed after 2026-06-01. Please replace with `st.iframe`."). 18 call sites across `marker_runtime.py`, `marker.py`, `bib_preview.py`, `loading.py` (3), `auth.py`, `browser.py`, `book.py` (5), `mermaid.py`, `plantuml.py`, `latex.py`, `tikz.py`, `export.py`; plus the cache-pre-generation monkey-patch in `cli/cache_cmd.py` now patches both `st.iframe` (the new path) and `streamlit.components.v1.html` (legacy user code) so unmigrated callers stay neutralised.
- **Minimum Streamlit bumped to `>=1.56.0`** in `streamtex/pyproject.toml` — `st.iframe` was added in 1.56. Anyone on 1.54/1.55 must upgrade.
- `st_html(..., scrolling=…)` — `scrolling` kwarg kept in the signature for backwards compat but is now a **no-op**; `st.iframe` has no `scrolling` parameter and uses native iframe scrollbars when content overflows the configured height. Visual verification on Mermaid / PlantUML / LaTeX / TikZ / export is the responsibility of the integrator.
- All previously-tested behaviour preserved: marker observer still injected via iframe → reaches `window.parent.document`, idempotency guard on `hostWin.__stxMarkerObs` unchanged, sentinel-class logic unchanged, all 1.9k tests still pass.

### Notes
- Why not use `st.html(unsafe_allow_javascript=True)` instead — the doc-recommended path? **Verified empirically on Streamlit 1.52 → 1.57 with a 5-probe reproducer** (`documentation/maintenance/components.v1_issue/reproducer/app.py`): `st.html(..., unsafe_allow_javascript=True)` does **not** execute injected JavaScript (neither `<script>` tags nor DOM event handlers `onload`/`onerror`). The proto flag is forwarded by the Python API but the released frontend strips JS regardless. `st.iframe` is the only working JS-execution path as of 2026-05-12.
- Test mocks across 7 test files (`test_marker.py`, `test_marker_runtime.py`, `test_bib_preview.py`, `test_browser.py`, `test_auth.py`, `test_loading.py`, `test_latex.py`, `test_mermaid.py`, `test_plantuml.py`, `test_tikz.py`, `test_export.py`, `test_export_guard.py`) rewired from `streamtex.MODULE.components.html` / `streamlit.components.v1.html` to `streamtex.MODULE.st.iframe`.
- The maintenance directory `documentation/maintenance/components.v1_issue/` (gitignored, local-only) contains the reproducer, the migration plan, and the (now-obsolete) upstream-issue draft against `st.html`'s broken `unsafe_allow_javascript` flag.

## [0.6.18] — 2026-05-12

### Fixed
- **Marker-runtime observer now actually executes (real fix)**: 0.6.17 attempted to keep the observer inline in the host page via `st.html(..., unsafe_allow_javascript=True)`, but verification on Streamlit 1.57.0 (and 1.54+) showed `window.__stxMarkerObs === undefined` and `.stx-grid` count `0`. The `unsafe_allow_javascript` proto field is forwarded by the Python API but the released Streamlit frontend does not honor it in any version checked (1.52 through 1.57) — neither for `<script>` tags nor for DOM event handlers (`onload`, `onerror`). The visible regressions from 0.6.16 (broken grids, missing `st_zoom` containment, ignored custom font sizes, AI-image WYSIWYG zoom dropping to 100%) persisted in 0.6.17.
- `streamtex/marker_runtime.py:inject_marker_runtime()` now splits injection: CSS through `st.html("<style>…</style>")` (inline, host page) and JS through `streamlit.components.v1.html("<script>…</script>", height=0)` (0-pixel iframe). Same pattern already proven by `streamtex/marker.py` and `streamtex/bib_preview.py`.
- `streamtex/static/js/stx_marker_observer.js` rewritten to operate on `window.parent.document`: idempotency guard moves to `hostWin.__stxMarkerObs`, `scan()` walks the parent body, the `MutationObserver` is constructed via `hostWin.MutationObserver` and observes `hostDoc.body`. Same-origin Streamlit allows the iframe to reach back into the host DOM.
- `tests/test_marker_runtime.py`: `test_injects_once_per_session` now patches both `st.html` and `components.html`; new `test_css_via_st_html` and `test_js_via_components_html` lock in the split-call contract (CSS goes through `st.html`, JS goes through `components.html` with `height=0`); `test_js_observer_has_idempotency_guard` asserts `hostWin.__stxMarkerObs`.

### Notes
- No public API change. No new env var. Users on 0.6.17 (or 0.6.16) just need to upgrade.
- **Acknowledged deprecation debt**: `streamlit.components.v1.html` is officially deprecated in Streamlit 1.56 (docs name `st.html` as the replacement). However, the replacement does not honor `unsafe_allow_javascript=True` on the frontend — verified on 1.57.0 with a self-contained reproducer for `<script>`, `<svg onload>`, and `<img onerror>`. Until Streamlit fixes the flag on the frontend, `components.v1.html` is the **only** path that actually runs injected JavaScript. See `documentation/maintenance/components.v1_issue/` for the reproducer, the upstream issue draft, and the migration plan.
- Browser verification: `window.__stxMarkerObs === true`, `document.querySelectorAll('.stx-grid').length > 0`, `document.querySelectorAll('.stx-marker-cell').length > 0`.

## [0.6.17] — 2026-05-12

### Fixed
- **Marker-runtime observer now actually executes**: critical hotfix on top of 0.6.16. Streamlit ≥ 1.54 silently strips `<script>` tags from `st.html()` payloads by default. Without execution of the observer, every marker-based CSS rule (`.stx-grid`, `.stx-zoom`, `.stx-list-item`, per-instance `[data-stx-block-uid="…"]`, …) silently no-oped, which surfaced as broken grids, missing `st_zoom` containment, ignored custom font sizes, and AI-image WYSIWYG zoom dropping to 100%.
- `streamtex/marker_runtime.py:inject_marker_runtime()` now calls `st.html(..., unsafe_allow_javascript=True)` so the bundled `static/js/stx_marker_observer.js` runs in the host-page context (no iframe, no `parent.document` indirection). Pattern aligned with Streamlit's deprecation of `st.components.v1.html` in 1.56.
- `tests/test_marker_runtime.py` gains `test_passes_unsafe_allow_javascript_flag` which would have caught the regression at unit-test time.

### Notes
- No public API change. No new env var. Users on 0.6.16 simply need to upgrade.
- The bundled observer is a fixed, version-controlled asset — the `unsafe_allow_javascript=True` flag is bounded to that single trusted payload.
- **Did not fix the regression in practice** — see 0.6.18 for the working fix.

## [0.6.16] — 2026-05-12

### Removed
- **Legacy `:has()` scoping pattern** (Phase 5 — final phase of the `:has()` removal plan). Removed from `streamtex/container.py`, `streamtex/list.py`, `streamtex/grid.py`, `streamtex/zoom.py`, `streamtex/block_helpers.py`. The marker-runtime path is now the only path; there is no fallback.
- Environment variables `STX_USE_MARKER_RUNTIME` and `STX_USE_LEGACY_HAS` are removed. `is_marker_runtime_enabled()` is removed from `streamtex/marker_runtime.py`. Setting either env var has no effect.
- Progress-emit throttle in `streamtex/loading.py` (introduced in 0.6.11). It was a defensive patch built on an incorrect hypothesis (iframe storm) and is no longer needed once the actual cause — `:has()` selector explosion — is gone.
- `TestProgressThrottle` test class in `tests/test_loading.py` (4 tests).
- All `_force_legacy_by_default` and `_marker_runtime_on` test fixtures across `tests/test_container.py`, `tests/test_list.py`, `tests/test_grid.py`, `tests/test_zoom.py`, `tests/test_section_zoom.py` — no longer needed.
- `TestStBlockMarkerPath` / `TestStSpanMarkerPath` / `TestStGridMarkerPath` / `TestStZoomMarkerPath` / `TestStListMarkerPath` / `TestListItemMarkerPath` classes folded into the regular test classes (the marker pattern is the only behavior).

### Changed
- `tests/test_export_guard.py`: `container.py` 2, `grid.py` 1 (was 3 with dual paths), `list.py` 2 (was 6), `block_helpers.py` 1 (was 3) — reflecting the now-single emit path.
- Several legacy-asserting tests in `tests/test_container.py`, `tests/test_list.py`, `tests/test_grid.py`, `tests/test_section_zoom.py` rewritten to assert the marker emit pattern.

### Notes
- The freeze fix is now permanent. Users on `0.6.15` who set `STX_USE_LEGACY_HAS=1` as a workaround must remove it before upgrading.
- See `documentation/maintenance/freeze-has/fix-plan.md`.

## [0.6.15] — 2026-05-12

### Changed
- **Marker runtime is now the default** (Phase 4 of the `:has()` removal plan). `is_marker_runtime_enabled()` returns `True` unless `STX_USE_LEGACY_HAS=1` is set or `STX_USE_MARKER_RUNTIME=0` is set explicitly. Every StreamTeX construct that used to emit `:has()`-scoped stylesheets (st_block, st_span, st_list, ListController.item, st_grid, st_zoom, _render_md_body) now emits sentinel marker spans + a global stylesheet + a `MutationObserver` by default.
- Tests that assert the legacy `:has()` emit pattern now use an autouse `_force_legacy_by_default` fixture (in `tests/test_container.py`, `tests/test_list.py`, `tests/test_grid.py`, `tests/test_zoom.py`, `tests/test_section_zoom.py`) to opt back into legacy. The `_marker_runtime_on` fixture used by marker-path tests now also unsets `STX_USE_LEGACY_HAS` so it overrides the autouse default.

### Notes
- **Escape hatch**: `export STX_USE_LEGACY_HAS=1` reverts to the legacy `:has()` path for users hitting an unforeseen regression. Removed in 0.6.16.
- **Expected impact**: Chrome cold-load freeze (~3-4 s) eliminated. The `<style>` element count on a typical manual drops from ~1 054 to < 50; the `:has()` selector count drops from ~958 to 0 (legacy off).
- See `documentation/maintenance/freeze-has/fix-plan.md`.

## [0.6.14] — 2026-05-11

### Added
- **`st_grid` marker-runtime path** (Phase 3 of the `:has()` removal plan). When `STX_USE_MARKER_RUNTIME=1` is set, `streamtex/grid.py` emits a sentinel `data-stx-kind="grid"` marker plus `data-stx-grid-template` / `data-stx-grid-gap` attributes that the observer forwards as CSS custom properties. Optional `grid_style` and `breakpoint` overrides become tiny per-instance stylesheets keyed by `[data-stx-grid-uid="…"]` (the `@container` query stays per-instance because CSS `var()` is not reliable inside query conditions across browsers).
- **`st_zoom` marker-runtime path**: `streamtex/zoom.py` emits a `data-stx-kind="zoom"` marker with `data-stx-zoom-factor` consumed by the global `.stx-zoom` rule via CSS custom property.
- **`_render_md_body` marker-runtime path**: `streamtex/block_helpers.py` emits a `data-stx-kind="md-big"` marker with a tiny per-instance stylesheet for the `StxStyles.big` font-size override (preserves the legacy `<p>`/`<li>` cascade override 1:1).
- `.stx-grid`, `.stx-zoom`, `.stx-md-big` rules in `streamtex/static/css/stx_global.css`. The grid's "hide non-cell element-container" behavior is collapsed into a single `.stx-grid > .element-container { display: none !important; }` rule (replacing the legacy three-way `:has(style|script|span)` union).
- New test classes `TestStGridMarkerPath` (7 tests), `TestStZoomMarkerPath` (3 tests) in `tests/test_grid.py` / `tests/test_zoom.py`.

### Notes
- Legacy `:has()` path remains the default (flag off). All existing tests for legacy emit continue to pass byte-identically.
- This release completes the migration of every StreamTeX construct using `:has()` for scoping. Phase 4 (0.6.15) flips the flag default to ON; Phase 5 (0.6.16) deletes the legacy code paths.
- See `documentation/maintenance/freeze-has/fix-plan.md`.

## [0.6.13] — 2026-05-11

### Added
- **`st_list` / `ListController.item` marker-runtime path** (Phase 2 of the `:has()` removal plan). When `STX_USE_MARKER_RUNTIME=1` is set, `streamtex/list.py` emits sentinel markers (`data-stx-kind="list"`, `data-stx-kind="list-item"`) instead of `:has()`-scoped stylesheets. Bullet `content` (including ordered counters like `counter(streamtex-counter, decimal) '.'`) is carried by a tiny per-item stylesheet keyed by `[data-stx-list-item-uid="…"]` — necessary because CSS `var()` cannot reliably carry a `counter()` function call across all browsers.
- `.stx-list` and `.stx-list-item` rules in `streamtex/static/css/stx_global.css`. Layout, gap, baseline alignment, marker-cell hide, and inner content wrapper now live in the global stylesheet.
- New test classes `TestStListMarkerPath`, `TestListItemMarkerPath` in `tests/test_list.py` (8 new tests).

### Changed
- **Observer kind-prefixed UID attribute**: `streamtex/static/js/stx_marker_observer.js` now sets `data-stx-{kind}-uid` (e.g. `data-stx-block-uid`, `data-stx-list-item-uid`) on the parent `stVerticalBlock` rather than a single `data-stx-uid`. This is required because a `ListController.item` wraps a `st_block` — both markers point at the same parent and a flat attribute would let one overwrite the other.
- `streamtex/container.py` marker path: per-instance stylesheets now use `[data-stx-block-uid="…"]` / `[data-stx-span-uid="…"]` instead of `[data-stx-uid="…"]`.
- `tests/test_container.py`, `tests/test_marker_runtime.py` updated for the kind-prefixed attribute.

### Notes
- Legacy `:has()` path remains the default (flag off). Every legacy test in `tests/test_list.py`, `tests/test_container.py` continues to pass byte-identically.
- See `documentation/maintenance/freeze-has/fix-plan.md` for the multi-phase plan.

## [0.6.12] — 2026-05-11

### Added
- **`st_block` / `st_span` marker-runtime path** (Phase 1 of the `:has()` removal plan). When `STX_USE_MARKER_RUNTIME=1` is set, `streamtex/container.py` emits a `<span class="stx-marker" data-stx-kind="block|span" data-stx-uid="…">` sentinel instead of a `:has()`-scoped stylesheet. Custom user `style=` is carried by a per-instance `[data-stx-uid="…"]` attribute-selector stylesheet (Option B — preserves cascade semantics 1:1).
- `.stx-span` rules in `streamtex/static/css/stx_global.css` (display:flex / flex-direction:row / white-space:pre / `>* {width:auto}`).
- New test classes `TestStBlockMarkerPath`, `TestStSpanMarkerPath`, `TestExportUnaffectedByMarkerPath` in `tests/test_container.py` covering the marker emit pattern, the absence of `:has()` in the new path, and the byte-identical export wrappers across both paths.

### Notes
- Legacy `:has()` path remains the default (flag off). Existing tests for the legacy emit pattern continue to pass unchanged.
- The same per-instance `<style>` count drops to 0 for blocks/spans when the new path is on and no `style=` is passed; rises to 1 when a user style is supplied.
- See `documentation/maintenance/freeze-has/fix-plan.md` for the multi-phase plan.

## [0.6.11] — 2026-05-11

### Added
- **Marker runtime scaffold** (Phase 0 of the `:has()` removal plan): new internal module `streamtex/marker_runtime.py` plus two shipped assets `streamtex/static/css/stx_global.css` and `streamtex/static/js/stx_marker_observer.js`. When the env var `STX_USE_MARKER_RUNTIME=1` is set, `st_book` injects a global stylesheet and a `MutationObserver` that will replace the per-instance `:has()` CSS scoping pattern in later phases. Default behavior is unchanged (flag off → legacy `:has()` path).
- Internal escape hatch `STX_USE_LEGACY_HAS=1` reserved for Phase 4 — currently a no-op since the legacy path is the default.
- Package data now includes `streamtex/static/css/*.css` and `streamtex/static/js/*.js`.
- New test module `tests/test_marker_runtime.py` covering the env-flag gating, idempotency within a session, and the presence of the static assets.

### Notes
- No user-facing API change; no rendering behavior change with the flag off.
- See `documentation/maintenance/freeze-has/fix-plan.md` for the multi-phase plan replacing the `:has()` selector storm that causes a 1.5–3.5 s freeze on Chrome at cold load.

## [0.6.10] — 2026-04-15

### Added
- **Slide break before/after spacing**: `SlideBreakDisplayConfig` now has `before` and `after` fields (replacing single `space`), allowing independent control of vertical spacing above and below the horizontal rule. Backward-compatible `space` property alias retained.
- **`space_before` in `SlideBreakConfig`**: new CSS-level `space_before` field for spacer div rendered before the rule.
- **`marker_hidden` in `SlideBreakConfig`**: controls whether navigation markers appear in the popup marker list (visible) or remain counter-only (hidden).
- **`MARKER_ONLY` and `HIDDEN` slide break modes**: two new `SlideBreakMode` variants now available in the sidebar selectbox.
- **Print CSS for before-spacer**: `.stx-slide-break-spacer-before` collapses to `height: 0` in print media.

### Fixed
- **`test_negative_int_size`**: test assertion corrected to match `margin-top` (not `height`) for negative `st_space()` values, aligning with the v0.6.9 implementation.

## [0.6.9] — 2026-04-08

### Added
- **Negative spacing in `st_space()`**: support for negative `size` values (e.g. `"-2em"`, `-3`). Negative vertical spacing uses `margin-top` instead of `height`; negative horizontal uses `margin-left` instead of `padding-left`. Enables pulling content closer together or overlapping elements.

## [0.6.8] — 2026-04-07

### Added
- **Diagnostic logging for image display persistence**: added `[DIAG:LOAD]`, `[DIAG:PERSIST]`, and `[DIAG:APPLY]` warning-level logs in `image.py` and `image_editor.py` to trace zoom/scale settings through the load → apply → persist pipeline. Helps diagnose zoom reset issues (see #18).

## [0.6.7] — 2026-04-05

### Added
- **`breaks` parameter in `st_write()`**: when `True` (default), newlines in text are converted to `<br>` for visible line breaks. When `False`, all newlines and `<br>` tags are collapsed to spaces. Enables natural triple-quoted strings with preserved line breaks.

## [0.6.6] — 2026-04-05

### Added
- **`/stx-ce:pause` command**: new session checkpoint command that captures in-progress work items, decisions log, pending issues, and context for the next session. Writes `docs/ce-checkpoint.md`.
- **Checkpoint template**: new `checkpoint.md` template for structured session state capture.
- **Checkpoint restoration in `/stx-ce:continue`**: Step 0 reads `docs/ce-checkpoint.md` if present, displays a restoration banner, integrates checkpoint items as HIGH-priority proposals, and archives the checkpoint after use.
- **Checkpoint display in `/stx-ce:status`**: dashboard now shows checkpoint info when `docs/ce-checkpoint.md` exists.

### Changed
- **CE cheatsheet**: updated to 12 commands (was 11) and 17 templates (was 16), added `/stx-ce:pause` section, updated `/stx-ce:continue` section with checkpoint restore step.

## [0.6.5] — 2026-04-04

### Fixed
- **Remove jinja2 from cli extras**: `jinja2` removed from `[cli]` optional dependencies — no longer needed after template refactoring.
- **Dockerfile template `--no-sources`**: added `--no-sources` flag to `uv sync` in generated Dockerfiles, reducing image size.
- **Silent except:pass replaced with logger.debug**: 31 bare `except: pass` blocks across 15 files now log exceptions via `logger.debug`, improving debuggability.
- **CLI test assertions**: updated test expectations to reflect `cli` extra always injected in `pyproject.toml`.
- **README stx-migration → stx-import**: replaced stale `stx-migration` namespace references with `stx-import`.

## [0.6.4] — 2026-04-01

### Fixed
- **AI managed images in Docker**: `_detect_project_root()` now prefers CWD (with `book.py`) over `__main__.__file__`, fixing 27 missing images in static HTML export when running via `uv run stx` in containers.

## [0.6.3] — 2026-04-01

### Added
- **PDF bookmarks from TOC**: `export_pdf()` now generates native PDF bookmarks (outlines) from the table of contents. Invisible headings are injected at TOC anchor positions; Chromium builds the bookmark tree with `outline=True` + `tagged=True`.
- **Dark theme in static HTML export**: `stx export html` reads `.streamlit/config.toml` before entering headless context and preserves dark theme colors. New CLI options: `--theme auto|dark|light`, `--theme-bg`, `--theme-text`.
- **Post-deploy smoke test**: `stx deploy hetzner` and `stx deploy update` verify `/html/` returns Nginx and `/` returns 200.
- **`cli` extra included by default**: all presets and project templates ship with `streamtex[cli]`.
- **Deploy files in project scaffold**: `stx project new` generates `Dockerfile`, `nginx.conf`, and `entrypoint.sh`.
- **Concurrent deploy limit**: `MAX_CONCURRENT_DEPLOYS=4` and `rebuild_batch()` for server-wide throttling.
- **Nginx 302 redirect** for `/html/` instead of meta refresh.

### Fixed
- **Dual-mode deployment end-to-end**: Traefik labels updated alongside `ports_exposes` when changing serve mode.
- **`stx export html` in Docker**: `rich` and `jinja2` installed via `[cli]` extra.
- **`set_env_var`**: handles existing vars (409 → PATCH fallback), omits `is_build_time` when False.

### Changed
- **Default serve mode is `dual`**: `stx deploy hetzner --serve-mode` defaults to `dual`.

## [0.6.2] — 2026-04-01

Intermediate release published to PyPI between 0.6.1 and 0.6.3. Introduced the
dual-mode deployment scaffold (Nginx static + Streamlit interactive) and PDF
TOC bookmarks. The polished/end-to-end versions of these features ship in
0.6.3, which supersedes 0.6.2 for new installs.

### Added
- **Dual-mode deployment templates**: Nginx + Streamlit Dockerfile/nginx.conf/entrypoint scaffold (`generate_dockerfile`, `generate_nginx_conf`, `generate_entrypoint`).
- **PDF bookmarks (initial)**: `export_pdf()` outline generation from TOC anchors.

## [0.6.1] — 2026-04-01

### Added
- **Dual-mode Dockerfile generator**: `generate_dockerfile()` now produces a container running both Nginx (static HTML on `/html/`) and Streamlit (interactive on `/`), controlled by `STX_SERVE_MODE` env var.
- **Nginx config generator**: `generate_nginx_conf()` for static file serving alongside Streamlit.
- **Entrypoint script generator**: `generate_entrypoint()` manages dual-mode startup with health checks.
- **Coherence audit expansion**: 45 checks (was 28) — added 13 AI-quality checks (ghost API, dead code, explanation drift, cross-block contradictions, test quality, secret leaks, etc.) and 4 CLI checks (help↔code, stx-guide↔CLI, deploy↔Docker, optional deps↔imports).

### Changed
- **Deploy CLI**: `stx deploy` templates updated for dual-mode serving with Nginx + Streamlit.

## [0.6.0] — 2026-04-01

### Added
- **Enriched HTML export from sidebar**: "Download as HTML" now offers a checkbox "Enriched navigation" (TOC sidebar, marker bar, search) and a customizable document title — equivalent to CLI `--no-nav` and `--title`.
- **Collapsible sidebar in HTML export**: hamburger button inside the sidebar hides/shows it with smooth transition. Preference persisted in localStorage.
- **"Powered with StreamTeX"**: sidebar header shows the real StreamTeX logo (logo-stx-tiny.png) linked to streamtex.org.
- **Serve modes** (`--serve-mode`): `dual` (Nginx + Streamlit), `static-only`, `streamlit-only` on `stx deploy hetzner` and `stx deploy update`.
- **`stx export html`** CLI command with `--output`, `--asset-mode`, `--title`, `--no-nav` options.
- **Horizontal scaling**: `stx deploy scale TARGET --replicas N` for load-balanced containers.

### Fixed
- **PDF export no longer includes sidebar TOC**: enrichment applied to HTML copy only, raw HTML preserved for PDF.
- **Keyboard navigation in HTML export**: Arrow keys (all 4) + PageUp/PageDown navigate between markers (previously required Ctrl+Arrow).

## [0.5.22] — 2026-03-31

### Fixed
- **Display zoom/size not applied in deployed mode**: `_load_display_from_metadata()` was gated behind `editable and name` — deployed apps never loaded zoom, width, or height from metadata JSON. Changed to `name` only, consistent with the managed image lookup fix in v0.5.21.

## [0.5.21] — 2026-03-31

### Fixed
- **Managed images not shown in deployed (non-editable) mode**: `get_current(name)` lookup was gated behind `editable and name` — deployed apps with `editable=False` never resolved managed images from `static/images/managed/`. Changed condition to `name` only, so managed images are found regardless of editable flag.

## [0.5.20] — 2026-03-31

### Fixed
- **AI auto-generate not triggering**: `get_image_src("")` returned a non-empty fallback path (`app/static/images/`) instead of empty string, preventing the AI generation fallback from activating. Added early return for empty URI.
- **Silent AI generation failures**: replaced `except Exception: pass` with `logger.warning(...)` in the auto-generate fallback so API errors are visible in the console.

### Changed
- **WebP-first lookup**: `get_current()` and `rollback()` in `history.py` now check `.webp` before `.png` for faster resolution when images are in WebP format.

## [0.5.19] — 2026-03-31

### Fixed
- **HTML/PDF export vertical stacking**: each `st_html()` fragment is now wrapped in a block-level `<div class="stx-el">` to reproduce Streamlit's element container behavior. `st_block()` export prepends `display:flex;flex-direction:column;gap:0.1rem` (mirrors Streamlit's `stVerticalBlock`).
- **Export alignment**: `.stx-block > * { align-self: stretch }` CSS rule ensures grid/list/block wrappers take full width (prevents `align-items:center` from shrinking children). `ol, ul { text-align: left }` prevents `text-align:center` inheritance through the flat DOM.
- **Generate button sidebar pollution**: export rebuild now uses a pre-created `st.empty()` placeholder in the main area, preventing blocks from rendering inside the sidebar on first "Generate" click.

### Added
- **AI auto-generate in `st_image()`**: `st_image(prompt=..., editable=True)` now handles AI generation natively — checks cache, auto-generates if `AIImageConfig.auto_generate=True`, and saves to managed history when `name=` is given.
- **WebP default for AI images**: new `AIImageConfig.save_format` (default `"webp"`) and `save_quality` (default `90`) fields. Generated images are transcoded via Pillow before saving, yielding ~10× smaller files. Graceful fallback to PNG if Pillow is not installed.
- **Pillow optional dependency**: added to all `ai` extras (`ai`, `ai-openai`, `ai-google`, `ai-fal`).

### Deprecated
- **`st_ai_image()`**: now emits `DeprecationWarning` at runtime. Use `st_image(prompt=..., editable=True, name=...)` instead.
- **`st_ai_image_widget()`**: now emits `DeprecationWarning`. Use `st_image(editable=True)` with the editor panel's AI tab instead.

## [0.5.18] — 2026-03-30

### Fixed
- **Deploy timestamps in local timezone**: `stx deploy status coolify` now displays last deploy timestamps converted to local timezone instead of raw UTC.
- **`stx deploy setup` Coolify token prompt**: setup now interactively asks for the Coolify API token and preserves existing values in `.stx-deploy.env` instead of silently skipping.

### Added
- **Last deploy timestamp**: `stx deploy status coolify` shows the last deployment timestamp for each service.

### Changed
- **PR #7 (Fre-Ar)**: `stx dev` CLI commands now use `uv` directly instead of `uv run`.

## [0.5.17] — 2026-03-30

### Fixed
- **Marker navigation jump-to-start**: fixed multiple falsy-zero bugs where `_stxMarkerStartIdx = 0` was treated as unset, causing navigation to reset to marker 0 (page "Who?") on Streamlit reruns. All null checks now use `== null` instead of `!value` or `|| 0`.
- **Navigation during init window**: added `_initialized` guard to `navigateTo()` and `keyHandler()` — keyboard/button navigation is blocked during the 500ms marker init, preventing jumps to wrong pages when `currentIdx` is still 0.
- **Scroll tracker race condition**: scroll handler now checks `_initialized` flag before updating `currentIdx`, preventing `doScrollReset()` from corrupting marker state during page transitions.
- **AI image regeneration display**: renamed `_mtime` parameter to `mtime` in `_get_base64_encoded_image()` — Streamlit's `@st.cache_data` excludes underscore-prefixed params from the cache key, causing regenerated images to display stale base64 data.

### Added
- **Navigation bar toggle**: added a "Navigation bar" toggle at the top of the Settings sidebar expander to show/hide the floating marker navigation widget at runtime. Keyboard navigation continues to work when the bar is hidden.
- **Nav bar position preservation**: `clampNav()` now skips position persistence when the nav widget is hidden (`display:none`), preventing localStorage from being overwritten with `{x:0, y:0}`.

## [0.5.16] — 2026-03-29

### Fixed
- **`stx update` CLI version check**: `_get_source_version` now reads from `pyproject.toml` instead of parsing `__init__.py`, which returned the literal string `_pkg_version("streamtex")` instead of the actual version — causing a reinstall attempt on every `stx update`.
- **`stx update` Python interpreter mismatch**: `_upgrade_cli_tool` now detects the Python interpreter used by the existing `uv tool` environment and passes `--python` to avoid falling back to the system interpreter (which may not satisfy `requires-python >= 3.11`).
- **Language consistency**: replaced French "la librairie" with English "the library" in CLAUDE.md terminology section across all profile templates.

## [0.5.15] — 2026-03-29

### Added
- **`stx dev` CLI commands**: `register`, `unregister`, `link`, `unlink`, `status` — manage development links between projects and local source repos (streamtex, streamtex-claude, streamtex-docs). Global registration persists in `~/.config/streamtex/dev.json`.
- **`ModelCapabilities` system**: each AI provider declares supported sizes, qualities, and defaults per model. `get_model_capabilities(provider, model)` returns a `ModelCapabilities` dataclass. The image editor uses this to populate size/quality dropdowns dynamically.
- **`Wrap.hyphens` style**: `s.text.wrap.hyphens` enables automatic CSS hyphenation (`hyphens: auto; overflow-wrap: break-word`) for large text in narrow containers.
- **Image Display tab persistence**: `display_zoom`, `display_width`, `display_height`, `display_keep_ratio` fields added to `ImageMetadata`. Display settings from the editor's Display tab are now applied to image rendering automatically.

### Fixed
- **Marker cross-page navigation**: the marker init now scrolls to the target marker after page transitions instead of leaving the viewport at the top while `currentIdx` points elsewhere. Fixes the issue where LEFT/RIGHT arrows skipped sections after cross-page navigation.

## [0.5.14] — 2026-03-26

### Fixed
- **`__version__` desync**: replaced hardcoded `__version__` string in `__init__.py` with dynamic `importlib.metadata.version("streamtex")` — version is now always read from `pyproject.toml`, eliminating the single/double source of truth problem that caused v0.5.13 to display "lib 0.5.12" at runtime.

## [0.5.13] — 2026-03-26

### Fixed
- **`stx` CLI shadowed in project venvs**: when streamtex is installed as a project dependency without `[cli]` extras, `.venv/bin/stx` now transparently delegates to the global `stx` tool install (`~/.local/bin/stx`) instead of showing a misleading "missing dependencies" error. Users can now run `stx status`, `stx run`, etc. with their project venv activated.

### Added
- **Auto-port resolution in `stx run`**: when no port is specified and no config exists, `stx run` now finds the first available port starting from 8501 instead of always using 8501. Prevents "port already in use" errors when running multiple projects.
- **`_find_global_stx()` helper**: locates the global stx executable by walking PATH (skipping venv entries) with fallback to `~/.local/bin/stx`.
- **`_is_port_free()` / `_find_free_port()` helpers**: socket-based port availability check for `stx run`.

## [0.5.12] — 2026-03-26

### Added
- **Hetzner/Coolify deployment CLI**: 7 new `stx deploy` commands — `setup`, `provision`, `secure`, `install-coolify`, `configure-domain`, `hetzner`, `update` — covering the full deployment lifecycle from zero.
- **`coolify.py` API client module**: `CoolifyClient` with `rebuild()`, `restart()`, `create_app()`, `delete_app()`, `wait_healthy()`, `set_env_var()`, `set_fqdn()`, `verify_token()`.
- **`DeployState` typed schema**: dataclasses for `.stx-deploy.json` (ServerInfo, DomainInfo, CoolifyInfo, AppEntry) with `to_dict()`/`from_dict()` serialization.
- **Shared constants**: `DEFAULT_SSH_KEY_PATH`, `DEFAULT_SERVER_TYPE`, `STREAMLIT_PORT`, etc. — single source of truth for CLI and Claude commands.
- **`stx deploy status coolify`**: new platform option to check Coolify service health.

### Changed
- **`stx deploy update`**: uses `/start` (full rebuild) by default, `--quick` for `/restart` (same image). Previously used `/restart` incorrectly.
- **Deploy commands refactored**: extracted `_assert_preflight()`, `_ensure_dockerfile()`, `_resolve_server_ip()` helpers to eliminate 60+ lines of duplication.
- **`render_service_url()`**: accepts configurable domain instead of hardcoding `streamtex.org`.
- **CLI commands write `phases_completed`**: `provision`, `secure`, `install-coolify`, `configure-domain` now write ISO timestamps to `.stx-deploy.json` for interop with Claude commands.

## [0.5.11] — 2026-03-25

### Added
- **Section Spacing system**: new `Spacing` and `SpacingConfig` dataclasses for configurable margins around blocks and sections.
- **5-level override hierarchy**: Built-in → Book (`set_spacing`) → Profile (`PresentationProfile.spacing`) → Block (`set_block_spacing`) → Call-site (`st_slide_break(spacing=)`).
- **Vertical spacing**: `block.top/bottom` replaces the hardcoded 70px inter-block gap. `section.top/bottom` controls gaps between `st_slide_break` sections.
- **Horizontal spacing**: `left/right` margins on sections affect both StreamTeX content (`_render()` wrapping) and Streamlit containers (`st_block`/`st_span` CSS `:has()` injection).
- **Double-spacing prevention**: `block.top` and `section.top` never stack at the start of a block.
- **`spacing` parameter on `st_write()`**: per-title spacing override when `auto_marker_on_toc` is active.
- **Block-level horizontal CSS injection**: `_inject_block_horizontal_css()` for `width`/`left`/`right` at block level.
- **74 new tests** in `test_spacing.py`: dataclasses, DI, resolution, double-spacing, container integration, render wrapping.
- **Manual blocks**: `bck_spacing` (intro) and `bck_spacing_profiles` (advanced).
- **Updated cheatsheet** with Section Spacing reference.
- **Updated project template** (`stx project new`) with `set_spacing()` example.

### Changed
- **`st_slide_break()` signature**: new `spacing: Spacing | None` parameter.
- **`st_book()` block loop**: injects `block.top`/`block.bottom` from resolved `SpacingConfig` instead of hardcoded `st_space("v", "70px")`.

## [0.5.10] — 2026-03-23

### Added
- **PDF presentation formats**: 16:9, 16:10, 4:3 and custom free-form ratios (e.g. "21:9", "2.35:1") in the PDF export page size selector.
- **`content_width` parameter on `PdfConfig`**: controls content width as a percentage (10-100%) of the PDF page, same logic as `PageLayout(width=...)` for on-screen display. Background fills full page, content is centered.
- **Auto-viewport in PDF export**: viewport width is automatically computed from page format, margins, and scale so content fills the PDF page width exactly. No more narrow content on landscape pages.
- **Page format dimension lookup**: `_page_dimensions_mm()` supports all standard paper formats and arbitrary W:H ratios.
- **22 new tests**: page dimensions, viewport calculation, content width CSS injection, format ratios.

### Changed
- **PDF Scale and Content width inputs**: replaced slider with `st.number_input` — integer percentage, +/- buttons step by 10, free keyboard entry for precise values.
- **PDF sidebar**: "Custom ratio" option with always-visible text input field (disabled when a preset format is selected).

### Fixed
- **Export slide breaks created phantom markers**: `st_slide_break()` called between blocks during export cache build now uses `marker=False`, preventing hidden markers from polluting the navigation registry.
- **Stale cache after library upgrade**: version was already in the cache hash but the v0.5.9 cache persisted because version wasn't bumped with the fix. Cache is now properly invalidated.
- **Content width CSS targeted wrong classes**: exported HTML uses `.streamtex-page`, not Streamlit's `.stMain` classes. CSS injection now targets the correct class.

## [0.5.9] — 2026-03-23

### Fixed
- **Marker counter desynchronized in paginated mode**: slide break markers inserted during export cache build were missing `page_idx` tags, causing pre-seed/post-seed to lose them. This desynchronized the floating bar counter and popup navigation.

## [0.5.8] — 2026-03-23

### Added
- **CE docs scaffold in `stx project new`**: New projects now include `docs/` directory structure for Compound Engineering artifacts (collect/, assess/, plans/, reviews/, solutions/ with 9 category subdirectories + governance/).

### Fixed
- **Version alignment**: `__init__.py` version now matches `pyproject.toml`.

## [0.5.7] — 2026-03-22

### Changed
- **CLAUDE.md updated**: Enhanced with stx-ce Compound Document Engineering workflow section (8 commands, 7-phase cycle).

## [0.5.6] — 2026-03-22

### Added
- **Bibliography entry styles**: `BibStyle.entry_style` and `BibStyle.number_style` for fine-grained control over bibliography rendering (font size, color, spacing).
- **PDF export dark theme support**: `PdfConfig` now detects `theme.base = "dark"` and adjusts export backgrounds. Fallback to `get_option("theme.base")` when config.toml detection fails.
- **pt scale system**: `PdfConfig.pt_scale` parameter for consistent font scaling in PDF output (default 1.0).

### Fixed
- **Bibliography `only_cited=True` empty in paginated mode**: cited keys were not collected across pages because each page had its own render context. Fix: cache cited keys in `st.session_state` across page renders.
- **Dark theme PDF export**: `theme.base = "dark"` was not detected by `get_option()` in some Streamlit versions. Added fallback to parse `.streamlit/config.toml` directly.
- **PDF widget persistence**: `PdfConfig` was disconnected from the export panel widgets. Widget key fingerprinting now ensures config stays in sync.

## [0.5.5] — 2026-03-22

### Fixed
- **`stx claude update` does not re-render CLAUDE.md from template**: `CLAUDE.md.j2` was copied as-is but never rendered to `CLAUDE.md`. Now both `stx claude install` and `stx claude update` render the template with `{{ project_name }}`, `{{ profile }}`, and `{% if %}` conditionals.
- **`stx claude update` skip message unclear**: improved the message when locally modified files are skipped, with explicit instructions to use `--force` and note about automatic backup.
- **`.claude/` files lose read-only protection after git operations**: git resets chmod 444 to 644 on checkout/pull. `.claude/` managed files are now excluded from git tracking via `.gitignore`. Migration is automatic: `stx update` adds the gitignore rules, untracks files, and auto-commits when safe.

### Changed
- **`generate_gitignore()`** now includes `.claude/*` exclusion rules (with `!.claude/custom/` and `!.claude/.stx-profile` exceptions) for new projects.

## [0.5.4] — 2026-03-21

- **Chrome banner shown on iOS Chrome**: banner incorrectly appeared because iOS Chrome uses `CriOS` (not `Chrome`) in its user-agent string. Now detects `CriOS` and skips the banner entirely on iOS since all iOS browsers use WebKit (no Chrome advantage).
- **Marker popup list not scrollable on touch devices**: touching inside the popup block list started a drag instead of scrolling. Fixed by excluding the popup from drag targets (`isDragTarget`) and toggling `touch-action` on the nav element when the popup opens/closes.

### Added
- **`view_modes` parameter on `st_book()`**: restrict available view modes in the sidebar. Pass `view_modes=[ViewMode.PAGINATED]` to lock paginated-only (hides the View radio), or `[ViewMode.PAGINATED, ViewMode.CONTINUOUS]` to allow both (default). Useful for deployed documents where continuous mode should be disabled.
- **Safety protections for `stx update` and `stx claude update`**:
  - `stx update`: skips `git pull` on repos with uncommitted changes (warns with file list). Now also detects staged changes.
  - `stx claude update`: skips all locally modified `.claude/` files (not just `CLAUDE.md`) unless `--force` is used.
  - `stx claude update --force`: creates a timestamped backup in `.claude/.backup/<timestamp>/` before overwriting modified files.
- **Loading overlay**: full-screen semi-transparent mauve overlay with progress percentage during app loading. Shows "Initializing…" with pulse animation during setup, then real-time `module X / Y` progress during block rendering. Works in both continuous and paginated modes (during cache build). New `loading` parameter on `st_book()` (default `True`). Automatically disabled in warmup mode.
- **Loading overlay UX improvements**: smoother progress bar (1.5s CSS transition), current module name displayed below counter (e.g. `bck_intro`), bouncing-dots heartbeat animation to show activity even when a heavy module stalls the progress bar.

## [0.5.3] — 2026-03-20

### Added
- **Mobile-friendly floating bar**: `max-width` constraint + `flex-wrap` for 2-line layout on mobile (<600px). Line 1: controls (profile, nav, list). Line 2: label, collapse, brand, grip.
- **Touch drag support**: `touchstart`/`touchmove`/`touchend` handlers alongside mouse handlers for mobile/tablet drag. Shared `startDrag()`/`moveDrag()`/`endDrag()` functions.
- **Drag grip handle**: braille dots (`⠿`) visible only in collapsed state, positioned at end of bar for touch-friendly repositioning.
- **`draggable` and `collapsible` default to `True`** in `MarkerConfig` — all users get drag and collapse without explicit config.

### Fixed
- **Hidden profile buttons visible in sidebar**: replaced one-shot hiding script with `MutationObserver` on sidebar. Buttons now hidden via inline `style.cssText` (no CSS class dependency). Eliminates race condition where `components.html` script ran before React rendered buttons.
- **Profile asterisk on first load**: `is_profile_modified()` now ignores missing `session_state` keys (returns `False` instead of `True` when widgets haven't rendered yet).
- **Profile reset button layout**: moved `↻` button inline with selectbox using `vertical_alignment="bottom"`, full-width selectbox with `label_visibility="collapsed"`.

### Changed
- **Floating bar drag refactored**: extracted `isDragTarget()`, `startDrag()`, `moveDrag()`, `endDrag()` shared between mouse and touch handlers.

### Removed
- **"Save configuration" expander** from sidebar (ProfileConfig remains in library API).
- **CSS class `.stx-hidden-btns`** — replaced by inline styles via MutationObserver (more reliable).

## [0.5.2] — 2026-03-20

### Added
- **README**: prerequisites section, pip alternative install instructions, uv install guidance.
- **CLI**: improved error messages when uv is not installed (shows install commands for all platforms).

## [0.5.1] — 2026-03-20

### Fixed
- **Slide break space default**: Changed from 60vh to 5vh everywhere — `SlideBreakDisplayConfig.space`, `presentation_preset()` Presenter profile, `_effective_config()` fallback, and `_from_dict()` deserialization default.

## [0.5.0] — 2026-03-19

### Added
- **Presentation profiles** (`PresentationProfile`): named display configurations switchable at runtime via sidebar or floating navigation bar. Each profile bundles mode, layout (width/zoom), wrap, and slide break settings.
- **`PageLayout`**: dataclass for page dimensions (width %, zoom %). No range limits — accepts any numeric value.
- **`ViewMode`** enum: `PAGINATED` / `CONTINUOUS` — document view mode.
- **`SlideBreakDisplayConfig`**: dataclass for slide break settings (enabled, mode, space) within a profile.
- **`ProfileConfig`**: JSON-serializable wrapper for a named list of profiles. Supports `to_json()`, `from_json()`, `save()`, `load()` for configuration export/import.
- **Factory presets**: `PresentationProfile.responsive_preset()` (Desktop/Tablet/Mobile), `.presentation_preset()` (Presenter/Audience/Handout), `.desktop_mobile_preset()` (Desktop/Mobile pair). All default to `PAGINATED` mode.
- **Sidebar profile selector**: phone icon (`📱`) + selectbox with `*` indicator for modified profiles + `↻` reset button.
- **Floating bar profile menu**: phone icon SVG button (left side of navigation bar) opens a popup with all profiles. Active profile highlighted, modified profiles show `*`.
- **Save configuration UI**: "Save configuration" expander in sidebar with download button for JSON export (appears when user-defined profiles are provided).
- **`presentation_profiles` parameter** on `st_book()`: accepts a list of `PresentationProfile` instances.
- **40+ tests** in `test_presentation_profile.py` covering data classes, factory presets, apply/modified detection, JSON round-trip serialization.

### Fixed
- **Paginated export panel kills marker navigation bar** — the export "Download as..." panel was rendered in the sidebar AFTER the marker iframe injection, causing Streamlit to rebuild the sidebar DOM and destroy the marker `components.html` iframe. Fixed by moving the export panel BEFORE `inject_marker_navigation()`.
- **On-demand full-book HTML rebuild** — replaced the synchronous `_build_page_cache()` rebuild (which created temporary iframes that interfered with navigation) with an on-demand callback triggered when the user clicks "Generate" in the export panel.

### Changed
- **All 6 manuals** now include `presentation_profiles=PresentationProfile.desktop_mobile_preset()` for Desktop + Mobile display switching.
- **Templates** (project, presentation) now include display profiles by default.

## [0.4.23] — 2026-03-18

### Added
- **External asset export** (`AssetMode.EXTERNAL`): HTML exports now extract media assets (images, audio, video) from base64 data URIs into a separate `data/` folder with relative paths. Download is a ZIP archive containing `document.html` + `data/{images,audio,video}/`. Deduplication by SHA-256 content hash.
- **`AssetMode` enum**: New public enum (`EMBEDDED`, `EXTERNAL`) controlling how media assets are stored in HTML exports.
- **`AssetCollector` class**: Collects, deduplicates, and packages media assets during export. Supports `rewrite_html()`, `to_zip()`, and `write_to_disk()` methods.
- **`ExportConfig.asset_mode`**: New field defaulting to `AssetMode.EXTERNAL`. Set to `AssetMode.EMBEDDED` for legacy single-file base64 behavior.
- **25 new tests** in `test_asset_collector.py` covering asset registration, deduplication, HTML rewriting, ZIP generation, and disk writing.
- **`PresentationConfig.counter_mode`**: New field (`"bloc"` or `"slide"`) controlling the footer counter display. `"bloc"` (default) shows "Bloc N / M" counting sections. `"slide"` shows "Slide N / M" synced with the floating marker navigation bar via JavaScript.

### Changed
- **HTML download button**: When asset mode is `EXTERNAL`, the download button label changes to "Download HTML (ZIP)" and serves a `.zip` file instead of a plain `.html` file.
- **Auto-export** (`ExportMode.ALWAYS`): When asset mode is `EXTERNAL`, auto-export writes a folder structure (`name/name.html` + `name/data/...`) instead of a single file.

## [0.4.22] — 2026-03-17

### Added
- **Browser tests**: New `test_browser.py` with 4 tests covering `st_chrome_banner()` — previously the only module with zero test coverage

### Fixed
- **Documentation examples**: Fixed incorrect kwargs in developer manual `show_code()` examples — `sidebar_depth` → `sidebar_max_level`, `auto_markers` → `auto_marker_on_toc`, `keyboard_nav` → `next_keys`/`prev_keys` (TOCConfig and MarkerConfig)
- **Enum reference**: Fixed `NumberingMode.INLINE` → `NumberingMode.BOTH` in advanced manual marker config block
- **Ghost API reference**: Removed `inject_slide_break_css()` from all documentation — this function never existed in the library; CSS variable injection is handled internally by `add_slide_break_options()` and `st_slide_break()`

## [0.4.21] — 2026-03-17

### Added
- **Auto-export to disk** (`exports=[ExportConfig(...)]`): New `exports` parameter on `st_book()` accepts a list of `ExportConfig` objects, each describing one output file (HTML or PDF) with format, filename, output directory, timestamp, and PDF settings. Three modes: `ExportMode.ALWAYS` (auto-export after every render), `ExportMode.MANUAL` (sidebar panel), `ExportMode.NEVER` (disabled). Multiple configs enable simultaneous export of different formats/settings (e.g. A4 portrait for print + landscape for projection + HTML archive).
- **`ExportMode` enum**: New public enum (`ALWAYS`, `MANUAL`, `NEVER`) controlling when export happens.
- **`build_export_filename()` helper**: Builds output paths with optional timestamp suffix (`-YYMMDD-HHMMSS`).
- **Timestamp support**: `ExportConfig(timestamp=True)` appends `-YYMMDD-HHMMSS` to the filename for versioned exports.

### Changed
- **`stx run` auto-detects Chrome**: When no `--browser` option is specified, `stx run` now automatically opens Chrome if available on the machine; falls back to the system default browser otherwise. The `--browser` flag still overrides this behavior.
- **README redesigned**: New "Why StreamTeX?" section with 10 reasons, user profiles, two-path table (zero-code / code-first), and embedded YouTube demo video. Tagline updated to "Think with AI. Present with StreamTeX."
- **`ExportConfig` extended**: New fields `format`, `mode`, `output_dir`, `filename`, `timestamp`, `pdf` for auto-export configuration. Fully backward-compatible — existing `enabled`/`page_title`/`page_width`/`page_padding`/`zoom` fields unchanged.

## [0.4.20] — 2026-03-17

### Fixed
- **Draggable marker navigation — viewport clamping**: the floating navigation bar can no longer be lost off-screen; a centralized `clampNav()` function clamps position to the visible viewport on restore, during drag (continuous, no snap), on `mouseup`, on window resize, and after collapse/expand toggle
- **HTML export lists**: ordered and unordered lists now render correctly in exported HTML — added `display: list-item`, `list-style-type`, and proper `padding-left` rules in `default.css` so `<ol>`/`<ul>`/`<li>` elements display with native browser list formatting instead of flowing inline

## [0.4.19] — 2026-03-16

### Fixed
- **PDF export on Render**: `_is_pdf_available()` now checks for the actual Chromium binary, not just the `playwright` import — prevents a non-functional PDF checkbox from appearing when the browser is missing
- **Full document PDF export in paginated mode**: Added "Full document" / "Current section" scope selector so users can export the entire book without switching to continuous view mode
- **Full export HTML always available**: When cache is restored from disk (Tier 2), a dedicated export pass now captures the full-book HTML automatically

### Changed
- **Export UI refactored**: "Download as..." panel reorganised with clear Content / PDF layout sections; format checkboxes (HTML/PDF) moved outside the form for dynamic show/hide of PDF options; radios replace truncated selectboxes for Scope and Section breaks
- **Section breaks terminology**: "Slide breaks: Paginated/Continuous" renamed to "Section breaks: Page break between sections / Continuous flow" — clearer and avoids confusion with the view mode
- **PDF margins**: `number_input` (integers, mm) replaces free-text input — prevents invalid CSS values
- **Dockerfile**: Added `playwright install --with-deps chromium` to install Chromium and system dependencies for PDF export on Render

## [0.4.18] — 2026-03-13

### Changed
- **`_install_global_commands` directory support**: `stx update` Step 4 now copies shared command directories (not just files) to `~/.claude/commands/`, enabling `/stx-issue:*` commands globally

## [0.4.17] — 2026-03-12

### Fixed
- **`stx run` uses project `.venv` via `uv run`**: `stx run` now delegates to `uv run streamlit run` instead of `sys.executable -m streamlit`, so project-specific extras (`streamtex[ai]`, `streamtex[pdf]`, etc.) are available at runtime (fixes #1)

### Changed
- **Command namespace `stx-` prefix convention**: All Claude command namespaces renamed to use `stx-` prefix — `/developer:` → `/stx-developer:`, `/project:` → `/stx-project:`, `/designer:` merged into `/stx-designer:`, `/migration:` → `/stx-migration:`, `/coherence:` → `/stx-coherence:`, `/presentation:` → `/stx-presentation:` (streamtex-claude#1)
- Updated all cross-references in AI_GUIDE.md, README.md, CONTRIBUTING.md, CLAUDE.md, and installed `.claude/` profile copies

## [0.4.16] — 2026-03-12

### Added
- **Test coverage**: 53 new tests — `test_bib_preview` (5), `test_link_config` (6), `test_link_preview` (13), `test_image_utils` (13), `test_image_editor` (10)
- **GitHub issue templates**: Bug report, feature request, question, and docs templates in `.github/ISSUE_TEMPLATE/`

## [0.4.15] — 2026-03-12

### Added
- **`stx run --force`**: Kill any process using the target port before starting — port resolved from `--port` arg, `.streamlit/config.toml`, or default (8501)

## [0.4.14] — 2026-03-12

### Added
- **`stx run` CLI command**: New shortcut to launch StreamTeX projects — `stx run` auto-detects `book.py`, supports `--port`, `--browser` (chrome/firefox/safari/edge), and `--headless` options

## [0.4.13] — 2026-03-12

### Fixed
- **Ordered lists with string `list_type`**: `ListType.__eq__` now accepts string comparison — `list_type="ol"` works correctly alongside `list_type=lt.ordered` (previously `"ol"` silently rendered as unordered)

## [0.4.12] — 2026-03-12

### Added
- **Draggable marker navigation**: `MarkerConfig(draggable=True)` lets users drag the floating navigation bar anywhere on screen (position persisted in localStorage)
- **Collapsible marker navigation**: `MarkerConfig(collapsible=True)` adds a ⋮ button to collapse/expand the navigation bar (state persisted in localStorage)

## [0.4.11] — 2026-03-12

### Fixed
- **Presentation footer in paginated mode**: `st_presentation_footer()` was not called in `_paginated_book()` — footer with slide counter and title now renders correctly in paginated mode
- **Grid cell text overflow**: added `overflow-wrap: break-word` to `st_grid` cell CSS so long text wraps instead of overflowing cell boundaries

## [0.4.10] — 2026-03-12

### Added
- **Coherence audit checks 18-19**: Manifest File Existence (validates all manifest.toml declarations against filesystem) and CLI Template Registry Sync (ensures AVAILABLE_TEMPLATES, click.Choice, template directories, and documentation are aligned)
- **Improved Check 4**: Source existence guard — verifies shared reference files exist before comparing copies
- **Improved Check 8**: Template and preset documentation validation against CLI code

### Fixed
- **Documentation profile manifest**: removed incorrect `stx-designer` command declarations (files never existed in this profile)
- **`presentation_cheatsheet_en.md`**: added missing source file to `shared/references/`
- **CLI `--template` sync**: `click.Choice` in `project_cmd.py` now matches `AVAILABLE_TEMPLATES` (was missing `slides`)
- **Documentation**: corrected CLI template lists across README, stx-guide, and install_cmd help text (was listing stx-designer templates instead of CLI templates)

## [0.4.9] — 2026-03-12

### Added
- **Presentation mode** (`presentation.py`): fullscreen 16/9 slide deck with footer and centering
  - `PresentationConfig` dataclass with aspect ratio, footer, centering, Streamlit UI hiding
  - `set_presentation_config()` / `get_presentation_config()` — DI pattern (matches AIImageConfig)
  - `st_presentation_footer()` — fixed footer bar with slide counter ("Slide N / M — Title")
  - `add_presentation_options()` — sidebar controls for presenter (footer toggle, fullscreen toggle)
  - CSS injection: aspect-ratio enforcement, vertical centering, Streamlit chrome hiding
  - Auto-integration with `st_book()`: footer rendered automatically when config is active
- **SlideBreakConfig.fullscreen** field: when True, forces `space="100vh"` regardless of configured value
  - Hidden mode with fullscreen still renders navigation markers for PageUp/PageDown
- **50+ new tests** in `test_presentation.py` covering config, DI, CSS injection, footer, sidebar
- **`--template slides`** option for `stx project new`: generates a minimal presentation project with 5 illustrative slides, projection-optimized styles, fullscreen 16/9 config, and dark theme

## [0.4.8] — 2026-03-11

### Added
- **Project migration system** (`stx project upgrade`): versioned structural migrations with AST-based compatibility checking
  - `--check` for compatibility verification only (no modifications)
  - `--dry-run` to preview changes before applying
  - `--skip-sync` / `--skip-claude` to skip post-upgrade steps
  - Migration v0.4.0: adds ruff lint config + pyright extraPaths + pre-commit
  - Migration v0.4.6: adds preset extras to dependencies + static/images/ + setup.py
  - `/stx-migrate` Claude skill for assisted code fixes when breaking changes are detected
- **40 new tests** for migration system, compatibility checker, and upgrade CLI
- **10 undocumented exports** now covered in manual blocks: `BlockImportError`, `BlockNotFoundError`, `toc_entries`, `st_chrome_banner`, `PdfMode`, `export_pdf`, `format_entry`, `set_bib_config`, `get_available_models`, `ImageMetadata`
- **New block** `bck_pdf_export.py` in advanced manual (PdfMode + export_pdf + PdfConfig)
- **Cheatsheet updated** with 8 missing exports (AI models, image history, st_chrome_banner)

### Fixed
- 8 incorrect `st_list()` examples in `bck_list_styles.py` (now use context manager pattern)
- `banner_config=` → `banner=` and removed invalid `link_preview=` in `bck_arch_book.py` show_code examples
- Removed invalid `editable=True` on `st_ai_image_widget()` in Claude profile artifacts
- Missing `static/pdf/sample_document.pdf` — added graceful fallback in `bck_static_assets.py`
- `stx-guide.md` synchronized across all 7 copies (was 3 different versions)
- Unused variables in `run-manuals.py` (`patterns`, `defaults`)

## [0.4.7] — 2026-03-11

### Changed
- **CLI refactoring**: `stx workspace` subcommands replaced by top-level commands
  - `stx workspace init . [--preset X]` → `stx install [--preset X]`
  - `stx workspace update` → `stx update`
  - `stx workspace upgrade X` → `stx install --preset X` (in existing workspace)
  - `stx workspace status` → `stx status`
- **New preset**: `power` added between `standard` and `developer` (repos: docs + claude, forces `--project`, extras: pdf, ai, inspector)
- **New options**: `stx install --project NAME --template TEMPLATE` for creating a project during install
  - Templates: project (default), presentation, collection, course
- **Extras per preset** (when `--project` is used): basic/user get pdf; standard gets pdf + ai; power/developer get pdf + ai + inspector
- **35 new tests** for install/update/status commands

### Removed
- `stx workspace` command group (no existing users — replaced by `stx install`/`stx update`/`stx status`)
- Deprecated subcommands: `stx workspace clone`, `stx workspace sync`, `stx workspace link`, `stx workspace hooks`

## [0.4.6] — 2026-03-10

### Added
- Preset extras mapping (`PRESET_EXTRAS`) for automatic dependency management per preset

## [0.4.5] — 2026-03-10

### Added
- AI image project root detection: images save relative to `book.py` instead of `os.getcwd()`
- Managed image versioning: `st_image(editable=True, name=)` checks for managed versions before rendering
- Rename collision guard: `rename_image()` raises `FileExistsError` instead of silently overwriting
- Coherence check 17: Claude component counter verification across profiles

### Changed
- Default `SlideBreakConfig.space` changed from `60vh` to `5vh`
- Default `rule_margin_top` and `rule_margin_bottom` set to `5em`
- `add_slide_break_options()` sidebar widget reads default space from project config instead of hardcoded 60

## [0.4.1] — 2026-03-09

### Fixed
- `stx claude install` no longer fails on read-only shared files

## [0.4.0] — 2026-03-09

### Added
- **AI image generation** (`streamtex.ai`): generate images with OpenAI (gpt-image-1), Google Imagen, and fal.ai (Stable Diffusion) directly in slides
- `st_ai_image(prompt)` — generate and display an AI image
- `st_ai_image_widget()` — interactive generation widget with provider/model selection
- `st_image(editable=True, name=, prompt=)` — unified image editing panel with AI generation
- `AIImageConfig` with DI pattern (`set_ai_image_config()` / `get_ai_image_config()`)
- Deterministic cache: `hash(prompt + provider + size + quality + seed)` avoids duplicate API calls
- Image history with versioned archive (`save_version`, `rollback`, `rename_image`)
- JSON sidecar metadata for full traceability (prompt, provider, model, timestamps)
- Optional extras: `streamtex[ai]`, `streamtex[ai-openai]`, `streamtex[ai-google]`, `streamtex[ai-fal]`

## [0.3.9] — 2026-03-08

### Changed
- `stx update` (formerly `stx workspace update`) now upgrades streamtex in all projects

## [0.3.8] — 2026-03-08

### Added
- `st_grid(breakpoint=)` — responsive breakpoint parameter using container queries
- Mobile navigation bar layout fix

## [0.3.7] — 2026-03-08

### Added
- Floating navigation bar with branding and logo support
- Trackpad inertia cooldown for paginated navigation
- Headless cache warmup mode for faster first-load

### Fixed
- LFS checkout in CI/publish workflow
- Logo packaging for PyPI distribution

## [0.3.6] — 2026-03-07

### Changed
- License changed from MIT to BUSL-1.1 (converts to Apache 2.0 on 2030-11-29)
- Added GitHub Sponsors badge and support section in README

## [0.3.3] — 2026-03-05

### Added
- `stx update` (formerly `stx workspace update`) — single command for all workspace operations: git pull, clone missing repos, uv sync, install pre-commit hooks, update Claude profiles, install global commands. Adds `--dry-run` and `--repair` flags
- `stx update --repair` — detects and fixes broken `.venv`, missing `__init__.py`, broken `[tool.uv.sources]` paths

### Changed
- `stx workspace clone/sync/link/hooks` — deprecated with warning, redirects to `stx update`
- `stx install --preset` output now says `stx update` instead of `stx workspace clone`
- User update workflow simplified from 5 commands to 2: `uv tool install "streamtex[cli]" -U` then `stx update`
- `stx deploy env-sync` — synchronize env vars from `render.yaml` to live Render services via the Render API (`--dry-run`, `--service` options, interactive redeploy prompt)
- `.github/workflows/render-deploy.yml` — GitHub Actions workflow for auto-deploying all Render services on push to `main` (bypasses Render's GitHub App, reads service names from `render.yaml`)
- `AI_GUIDE.md` — complete zero-code workflow guide for Claude/Cursor users (22 commands, 4 agents, 10 blueprints, 4 profiles, FAQ)
- `CONTRIBUTING.md` — contributor guidelines for code, content, and AI profile contributions
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1 reference
- `.github/ISSUE_TEMPLATE/bug_report.md` — structured bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` — structured feature request template
- `.github/PULL_REQUEST_TEMPLATE.md` — pull request checklist template
- README badges: PyPI version, Python versions, License, CI status, Claude Code, Cursor

### Changed
- `README.md` — repositioned as "AI-powered content framework" with dual Getting Started (zero-code with Claude/Cursor + code-first with Python), AI-Powered Features section, Claude & Cursor Integration section
- `pyproject.toml` — updated description, keywords (`ai-assisted`, `claude`, `cursor`, `no-code`, `generative-ai`), classifiers (AI, Presentation), project URLs (AI Guide, Claude Profiles)
- `streamtex-claude/README.md` — enriched with end-user Quick Start, command overview tables, agent reference, cross-links to AI Guide

## [0.3.1] - 2026-03-03

### Fixed
- Fixed broken documentation URLs in README (intro, advanced, deploy manuals)
- Added missing Developer Guide link to README
- Fixed Cheatsheet and Coding Standards reference links (moved from `documentation/` to `.claude/references/`)
- Fixed examples section: repo name `streamtex-manuals` → `streamtex-docs`, corrected book.py path

## [0.3.0] - 2026-03-02

### Added
- First public release on PyPI
- BUSL-1.1 license (converts to Apache 2.0 on 2030-11-29)
- PyPI-oriented README with installation and quick start guide
- GitHub Actions workflow for automated publishing via Trusted Publishing
- CHANGELOG

### Changed
- Moved `streamlit-ace` from required to optional dependency (`pip install "streamtex[inspector]"`)
- Updated project metadata (authors, classifiers, keywords, URLs)

## [0.2.0] - 2026-02-20

### Added
- **Bibliography system** (`streamtex.bib`): BibTeX/RIS/CSL-JSON import, citations, formatted references
- **Collection system** (`streamtex.collection`): multi-project hubs with TOML configuration
- **Block helpers** (`streamtex.block_helpers`): hybrid helper system with 3 usage modes (functions, config injection, OOP inheritance)
- **Block registry** (`streamtex.blocks`): `ProjectBlockRegistry` for single-project lazy loading, `LazyBlockRegistry` for multi-source resolution
- **Google Sheets** (`streamtex.gsheet`): load spreadsheet data as DataFrames
- **Export system** (`streamtex.export`): self-contained HTML export with dual rendering pipeline
- **Export widgets** (`streamtex.export_widgets`): export-aware wrappers for Streamlit widgets
- **Diagram rendering**: Mermaid, PlantUML, TikZ with pan/zoom support
- **LaTeX rendering**: math formulas and full documents via LaTeX.js
- **Navigation markers** (`streamtex.marker`): slide-like PageUp/PageDown navigation
- **Banner system** (`streamtex.banner`): configurable paginated navigation (full/compact/hidden presets)
- **Zoom controls** (`streamtex.zoom`): CSS-based width and zoom adjustments
- **Block inspector** (`streamtex.inspector`): live code editor in sidebar
- **Link preview** (`streamtex.link_preview`): hover preview scaffold

### Core
- `st_write` with tuple support for inline mixed-style text
- `st_grid` for CSS Grid layouts with responsive columns
- `st_block` / `st_span` context managers
- `st_list` with ul/ol support and centered alignment
- `st_markdown` with file loading
- `st_image` with base64 encoding and MIME detection
- `st_code` with Pygments syntax highlighting
- `st_book` with paginated and continuous modes
- `st_toc` with auto-numbering and anchoring
- Style composition with `+` / `-` operators
