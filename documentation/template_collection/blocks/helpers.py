"""Block helpers — project-specific configuration."""
from streamtex import (
    BlockHelperConfig, set_block_helper_config,
    show_code, show_explanation, show_details, show_code_inline,
)
from custom.styles import Styles as s


class ProjectBlockHelperConfig(BlockHelperConfig):
    """Override default styles with project-specific ones."""

    def get_code_style(self):
        return None

    def get_explanation_style(self):
        return None

    def get_details_style(self):
        return None


# Activate at import time — all blocks will use these styles
set_block_helper_config(ProjectBlockHelperConfig())
