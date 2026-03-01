"""Welcome page — Advanced header + level badge.

Renders a project-specific gradient header and level badge.
Both appear on the same page in paginated mode because they
are in a single module.
"""

from streamtex import *
import streamtex as stx
from streamtex.styles import Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s


class BlockStyles:
    """Level badge styles."""
    # Indigo-purple gradient header (Advanced identity)
    header = Style(
        "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        "padding: 40px 20px; border-radius: 8px;",
        "advanced_header"
    )
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
    """Render Advanced header + level badge on the same page."""
    # --- Advanced gradient header ---
    st_space("v", 1)
    with st_block(bs.header):
        st_write(
            stx.StxStyles.huge + stx.StxStyles.bold + "color:white;",
            "StreamTeX Training Course: Advanced",
            tag=t.div,
            toc_lvl="1",
        )
        st_write(
            stx.StxStyles.large + "color:white;",
            "A Streamlit-based content rendering framework",
            tag=t.div
        )
    st_space("v", 1)

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
