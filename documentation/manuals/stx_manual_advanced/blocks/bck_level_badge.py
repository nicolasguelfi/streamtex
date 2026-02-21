"""Welcome page — shared header + Advanced level badge.

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
    / "stx_manuals_shared-blocks" / "blocks" / "bck_header_training.py"
)
_spec = importlib.util.spec_from_file_location("bck_header_training", _header_path)
_header = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_header)


class BlockStyles:
    """Level badge styles."""
    level_box = Style(
        "background: rgba(118, 75, 162, 0.08); "
        "border-left: 4px solid #764ba2; "
        "padding: 20px 24px; border-radius: 0 8px 8px 0;",
        "advanced_level_box"
    )
    level_label = Style(
        "color: #764ba2; font-weight: bold; font-size: 14pt; "
        "text-transform: uppercase; letter-spacing: 2px;",
        "advanced_level_label"
    )
    description = s.large + s.project.colors.neutral_gray


bs = BlockStyles


def build():
    """Render shared header + Advanced level badge on the same page."""
    # --- Shared gradient header (from shared-blocks) ---
    st_include(_header)

    # --- Advanced level badge ---
    with st_block(bs.level_box):
        st_write(bs.level_label, "Advanced Level")
        st_space("v", 0.5)
        st_write(
            s.Large + s.text.weights.bold_weight,
            "Master Advanced Patterns and Enterprise Features",
        )
        st_space("v", 1)
        st_write(
            bs.description,
            "This course covers advanced StreamTeX patterns for production use. "
            "Multi-source blocks, collections, export, and deployment strategies.",
        )
        st_space("v", 1)
        with st_list(list_type="ul"):
            st_write(s.medium, "Registry: LazyBlockRegistry, shared blocks, static resolution")
            st_write(s.medium, "Advanced: overlays, themes, helpers, collections")
            st_write(s.medium, "Production: export, deployment, data visualization")

    st_space("v", 2)
