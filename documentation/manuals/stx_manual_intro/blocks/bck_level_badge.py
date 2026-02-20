"""Welcome page — shared header + Introduction level badge.

Uses st_include() to render the shared bck_header_training block,
then renders the project-specific level badge. Both appear on the
same page in paginated mode because they are in a single module.
"""

import importlib.util
from pathlib import Path

from streamtex import *
from streamtex.styles import Style
from custom.styles import Styles as s

# Load the shared header block (kept as a separate, reusable file)
_header_path = (
    Path(__file__).resolve().parent.parent.parent
    / "sx_manuals_shared-blocks" / "blocks" / "bck_header_training.py"
)
_spec = importlib.util.spec_from_file_location("bck_header_training", _header_path)
_header = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_header)


class BlockStyles:
    """Level badge styles."""
    level_box = Style(
        "background: rgba(102, 126, 234, 0.08); "
        "border-left: 4px solid #667eea; "
        "padding: 20px 24px; border-radius: 0 8px 8px 0;",
        "intro_level_box"
    )
    level_label = Style(
        "color: #667eea; font-weight: bold; font-size: 14pt; "
        "text-transform: uppercase; letter-spacing: 2px;",
        "intro_level_label"
    )
    description = s.large + s.project.colors.neutral_gray


bs = BlockStyles


def build():
    """Render shared header + Introduction level badge on the same page."""
    # --- Shared gradient header (from shared-blocks) ---
    st_include(_header)

    # --- Introduction level badge ---
    with st_block(bs.level_box):
        st_write(bs.level_label, "Introduction Level")
        st_space("v", 0.5)
        st_write(
            s.Large + s.text.weights.bold_weight,
            "A Hands-On Guide to the Basic Features",
        )
        st_space("v", 1)
        st_write(
            bs.description,
            "This course teaches the fundamentals of StreamTeX step by step. "
            "Each section demonstrates one concept with live examples.",
        )
        st_space("v", 1)
        with st_list(list_type="ul"):
            st_write(s.medium, "Quick Start: install, create a project, write your first block")
            st_write(s.medium, "Core features: text, styles, grids, lists, images, code")
            st_write(s.medium, "Navigation: book, TOC, markers, zoom, export")

    st_space("v", 2)
