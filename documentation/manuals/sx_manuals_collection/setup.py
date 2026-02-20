"""Setup module to configure Python path for sx_manuals_collection."""

import os
import sys

# Add the project directory to the path so imports like 'custom' works
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
