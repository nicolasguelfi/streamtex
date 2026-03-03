"""
Block rendering helpers with 3 usage modes:
1. Simple: from streamtex import show_code; show_code(...)
2. Advanced: class MyHelper(BlockHelper): ...
3. Expert: set_block_helper_config(MyConfig())
"""

import textwrap
from typing import Optional

import streamlit as st

import streamtex as stx
from streamtex import st_block, st_space, st_write
from streamtex.styles import StxStyles
from streamtex.utils import generate_key


def _render_md_body(body: str) -> None:
    """Render Markdown with StxStyles.big, overriding Streamlit's <p>/<li> font-size.

    Uses the same :has() scoping mechanism as st_block but adds explicit
    CSS rules for <p> and <li> descendants so that Streamlit's own
    font-size declarations are overridden.
    """
    uid = generate_key("md")
    big_css = str(StxStyles.big)
    sel = f"div:has(> .element-container > .stHtml > span.{uid})"
    st.html(
        f"<style>"
        f"{sel} {{ {big_css} }} "
        f"{sel} p, {sel} li {{ {big_css} }} "
        f".element-container:has(.stHtml > span.{uid}) {{ width: auto; }}"
        f"</style>"
    )
    with st.container():
        st.html(f'<span class="{uid}" style="display:none"></span>')
        st.markdown(body, unsafe_allow_html=True)


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
    code_string: str = "",
    language: str = "python",
    line_numbers: bool = True,
    style: Optional[object] = None,
    wrap: Optional[bool] = None,
    file: str | None = None,
    encoding: str = "utf-8",
    line_start: int | None = None,
    start_line: int | None = None,
    end_line: int | None = None,
) -> None:
    """Display syntax-highlighted code in a styled box.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_code_style() (if set_block_helper_config() was called)
    3. None (raw code box)

    Args:
        code_string: Code to display (mutually exclusive with *file*)
        language: Programming language for syntax highlighting
        line_numbers: Show line numbers
        style: Optional style override
        wrap: When True, long lines wrap instead of scrolling horizontally
        file: Path to a source file (resolved via resolve_static)
        encoding: File encoding (only used with *file*)
        line_start: First line number displayed (Pygments linenostart)
        start_line: 1-based first line to extract from content
        end_line: 1-based last line to extract from content (inclusive)

    Example:
        # Simple usage (no style)
        show_code("print('hello')")

        # From file
        show_code(file="examples/text/basics_plain.py")

        # With config (auto style via BlockHelperConfig)
        set_block_helper_config(MyConfig())
        show_code("print('hello')")  # Uses MyConfig.get_code_style()
    """
    resolved_style = style or _block_helper_config.get_code_style()
    stx.st_code(
        resolved_style,
        code=code_string,
        language=language,
        line_numbers=line_numbers,
        wrap=wrap,
        file=file,
        encoding=encoding,
        line_start=line_start,
        start_line=start_line,
        end_line=end_line,
    )


def show_code_inline(
    code_string: str = "",
    language: str = "python",
    line_numbers: bool = True,
    style: Optional[object] = None,
    wrap: Optional[bool] = None,
    file: str | None = None,
    encoding: str = "utf-8",
    line_start: int | None = None,
    start_line: int | None = None,
    end_line: int | None = None,
) -> None:
    """Display code without box wrapper — for use inside containers.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_code_inline_style()
    3. None (raw code)

    Args:
        code_string: Code to display (mutually exclusive with *file*)
        language: Programming language for syntax highlighting
        line_numbers: Show line numbers
        style: Optional style override
        wrap: When True, long lines wrap instead of scrolling horizontally
        file: Path to a source file (resolved via resolve_static)
        encoding: File encoding (only used with *file*)
        line_start: First line number displayed (Pygments linenostart)
        start_line: 1-based first line to extract from content
        end_line: 1-based last line to extract from content (inclusive)
    """
    resolved_style = style or _block_helper_config.get_code_inline_style()
    stx.st_code(
        resolved_style,
        code=code_string,
        language=language,
        line_numbers=line_numbers,
        wrap=wrap,
        file=file,
        encoding=encoding,
        line_start=line_start,
        start_line=start_line,
        end_line=end_line,
    )


def show_explanation(text: str, style: Optional[object] = None) -> None:
    """Display styled explanation box before an example.

    Pass a multi-line string with standard Markdown formatting
    (bold, italic, lists, links, code spans…).  Indentation is
    automatically removed (textwrap.dedent) so callers don't need to.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_explanation_style()
    3. None (no box styling)

    Args:
        text: Multi-line Markdown explanation text
        style: Optional style override

    Example:
        show_explanation('''
            **st_markdown()** renders interpreted Markdown content.
            Use it for documentation with *formatting*.
        ''')
    """
    resolved_style = style or _block_helper_config.get_explanation_style()
    body = textwrap.dedent(text).strip()
    with st_block(resolved_style):
        st_write(StxStyles.big + StxStyles.bold, "Purpose")  # Label
        st_space("v", 1)
        if body:
            _render_md_body(body)


def show_details(text: str, style: Optional[object] = None) -> None:
    """Display 'Details:' section with Markdown-formatted content.

    Pass a multi-line string with standard Markdown formatting
    (bold, italic, lists, links, code spans…).  Indentation is
    automatically removed (textwrap.dedent) so callers don't need to.

    Style resolution (in order):
    1. Explicit style parameter (if provided)
    2. Config's get_details_style()
    3. None (no box styling)

    Args:
        text: Multi-line Markdown text
        style: Optional style override

    Example:
        show_details('''
            **Key point**: this is the main takeaway.

            Additional details with *emphasis* and `code`.
        ''')
    """
    resolved_style = style or _block_helper_config.get_details_style()
    body = textwrap.dedent(text).strip()
    with st_block(resolved_style):
        st_write(StxStyles.big + StxStyles.bold, "Details:")  # Label
        st_space("v", 1)
        if body:
            _render_md_body(body)


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
        code_string: str = "",
        language: str = "python",
        line_numbers: bool = True,
        style: Optional[object] = None,
        wrap: Optional[bool] = None,
        file: str | None = None,
        encoding: str = "utf-8",
        line_start: int | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> None:
        """Delegate to module-level show_code()."""
        show_code(
            code_string, language, line_numbers, style, wrap=wrap,
            file=file, encoding=encoding, line_start=line_start,
            start_line=start_line, end_line=end_line,
        )

    def show_code_inline(
        self,
        code_string: str = "",
        language: str = "python",
        line_numbers: bool = True,
        style: Optional[object] = None,
        wrap: Optional[bool] = None,
        file: str | None = None,
        encoding: str = "utf-8",
        line_start: int | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> None:
        """Delegate to module-level show_code_inline()."""
        show_code_inline(
            code_string, language, line_numbers, style, wrap=wrap,
            file=file, encoding=encoding, line_start=line_start,
            start_line=start_line, end_line=end_line,
        )

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
