"""Validate generated StreamTeX block files.

Checks:
- Python syntax validity
- Required imports present
- BlockStyles class defined
- build() function defined
- No raw HTML strings
- Image references exist in registry

Usage:
    uv run python tools/validate_blocks.py
    uv run python tools/validate_blocks.py --block bck_title_break
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def validate_block(block_path: Path, image_registry: dict) -> list[str]:
    """Validate a single block file. Returns list of issues (empty = OK)."""
    issues = []
    code = block_path.read_text(encoding="utf-8")

    # 1. Python syntax
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        issues.append(f"SYNTAX ERROR: {e}")
        return issues

    # 2. Required imports
    if "from streamtex import" not in code:
        issues.append("MISSING: streamtex import")
    if "from shared.custom.styles import" not in code:
        issues.append("MISSING: shared styles import")

    # 3. BlockStyles class
    has_block_styles = any(
        isinstance(node, ast.ClassDef) and node.name == "BlockStyles"
        for node in ast.walk(tree)
    )
    if not has_block_styles:
        issues.append("MISSING: BlockStyles class")

    # 4. build() function
    has_build = any(
        isinstance(node, ast.FunctionDef) and node.name == "build"
        for node in ast.walk(tree)
    )
    if not has_build:
        issues.append("MISSING: build() function")

    # 5. No raw HTML (basic check)
    raw_html_patterns = ["<div", "<span", "<table", "<p>", "<br>", "<img"]
    for pattern in raw_html_patterns:
        if f'"{pattern}' in code or f"'{pattern}" in code:
            issues.append(f"RAW HTML: found '{pattern}' string literal")
            break

    # 6. Image references
    import re
    image_refs = re.findall(r'uri=["\']([^"\']+\.png)["\']', code)
    if image_registry:
        known_images = {v["name"] for v in image_registry.values()}
        for ref in image_refs:
            if ref not in known_images:
                issues.append(f"IMAGE NOT IN REGISTRY: {ref}")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate StreamTeX block files")
    parser.add_argument(
        "--block", type=str, default=None,
        help="Validate a specific block by name")
    args = parser.parse_args()

    blocks_dir = PROJECT_ROOT / "shared" / "blocks"
    registry_path = PROJECT_ROOT / "tools" / "image_registry.json"

    image_registry = {}
    if registry_path.exists():
        with open(registry_path) as f:
            image_registry = json.load(f)

    if args.block:
        block_path = blocks_dir / f"{args.block}.py"
        if not block_path.exists():
            print(f"ERROR: block not found: {block_path}")
            sys.exit(1)
        issues = validate_block(block_path, image_registry)
        if issues:
            print(f"FAIL {args.block}:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"OK {args.block}")
    else:
        block_files = sorted(blocks_dir.glob("bck*.py"))
        total = len(block_files)
        ok_count = 0
        fail_count = 0

        for block_path in block_files:
            issues = validate_block(block_path, image_registry)
            if issues:
                fail_count += 1
                print(f"FAIL {block_path.stem}:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                ok_count += 1

        print(f"\n{'=' * 40}")
        print(f"Total: {total}  OK: {ok_count}  FAIL: {fail_count}")


if __name__ == "__main__":
    main()
