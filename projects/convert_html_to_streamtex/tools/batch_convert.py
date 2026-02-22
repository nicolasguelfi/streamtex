"""Batch converter: HTML blocks -> StreamTeX Python files in shared/blocks/.

Usage:
    uv run python tools/batch_convert.py                # Convert all blocks
    uv run python tools/batch_convert.py --filter "bck_title_*"  # Filter by pattern
    uv run python tools/batch_convert.py --dry-run      # Simulate without writing
    uv run python tools/batch_convert.py --force        # Overwrite existing blocks
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import time
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.html_parser import parse_html
from tools.block_generator import generate_block


def load_image_registry(registry_path: Path) -> dict:
    """Load image registry JSON, return empty dict if missing."""
    if registry_path.exists():
        with open(registry_path) as f:
            return json.load(f)
    return {}


def should_decompose(parsed) -> bool:
    """Determine if a block should be decomposed into sub-blocks."""
    html_path = PROJECT_ROOT / "exports" / "html" / parsed.name / "index.html"
    file_size = html_path.stat().st_size if html_path.exists() else 0
    return (
        file_size > 20_000
        or len(parsed.all_images) > 10
        or parsed.has_tables and len(parsed.all_images) > 5
    )


def discover_blocks(exports_dir: Path, pattern: str | None = None) -> list[Path]:
    """Find all block directories in exports/html/."""
    block_dirs = []
    for d in sorted(exports_dir.iterdir()):
        if d.is_dir() and (d / "index.html").exists():
            if pattern is None or fnmatch.fnmatch(d.name, pattern):
                block_dirs.append(d)
    return block_dirs


def main():
    parser = argparse.ArgumentParser(description="Convert HTML blocks to StreamTeX")
    parser.add_argument(
        "--filter", type=str, default=None,
        help='Filter blocks by glob pattern (e.g. "bck_title_*")')
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate without writing files")
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing block files")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of blocks to convert (for testing)")
    args = parser.parse_args()

    exports_dir = PROJECT_ROOT / "exports" / "html"
    dest_dir = PROJECT_ROOT / "shared" / "blocks"
    registry_path = PROJECT_ROOT / "tools" / "image_registry.json"

    if not exports_dir.exists():
        print(f"ERROR: exports directory not found: {exports_dir}")
        sys.exit(1)

    # Load image registry
    image_registry = load_image_registry(registry_path)
    if not image_registry:
        print("WARNING: No image_registry.json found. Image names will use fallback.")

    # Discover blocks
    block_dirs = discover_blocks(exports_dir, args.filter)
    if args.limit:
        block_dirs = block_dirs[:args.limit]

    total = len(block_dirs)
    print(f"Found {total} blocks to convert" + (f" (filter: {args.filter})" if args.filter else ""))

    if args.dry_run:
        print("DRY RUN — no files will be written\n")

    # Ensure output dir exists
    if not args.dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "sub").mkdir(exist_ok=True)

    stats = {"simple": 0, "medium": 0, "complex": 0, "skipped": 0, "errors": 0}
    t0 = time.time()

    for i, block_dir in enumerate(block_dirs, 1):
        block_name = block_dir.name
        dest_file = dest_dir / f"{block_name}.py"

        # Skip if exists and not forcing
        if dest_file.exists() and not args.force and not args.dry_run:
            stats["skipped"] += 1
            continue

        try:
            # Parse HTML
            html_file = block_dir / "index.html"
            parsed = parse_html(html_file)

            # Generate StreamTeX code
            code = generate_block(parsed, image_registry)

            if not args.dry_run:
                dest_file.write_text(code, encoding="utf-8")

            stats[parsed.estimated_complexity] += 1

            status = "DRY" if args.dry_run else "OK"
            print(f"  [{i}/{total}] {status} {block_name} ({parsed.estimated_complexity})")

        except Exception as e:
            stats["errors"] += 1
            print(f"  [{i}/{total}] ERROR {block_name}: {e}")

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Conversion complete in {elapsed:.1f}s")
    print(f"  Simple:  {stats['simple']}")
    print(f"  Medium:  {stats['medium']}")
    print(f"  Complex: {stats['complex']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors:  {stats['errors']}")
    print(f"  Total:   {total}")

    if not args.dry_run and stats["errors"] == 0:
        # Generate __init__.py for block registry
        _generate_init(dest_dir)
        print(f"\nGenerated {dest_dir / '__init__.py'}")

    if stats["errors"] > 0:
        print(f"\n{stats['errors']} errors occurred. Fix and re-run with --force.")

    print(f"\nNext steps:")
    print(f"  1. Create blocks.csv for each course in courses/{{course}}/")
    print(f"  2. Run: uv run python tools/book_generator.py --all")


def _generate_init(dest_dir: Path):
    """Generate shared/blocks/__init__.py with LazyBlockRegistry."""
    block_files = sorted(
        f.stem for f in dest_dir.glob("bck*.py")
        if f.stem != "__init__"
    )

    code = '''"""Shared block registry — all converted HTML blocks.

Auto-generated by batch_convert.py. Do not edit manually.
"""

from pathlib import Path
from streamtex import LazyBlockRegistry

_registry = LazyBlockRegistry([str(Path(__file__).parent)])


def __getattr__(name: str):
    return _registry.get(name)


def __dir__():
    return sorted(_registry.list_blocks())
'''
    (dest_dir / "__init__.py").write_text(code, encoding="utf-8")


if __name__ == "__main__":
    main()
