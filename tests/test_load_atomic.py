"""Tests for load_atomic_block()."""

import pytest
from pathlib import Path
from streamtex.blocks import load_atomic_block, BlockNotFoundError, BlockImportError


@pytest.fixture
def atomic_dir(tmp_path):
    """Create a temporary _atomic/ directory with test blocks."""
    atomic = tmp_path / "_atomic"
    atomic.mkdir()

    # Valid block
    (atomic / "bck_valid.py").write_text(
        '"""Valid atomic block."""\n\ndef build():\n    return "ok"\n'
    )

    # Broken block (syntax error)
    (atomic / "bck_broken.py").write_text("def build(\n")

    # Caller file (simulates a composite block in tmp_path)
    caller = tmp_path / "bck_composite.py"
    caller.write_text("")

    return tmp_path, str(caller)


def test_load_valid_block(atomic_dir):
    """load_atomic_block loads a valid block and returns the module."""
    _, caller_file = atomic_dir
    mod = load_atomic_block("bck_valid", caller_file)
    assert hasattr(mod, "build")
    assert mod.build() == "ok"


def test_block_not_found(atomic_dir):
    """load_atomic_block raises BlockNotFoundError for missing blocks."""
    _, caller_file = atomic_dir
    with pytest.raises(BlockNotFoundError, match="not found"):
        load_atomic_block("bck_nonexistent", caller_file)


def test_block_import_error(atomic_dir):
    """load_atomic_block raises BlockImportError for broken blocks."""
    _, caller_file = atomic_dir
    with pytest.raises(BlockImportError, match="Failed to import"):
        load_atomic_block("bck_broken", caller_file)


def test_exported_from_init():
    """load_atomic_block is accessible from streamtex namespace."""
    import streamtex as stx
    assert hasattr(stx, "load_atomic_block")
    assert callable(stx.load_atomic_block)
