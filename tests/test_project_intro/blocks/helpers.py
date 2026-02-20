"""Block helpers for test_project_intro — hybrid approach.

This module demonstrates the hybrid block helpers pattern:
1. Dependency Injection: ProjectBlockHelperConfig customizes defaults
2. Standalone functions: Direct usage with config injection
3. OOP inheritance: Optional ProjectBlockHelper class for advanced overrides
4. Project-specific helpers: Unique features for this project

All helpers automatically use project styles via set_block_helper_config().
"""

from streamtex import (
    BlockHelperConfig, BlockHelper,
    show_code as _show_code,
    show_code_inline as _show_code_inline,
    show_explanation as _show_explanation,
    show_details as _show_details,
    set_block_helper_config,
)
from streamtex import st_write, st_block, st_space
from custom.styles import Styles as s


# ============================================================================
# DEPENDENCY INJECTION: Config class with project-specific styles
# ============================================================================

class ProjectBlockHelperConfig(BlockHelperConfig):
    """Custom config injecting project-specific styles into all helpers.

    This is called once at project startup to set default styles globally.
    All helpers (show_code, show_explanation, etc.) will use these styles
    automatically, without needing to pass them as parameters.
    """

    def get_code_style(self):
        """Default style for code boxes in this project."""
        return s.project.containers.code_box

    def get_code_inline_style(self):
        """Default style for inline code in this project."""
        return None  # Use bare code (no wrapper)

    def get_explanation_style(self):
        """Default style for explanation boxes in this project."""
        return s.project.containers.explanation_box

    def get_details_style(self):
        """Default style for details boxes in this project."""
        return s.project.containers.details_box


# Initialize: inject project config globally
set_block_helper_config(ProjectBlockHelperConfig())


# ============================================================================
# SIMPLE WRAPPERS: Optional convenience wrappers for local shortcuts
# ============================================================================

def show_code(code_string: str, language: str = "python", line_numbers: bool = True):
    """Convenience wrapper — uses config-injected style automatically."""
    return _show_code(code_string, language, line_numbers)


def show_code_inline(code_string: str, language: str = "python", line_numbers: bool = True):
    """Convenience wrapper — uses config-injected style automatically."""
    return _show_code_inline(code_string, language, line_numbers)


def show_explanation(text: str):
    """Convenience wrapper — uses config-injected style automatically."""
    return _show_explanation(text)


def show_details(text: str):
    """Convenience wrapper — uses config-injected style automatically."""
    return _show_details(text)


# ============================================================================
# OPTIONAL OOP BASE: For advanced users wanting to override via inheritance
# ============================================================================

class ProjectBlockHelper(BlockHelper):
    """Optional OOP base class for this project's blocks.

    Inherits from streamtex.BlockHelper and adds project-specific methods.

    Usage:
        from blocks.helpers import ProjectBlockHelper
        helper = ProjectBlockHelper()
        helper.show_code("print('hello')")
    """

    def show_intro_milestone(self, step: int, title: str, description: str):
        """Project-specific helper: Milestone box for intro flow."""
        with st_block(s.intro.milestone_style):
            st_write(s.intro.milestone_number, f"Step {step}")
            st_write(s.intro.milestone_title, title)
            st_space("v", 1)
            st_write(s.body, description)


# ============================================================================
# PROJECT-SPECIFIC HELPERS: Unique to this intro project
# ============================================================================

def show_intro_welcome(title: str, subtitle: str, description: str):
    """Welcome box for intro project homepage."""
    with st_block(s.intro.welcome_container):
        st_write(s.titles.page_title, title)
        st_write(s.titles.section_subtitle, subtitle)
        st_space("v", 2)
        st_write(s.body, description)


def show_feature_highlight(feature_name: str, icon: str, description: str):
    """Highlight a specific feature with icon and description."""
    with st_block(s.intro.feature_box):
        st_write(s.intro.feature_icon, icon)
        st_write(s.titles.section_title, feature_name)
        st_space("v", 1)
        st_write(s.body, description)


def show_intro_tip(text: str):
    """Intro-specific tip box (styled differently than generic explanation)."""
    with st_block(s.intro.tip_box):
        st_write(s.intro.tip_label, "💡 Pro Tip")
        st_space("v", 1)
        st_write(s.body, text)
