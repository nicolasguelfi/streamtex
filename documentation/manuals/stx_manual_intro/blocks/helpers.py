"""Block helpers for stx_manual_intro — config injection pattern.

This module defines the project-specific style configuration and
re-exports the library helpers so that blocks can import from here:

    from blocks.helpers import show_code, show_explanation, show_details

No wrapper functions needed — the library functions use the global
config set by set_block_helper_config() at import time.
"""

from streamtex import (
    BlockHelperConfig, set_block_helper_config,
    show_code, show_code_inline, show_explanation, show_details,  # noqa: F401
    st_write, st_block, st_space,
)
from custom.styles import Styles as s


# ============================================================================
# Style configuration (one-time setup at import)
# ============================================================================

class ProjectBlockHelperConfig(BlockHelperConfig):
    """Inject intro project's styles into all helpers."""

    def get_code_style(self):
        return s.project.containers.code_box

    def get_code_inline_style(self):
        return None

    def get_explanation_style(self):
        return s.project.containers.explanation_box

    def get_details_style(self):
        return s.project.containers.details_box


set_block_helper_config(ProjectBlockHelperConfig())


# ============================================================================
# Project-specific helpers (unique to intro project)
# ============================================================================

def show_intro_welcome(title: str, subtitle: str, description: str):
    """Welcome box for intro homepage."""
    with st_block(s.project.containers.tip_callout):
        st_write(s.project.titles.page_title, title)
        st_write(s.project.titles.section_subtitle, subtitle)
        st_space("v", 2)
        st_write(s.large, description)


def show_feature_highlight(feature_name: str, icon: str, description: str):
    """Highlight a specific feature with icon."""
    with st_block(s.project.containers.explanation_box):
        st_write(s.large + s.bold, icon)
        st_write(s.project.titles.section_title, feature_name)
        st_space("v", 1)
        st_write(s.large, description)
