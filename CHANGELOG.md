# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
