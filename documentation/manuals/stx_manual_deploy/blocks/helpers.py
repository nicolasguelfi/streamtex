"""Block helpers for stx_manual_deploy — Config injection pattern.

Uses the DI pattern: define styles once, all helpers use them automatically.
"""

from streamtex import (
    BlockHelperConfig,
    show_code as _show_code,
    show_code_inline as _show_code_inline,
    show_explanation as _show_explanation,
    show_details as _show_details,
    set_block_helper_config,
)
from custom.styles import Styles as s


class ProjectBlockHelperConfig(BlockHelperConfig):
    """Inject deployment manual styles into all helpers."""

    def get_code_style(self):
        return s.project.containers.code_box

    def get_code_inline_style(self):
        return None

    def get_explanation_style(self):
        return s.project.containers.explanation_box

    def get_details_style(self):
        return s.project.containers.details_box


# Initialize the global config
set_block_helper_config(ProjectBlockHelperConfig())


def show_code(code_string: str, language: str = "python", line_numbers: bool = True):
    """Show a code block with project styles."""
    return _show_code(code_string, language, line_numbers)


def show_code_inline(code_string: str, language: str = "python", line_numbers: bool = True):
    """Show an inline code block with project styles."""
    return _show_code_inline(code_string, language, line_numbers)


def show_explanation(text: str):
    """Show an explanation callout with project styles."""
    return _show_explanation(text)


def show_details(text: str):
    """Show a details callout with project styles."""
    return _show_details(text)
