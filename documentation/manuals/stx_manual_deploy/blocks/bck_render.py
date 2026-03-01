"""Block — Deploy on Render.com."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os

# Resolve path to render.yaml
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(_project_root)))
_render_yaml_path = os.path.join(_repo_root, "render.yaml")


class BlockStyles:
    """Render.com block styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Render.com", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(
            "Production-ready hosting with a free tier (750h/month) and custom domains. "
            "No credit card required. Supports Docker and auto-deploys from GitHub."
        )
        st_space("v", 2)

        # --- Plans ---
        st_write(bs.sub, "Plans", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Plan")
            with g.cell(): st_write(s.bold + s.large, "Cost")
            with g.cell(): st_write(s.bold + s.large, "Details")

            with g.cell(): st_write(s.project.colors.success_green + s.large, "Free")
            with g.cell(): st_write(s.large, "$0/month")
            with g.cell(): st_write(s.large,
                                    "750h/month, sleep after 15 min, 100 GB bandwidth")

            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "Starter")
            with g.cell(): st_write(s.large, "$7/month")
            with g.cell(): st_write(s.large, "Always-on, no sleep, custom domain with SSL")

        st_space("v", 2)

        # --- Automated deployment ---
        st_write(bs.sub, "Automated deployment", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Use the deployment script. It runs preflight checks, "
            "validates render.yaml, optionally tests Docker locally, "
            "and guides you through the Render.com setup."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Deploy the default project
            ./deploy/render.sh

            # Deploy a specific project
            ./deploy/render.sh projects/project_aiai18h
        """), language="bash")
        st_space("v", 2)

        # --- render.yaml ---
        st_write(bs.sub, "render.yaml (Infrastructure-as-Code)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "The repository includes a render.yaml at the root. "
            "When you connect your GitHub repo, Render auto-detects this file "
            "and creates the service. To deploy a different project, "
            "change the FOLDER env var."
        )
        st_space("v", 1)

        try:
            with open(_render_yaml_path) as f:
                render_content = f.read()
        except FileNotFoundError:
            render_content = "# render.yaml not found"

        show_code(render_content, language="yaml")
        st_space("v", 2)

        # --- Manual setup ---
        st_write(bs.sub, "Manual setup on Render.com", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Steps on dashboard.render.com:
            # 1. Click New → Web Service
            # 2. Connect your GitHub repo
            # 3. Configure:
            #    - Runtime: Docker
            #    - Dockerfile Path: ./Dockerfile
            #    - Docker Build Context: .
            # 4. Add environment variable:
            #    FOLDER = projects/your_project
            # 5. Set health check path: /_stcore/health
            # 6. Choose plan (Free or Starter)
            # 7. Click Create Web Service
        """), language="text")
        st_space("v", 2)

        # --- Multiple projects ---
        st_write(bs.sub, "Deploying multiple projects", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Create multiple Render services from the same repo, "
            "each with a different FOLDER env var. "
            "Each service gets its own URL."
        )
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Service")
            with g.cell(): st_write(s.bold + s.large, "FOLDER")
            with g.cell(): st_write(s.bold + s.large, "URL")

            with g.cell(): st_write(s.large, "streamtex-intro")
            with g.cell(): st_write(s.project.colors.neutral_gray + s.large,
                                    "documentation/manuals/stx_manual_intro")
            with g.cell(): st_write(s.large, "streamtex-intro.onrender.com")

            with g.cell(): st_write(s.large, "streamtex-advanced")
            with g.cell(): st_write(s.project.colors.neutral_gray + s.large,
                                    "documentation/manuals/stx_manual_advanced")
            with g.cell(): st_write(s.large, "streamtex-advanced.onrender.com")

            with g.cell(): st_write(s.large, "my-project")
            with g.cell(): st_write(s.project.colors.neutral_gray + s.large,
                                    "projects/project_aiai18h")
            with g.cell(): st_write(s.large, "my-project.onrender.com")

        st_space("v", 2)

        show_details(
            "Render auto-deploys on every push to main.\n\n"
            "Free tier: one always-on app fits in 750h/month (31 days x 24h = 744h). "
            "Two apps won't fit in the free quota.\n\n"
            "Custom domains get auto-SSL via Let's Encrypt."
        )
