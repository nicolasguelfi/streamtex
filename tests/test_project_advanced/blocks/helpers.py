"""Block helpers for test_project_advanced — hybrid approach.

This module demonstrates the hybrid block helpers pattern:
1. Dependency Injection: ProjectBlockHelperConfig customizes defaults
2. Standalone functions: Direct usage with config injection
3. OOP inheritance: Optional ProjectBlockHelper class for advanced overrides
4. Project-specific helpers: Advanced features unique to this project
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

    def show_advanced_comparison(self, before: str, after: str, label: str = "Comparison"):
        """Advanced-specific helper: Side-by-side comparison."""
        with st_block(s.advanced.comparison_container):
            st_write(s.titles.section_title, label)
            st_space("v", 1)
            # Layout comparison (simplified)
            st_write(s.body, "Before:")
            _show_code(before)
            st_space("v", 2)
            st_write(s.body, "After:")
            _show_code(after)


# ============================================================================
# PROJECT-SPECIFIC HELPERS: Advanced features unique to this project
# ============================================================================

def show_advanced_warning(title: str, description: str):
    """Advanced warning box — for deprecated features, breaking changes."""
    with st_block(s.advanced.warning_box):
        st_write(s.advanced.warning_label, f"⚠️ {title}")
        st_space("v", 1)
        st_write(s.body, description)


def show_advanced_note(title: str, description: str):
    """Advanced note box — for important notes and considerations."""
    with st_block(s.advanced.note_box):
        st_write(s.advanced.note_label, f"📌 {title}")
        st_space("v", 1)
        st_write(s.body, description)


def show_performance_insight(metric: str, value: str, note: str):
    """Performance-specific helper — for optimization tips."""
    with st_block(s.advanced.perf_box):
        st_write(s.advanced.perf_metric, f"{metric}: {value}")
        st_space("v", 1)
        st_write(s.body, note)


def show_api_reference(method_name: str, signature: str, description: str):
    """API reference helper — for documenting functions/methods."""
    with st_block(s.advanced.api_box):
        st_write(s.advanced.api_method, method_name)
        _show_code(signature, language="python")
        st_space("v", 1)
        st_write(s.body, description)
