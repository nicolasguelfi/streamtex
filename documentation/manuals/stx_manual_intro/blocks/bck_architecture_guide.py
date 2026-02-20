"""Composite block - groups multiple atomic blocks."""

import streamlit as st
from streamtex import st_include
import importlib.util
from pathlib import Path


def _load_atomic(name):
    """Load an atomic block from _atomic/ folder."""
    path = Path(__file__).parent / "_atomic" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"atomic_{name}", path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load atomic block: {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bck_architecture = _load_atomic("bck_architecture")


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_architecture)
