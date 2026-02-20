"""Block helpers — hybrid approach template.

OVERVIEW:
This module shows how to use StreamTeX's hybrid block helpers system:

1. CONFIG INJECTION (Recommended for most projects)
   - Define ProjectBlockHelperConfig with your project's styles
   - Call set_block_helper_config() once at startup
   - All helpers automatically use your styles globally
   - Simple, DRY, no boilerplate

2. STANDALONE FUNCTIONS (Optional convenience)
   - Import helpers from streamtex or use local wrappers
   - Can override style per-call with style= parameter
   - Good for simple cases

3. OOP INHERITANCE (Advanced)
   - Subclass BlockHelper for custom behavior
   - Override methods to add logic before/after parent calls
   - Good for complex cases, custom workflows

4. PROJECT-SPECIFIC HELPERS (Always add these)
   - Create helpers unique to your project
   - Use local styles, custom logic, domain-specific UI

START HERE:
1. Rename "ProjectBlockHelperConfig" to match your project
2. Fill in get_*_style() methods with YOUR project's styles
3. Add your project-specific helpers at the bottom
4. Call set_block_helper_config() once in your book.py

See documentation/manuals/sx_manual_intro/blocks/helpers.py for a complete example.
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
# 1. DEPENDENCY INJECTION CONFIG (Required step)
# ============================================================================
# This is the key to the hybrid approach!
# Your project-specific styles are injected globally, so all helpers
# use them automatically without passing style= parameters everywhere.

class ProjectBlockHelperConfig(BlockHelperConfig):
    """Dependency Injection: Inject your project styles into all helpers.

    Override the get_*_style() methods to return your project's styles.
    These styles will be used automatically by show_code(), show_explanation(),
    and other helpers throughout your project.

    Example:
        def get_code_style(self):
            return s.project.containers.code_box
    """

    def get_code_style(self):
        """Style for show_code() — override with your project style."""
        # EXAMPLE: return s.project.containers.code_box
        return None

    def get_code_inline_style(self):
        """Style for show_code_inline() — override with your project style."""
        # EXAMPLE: return s.project.containers.code_inline
        return None

    def get_explanation_style(self):
        """Style for show_explanation() — override with your project style."""
        # EXAMPLE: return s.project.containers.explanation_box
        return None

    def get_details_style(self):
        """Style for show_details() — override with your project style."""
        # EXAMPLE: return s.project.containers.details_box
        return None


# CRITICAL: Initialize the config once at startup
# (This happens when helpers.py is imported, usually from book.py)
set_block_helper_config(ProjectBlockHelperConfig())


# ============================================================================
# 2. OPTIONAL WRAPPERS (Convenience shortcuts)
# ============================================================================
# These are optional! You can use them OR call streamtex functions directly.
# They add nothing, just convenience if you prefer local imports.

def show_code(code_string: str, language: str = "python", line_numbers: bool = True):
    """Shortcut: uses config-injected style automatically (via _show_code)."""
    return _show_code(code_string, language, line_numbers)


def show_code_inline(code_string: str, language: str = "python", line_numbers: bool = True):
    """Shortcut: uses config-injected style automatically."""
    return _show_code_inline(code_string, language, line_numbers)


def show_explanation(text: str):
    """Shortcut: uses config-injected style automatically."""
    return _show_explanation(text)


def show_details(text: str):
    """Shortcut: uses config-injected style automatically."""
    return _show_details(text)


# ============================================================================
# 3. OPTIONAL OOP BASE CLASS (For advanced inheritance patterns)
# ============================================================================
# Only use this if you need to override helpers via inheritance.
# Most projects don't need this.

class ProjectBlockHelper(BlockHelper):
    """Optional OOP base for advanced helper customization.

    Only inherit from this if you need to override helper methods
    with custom logic. For most projects, the config injection above
    is sufficient.

    Example:
        class ProjectBlockHelper(BlockHelper):
            def show_code(self, code_string):
                # Custom logic before/after
                return super().show_code(code_string)

    Usage in blocks:
        from blocks.helpers import ProjectBlockHelper
        helper = ProjectBlockHelper()
        helper.show_code("print('hello')")
    """
    pass


# ============================================================================
# 4. PROJECT-SPECIFIC HELPERS (Add your own!)
# ============================================================================
# This is where you define helpers unique to your project.
# Examples:
#   - show_welcome_box() for your homepage
#   - show_feature_highlight() for feature pages
#   - show_code_with_explanation() combining multiple primitives
#   - show_custom_diagram() with your domain-specific styling

# TODO: Add your project-specific helpers here
# Examples:

# def show_welcome_box(title: str, subtitle: str):
#     """Homepage welcome section."""
#     with st_block(s.project.welcome_style):
#         st_write(s.titles.page_title, title)
#         st_write(s.titles.subtitle, subtitle)


# def show_feature_box(icon: str, name: str, description: str):
#     """Feature highlight card."""
#     with st_block(s.project.feature_style):
#         st_write(s.project.feature_icon, icon)
#         st_write(s.titles.feature_title, name)
#         st_space("v", 1)
#         st_write(s.body, description)


# ============================================================================
# USAGE PATTERNS
# ============================================================================
#
# Pattern 1: Simple usage (recommended for most cases)
# ─────────────────────────────────────────────────
#   from blocks.helpers import show_code
#   show_code("print('hello')")
#   # Style is injected automatically from ProjectBlockHelperConfig
#
# Pattern 2: Override style for a single call
# ─────────────────────────────────────────────
#   from streamtex import show_code
#   show_code("print('hello')", style=s.custom.special_style)
#   # Uses your custom style instead of config default
#
# Pattern 3: OOP pattern (advanced)
# ─────────────────────────────────
#   from blocks.helpers import ProjectBlockHelper
#   helper = ProjectBlockHelper()
#   helper.show_code("print('hello')")
#   # Delegates to config-injected version
#
# Pattern 4: Add new config at runtime (expert)
# ──────────────────────────────────────────────
#   from streamtex import set_block_helper_config
#   class SpecialConfig(BlockHelperConfig):
#       def get_code_style(self): return s.special.code
#   set_block_helper_config(SpecialConfig())
#   # All subsequent calls use SpecialConfig
