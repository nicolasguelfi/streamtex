"""Migration v0.4.0 — Add ruff lint config and pyright extraPaths."""

import os

from .base import Migration, MigrationResult
from .registry import register


@register
class MigrateV040(Migration):
    version = "0.4.0"
    description = "Add ruff lint config and pyright extraPaths"

    def check(self, project_path: str) -> bool:
        pyproject = os.path.join(project_path, "pyproject.toml")
        if not os.path.isfile(pyproject):
            return False
        with open(pyproject, encoding="utf-8") as f:
            content = f.read()
        # Need migration if ruff config or pyright config is missing
        return "[tool.ruff.lint]" not in content or "[tool.pyright]" not in content

    def apply(self, project_path: str, *, dry_run: bool = False) -> MigrationResult:
        changes: list[str] = []
        pyproject = os.path.join(project_path, "pyproject.toml")

        if not os.path.isfile(pyproject):
            return MigrationResult(
                version=self.version,
                description=self.description,
                applied=False,
                skipped_reason="pyproject.toml not found",
            )

        with open(pyproject, encoding="utf-8") as f:
            content = f.read()

        modified = False

        # Add [tool.ruff.lint] if missing
        if "[tool.ruff.lint]" not in content:
            ruff_block = '\n[tool.ruff.lint]\nignore = ["F403", "F405", "E701", "E741"]\n'
            if "[tool.uv]" in content:
                content = content.replace("[tool.uv]", ruff_block + "\n[tool.uv]")
            else:
                content += ruff_block
            changes.append("Added [tool.ruff.lint] with standard ignores")
            modified = True

        # Add [tool.pyright] if missing
        if "[tool.pyright]" not in content:
            pyright_block = '\n[tool.pyright]\nextraPaths = [".."]\n'
            content += pyright_block
            changes.append("Added [tool.pyright] extraPaths")
            modified = True

        if modified and not dry_run:
            with open(pyproject, "w", encoding="utf-8") as f:
                f.write(content)

        # Add .pre-commit-config.yaml if missing
        precommit = os.path.join(project_path, ".pre-commit-config.yaml")
        if not os.path.isfile(precommit):
            precommit_content = """\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.2
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
"""
            if not dry_run:
                with open(precommit, "w", encoding="utf-8") as f:
                    f.write(precommit_content)
            changes.append("Created .pre-commit-config.yaml")

        return MigrationResult(
            version=self.version,
            description=self.description,
            applied=bool(changes),
            changes=changes,
        )
