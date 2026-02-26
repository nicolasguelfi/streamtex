"""Block helpers for stx_manual_advanced — COMPLETE hybrid showcase.

This module demonstrates ALL 3 usage patterns of the hybrid block helpers system:

1. CONFIG INJECTION (DI Pattern)
   - Define ProjectBlockHelperConfig
   - set_block_helper_config() injects styles globally
   - All helpers automatically use project styles

2. STANDALONE FUNCTIONS (Simple Pattern)
   - Import from streamtex or use local wrappers
   - Can override style per-call

3. OOP INHERITANCE (Advanced Pattern)
   - Subclass BlockHelper
   - Override methods, add custom logic
   - Chain via super()

This project is used to DOCUMENT and SHOWCASE all patterns in detail.
Each pattern is explained in dedicated advanced blocks (bck_*).

See stx_manual_intro/blocks/helpers.py for the minimal SIMPLE pattern only.
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
# PATTERN 1: CONFIG INJECTION (Dependency Injection)
# ============================================================================
# This is the recommended pattern for most projects.
# Define your config once, and all helpers use your styles globally.

class ProjectBlockHelperConfig(BlockHelperConfig):
    """DI Config: Inject advanced project styles into all helpers.

    This is called once at startup via set_block_helper_config().
    All show_code(), show_explanation(), etc. will use these styles
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


# Initialize the global config
set_block_helper_config(ProjectBlockHelperConfig())


# ============================================================================
# PATTERN 2: STANDALONE FUNCTIONS (Simple Pattern)
# ============================================================================
# Optional convenience wrappers. Use these OR call streamtex functions directly.

def show_code(code_string: str, language: str = "python", line_numbers: bool = True, wrap=None):
    """Simple wrapper — uses config-injected style automatically."""
    return _show_code(code_string, language, line_numbers, wrap=wrap)


def show_code_inline(code_string: str, language: str = "python", line_numbers: bool = True, wrap=None):
    """Simple wrapper — uses config-injected style automatically."""
    return _show_code_inline(code_string, language, line_numbers, wrap=wrap)


def show_explanation(text: str):
    """Simple wrapper — uses config-injected style automatically."""
    return _show_explanation(text)


def show_details(text: str):
    """Simple wrapper — uses config-injected style automatically."""
    return _show_details(text)


# ============================================================================
# PATTERN 3: OOP INHERITANCE (Advanced Pattern)
# ============================================================================
# Use this when you need to override helpers with custom logic.

class ProjectBlockHelper(BlockHelper):
    """Advanced OOP base for custom helper logic.

    Demonstrates how to override parent methods from BlockHelper
    and add project-specific methods.

    Usage:
        helper = ProjectBlockHelper()
        helper.show_code("...")
        helper.show_advanced_comparison("before", "after")
    """

    # Override: Add custom logic before parent call
    def show_code(self, code_string: str, language: str = "python", line_numbers: bool = True, wrap=None):
        """Example override: Could add logging, analytics, etc."""
        # Custom logic here if needed
        return super().show_code(code_string, language, line_numbers, wrap=wrap)

    # New method: Project-specific helper
    def show_advanced_comparison(self, before: str, after: str, label: str = "Comparison"):
        """Advanced-specific helper: Side-by-side comparison."""
        with st_block(s.project.containers.code_box):
            st_write(s.project.titles.section_title, label)
            st_space("v", 1)
            st_write(s.large, "Before:")
            _show_code(before)
            st_space("v", 2)
            st_write(s.large, "After:")
            _show_code(after)


# ============================================================================
# BONUS: EXPERT PATTERN (Advanced users only)
# ============================================================================
# For users who want to combine OOP + Config Injection + Runtime overrides.

class ExpertBlockHelper(ProjectBlockHelper):
    """Expert pattern: Combines all 3 modes.

    - Inherits from ProjectBlockHelper (OOP mode)
    - Uses global config (DI mode)
    - Can override at call-time (Function mode)

    This is for power users who need maximum flexibility.
    """

    def show_code_with_override(
        self,
        code_string: str,
        language: str = "python",
        line_numbers: bool = True,
        expert_style = None
    ):
        """Show code with optional expert-level style override."""
        return super().show_code(code_string, language, line_numbers)


# ============================================================================
# PROJECT-SPECIFIC HELPERS: Unique to advanced project
# ============================================================================
# These are helpers that only make sense in the advanced context.

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
        _show_code(signature, language="python")
        st_space("v", 1)
        st_write(s.large, description)


# ============================================================================
# DEMONSTRATION HELPER (For documenting the patterns)
# ============================================================================

def demonstrate_simple_pattern():
    """Simple pattern: just call the function."""
    show_code("print('hello')")


def demonstrate_config_pattern():
    """Config pattern: styles injected automatically."""
    # ProjectBlockHelperConfig was set at module load time
    # All subsequent show_code() calls use those styles
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
