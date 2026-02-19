"""Setup module to configure Python path for StreamTeX project."""

import os
import sys

# Add the parent directory to the path so imports like 'custom' and 'blocks' work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
