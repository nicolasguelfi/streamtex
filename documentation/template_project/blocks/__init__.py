import os
import glob
import importlib

# Get the directory of this __init__.py file
current_dir = os.path.dirname(__file__)

# Find all .py files 
# We exclude __init__.py itself to avoid recursion
module_paths = glob.glob(os.path.join(current_dir, "*.py"))
module_names = [
    os.path.basename(f)[:-3] 
    for f in module_paths 
    if os.path.isfile(f) and not f.endswith("__init__.py")
]

# This defines what gets imported when you use "from blocks import *"
__all__ = module_names

# Dynamically import the modules so they are available in this namespace
for module_name in module_names:
    globals()[module_name] = importlib.import_module(f".{module_name}", package=__name__)