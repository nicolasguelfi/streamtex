"""Quick Start — Installation."""

import textwrap
from streamtex import *
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details


class BlockStyles:
    """Quick Start installation styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle


bs = BlockStyles


def build():
    """Quick Start Step 1: Install StreamTeX and verify the environment."""
    st_space("v", 1)
    st_write(bs.heading, "Quick Start — Installation",
             tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Prerequisites ---
    st_write(bs.sub, "Step 1: Prerequisites", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        StreamTeX requires Python 3.10 or later
        and uses uv as its package manager.

        Make sure both are installed before continuing.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # Check Python version (3.10+ required)
        python3 --version

        # Install uv (if not already installed)
        curl -LsSf https://astral.sh/uv/install.sh | sh
    """), language="bash", line_numbers=False)
    st_space("v", 2)

    # --- Clone the repository ---
    st_write(bs.sub, "Step 2: Clone the repository", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Clone the StreamTeX repository from GitHub.

        This gives you the library source, templates,
        and example projects.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        git clone https://github.com/your-org/streamtex.git
        cd streamtex
    """), language="bash", line_numbers=False)
    st_space("v", 2)

    # --- Setup the environment ---
    st_write(bs.sub, "Step 3: Setup the environment", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Run uv sync to create a virtual environment
        and install all dependencies automatically.

        This reads pyproject.toml and resolves packages.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # Install all dependencies (creates .venv/)
        uv sync
    """), language="bash", line_numbers=False)
    st_space("v", 2)

    # --- Verify installation ---
    st_write(bs.sub, "Step 4: Verify installation", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Run the test suite to confirm everything
        is set up correctly. All tests should pass.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        uv run pytest tests/ -v
    """), language="bash", line_numbers=False)
    st_space("v", 2)

    show_details(textwrap.dedent("""\
        Always prefix commands with uv run.
        This ensures the correct virtual environment
        and dependencies are used.

        Never call python,
        pytest, or streamlit directly.
    """))
    st_space("v", 1)
