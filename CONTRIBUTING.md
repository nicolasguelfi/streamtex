# Contributing to StreamTeX

Thank you for your interest in contributing to StreamTeX!

## Ways to Contribute

### As a Developer (Python)

1. Fork the repository and create a feature branch
2. Install dependencies: `uv sync`
3. Make your changes following [coding standards](https://github.com/nicolasguelfi/streamtex/blob/main/.claude/references/coding_standards.md)
4. Run tests: `uv run pytest tests/ -v`
5. Run linter: `uv run ruff check streamtex/`
6. Submit a Pull Request

### As a Content Creator (AI-Assisted)

You don't need to write Python code to contribute content:

1. Install a Claude profile from [streamtex-claude](https://github.com/nicolasguelfi/streamtex-claude)
2. Create example projects using `/stx-block:init`
3. Submit interesting projects as example repositories

### As a Claude Profile Developer

Improve the AI-assisted experience:

1. Add new commands, skills, or agents in `streamtex-claude/profiles/`
2. Follow the `manifest.toml` structure for each profile
3. Test commands against real projects before submitting

## Development Setup

### Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (package manager)

### Install

```bash
git clone https://github.com/nicolasguelfi/streamtex
cd streamtex
uv sync
```

### Test

```bash
uv run pytest tests/ -v
```

### Lint

```bash
uv run ruff check streamtex/
uv run ruff check streamtex/ --fix  # auto-fix
```

## Conventions

### Environment variables

Environment variables are reserved for four purposes only:

1. **Secrets** — API keys, passwords, tokens (`STX_PASSWORD`,
   `STX_OPENAI_API_KEY`, `COOLIFY_API_TOKEN`, …). Prefer a project-local
   `.env` file (loaded via `python-dotenv`) over exporting in the shell.
2. **System integration** — values the OS or another tool owns and we only
   read (`PATH`, `VIRTUAL_ENV`, `LIBGS`, `PLAYWRIGHT_BROWSERS_PATH`, …). This
   also covers *environment capability* facts consumed at install/build time,
   e.g. `STX_SKIP_BROWSER_INSTALL` (the browser is already cached / cannot be
   installed here) — set once in CI/Docker, not a per-project choice.
3. **Subprocess IPC** — values we set to pass to a child process that reads
   its own environment (`HCLOUD_TOKEN` for `hcloud`, `UV_NO_SOURCES` for
   `uv`, …).
4. **Deployment- / runtime-varying config** — values that legitimately differ
   per deployment environment and must be injectable without editing committed
   files (12-factor). Examples: `STX_URL_<PROJECT>` (per-environment URL
   override in a collection hub), `STX_GATE` (local preview of the auth gate,
   the mirror of how production toggles it via env). These are read at runtime
   by `book.py` / Streamlit, where no CLI flag can attach, and are often paired
   with a secret (`STX_GATE` ↔ `STX_PASSWORD`) — splitting them would fragment
   coupled settings.

**Do not** introduce an environment variable to toggle *project behaviour* or
silence a warning — that is the one thing env vars must never do. Use a CLI
flag or a key in the project's `stx.toml` instead. Context-dependent behaviour
(e.g. "are we running in the project venv?") must be derived in-process
(inspect `sys.executable`, read a file), never signalled by an env flag.
Removed examples of this anti-pattern: `STX_NO_DIVERGENCE_CHECK`,
`STX_DELEGATED`.

Rationale: shell-level env vars are invisible, machine-specific, and leak
across projects — fine for secrets, system facts, IPC, and deploy-varying
config (categories 1–4), but wrong for behaviour switches, which belong in CLI
flags or `stx.toml` so they are explicit, discoverable, and committed.

## Pull Request Guidelines

- One feature or fix per PR
- Include tests for new functionality
- Run lint and tests before submitting
- Reference the relevant issue number if applicable
- Update `CHANGELOG.md` for user-facing changes
- Update `AI_GUIDE.md` if your change affects AI workflows

## Code of Conduct

This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
Contact: nicolas.guelfi@laposte.net

## Questions?

Open an [issue](https://github.com/nicolasguelfi/streamtex/issues) or start a
[discussion](https://github.com/nicolasguelfi/streamtex/discussions).
