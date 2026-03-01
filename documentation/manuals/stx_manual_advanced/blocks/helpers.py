"""Block helpers for stx_manual_advanced — complete hybrid showcase.

This module demonstrates ALL usage patterns of the hybrid block helpers system:

1. CONFIG INJECTION (DI Pattern) — ProjectBlockHelperConfig
2. RE-EXPORT (Zero wrapper) — import directly from streamtex
3. OOP INHERITANCE (Advanced) — ProjectBlockHelper subclass
4. PROJECT-SPECIFIC HELPERS — domain-specific helpers

The library functions (show_code, show_explanation, etc.) are re-exported
directly — no wrapper functions needed. The global config set by
set_block_helper_config() injects styles automatically.
"""

from streamtex import (
    BlockHelperConfig, BlockHelper,
    show_code, show_code_inline, show_explanation, show_details,  # noqa: F401
    set_block_helper_config,
    st_write, st_block, st_space,
)
from custom.styles import Styles as s


# ============================================================================
# PATTERN 1: CONFIG INJECTION (Dependency Injection)
# ============================================================================

class ProjectBlockHelperConfig(BlockHelperConfig):
    """DI Config: Inject advanced project styles into all helpers.

    Called once at startup via set_block_helper_config().
    All show_code(), show_explanation(), etc. use these styles
    automatically without passing style= parameters.
    """

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
# PATTERN 2: OOP INHERITANCE (Advanced Pattern)
# ============================================================================

class ProjectBlockHelper(BlockHelper):
    """Advanced OOP base for custom helper logic.

    Demonstrates how to override parent methods from BlockHelper
    and add project-specific methods.

    Usage:
        helper = ProjectBlockHelper()
        helper.show_code("...")
        helper.show_advanced_comparison("before", "after")
    """

    def show_advanced_comparison(self, before: str, after: str, label: str = "Comparison"):
        """Advanced-specific helper: Side-by-side comparison."""
        with st_block(s.project.containers.code_box):
            st_write(s.project.titles.section_title, label)
            st_space("v", 1)
            st_write(s.large, "Before:")
            show_code(before)
            st_space("v", 2)
            st_write(s.large, "After:")
            show_code(after)


class ExpertBlockHelper(ProjectBlockHelper):
    """Expert pattern: Combines OOP + Config Injection.

    Inherits from ProjectBlockHelper (OOP mode) and uses
    global config (DI mode) for maximum flexibility.
    """

    def show_code_with_override(
        self,
        code_string: str,
        language: str = "python",
        line_numbers: bool = True,
        expert_style=None,
    ):
        """Show code with optional expert-level style override."""
        return super().show_code(code_string, language, line_numbers, style=expert_style)


# ============================================================================
# PROJECT-SPECIFIC HELPERS
# ============================================================================

def show_advanced_warning(title: str, description: str):
    """Warning box for deprecated features."""
    with st_block(s.project.containers.bad_callout):
        st_write(s.project.titles.warning_label, f"⚠️ {title}")
        st_space("v", 1)
        st_write(s.large, description)


def show_advanced_note(title: str, description: str):
    """Note box for important considerations."""
    with st_block(s.project.containers.note_callout):
        st_write(s.project.titles.tip_label, f"📌 {title}")
        st_space("v", 1)
        st_write(s.large, description)


def show_performance_insight(metric: str, value: str, note: str):
    """Performance metrics and optimization tips."""
    with st_block(s.project.containers.explanation_box):
        st_write(s.project.titles.section_subtitle, f"{metric}: {value}")
        st_space("v", 1)
        st_write(s.large, note)


def show_api_reference(method_name: str, signature: str, description: str):
    """API reference documentation."""
    with st_block(s.project.containers.code_box):
        st_write(s.project.titles.section_subtitle, method_name)
        show_code(signature, language="python")
        st_space("v", 1)
        st_write(s.large, description)


# ============================================================================
# DEMONSTRATION HELPERS (For documenting the patterns)
# ============================================================================

def demonstrate_simple_pattern():
    """Simple pattern: just call the function."""
    show_code("print('hello')")


def demonstrate_config_pattern():
    """Config pattern: styles injected automatically."""
    show_code("print('hello')")


def demonstrate_oop_pattern():
    """OOP pattern: use class with methods."""
    helper = ProjectBlockHelper()
    helper.show_code("print('hello')")
    helper.show_advanced_comparison("old_code()", "new_code()")


def demonstrate_expert_pattern():
    """Expert pattern: combine all three."""
    expert = ExpertBlockHelper()
    expert.show_code_with_override("print('hello')")
