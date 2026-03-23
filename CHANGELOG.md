# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
