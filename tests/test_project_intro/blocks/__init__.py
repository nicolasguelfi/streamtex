"""Blocks registry with lazy-loading to avoid import racing.

This module implements lazy-loading of blocks to prevent import racing issues
when many modules are loaded simultaneously.

Usage:
    # Old style (backward compatible)
    import blocks
    blocks.bck_welcome_intro  # ← lazy-loaded on first access

    # New style (recommended)
    from blocks import registry
    registry.get("bck_welcome_intro")
    registry.list_blocks()
    registry.get_stats()
"""

from pathlib import Path
import importlib
from typing import Optional

# Import registry components
from .registry import BlockRegistry, BlockNotFoundError, BlockImportError, get_registry

# Initialize the global registry
registry = get_registry()

# Export public API
__all__ = ["registry", "get_registry", "BlockNotFoundError", "BlockImportError"]


def __getattr__(name: str):
    """Lazy-load blocks on attribute access (backward compatibility).

    This enables accessing blocks like:
        import blocks
        blocks.bck_welcome_intro

    But the recommended modern way is:
        from blocks import registry
        registry.get("bck_welcome_intro")
    """
    # Try to get from registry
    try:
        return registry.get(name)
    except (BlockNotFoundError, BlockImportError) as e:
        # Provide helpful error message
        raise AttributeError(
            f"module '{__name__}' has no attribute '{name}'\n{str(e)}"
        ) from e


def __dir__():
    """Return list of available blocks for IDE autocompletion."""
    return sorted(registry.list_blocks() + __all__)
