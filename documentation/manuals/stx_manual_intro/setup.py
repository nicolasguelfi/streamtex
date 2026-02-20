"""Setup module to configure Python path for stx_manual_intro."""

import os
import sys

# Add the project directory to the path so imports like 'custom' and 'blocks' work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
