"""Image history management — versioned archiving of managed images."""

from __future__ import annotations

import glob
import os
import shutil
from typing import Optional

from .config import _detect_project_root
from .metadata import ImageMetadata, load_metadata, metadata_path_for, save_metadata

# Default managed images directory (relative to project root)
MANAGED_DIR = "static/images/managed"


def _resolve_managed_dir(base_dir: Optional[str] = None) -> str:
    """Resolve and create the managed images directory.

    When *base_dir* is ``None``, the path is resolved relative to the
    project root (the directory containing the main ``book.py``), **not**
    ``os.getcwd()``.
    """
    d = base_dir or os.path.join(_detect_project_root(), MANAGED_DIR)
    os.makedirs(d, exist_ok=True)
    return d


def _current_path(managed_dir: str, name: str, ext: str = "png") -> str:
    """Return path for the current version of a named image."""
    return os.path.join(managed_dir, f"{name}.{ext}")


def _version_path(managed_dir: str, name: str, version: int, ext: str = "png") -> str:
    """Return path for a specific version of a named image."""
    return os.path.join(managed_dir, f"{name}_v{version}.{ext}")


def get_extension(path: str) -> str:
    """Extract file extension without dot, defaulting to 'png'."""
    _, ext = os.path.splitext(path)
    return ext.lstrip(".").lower() or "png"


def save_version(
    name: str,
    image_path: str,
    *,
    source_type: str = "local",
    prompt: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    size: Optional[str] = None,
    quality: Optional[str] = None,
    base_image: Optional[str] = None,
    revised_prompt: Optional[str] = None,
    managed_dir: Optional[str] = None,
) -> str:
    """Save an image as a new version of *name*.

    If *name* already has a current image, it is archived as *name*_vN before
    the new image takes its place.

    Args:
        name: Semantic name (e.g. "hero_intro").
        image_path: Path to the new image file.
        source_type: "local", "url", or "ai_generated".
        prompt: AI prompt (if applicable).
        provider: AI provider (if applicable).
        model: AI model (if applicable).
        size: AI size (if applicable).
        quality: AI quality (if applicable).
        base_image: Path to base image for img2img (if applicable).
        revised_prompt: Provider-revised prompt (if applicable).
        managed_dir: Override managed directory.

    Returns:
        Path to the current (new) image file.
    """
    d = _resolve_managed_dir(managed_dir)
    ext = get_extension(image_path)

    current = _current_path(d, name, ext)
    current_json = metadata_path_for(current)

    # Determine next version number
    next_version = 1
    existing_meta = load_metadata(current_json)
    if existing_meta and os.path.isfile(current):
        next_version = existing_meta.version + 1
        # Archive current → _vN
        archive_img = _version_path(d, name, existing_meta.version, ext)
        archive_json = metadata_path_for(archive_img)
        shutil.copy2(current, archive_img)
        shutil.copy2(current_json, archive_json)

    # Copy new image to current
    shutil.copy2(image_path, current)

    # Write metadata
    meta = ImageMetadata(
        name=name,
        version=next_version,
        source_type=source_type,
        original_path=image_path,
        prompt=prompt,
        provider=provider,
        model=model,
        size=size,
        quality=quality,
        base_image=base_image,
        revised_prompt=revised_prompt,
    )
    save_metadata(meta, current_json)

    return current


def get_current(name: str, *, managed_dir: Optional[str] = None) -> Optional[str]:
    """Return the path to the current version of *name*, or None if not found."""
    d = _resolve_managed_dir(managed_dir)
    # Try common extensions
    for ext in ("png", "jpeg", "jpg", "webp", "svg"):
        path = _current_path(d, name, ext)
        if os.path.isfile(path):
            return path
    return None


def get_current_metadata(name: str, *, managed_dir: Optional[str] = None) -> Optional[ImageMetadata]:
    """Return metadata for the current version of *name*."""
    current = get_current(name, managed_dir=managed_dir)
    if not current:
        return None
    return load_metadata(metadata_path_for(current))


def list_versions(name: str, *, managed_dir: Optional[str] = None) -> list[tuple[int, ImageMetadata]]:
    """Return a list of (version, metadata) for all versions of *name*.

    Sorted by version number ascending. Includes the current version.
    """
    d = _resolve_managed_dir(managed_dir)
    versions = []

    # Find archived versions (_vN files)
    pattern = os.path.join(d, f"{name}_v*.json")
    for json_path in glob.glob(pattern):
        meta = load_metadata(json_path)
        if meta:
            versions.append((meta.version, meta))

    # Add current version
    current_meta = get_current_metadata(name, managed_dir=d)
    if current_meta:
        versions.append((current_meta.version, current_meta))

    return sorted(versions, key=lambda x: x[0])


def rollback(name: str, version: int, *, managed_dir: Optional[str] = None) -> Optional[str]:
    """Rollback *name* to a specific version.

    The current version is archived first, then the target version
    becomes the new current.

    Returns:
        Path to the restored image, or None if version not found.
    """
    d = _resolve_managed_dir(managed_dir)

    # Find the target version file
    target_meta = None
    target_img = None
    for ext in ("png", "jpeg", "jpg", "webp"):
        candidate = _version_path(d, name, version, ext)
        if os.path.isfile(candidate):
            target_img = candidate
            target_meta = load_metadata(metadata_path_for(candidate))
            break

    if not target_img or not target_meta:
        return None

    # Archive current first
    current = get_current(name, managed_dir=d)
    current_meta = get_current_metadata(name, managed_dir=d)
    if current and current_meta:
        ext_current = get_extension(current)
        archive_img = _version_path(d, name, current_meta.version, ext_current)
        archive_json = metadata_path_for(archive_img)
        if not os.path.isfile(archive_img):
            shutil.copy2(current, archive_img)
            shutil.copy2(metadata_path_for(current), archive_json)

    # Copy target to current
    ext_target = get_extension(target_img)
    new_current = _current_path(d, name, ext_target)
    shutil.copy2(target_img, new_current)

    # Update metadata with new version number
    new_version = (current_meta.version + 1) if current_meta else target_meta.version
    target_meta.version = new_version
    save_metadata(target_meta, metadata_path_for(new_current))

    return new_current


def rename_image(
    old_name: str,
    new_name: str,
    *,
    managed_dir: Optional[str] = None,
) -> Optional[str]:
    """Rename a managed image (current + all versions).

    Returns the new current path, or None if old_name not found.
    """
    d = _resolve_managed_dir(managed_dir)
    current = get_current(old_name, managed_dir=d)
    if not current:
        return None

    ext = get_extension(current)

    # Rename current
    new_current = _current_path(d, new_name, ext)
    os.rename(current, new_current)
    old_json = metadata_path_for(current)
    new_json = metadata_path_for(new_current)
    if os.path.isfile(old_json):
        meta = load_metadata(old_json)
        if meta:
            meta.name = new_name
            save_metadata(meta, new_json)
        os.remove(old_json)

    # Rename archived versions
    pattern = os.path.join(d, f"{old_name}_v*")
    for old_path in glob.glob(pattern):
        basename = os.path.basename(old_path)
        new_basename = basename.replace(old_name, new_name, 1)
        new_path = os.path.join(d, new_basename)
        os.rename(old_path, new_path)
        # Update metadata name if it's a json
        if new_path.endswith(".json"):
            meta = load_metadata(new_path)
            if meta:
                meta.name = new_name
                save_metadata(meta, new_path)

    return new_current
