"""Lazy block registry for multi-source block loading."""

import importlib.util
import os
from pathlib import Path
from typing import Dict, List, Optional


class LazyBlockRegistry:
    """
    A registry for lazy-loading block modules from multiple source directories.

    Blocks are imported on first access (lazy), with priority given to the first
    source directory in the list. Once loaded, blocks are cached.

    Example:
        ```python
        import streamtex as stx
        from streamtex import st_book

        # Create a registry pointing to local and shared block directories
        shared_blocks = stx.LazyBlockRegistry([
            "../../shared-course-blocks/blocks",
        ])
        import blocks  # Local blocks

        # Use both in st_book:
        st_book([
            shared_blocks.bck_header_university,   # Lazy-loaded on access
            blocks.bck_content_01,
            shared_blocks.bck_footer_university,
        ])
        ```
    """

    _instances: List["LazyBlockRegistry"] = []

    def __init__(self, sources: List[str]):
        """
        Initialize the registry with a list of source directories.

        Args:
            sources: List of directory paths to search for blocks (relative or absolute).
                    First source has highest priority.
        """
        self.sources = [os.path.abspath(s) for s in sources]
        self._cache = {}
        self._not_found = set()  # Track blocks we've already searched for (not found)
        LazyBlockRegistry._instances.append(self)

    def __getattr__(self, block_name: str):
        """
        Get a block module by name. Blocks are loaded lazily on first access.

        Args:
            block_name: Name of the block (e.g., "bck_header_university")

        Returns:
            The imported module object

        Raises:
            AttributeError: If the block is not found in any source directory
        """
        # Avoid infinite recursion for __dict__ and other special attributes
        if block_name.startswith('_'):
            raise AttributeError(f"LazyBlockRegistry has no attribute '{block_name}'")

        # Return cached block if already loaded
        if block_name in self._cache:
            return self._cache[block_name]

        # Skip if we already searched and didn't find it
        if block_name in self._not_found:
            raise AttributeError(f"Block '{block_name}' not found in sources: {self.sources}")

        # Search for the block in each source directory
        for source_dir in self.sources:
            block_path = os.path.join(source_dir, f"{block_name}.py")

            if os.path.isfile(block_path):
                # Load the block module
                spec = importlib.util.spec_from_file_location(
                    f"lazy_blocks.{block_name}",
                    block_path
                )

                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Cache and return
                    self._cache[block_name] = module
                    return module

        # Block not found in any source
        self._not_found.add(block_name)
        raise AttributeError(f"Block '{block_name}' not found in sources: {self.sources}")

    def list_blocks(self) -> list:
        """List all discoverable block names across all sources."""
        blocks = set()
        for source_dir in self.sources:
            if os.path.isdir(source_dir):
                for f in os.listdir(source_dir):
                    if f.startswith("bck_") and f.endswith(".py"):
                        blocks.add(f[:-3])  # Remove .py
        return sorted(blocks)

    def get(self, block_name: str):
        """Get a block by name. Same as attribute access but explicit."""
        return getattr(self, block_name)

    def invalidate(self) -> None:
        """Clear the block cache so modules are reloaded from disk."""
        self._cache.clear()
        self._not_found.clear()

    @classmethod
    def invalidate_all(cls) -> None:
        """Clear caches on **all** ``LazyBlockRegistry`` instances."""
        for reg in cls._instances:
            reg.invalidate()

    def __repr__(self) -> str:
        return f"LazyBlockRegistry(sources={self.sources}, cached={len(self._cache)})"


class BlockNotFoundError(ImportError):
    """Raised when a requested block is not found."""
    pass


class BlockImportError(ImportError):
    """Raised when a block fails to import."""
    pass


class ProjectBlockRegistry:
    """
    Registry for a single project's blocks/ directory.

    Features:
    - Lazy-loading with O(1) startup (manifest-based)
    - Block type detection (atomic vs composite)
    - Introspection: list_blocks(), get_stats(), load_all()
    - Attribute access: registry.bck_name or registry.get("bck_name")
    - Custom error classes with helpful messages

    Usage in blocks/__init__.py:
        from pathlib import Path
        from streamtex import ProjectBlockRegistry

        registry = ProjectBlockRegistry(Path(__file__).parent)
    """

    _instances: List["ProjectBlockRegistry"] = []

    def __init__(self, blocks_dir: Path):
        self.blocks_dir = Path(blocks_dir)
        self._cache: Dict[str, object] = {}
        self._manifest: Optional[Dict] = None
        ProjectBlockRegistry._instances.append(self)

    @property
    def manifest(self) -> Dict[str, dict]:
        if self._manifest is None:
            self._manifest = self._build_manifest()
        return self._manifest

    def _build_manifest(self) -> Dict[str, dict]:
        manifest = {}
        composites = self._detect_composites()
        for path in sorted(self.blocks_dir.glob("bck_*.py")):
            name = path.stem
            manifest[name] = {
                "path": str(path),
                "loaded": False,
                "type": "composite" if name in composites else "atomic",
            }
        return manifest

    def _detect_composites(self) -> set:
        composites = set()
        for path in self.blocks_dir.glob("bck_*.py"):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read(1000)
                    if "_load_atomic" in content or "load_atomic_block" in content or "st_include" in content:
                        composites.add(path.stem)
            except (IOError, UnicodeDecodeError):
                pass
        return composites

    def get(self, block_name: str) -> object:
        if block_name not in self.manifest:
            available = ", ".join(sorted(self.manifest.keys()))
            raise BlockNotFoundError(
                f"Block '{block_name}' not found.\nAvailable: {available}"
            )
        if block_name not in self._cache:
            path = self.manifest[block_name]["path"]
            try:
                spec = importlib.util.spec_from_file_location(
                    f"project_blocks.{block_name}", path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self._cache[block_name] = module
                    self.manifest[block_name]["loaded"] = True
                else:
                    raise BlockImportError(f"Cannot create spec for '{block_name}'")
            except Exception as e:
                raise BlockImportError(f"Failed to import '{block_name}': {e}") from e
        return self._cache[block_name]

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(f"ProjectBlockRegistry has no attribute '{name}'")
        try:
            return self.get(name)
        except (BlockNotFoundError, BlockImportError) as e:
            raise AttributeError(str(e)) from e

    def load_all(self) -> None:
        for name in sorted(self.manifest.keys()):
            self.get(name)

    def list_blocks(self, block_type: Optional[str] = None) -> list:
        if block_type:
            return sorted(n for n, m in self.manifest.items() if m["type"] == block_type)
        return sorted(self.manifest.keys())

    def get_stats(self) -> dict:
        m = self.manifest
        return {
            "total": len(m),
            "loaded": sum(1 for v in m.values() if v["loaded"]),
            "composites": sum(1 for v in m.values() if v["type"] == "composite"),
            "atomics": sum(1 for v in m.values() if v["type"] == "atomic"),
        }

    def invalidate(self) -> None:
        """Clear the block cache and manifest so modules are reloaded from disk."""
        self._cache.clear()
        self._manifest = None

    @classmethod
    def invalidate_all(cls) -> None:
        """Clear caches on **all** ``ProjectBlockRegistry`` instances."""
        for reg in cls._instances:
            reg.invalidate()

    def __repr__(self) -> str:
        s = self.get_stats()
        return (f"ProjectBlockRegistry(total={s['total']}, loaded={s['loaded']}, "
                f"composites={s['composites']}, atomics={s['atomics']})")


def load_atomic_block(name: str, caller_file: str):
    """Load an atomic block from _atomic/ subfolder relative to caller_file.

    Args:
        name: Block module name (e.g. "bck_text_basics")
        caller_file: Pass __file__ from the calling composite block

    Returns:
        The imported module object

    Raises:
        BlockNotFoundError: If the block file does not exist
        BlockImportError: If the block fails to import
    """
    caller_dir = Path(caller_file).parent
    block_path = caller_dir / "_atomic" / f"{name}.py"
    if not block_path.is_file():
        raise BlockNotFoundError(f"Atomic block '{name}' not found at: {block_path}")
    try:
        spec = importlib.util.spec_from_file_location(f"atomic_{name}", block_path)
        if not spec or not spec.loader:
            raise BlockImportError(f"Cannot create spec for atomic block: {name}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (BlockNotFoundError, BlockImportError):
        raise
    except Exception as e:
        raise BlockImportError(f"Failed to import atomic block '{name}': {e}") from e


# Global state for static file resolution
_static_sources: List[str] = []


def set_static_sources(sources: List[str]) -> None:
    """
    Set the list of directories to search for static files.

    This is typically called once at the start of a project, before loading blocks.

    Args:
        sources: List of directory paths (relative or absolute). First source has priority.
    """
    global _static_sources
    _static_sources = [os.path.abspath(s) for s in sources]


def get_static_sources() -> List[str]:
    """
    Get the currently configured static source directories.

    Returns:
        List of absolute paths to static source directories
    """
    return _static_sources.copy()


def resolve_static(relative_path: str) -> str:
    """
    Resolve a static file path across configured source directories.

    Searches each static source directory in order. Returns the absolute path of the
    first match found, or returns the original relative_path if no match is found
    (fallback for Streamlit's built-in static serving).

    Example:
        ```python
        import streamtex as stx

        stx.set_static_sources(["static", "../../shared-course-blocks/static"])

        # In a block:
        data_path = stx.resolve_static("data/trainers.json")
        with open(data_path) as f:
            trainers = json.load(f)
        ```

    Args:
        relative_path: Path relative to a static directory (e.g., "images/logo.png")

    Returns:
        Absolute path to the file if found, otherwise the original relative_path
    """
    for base in _static_sources:
        full_path = os.path.join(base, relative_path)
        if os.path.exists(full_path):
            return full_path

    # Fallback: return the original path (for Streamlit static serving)
    return relative_path
