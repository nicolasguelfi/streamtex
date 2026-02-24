"""Atomic block — Docker Compose for multi-project deployment."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os

# Resolve path to docker-compose.yml
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(_project_root)))
_compose_path = os.path.join(_repo_root, "docker-compose.yml")


class BlockStyles:
    """Docker Compose block styles."""
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.sub, "Docker Compose (multi-project)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Use docker-compose.yml to launch multiple projects simultaneously. "
            "The file at the repo root defines 3 services: collection, intro, and advanced, "
            "each on a different port."
        )
        st_space("v", 1)

        # Show the docker-compose.yml
        try:
            with open(_compose_path) as f:
                compose_content = f.read()
        except FileNotFoundError:
            compose_content = "# docker-compose.yml not found"

        show_code(compose_content, language="yaml")
        st_space("v", 2)

        # --- Commands ---
        st_write(bs.sub, "Docker Compose commands", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Build and run all 3 projects
            docker compose up --build

            # Run only the intro project
            docker compose up --build intro

            # Run in background (detached)
            docker compose up -d --build

            # Stop all projects
            docker compose down

            # Follow logs for a specific project
            docker compose logs -f intro
        """), language="bash")
        st_space("v", 2)

        # --- Port mapping ---
        st_write(bs.sub, "Default port mapping", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Service")
            with g.cell(): st_write(s.bold + s.large, "URL")
            with g.cell(): st_write(s.bold + s.large, "Project")

            with g.cell(): st_write(s.large, "collection")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large,
                                    "http://localhost:8501")
            with g.cell(): st_write(s.large, "stx_manuals_collection")

            with g.cell(): st_write(s.large, "intro")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large,
                                    "http://localhost:8502")
            with g.cell(): st_write(s.large, "stx_manual_intro")

            with g.cell(): st_write(s.large, "advanced")
            with g.cell(): st_write(s.project.colors.accent_teal + s.large,
                                    "http://localhost:8503")
            with g.cell(): st_write(s.large, "stx_manual_advanced")

        st_space("v", 2)

        show_details(
            "Each service builds its own Docker image with the appropriate FOLDER build-arg. "
            "All services include health checks and auto-restart (unless-stopped). "
            "To add your own project, duplicate a service block and change the FOLDER arg."
        )
