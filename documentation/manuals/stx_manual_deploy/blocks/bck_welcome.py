"""Welcome block — deployment overview and decision matrix."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_explanation, show_details


class BlockStyles:
    """Local styles for the welcome block."""
    heading = s.project.titles.course_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "StreamTeX Deployment Guide", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(
            "This manual covers every deployment option for StreamTeX projects: "
            "from local Docker testing to production cloud hosting. "
            "Each section includes step-by-step instructions and automation scripts."
        )
        st_space("v", 3)

        # --- Decision matrix ---
        st_write(bs.sub, "Which option should I use?", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=4, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            # Header row
            with g.cell(): st_write(s.bold + s.large, "I want to...")
            with g.cell(): st_write(s.bold + s.large, "Option")
            with g.cell(): st_write(s.bold + s.large, "Cost")
            with g.cell(): st_write(s.bold + s.large, "Docker?")
            # Row 1
            with g.cell(): st_write(s.large, "Test locally")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "Docker local")
            with g.cell(): st_write(s.large, "$0")
            with g.cell(): st_write(s.large, "Yes")
            # Row 2
            with g.cell(): st_write(s.large, "Share a quick demo")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "Streamlit Cloud")
            with g.cell(): st_write(s.large, "$0")
            with g.cell(): st_write(s.large, "No")
            # Row 3
            with g.cell(): st_write(s.large, "Free hosting with Docker")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "HuggingFace Spaces")
            with g.cell(): st_write(s.large, "$0")
            with g.cell(): st_write(s.large, "Yes")
            # Row 4
            with g.cell(): st_write(s.large, "Production + custom domain")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "Render.com")
            with g.cell(): st_write(s.large, "$0-7/mo")
            with g.cell(): st_write(s.large, "Yes")
            # Row 5
            with g.cell(): st_write(s.large, "Full server control")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large, "GCP VM + Ansible")
            with g.cell(): st_write(s.large, "~$5-25/mo")
            with g.cell(): st_write(s.large, "Optional")

        st_space("v", 3)

        # --- Comparison table ---
        st_write(bs.sub, "Platform comparison", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=5, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            # Header
            with g.cell(): st_write(s.bold + s.large, "Platform")
            with g.cell(): st_write(s.bold + s.large, "Custom domain")
            with g.cell(): st_write(s.bold + s.large, "Sleep")
            with g.cell(): st_write(s.bold + s.large, "Auto-deploy")
            with g.cell(): st_write(s.bold + s.large, "Best for")
            # Streamlit Cloud
            with g.cell(): st_write(s.large, "Streamlit Cloud")
            with g.cell(): st_write(s.project.colors.warning_red + s.large, "No")
            with g.cell(): st_write(s.large, "12h")
            with g.cell(): st_write(s.project.colors.success_green + s.large, "Yes")
            with g.cell(): st_write(s.large, "Quick demos")
            # HuggingFace
            with g.cell(): st_write(s.large, "HuggingFace")
            with g.cell(): st_write(s.large, "Paid only")
            with g.cell(): st_write(s.large, "~15 min")
            with g.cell(): st_write(s.project.colors.success_green + s.large, "Yes")
            with g.cell(): st_write(s.large, "Free Docker hosting")
            # Render
            with g.cell(): st_write(s.large, "Render.com")
            with g.cell(): st_write(s.project.colors.success_green + s.large, "Yes")
            with g.cell(): st_write(s.large, "15 min (free)")
            with g.cell(): st_write(s.project.colors.success_green + s.large, "Yes")
            with g.cell(): st_write(s.large, "Production apps")
            # GCP
            with g.cell(): st_write(s.large, "GCP VM")
            with g.cell(): st_write(s.project.colors.success_green + s.large, "Yes")
            with g.cell(): st_write(s.project.colors.success_green + s.large, "Never")
            with g.cell(): st_write(s.large, "Manual")
            with g.cell(): st_write(s.large, "Full control")

        st_space("v", 2)

        show_details(
            "All Docker-based deployments use the same Dockerfile at the repository root. "
            "The FOLDER build-arg selects which project to deploy.\n\n"
            "Before deploying, always run the preflight checks (next section)."
        )
