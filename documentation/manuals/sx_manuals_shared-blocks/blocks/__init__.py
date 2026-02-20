"""Shared blocks module for StreamTeX training courses."""

import os
import glob
import importlib

# Discover and import all block modules from this directory
current_dir = os.path.dirname(__file__)
module_paths = glob.glob(os.path.join(current_dir, "bck_*.py"))
module_names = [
    os.path.basename(f)[:-3]
    for f in module_paths
    if os.path.isfile(f) and not f.endswith("__init__.py")
]

__all__ = sorted(module_names)

for module_name in __all__:
    globals()[module_name] = importlib.import_module(f".{module_name}", package=__name__)
