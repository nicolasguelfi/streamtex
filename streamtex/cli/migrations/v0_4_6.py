"""Migration v0.4.6 — Add preset extras (pdf, ai, inspector) and structural files."""

import os
import re

from .base import Migration, MigrationResult
from .registry import register


def _get_workspace_extras(project_path: str) -> list[str]:
    """Determine the extras for this project based on workspace preset."""
    try:
        from ..workspace_cmd import PRESET_EXTRAS, find_workspace_root, load_stx_toml

        ws_root = find_workspace_root(project_path)
        if ws_root:
            config = load_stx_toml(ws_root)
            preset = config.get("workspace", {}).get("preset", "standard")
            return PRESET_EXTRAS.get(preset, ["pdf"])
    except Exception:
        pass
    return ["pdf"]


@register
class MigrateV046(Migration):
    version = "0.4.6"
    description = "Add preset extras (pdf, ai, inspector) to dependencies"

    def check(self, project_path: str) -> bool:
        pyproject = os.path.join(project_path, "pyproject.toml")
        if not os.path.isfile(pyproject):
            return False
        with open(pyproject, encoding="utf-8") as f:
            content = f.read()

        # Need migration if streamtex dep has no extras brackets
        m = re.search(r'"streamtex(\[[^\]]*\])?>=', content)
        if m is None:
            return False
        extras_str = m.group(1) or ""

        expected = _get_workspace_extras(project_path)
        for extra in expected:
            if extra not in extras_str:
                return True
        return False

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

        extras = _get_workspace_extras(project_path)
        extras_str = ",".join(extras)

        # Replace streamtex dep line: "streamtex>=X.Y.Z" or "streamtex[old]>=X.Y.Z"
        pattern = r'"streamtex(?:\[[^\]]*\])?>=([\d.]+)"'
        m = re.search(pattern, content)
        if m:
            version_num = m.group(1)
            new_dep = f'"streamtex[{extras_str}]>={version_num}"'
            old_dep = m.group(0)
            if old_dep != new_dep:
                content = content.replace(old_dep, new_dep)
                changes.append(f"Updated dependency: {old_dep} -> {new_dep}")

        # Ensure static/images/ directory exists
        images_dir = os.path.join(project_path, "static", "images")
        if not os.path.isdir(images_dir):
            if not dry_run:
                os.makedirs(images_dir, exist_ok=True)
            changes.append("Created static/images/ directory")

        # Ensure setup.py exists
        setup_py = os.path.join(project_path, "setup.py")
        if not os.path.isfile(setup_py):
            name = os.path.basename(project_path)
            if not dry_run:
                with open(setup_py, "w", encoding="utf-8") as f:
                    f.write(f'"""Setup for {name} project."""\n')
            changes.append("Created setup.py")

        if changes and not dry_run:
            with open(pyproject, "w", encoding="utf-8") as f:
                f.write(content)

        return MigrationResult(
            version=self.version,
            description=self.description,
            applied=bool(changes),
            changes=changes,
        )
