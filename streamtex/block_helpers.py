"""
Block rendering helpers with 3 usage modes:
1. Simple: from streamtex import show_code; show_code(...)
2. Advanced: class MyHelper(BlockHelper): ...
3. Expert: set_block_helper_config(MyConfig())
"""

from typing import Optional

import streamtex as stx
from streamtex import st_block, st_br, st_space, st_write
from streamtex.styles import StxStyles


class BlockHelperConfig:
    """Configuration injectable for block helpers (Dependency Injection).

    Override in projects to customize default styles for all helpers.

    Example:
        class ProjectBlockHelperConfig(BlockHelperConfig):
            def get_code_style(self):
                return my_styles.project.containers.code_box

        set_block_helper_config(ProjectBlockHelperConfig())
    """

    def get_code_style(self) -> Optional[object]:
        """Default style for show_code() — override in subclass."""
        return None

    def get_code_inline_style(self) -> Optional[object]:
        """Default style for show_code_inline() — override in subclass."""
        return None

    def get_explanation_style(self) -> Optional[object]:
        """Default style for show_explanation() — override in subclass."""
        return None

    def get_details_style(self) -> Optional[object]:
        """Default style for show_details() — override in subclass."""
        return None


# Global configuration instance
_block_helper_config: BlockHelperConfig = BlockHelperConfig()


def set_block_helper_config(config: BlockHelperConfig) -> None:
    """Set global block helper configuration (Dependency Injection).

    Call this once at project startup to inject project-specific styles.

    Args:
        config: BlockHelperConfig subclass instance with custom styles

    Example:
        from streamtex import set_block_helper_config
        from custom.styles import Styles as s

        class MyConfig(BlockHelperConfig):
            def get_code_style(self):
                return s.project.containers.code_box

        set_block_helper_config(MyConfig())
    """
    global _block_helper_config
    _block_helper_config = config


def get_block_helper_config() -> BlockHelperConfig:
    """Get current block helper configuration."""
    return _block_helper_config


def show_code(
    code_string: str,
    language: str = "python",
    line_numbers: bool = True,
    style: Optional[object] = None,
    wrap: bool = False,
) -> None:
    """Display syntax-highlighted code in a styled box.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_code_style() (if set_block_helper_config() was called)
    3. None (raw code box)

    Args:
        code_string: Code to display
        language: Programming language for syntax highlighting
        line_numbers: Show line numbers
        style: Optional style override
        wrap: When True, long lines wrap instead of scrolling horizontally

    Example:
        # Simple usage (no style)
        show_code("print('hello')")

        # With explicit style
        show_code("print('hello')", style=my_style)

        # With config (auto style via BlockHelperConfig)
        set_block_helper_config(MyConfig())
        show_code("print('hello')")  # Uses MyConfig.get_code_style()
    """
    resolved_style = style or _block_helper_config.get_code_style()
    stx.st_code(resolved_style, code=code_string, language=language, line_numbers=line_numbers, wrap=wrap)


def show_code_inline(
    code_string: str,
    language: str = "python",
    line_numbers: bool = True,
    style: Optional[object] = None,
    wrap: bool = False,
) -> None:
    """Display code without box wrapper — for use inside containers.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_code_inline_style()
    3. None (raw code)

    Args:
        code_string: Code to display
        language: Programming language for syntax highlighting
        line_numbers: Show line numbers
        style: Optional style override
        wrap: When True, long lines wrap instead of scrolling horizontally
    """
    resolved_style = style or _block_helper_config.get_code_inline_style()
    stx.st_code(resolved_style, code=code_string, language=language, line_numbers=line_numbers, wrap=wrap)


def show_explanation(text: str, style: Optional[object] = None) -> None:
    """Display styled explanation box before an example.

    Pass a multi-line string (use textwrap.dedent). Each non-empty line
    is rendered on its own line for readability.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_explanation_style()
    3. None (no box styling)

    Args:
        text: Multi-line explanation text
        style: Optional style override

    Example:
        show_explanation(textwrap.dedent('''
            This is the purpose of the example.
            It shows how to use the feature.
        '''))
    """
    resolved_style = style or _block_helper_config.get_explanation_style()
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    with st_block(resolved_style):
        st_write(StxStyles.big + StxStyles.bold, "Purpose")  # Label
        st_space("v", 1)
        for i, line in enumerate(lines):
            st_write(StxStyles.big, line)
            if i < len(lines) - 1:
                st_br()


def show_details(text: str, style: Optional[object] = None) -> None:
    """Display 'Details:' section with summary + expanded text.

    Pass a multi-line string (use textwrap.dedent). The first line becomes
    the bold summary; subsequent lines are detail text.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_details_style()
    3. None (no box styling)

    Args:
        text: Multi-line text (first line = summary, rest = details)
        style: Optional style override

    Example:
        show_details(textwrap.dedent('''
            This is the main point.
            This is an additional detail.
            Another detail here.
        '''))
    """
    resolved_style = style or _block_helper_config.get_details_style()
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    with st_block(resolved_style):
        st_write(StxStyles.big + StxStyles.bold, "Details:")  # Label
        st_space("v", 1)
        if lines:
            st_write(StxStyles.big, lines[0])  # Summary
            if len(lines) > 1:
                st_space("v", 1)
                for i, line in enumerate(lines[1:]):
                    st_write(StxStyles.big, line)
                    if i < len(lines) - 2:
                        st_br()


class BlockHelper:
    """Base class for advanced block helper patterns (OOP inheritance).

    Use this if you want to override helpers via inheritance in your project.
    Methods delegate to the module-level functions, respecting global config.

    Example:
        class ProjectBlockHelper(BlockHelper):
            def show_code(self, code_string, language="python", line_numbers=True):
                # Add custom logic before/after
                return super().show_code(code_string, language, line_numbers)
    """

    def show_code(
        self,
        code_string: str,
        language: str = "python",
        line_numbers: bool = True,
        style: Optional[object] = None,
        wrap: bool = False,
    ) -> None:
        """Delegate to module-level show_code()."""
        show_code(code_string, language, line_numbers, style, wrap=wrap)

    def show_code_inline(
        self,
        code_string: str,
        language: str = "python",
        line_numbers: bool = True,
        style: Optional[object] = None,
        wrap: bool = False,
    ) -> None:
        """Delegate to module-level show_code_inline()."""
        show_code_inline(code_string, language, line_numbers, style, wrap=wrap)

    def show_explanation(
        self,
        text: str,
        style: Optional[object] = None
    ) -> None:
        """Delegate to module-level show_explanation()."""
        show_explanation(text, style)

    def show_details(
        self,
        text: str,
        style: Optional[object] = None
    ) -> None:
        """Delegate to module-level show_details()."""
        show_details(text, style)
