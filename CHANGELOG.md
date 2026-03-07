# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.6] — 2026-03-07

### Changed
- License changed from MIT to BUSL-1.1 (converts to Apache 2.0 on 2030-11-29)
- Added GitHub Sponsors badge and support section in README

## [0.3.3] — 2026-03-05

### Added
- `stx workspace update` — single command for all workspace operations: git pull, clone missing repos, uv sync, install pre-commit hooks, update Claude profiles, install global commands. Adds `--dry-run` and `--repair` flags
- `stx workspace update --repair` — detects and fixes broken `.venv`, missing `__init__.py`, broken `[tool.uv.sources]` paths

### Changed
- `stx workspace clone/sync/link/hooks` — deprecated with warning, redirects to `stx workspace update`
- `stx workspace upgrade` output now says `stx workspace update` instead of `stx workspace clone`
- User update workflow simplified from 5 commands to 2: `uv tool install "streamtex[cli]" -U` then `stx workspace update`
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
