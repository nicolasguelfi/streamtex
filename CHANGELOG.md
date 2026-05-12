# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.18] — 2026-05-12

### Fixed
- **Marker-runtime observer now actually executes (real fix)**: 0.6.17 attempted to keep the observer inline in the host page via `st.html(..., unsafe_allow_javascript=True)`, but verification on Streamlit 1.57.0 (and 1.54+) showed `window.__stxMarkerObs === undefined` and `.stx-grid` count `0` — the `unsafe_allow_javascript` proto field is forwarded by the Python API but the released Streamlit frontend does not honor it in any version checked (1.44 through 1.57). The visible regressions from 0.6.16 (broken grids, missing `st_zoom` containment, ignored custom font sizes, AI-image WYSIWYG zoom dropping to 100%) persisted in 0.6.17.
- `streamtex/marker_runtime.py:inject_marker_runtime()` now splits injection: CSS through `st.html("<style>…</style>")` (inline, host page) and JS through `streamlit.components.v1.html("<script>…</script>", height=0)` (0-pixel iframe). Same pattern already proven by `streamtex/marker.py` and `streamtex/bib_preview.py`.
- `streamtex/static/js/stx_marker_observer.js` rewritten to operate on `window.parent.document`: idempotency guard moves to `hostWin.__stxMarkerObs`, `scan()` walks the parent body, the `MutationObserver` is constructed via `hostWin.MutationObserver` and observes `hostDoc.body`. Same-origin Streamlit allows the iframe to reach back into the host DOM.
- `tests/test_marker_runtime.py`: `test_injects_once_per_session` now patches both `st.html` and `components.html`; new `test_css_via_st_html` and `test_js_via_components_html` lock in the split-call contract (CSS goes through `st.html`, JS goes through `components.html` with `height=0`); `test_js_observer_has_idempotency_guard` asserts `hostWin.__stxMarkerObs`.

### Notes
- No public API change. No new env var. Users on 0.6.17 (or 0.6.16) just need to upgrade.
- `components.v1.html` is deprecated in Streamlit 1.56 but is the only path that reliably executes injected `<script>` tags as of 2026-05-12; the deprecation will be revisited if and when a released Streamlit honors `unsafe_allow_javascript` on the frontend.
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
