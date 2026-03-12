Run the linter on the StreamTeX codebase and fix issues.

1. Run `uv run ruff check streamtex/` from the project root
2. If there are auto-fixable issues, run `uv run ruff check --fix streamtex/`
3. Report remaining issues that need manual attention
4. Run `uv run pytest tests/ -v` to confirm fixes didn't break anything
5. If pre-commit is not installed, recommend: `uv run pre-commit install`
