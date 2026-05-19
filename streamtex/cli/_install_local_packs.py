"""Install local primary/secondary packs declared in stx.toml.

Invoked from the Dockerfile after `COPY . .` to ensure each
`[[packs]] type="local"` entry with a *relative* path is pip-installed
inside the container — without this step, entry-point discovery would
miss the local pack and ``stx validate`` would report PR002.

Absolute paths are skipped with a warning: they cannot exist inside the
build context. Use ``stx deploy preflight`` (G4b) to surface these
upstream of build time.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _read_stx_toml(stx_toml: Path) -> dict:
    import tomllib

    with stx_toml.open("rb") as fh:
        return tomllib.load(fh)


def _iter_local_packs(data: dict):
    for entry in data.get("packs", []):
        if isinstance(entry, dict) and entry.get("type") == "local":
            yield entry


def install_local_packs(project_dir: Path) -> int:
    """Install each local pack with a relative path. Returns exit code."""
    stx_toml = project_dir / "stx.toml"
    if not stx_toml.is_file():
        print("[install-local-packs] no stx.toml — skipping", flush=True)
        return 0

    data = _read_stx_toml(stx_toml)
    failures = 0
    for entry in _iter_local_packs(data):
        path_raw = entry.get("path")
        if not path_raw:
            print(
                f"[install-local-packs] WARN: pack '{entry.get('name', '<unnamed>')}' "
                f"has no 'path' — skipping",
                flush=True,
            )
            continue
        path = Path(path_raw)
        if path.is_absolute():
            print(
                f"[install-local-packs] WARN: pack '{entry.get('name', '<unnamed>')}' "
                f"path '{path_raw}' is absolute — skipping (use a relative path "
                f"or `stx component promote` to a git pack for deployment).",
                flush=True,
            )
            continue
        target = (project_dir / path).resolve()
        if not target.is_dir():
            print(
                f"[install-local-packs] WARN: pack '{entry.get('name', '<unnamed>')}' "
                f"path '{target}' does not exist — skipping.",
                flush=True,
            )
            continue
        if not (target / "pyproject.toml").is_file():
            print(
                f"[install-local-packs] WARN: pack '{entry.get('name', '<unnamed>')}' "
                f"at '{target}' has no pyproject.toml — skipping.",
                flush=True,
            )
            continue
        print(
            f"[install-local-packs] installing '{entry.get('name', target.name)}' "
            f"from {target}",
            flush=True,
        )
        result = subprocess.run(
            ["uv", "pip", "install", "--no-deps", "-e", str(target)],
            cwd=str(project_dir),
        )
        if result.returncode != 0:
            failures += 1
            print(
                f"[install-local-packs] FAIL: '{entry.get('name', target.name)}' "
                f"exit code {result.returncode}",
                flush=True,
            )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(install_local_packs(Path.cwd()))
