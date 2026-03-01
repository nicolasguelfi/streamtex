"""Block helpers — project-specific configuration.

OVERVIEW:
This module configures the hybrid block helpers system for your project.
The library functions (show_code, show_explanation, etc.) are re-exported
directly — NO wrapper functions needed.

HOW IT WORKS:
1. Define ProjectBlockHelperConfig with your project's styles
2. Call set_block_helper_config() once at import time
3. All helpers automatically use your styles globally
4. Blocks import from here: `from blocks.helpers import show_code`

START HERE:
1. Fill in get_*_style() methods with YOUR project's styles
2. Add your project-specific helpers at the bottom
"""

from streamtex import (
    BlockHelperConfig, BlockHelper,  # noqa: F401
    show_code, show_code_inline, show_explanation, show_details,  # noqa: F401
    set_block_helper_config,
    st_write, st_block, st_space,
)
from custom.styles import Styles as s


# ============================================================================
# Style configuration (required — fill in your styles)
# ============================================================================

class ProjectBlockHelperConfig(BlockHelperConfig):
    """Inject your project styles into all helpers.

    Override the get_*_style() methods to return your project's styles.
    These styles will be used automatically by show_code(), show_explanation(),
    and other helpers throughout your project.
    """

    def get_code_style(self):
        # TODO: return s.project.containers.code_box
        return None

    def get_code_inline_style(self):
        # TODO: return s.project.containers.code_inline
        return None

    def get_explanation_style(self):
        # TODO: return s.project.containers.explanation_box
        return None

    def get_details_style(self):
        # TODO: return s.project.containers.details_box
        return None


set_block_helper_config(ProjectBlockHelperConfig())


# ============================================================================
# Project-specific helpers (add your own below)
# ============================================================================
# Examples:
#
# def show_welcome_box(title: str, subtitle: str):
#     """Homepage welcome section."""
#     with st_block(s.project.welcome_style):
#         st_write(s.titles.page_title, title)
#         st_write(s.titles.subtitle, subtitle)
#
#
# def show_feature_box(icon: str, name: str, description: str):
#     """Feature highlight card."""
#     with st_block(s.project.feature_style):
#         st_write(s.project.feature_icon, icon)
#         st_write(s.titles.feature_title, name)
#         st_space("v", 1)
#         st_write(s.body, description)
