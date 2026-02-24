"""Block — CI/CD with GitHub Actions."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os

# Resolve path to the workflow file
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(_project_root)))
_ci_yml_path = os.path.join(_repo_root, ".github", "workflows", "ci.yml")


class BlockStyles:
    """CI/CD block styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "CI/CD with GitHub Actions", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(
            "Automated testing and Docker builds on every push and pull request. "
            "The workflow uses uv for fast dependency installation "
            "and verifies the Docker image with a health check."
        )
        st_space("v", 2)

        # --- What it does ---
        st_write(bs.sub, "Pipeline overview", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Job")
            with g.cell(): st_write(s.bold + s.large, "Trigger")
            with g.cell(): st_write(s.bold + s.large, "Steps")

            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "Tests & Lint")
            with g.cell(): st_write(s.large, "Every push and PR")
            with g.cell(): st_write(s.large,
                                    "Install uv → Install Python → Sync deps → Lint → Tests")

            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "Docker Build")
            with g.cell(): st_write(s.large, "Push to main only")
            with g.cell(): st_write(s.large,
                                    "Build image → Start container → Health check → Stop")

        st_space("v", 2)

        # --- The workflow file ---
        st_write(bs.sub, "The workflow file", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Located at .github/workflows/ci.yml. "
            "Uses the official astral-sh/setup-uv action for fast dependency caching."
        )
        st_space("v", 1)

        try:
            with open(_ci_yml_path) as f:
                ci_content = f.read()
        except FileNotFoundError:
            ci_content = "# ci.yml not found"

        show_code(ci_content, language="yaml")
        st_space("v", 2)

        # --- How to use ---
        st_write(bs.sub, "How it works", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "The workflow runs automatically. No manual setup required beyond "
            "having the file in .github/workflows/. "
            "GitHub provides free CI/CD minutes for public repos."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # The workflow triggers automatically on:
            # - Push to main branch
            # - Pull request targeting main

            # To check status:
            # 1. Go to your repo on GitHub
            # 2. Click the "Actions" tab
            # 3. See the workflow runs and their status

            # Failed runs block PR merges (if branch protection is enabled)
        """), language="text")
        st_space("v", 2)

        show_details(
            "The Docker Build job only runs on push to main (not on PRs) to save CI minutes. "
            "It builds the image, starts a container, waits 10 seconds, "
            "then verifies the health endpoint responds. "
            "To add deployment automation, extend the workflow with push-to-registry steps."
        )
