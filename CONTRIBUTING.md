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
2. Create example projects using `/stx-project:project-init`
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
