"""Lazy block registry for multi-source block loading."""

import os
import importlib.util
from typing import List, Optional


class LazyBlockRegistry:
    """
    A registry for lazy-loading block modules from multiple source directories.

    Blocks are imported on first access (lazy), with priority given to the first
    source directory in the list. Once loaded, blocks are cached.

    Example:
        ```python
        import streamtex as sx
        from streamtex import st_book

        # Create a registry pointing to local and shared block directories
        shared_blocks = sx.LazyBlockRegistry([
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

    def __repr__(self) -> str:
        return f"LazyBlockRegistry(sources={self.sources}, cached={len(self._cache)})"


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
        import streamtex as sx

        sx.set_static_sources(["static", "../../shared-course-blocks/static"])

        # In a block:
        data_path = sx.resolve_static("data/trainers.json")
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
