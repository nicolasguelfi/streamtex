"""BlockRegistry: Central registry for managing blocks with lazy-loading."""

import importlib
from pathlib import Path
from typing import Dict, Optional


class BlockRegistry:
    """Central registry for managing blocks in the project."""

    def __init__(self, blocks_dir: Path):
        """Initialize the registry for a blocks directory."""
        self.blocks_dir = blocks_dir
        self._cache: Dict[str, object] = {}
        self._manifest: Optional[Dict] = None

    @property
    def manifest(self) -> Dict[str, dict]:
        """Get manifest of all available blocks (without loading them)."""
        if self._manifest is None:
            self._manifest = self._build_manifest()
        return self._manifest

    def _build_manifest(self) -> Dict[str, dict]:
        """Scan bck_*.py files and build an index without importing."""
        manifest = {}
        composites = self._detect_composites()

        for path in sorted(self.blocks_dir.glob("bck_*.py")):
            if path.name == "__init__.py":
                continue

            module_name = path.stem
            manifest[module_name] = {
                "path": str(path),
                "loaded": False,
                "type": "composite" if module_name in composites else "atomic",
            }

        return manifest

    def _detect_composites(self) -> set:
        """Detect which modules are composites by reading file headers."""
        composites = set()

        for path in self.blocks_dir.glob("bck_*.py"):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read(1000)
                    if "_load_atomic" in content or "st_include" in content:
                        composites.add(path.stem)
            except (IOError, UnicodeDecodeError):
                pass

        return composites

    def get(self, block_name: str) -> object:
        """Get a block module (lazy-loaded and cached)."""
        if block_name not in self.manifest:
            available = ", ".join(sorted(self.manifest.keys()))
            raise BlockNotFoundError(
                f"Block '{block_name}' not found.\n"
                f"Available blocks: {available}"
            )

        if block_name not in self._cache:
            try:
                # Import from blocks package, not from blocks.registry
                module = importlib.import_module(f".{block_name}", package="blocks")
                self._cache[block_name] = module
                self.manifest[block_name]["loaded"] = True
            except ImportError as e:
                raise BlockImportError(
                    f"Failed to import block '{block_name}': {e}"
                ) from e

        return self._cache[block_name]

    def load_all(self) -> None:
        """Pre-load all blocks (optional)."""
        for block_name in sorted(self.manifest.keys()):
            self.get(block_name)

    def list_blocks(self, block_type: Optional[str] = None) -> list:
        """List all available blocks without loading them."""
        if block_type:
            return sorted(
                [
                    name
                    for name, meta in self.manifest.items()
                    if meta["type"] == block_type
                ]
            )
        return sorted(self.manifest.keys())

    def get_stats(self) -> dict:
        """Get statistics about blocks."""
        manifest = self.manifest
        return {
            "total": len(manifest),
            "loaded": sum(1 for m in manifest.values() if m["loaded"]),
            "composites": len(
                [m for m in manifest.values() if m["type"] == "composite"]
            ),
            "atomics": len(
                [m for m in manifest.values() if m["type"] == "atomic"]
            ),
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"BlockRegistry("
            f"total={stats['total']}, "
            f"loaded={stats['loaded']}, "
            f"composites={stats['composites']}, "
            f"atomics={stats['atomics']})"
        )


class BlockNotFoundError(ImportError):
    """Raised when a requested block is not found."""
    pass


class BlockImportError(ImportError):
    """Raised when a block fails to import."""
    pass


_registry = None


def get_registry() -> BlockRegistry:
    """Get the global BlockRegistry instance (lazy-initialized)."""
    global _registry
    if _registry is None:
        blocks_dir = Path(__file__).parent
        _registry = BlockRegistry(blocks_dir)
    return _registry
