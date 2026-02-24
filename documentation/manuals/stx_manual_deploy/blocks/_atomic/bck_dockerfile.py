"""Atomic block — The StreamTeX Dockerfile explained."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os

# _atomic/ → blocks/ → project root → manuals/ → documentation/ → repo root
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(_project_root)))
_dockerfile_path = os.path.join(_repo_root, "Dockerfile")
_dockerignore_path = os.path.join(_repo_root, ".dockerignore")


class BlockStyles:
    """Dockerfile block styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Docker Local Deployment", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # --- 1. The Dockerfile ---
        st_write(bs.sub, "The StreamTeX Dockerfile", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "The repository includes a production-ready Dockerfile at the root. "
            "It uses a multi-stage strategy: install uv, sync dependencies in a cached layer, "
            "then copy the target project. The FOLDER build-arg selects which project to deploy."
        )
        st_space("v", 1)

        try:
            with open(_dockerfile_path) as f:
                dockerfile_content = f.read()
        except FileNotFoundError:
            dockerfile_content = "# Dockerfile not found at expected path"

        show_code(dockerfile_content, language="dockerfile")
        st_space("v", 2)

        # --- 2. Environment variables ---
        st_write(bs.sub, "Environment variables", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "The Dockerfile sets several ENV variables for headless operation and performance."
        )
        st_space("v", 1)

        with st_grid(cols=2, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Variable")
            with g.cell(): st_write(s.bold + s.large, "Purpose")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "STREAMLIT_SERVER_HEADLESS=true")
            with g.cell():
                st_write(s.large, "Run without opening a browser")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "PYTHONDONTWRITEBYTECODE=1")
            with g.cell():
                st_write(s.large, "Skip .pyc file creation (smaller image)")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "PYTHONUNBUFFERED=1")
            with g.cell():
                st_write(s.large, "Real-time log output")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "UV_LINK_MODE=copy")
            with g.cell():
                st_write(s.large, "Copy files instead of hardlinks (Docker compat)")

        st_space("v", 2)

        # --- 3. .dockerignore ---
        st_write(bs.sub, "The .dockerignore file", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "The .dockerignore excludes files not needed in production images: "
            "tests, IDE config, .git, .venv, documentation markdown files, etc. "
            "This reduces image size and build time."
        )
        st_space("v", 1)

        try:
            with open(_dockerignore_path) as f:
                dockerignore_content = f.read()
        except FileNotFoundError:
            dockerignore_content = "# .dockerignore not found"

        show_code(dockerignore_content, language="text")
        st_space("v", 2)

        show_details(
            "The container exposes port 8501 with a built-in health check. "
            "uv is installed from the official Docker image (ghcr.io/astral-sh/uv). "
            "Dependencies are installed in a cached layer for fast rebuilds."
        )
