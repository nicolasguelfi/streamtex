"""Atomic block — Docker build, run, and project targeting."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Docker build/run block styles."""
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        # --- 1. Basic build & run ---
        st_write(bs.sub, "Build and run", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Build the Docker image and run it. "
            "The default target project is documentation/manuals/stx_manual_intro."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Build the image (default project)
            docker build -t streamtex-app .

            # Run the container
            docker run -p 8501:8501 streamtex-app

            # Open http://localhost:8501
        """), language="bash")
        st_space("v", 2)

        # --- 2. Targeting a specific project ---
        st_write(bs.sub, "Targeting a specific project", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Use --build-arg FOLDER to deploy any project in the repository. "
            "The path is relative to the repo root."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Deploy a user project
            docker build \\
                --build-arg FOLDER=projects/project_aiai18h \\
                -t aiai18h-app .
            docker run -p 8501:8501 aiai18h-app

            # Deploy the advanced manual
            docker build \\
                --build-arg FOLDER=documentation/manuals/stx_manual_advanced \\
                -t advanced-app .
            docker run -p 8502:8501 advanced-app

            # Deploy this deployment manual
            docker build \\
                --build-arg FOLDER=documentation/manuals/stx_manual_deploy \\
                -t deploy-manual .
            docker run -p 8503:8501 deploy-manual
        """), language="bash")
        st_space("v", 2)

        # --- 3. Health check ---
        st_write(bs.sub, "Verifying the deployment", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "The Dockerfile includes a built-in health check. "
            "You can also verify manually with curl."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Check if the app is healthy
            curl --fail http://localhost:8501/_stcore/health

            # Check container status (should show "healthy")
            docker ps

            # View logs
            docker logs <container_id>
        """), language="bash")
        st_space("v", 2)

        show_details(
            "Port mapping: -p HOST_PORT:8501. The container always listens on 8501.\n\n"
            "Map different host ports to run multiple projects simultaneously."
        )
