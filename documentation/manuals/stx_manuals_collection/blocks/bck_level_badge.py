"""Welcome page — mauve gradient header + Collection Hub level badge."""

from streamtex import *
import streamtex as stx
from streamtex.styles import Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s


class BlockStyles:
    """Level badge styles."""
    # Orange-amber gradient header (Collection Hub identity)
    header = Style(
        "background: linear-gradient(135deg, #f46b45 0%, #eea849 100%); "
        "padding: 40px 20px; border-radius: 8px;",
        "collection_header"
    )
    level_box = Style(
        "background: rgba(46, 196, 182, 0.08); "
        "border-left: 4px solid #2EC4B6; "
        "padding: 20px 24px; border-radius: 0 8px 8px 0;",
        "collection_level_box"
    )
    level_label = Style(
        "color: #2EC4B6; font-weight: bold; font-size: 14pt; "
        "text-transform: uppercase; letter-spacing: 2px;",
        "collection_level_label"
    )
    description = s.large + s.project.colors.neutral_gray


bs = BlockStyles


def build():
    """Render mauve header + Collection Hub level badge on the same page."""
    # --- Mauve gradient header (collection-specific) ---
    st_space("v", 1)
    with st_block(bs.header):
        st_write(
            stx.StxStyles.huge + stx.StxStyles.text.colors.white,
            "StreamTeX Training Course",
            tag=t.div
        )
        st_write(
            stx.StxStyles.large + stx.StxStyles.text.colors.white,
            "A Streamlit-based content rendering framework",
            tag=t.div
        )
    st_space("v", 1)

    # --- Collection level badge ---
    with st_block(bs.level_box):
        st_write(bs.level_label, "Collection Hub")
        st_space("v", 0.5)
        st_write(
            s.Large + s.text.weights.bold_weight,
            "Discover and Explore Our Learning Paths",
        )
        st_space("v", 1)
        st_write(
            bs.description,
            "Browse the curated StreamTeX training courses. "
            "Each course is self-contained and can be launched independently.",
        )
        st_space("v", 1)
        with st_list(list_type="ul"):
            st_write(s.medium, "Introduction: text, styles, grids, lists, images, code, export")
            st_write(s.medium, "Advanced: shared blocks, collections, deployment, data visualization")
            st_write(s.medium, "Shared blocks: reusable components across all courses")

    st_space("v", 2)
