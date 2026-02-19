"""Blocks for the test collection."""

import importlib.util
from pathlib import Path


def _load_block(name):
    """Lazy-load a block module by name."""
    block_path = Path(__file__).parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, block_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ModuleNotFoundError(f"Block {name} not found at {block_path}")


# Lazy-load available blocks
bck_home_collection = _load_block("bck_home_collection")

__all__ = ["bck_home_collection"]
