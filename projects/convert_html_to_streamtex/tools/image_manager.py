"""
Image Manager for HTML-to-StreamTeX conversion.

Scans all images in exports/html/*/images/ directories, deduplicates them
by MD5 hash, generates semantic names using Claude Vision API (Haiku model),
and deploys unique images to shared/static/images/.

Usage:
    uv run python tools/image_manager.py
    uv run python tools/image_manager.py --no-vision
    uv run python tools/image_manager.py --exports-dir exports/html --target-dir shared/static/images
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import re
import shutil
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional dependency: anthropic
# ---------------------------------------------------------------------------
try:
    import anthropic

    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALID_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

VISION_PROMPT = (
    "Generate a filename for this image using this format: "
    "{type}_{subtype}_{tags}\n"
    "- type: category (animal, diagram, screenshot, banner, icon, "
    "chart, photo, logo, illustration)\n"
    "- subtype: specific subject (1 word, lowercase)\n"
    "- tags: 1-3 distinctive words separated by hyphens\n"
    "Examples: animal_frog_orange-wall, diagram_cnn_architecture-layers\n"
    "Reply with ONLY the filename, no extension, no explanation."
)

VISION_MODEL = "claude-haiku-4-5-20251001"
VISION_MAX_TOKENS = 100

# Rate-limiting: maximum requests per minute to the Vision API
VISION_RPM = 50
_VISION_INTERVAL = 60.0 / VISION_RPM


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _md5(file_path: Path) -> str:
    """Compute the MD5 hex digest of a file."""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _mime_type(file_path: Path) -> str:
    """Return the MIME type for an image file."""
    mime, _ = mimetypes.guess_type(str(file_path))
    if mime:
        return mime
    ext = file_path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")


def _sanitize_name(raw: str) -> str:
    """Sanitize a Vision-generated name to filesystem-safe characters.

    Ensures the result follows the convention:
        {type}_{subtype}_{tags}
    with only lowercase alphanumerics and hyphens within each part.
    """
    # Strip whitespace and any extension the model may have added
    name = raw.strip().lower()
    name = re.sub(r"\.(png|jpe?g|gif|svg|webp)$", "", name)

    # Replace any character that is not alphanumeric, underscore, or hyphen
    name = re.sub(r"[^a-z0-9_-]", "-", name)

    # Collapse consecutive hyphens or underscores
    name = re.sub(r"-{2,}", "-", name)
    name = re.sub(r"_{2,}", "_", name)

    # Strip leading/trailing hyphens and underscores
    name = name.strip("-_")

    return name if name else "unknown_image_unclassified"


def _image_dimensions(file_path: Path) -> tuple[int | None, int | None]:
    """Try to read width and height from a PNG header (first 24 bytes).

    Returns (width, height) or (None, None) if the file is not a PNG
    or cannot be read.
    """
    if file_path.suffix.lower() != ".png":
        return None, None
    try:
        with open(file_path, "rb") as f:
            header = f.read(24)
            if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
                import struct

                width = struct.unpack(">I", header[16:20])[0]
                height = struct.unpack(">I", header[20:24])[0]
                return width, height
    except OSError:
        pass
    return None, None


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def build_image_inventory(exports_dir: Path) -> dict:
    """Scan all images under exports_dir/*/images/, compute MD5, detect duplicates.

    Returns a dict keyed by MD5 hash:
        {
            "<md5>": {
                "representative": Path,   # one representative file path
                "originals": [
                    {"block": str, "file": str, "path": Path},
                    ...
                ],
                "size_bytes": int,
            },
            ...
        }
    """
    inventory: dict[str, dict] = {}
    total_count = 0

    for block_dir in sorted(exports_dir.iterdir()):
        if not block_dir.is_dir():
            continue
        images_dir = block_dir / "images"
        if not images_dir.is_dir():
            continue

        for img_file in sorted(images_dir.iterdir()):
            if not img_file.is_file():
                continue
            if img_file.suffix.lower() not in VALID_IMAGE_EXTENSIONS:
                continue

            total_count += 1
            md5 = _md5(img_file)
            origin = {
                "block": block_dir.name,
                "file": img_file.name,
                "path": img_file,
            }

            if md5 not in inventory:
                inventory[md5] = {
                    "representative": img_file,
                    "originals": [origin],
                    "size_bytes": img_file.stat().st_size,
                }
            else:
                inventory[md5]["originals"].append(origin)

    unique_count = len(inventory)
    duplicate_count = total_count - unique_count
    print(f"  Scanned {total_count} images across {exports_dir}")
    print(f"  Unique: {unique_count} | Duplicates: {duplicate_count}")

    return inventory


def analyze_image_for_naming(image_path: Path, client=None) -> str:
    """Call Claude Haiku Vision to generate a semantic filename.

    Args:
        image_path: Path to the image file.
        client: An optional anthropic.Anthropic client instance.
                If None, a new client is created.

    Returns:
        A sanitized semantic name (without extension).

    Raises:
        RuntimeError: If the anthropic package is not installed.
    """
    if not _HAS_ANTHROPIC:
        raise RuntimeError(
            "The 'anthropic' package is required for Vision naming. "
            "Install it with: uv add anthropic\n"
            "Or use --no-vision to skip API calls."
        )

    if client is None:
        client = anthropic.Anthropic()

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    mime = _mime_type(image_path)

    try:
        response = client.messages.create(
            model=VISION_MODEL,
            max_tokens=VISION_MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": VISION_PROMPT,
                        },
                    ],
                }
            ],
        )
        raw_name = response.content[0].text.strip()
        return _sanitize_name(raw_name)

    except Exception as exc:
        print(f"    [WARN] Vision API failed for {image_path.name}: {exc}")
        return ""


def generate_fallback_name(block_name: str, image_file: str, index: int) -> str:
    """Generate a fallback name without the Vision API.

    Uses the block name and image filename to create a descriptive name.
    Format: illustration_{block-short-name}_{image-index}

    Args:
        block_name: The block directory name (e.g. "bck_ethics_overview").
        image_file: The original image filename (e.g. "image3.png").
        index: A numeric index for disambiguation among images with the
               same block origin.

    Returns:
        A sanitized fallback name (without extension).
    """
    # Remove common prefixes to shorten the name
    short = block_name
    for prefix in ("bck_", "bckcp_"):
        if short.startswith(prefix):
            short = short[len(prefix):]
            break

    # Replace underscores with hyphens for the subtype/tags parts
    short = short.replace("_", "-")

    # Extract any number from the original filename (e.g. "image3.png" -> "3")
    num_match = re.search(r"(\d+)", image_file)
    img_num = num_match.group(1) if num_match else str(index)

    name = f"illustration_{short}_img{img_num}"
    return _sanitize_name(name)


def _resolve_duplicate_names(inventory: dict) -> None:
    """Ensure all semantic names in the inventory are unique.

    If two different hashes end up with the same name, append a numeric
    suffix (_02, _03, ...) to resolve collisions.
    """
    name_counts: dict[str, list[str]] = {}
    for md5, entry in inventory.items():
        name = entry.get("name", "")
        if not name:
            continue
        name_counts.setdefault(name, []).append(md5)

    for name, md5_list in name_counts.items():
        if len(md5_list) <= 1:
            continue
        # First occurrence keeps the name, subsequent ones get suffixes
        for i, md5 in enumerate(md5_list[1:], start=2):
            inventory[md5]["name"] = f"{name}_{i:02d}"


def deploy_images(inventory: dict, target_dir: Path) -> None:
    """Copy deduplicated images to the target directory.

    Each unique image (by MD5) is copied once, using its semantic name.

    Args:
        inventory: The image inventory dict (keyed by MD5).
        target_dir: Destination directory (e.g. shared/static/images/).
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    deployed = 0
    skipped = 0

    for md5, entry in inventory.items():
        name = entry.get("name")
        if not name:
            print(f"  [WARN] No name for hash {md5[:12]}..., skipping")
            skipped += 1
            continue

        src = entry["representative"]
        ext = src.suffix.lower()
        dest = target_dir / f"{name}{ext}"

        if dest.exists():
            # Check if it is the same file (same size as a quick check)
            if dest.stat().st_size == entry["size_bytes"]:
                skipped += 1
                continue

        shutil.copy2(src, dest)
        deployed += 1

    print(f"  Deployed {deployed} images to {target_dir}")
    if skipped:
        print(f"  Skipped {skipped} (already present or unnamed)")


def save_registry(inventory: dict, registry_path: Path) -> None:
    """Write image_registry.json from the inventory.

    The output format matches the specification in PLAN.md section 5.4.

    Args:
        inventory: The image inventory dict (keyed by MD5).
        registry_path: Path to write the JSON file.
    """
    registry: dict[str, dict] = {}

    for md5, entry in inventory.items():
        name = entry.get("name", "")
        ext = entry["representative"].suffix.lower()

        # Parse type/subtype/tags from the name
        parts = name.split("_", 2) if name else []
        img_type = parts[0] if len(parts) >= 1 else "unknown"
        subtype = parts[1] if len(parts) >= 2 else "unknown"
        tags = parts[2] if len(parts) >= 3 else ""

        # Image dimensions (PNG only)
        width, height = _image_dimensions(entry["representative"])

        registry[md5] = {
            "name": f"{name}{ext}" if name else f"unnamed_{md5[:12]}{ext}",
            "type": img_type,
            "subtype": subtype,
            "tags": tags,
            "originals": [
                {"block": o["block"], "file": o["file"]}
                for o in entry["originals"]
            ],
            "width": width,
            "height": height,
            "size_bytes": entry["size_bytes"],
        }

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"  Registry saved to {registry_path} ({len(registry)} entries)")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _name_images_with_vision(inventory: dict) -> None:
    """Name all unique images using the Claude Vision API."""
    if not _HAS_ANTHROPIC:
        print(
            "\n  [ERROR] The 'anthropic' package is not installed.\n"
            "  Install with: uv add anthropic\n"
            "  Or re-run with --no-vision to use fallback naming.\n"
        )
        sys.exit(1)

    client = anthropic.Anthropic()
    total = len(inventory)
    named = 0
    failed = 0
    last_call_time = 0.0

    print(f"\n  Naming {total} unique images with Claude Vision ({VISION_MODEL})...")
    print(f"  Rate limit: ~{VISION_RPM} requests/min\n")

    for i, (md5, entry) in enumerate(inventory.items(), start=1):
        img_path = entry["representative"]
        block_name = entry["originals"][0]["block"]
        img_file = entry["originals"][0]["file"]

        # Rate limiting
        elapsed = time.time() - last_call_time
        if elapsed < _VISION_INTERVAL:
            time.sleep(_VISION_INTERVAL - elapsed)

        last_call_time = time.time()
        semantic_name = analyze_image_for_naming(img_path, client=client)

        if semantic_name:
            entry["name"] = semantic_name
            named += 1
            status = semantic_name
        else:
            # Fallback on Vision failure
            fallback = generate_fallback_name(block_name, img_file, i)
            entry["name"] = fallback
            failed += 1
            status = f"{fallback} (fallback)"

        # Progress
        if i % 50 == 0 or i == total:
            print(f"  [{i}/{total}] {status}")

    print(f"\n  Vision naming complete: {named} named, {failed} fallback")


def _name_images_fallback(inventory: dict) -> None:
    """Name all unique images using the fallback (no API) method."""
    total = len(inventory)
    print(f"\n  Naming {total} unique images with fallback method (no Vision API)...")

    for i, (md5, entry) in enumerate(inventory.items(), start=1):
        block_name = entry["originals"][0]["block"]
        img_file = entry["originals"][0]["file"]
        entry["name"] = generate_fallback_name(block_name, img_file, i)

    print(f"  Fallback naming complete: {total} images named")


def main() -> None:
    """Orchestrate image inventory, naming, deduplication, and deployment."""
    parser = argparse.ArgumentParser(
        description="Image manager for HTML-to-StreamTeX conversion. "
        "Deduplicates images, names them semantically, and deploys to shared/static/images/."
    )
    parser.add_argument(
        "--exports-dir",
        type=Path,
        default=Path("exports/html"),
        help="Root directory containing HTML block exports (default: exports/html)",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=Path("shared/static/images"),
        help="Target directory for deduplicated images (default: shared/static/images)",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("tools/image_registry.json"),
        help="Path to write the image registry JSON (default: tools/image_registry.json)",
    )
    parser.add_argument(
        "--no-vision",
        action="store_true",
        help="Skip Claude Vision API calls; use fallback naming based on block names",
    )
    args = parser.parse_args()

    # Resolve paths relative to the project root (parent of tools/)
    project_root = Path(__file__).resolve().parent.parent
    exports_dir = args.exports_dir
    if not exports_dir.is_absolute():
        exports_dir = project_root / exports_dir
    target_dir = args.target_dir
    if not target_dir.is_absolute():
        target_dir = project_root / target_dir
    registry_path = args.registry
    if not registry_path.is_absolute():
        registry_path = project_root / registry_path

    # Validate exports directory
    if not exports_dir.is_dir():
        print(f"[ERROR] Exports directory not found: {exports_dir}")
        sys.exit(1)

    print("=" * 60)
    print("IMAGE MANAGER — HTML-to-StreamTeX Conversion")
    print("=" * 60)

    # Phase 1: Build inventory
    print("\nPhase 1: Building image inventory...")
    inventory = build_image_inventory(exports_dir)

    if not inventory:
        print("\n  No images found. Nothing to do.")
        return

    # Phase 2: Name images
    print("\nPhase 2: Generating semantic names...")
    if args.no_vision:
        _name_images_fallback(inventory)
    else:
        _name_images_with_vision(inventory)

    # Phase 3: Resolve duplicate names
    print("\nPhase 3: Resolving name collisions...")
    _resolve_duplicate_names(inventory)
    # Count collisions resolved
    all_names = [e["name"] for e in inventory.values() if e.get("name")]
    unique_names = set(all_names)
    collisions = len(all_names) - len(unique_names)
    if collisions > 0:
        print(f"  Resolved {collisions} name collision(s)")
    else:
        print("  No collisions detected")

    # Phase 4: Deploy images
    print("\nPhase 4: Deploying deduplicated images...")
    deploy_images(inventory, target_dir)

    # Phase 5: Save registry
    print("\nPhase 5: Saving image registry...")
    save_registry(inventory, registry_path)

    # Summary
    total_originals = sum(len(e["originals"]) for e in inventory.values())
    total_bytes = sum(e["size_bytes"] for e in inventory.values())
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total images scanned:   {total_originals}")
    print(f"  Unique images:          {len(inventory)}")
    print(f"  Duplicates removed:     {total_originals - len(inventory)}")
    print(f"  Total unique size:      {total_bytes / (1024 * 1024):.1f} MB")
    print(f"  Deployed to:            {target_dir}")
    print(f"  Registry:               {registry_path}")
    print()


if __name__ == "__main__":
    main()
