"""Block helpers for sx_manual_intro — minimal hybrid approach.

This module shows the SIMPLE usage pattern:
- ProjectBlockHelperConfig for dependency injection
- Convenience wrappers with config injection
- A few project-specific helpers

For advanced patterns (OOP, multiple modes), see sx_manual_advanced/blocks/helpers.py
"""

from streamtex import (
    BlockHelperConfig,
    show_code as _show_code,
    show_code_inline as _show_code_inline,
    show_explanation as _show_explanation,
    show_details as _show_details,
    set_block_helper_config,
)
from streamtex import st_write, st_block, st_space
from custom.styles import Styles as s


# ============================================================================
# DEPENDENCY INJECTION: Config with project-specific styles
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


# Initialize config (one-time setup)
set_block_helper_config(ProjectBlockHelperConfig())


# ============================================================================
# CONVENIENCE WRAPPERS: Use when you want local shortcuts
# ============================================================================

def show_code(code_string: str, language: str = "python", line_numbers: bool = True):
    """Convenience wrapper — uses config-injected style."""
    return _show_code(code_string, language, line_numbers)


def show_code_inline(code_string: str, language: str = "python", line_numbers: bool = True):
    """Convenience wrapper — uses config-injected style."""
    return _show_code_inline(code_string, language, line_numbers)


def show_explanation(text: str):
    """Convenience wrapper — uses config-injected style."""
    return _show_explanation(text)


def show_details(text: str):
    """Convenience wrapper — uses config-injected style."""
    return _show_details(text)


# ============================================================================
# PROJECT-SPECIFIC HELPERS: Unique to intro project
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
