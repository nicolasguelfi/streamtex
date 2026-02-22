"""Setup module to configure Python path for test_pres project."""

import os
import sys

# Add the project directory (shared/) parent to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
