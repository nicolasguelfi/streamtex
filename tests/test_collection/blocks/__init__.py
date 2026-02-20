"""Blocks package — lazy-loaded via streamtex.ProjectBlockRegistry."""
from pathlib import Path
from streamtex import ProjectBlockRegistry, BlockNotFoundError, BlockImportError

registry = ProjectBlockRegistry(Path(__file__).parent)
__all__ = ["registry", "BlockNotFoundError", "BlockImportError"]


def __getattr__(name: str):
    try:
        return registry.get(name)
    except (BlockNotFoundError, BlockImportError) as e:
        raise AttributeError(str(e)) from e


def __dir__():
    return sorted(registry.list_blocks() + __all__)
