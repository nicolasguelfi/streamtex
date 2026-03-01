"""Preflight checks — common pre-deployment validation."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os

# Resolve path to the preflight script
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(_project_root)))
_preflight_path = os.path.join(_repo_root, "deploy", "preflight.sh")


class BlockStyles:
    """Local styles for preflight block."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Pre-Deployment Checks", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(
            "Before deploying to any platform, run the preflight script. "
            "It validates tests, configuration, static assets, and git status."
        )
        st_space("v", 2)

        # --- Usage ---
        st_write(bs.sub, "Usage", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # General checks (tests + Streamlit version)
            ./deploy/preflight.sh

            # Project-specific checks (also validates config and assets)
            ./deploy/preflight.sh projects/your_project
            ./deploy/preflight.sh documentation/manuals/stx_manual_intro
        """), language="bash")
        st_space("v", 2)

        # --- What it checks ---
        st_write(bs.sub, "What gets validated", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Check")
            with g.cell(): st_write(s.bold + s.large, "Level")
            with g.cell(): st_write(s.bold + s.large, "Details")

            with g.cell(): st_write(s.large, "Unit tests")
            with g.cell(): st_write(s.project.colors.warning_red + s.large, "Blocking")
            with g.cell(): st_write(s.large, "uv run pytest tests/ -v")

            with g.cell(): st_write(s.large, "Streamlit version")
            with g.cell(): st_write(s.project.colors.warning_red + s.large, "Blocking")
            with g.cell(): st_write(s.large, "streamlit>=1.54.0 in pyproject.toml")

            with g.cell(): st_write(s.large, "book.py exists")
            with g.cell(): st_write(s.project.colors.warning_red + s.large, "Blocking")
            with g.cell(): st_write(s.large, "Entry point in project folder")

            with g.cell(): st_write(s.large, "enableStaticServing")
            with g.cell(): st_write(s.project.colors.warning_red + s.large, "Blocking")
            with g.cell(): st_write(s.large, "Must be true in .streamlit/config.toml")

            with g.cell(): st_write(s.large, "Static assets")
            with g.cell(): st_write(s.project.colors.highlight_amber + s.large, "Warning")
            with g.cell(): st_write(s.large, "Counts image files in static/")

            with g.cell(): st_write(s.large, "Git status")
            with g.cell(): st_write(s.project.colors.highlight_amber + s.large, "Warning")
            with g.cell(): st_write(s.large, "Warns if uncommitted changes")

        st_space("v", 2)

        # --- The script itself ---
        st_write(bs.sub, "The preflight script", toc_lvl="+1")
        st_space("v", 1)

        try:
            with open(_preflight_path) as f:
                script_content = f.read()
        except FileNotFoundError:
            script_content = "# preflight.sh not found at expected path"

        show_code(script_content, language="bash")
        st_space("v", 2)

        show_details(
            "Exit code 0 means all checks passed.\n\n"
            "Exit code 1 means a critical check failed (tests, config).\n\n"
            "Warnings (git dirty, missing static/) do not block deployment."
        )
