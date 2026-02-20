import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os


class BlockStyles:
    """Docker deployment demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles

# Resolve the real Dockerfile path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_repo_root = os.path.dirname(os.path.dirname(_project_root))
_dockerfile_path = os.path.join(_repo_root, "Dockerfile")


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Deploy with Docker", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # --- 1. The StreamTeX Dockerfile ---
        st_write(bs.sub, "The StreamTeX Dockerfile", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The repository includes a production-ready Dockerfile.
            It uses uv for fast dependency installation
            and targets a specific project folder via build-arg.
        """))
        st_space("v", 1)

        # Read and display the actual Dockerfile
        try:
            with open(_dockerfile_path) as f:
                dockerfile_content = f.read()
        except FileNotFoundError:
            dockerfile_content = "# Dockerfile not found at expected path"

        show_code(dockerfile_content, language="dockerfile")
        st_space("v", 2)

        # --- 2. Build & Run ---
        st_write(bs.sub, "Build and run locally", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Build the Docker image and run it.
            The app will be available at http://localhost:8501.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Build the image
            docker build -t streamtex-app .

            # Run the container
            docker run -p 8501:8501 streamtex-app
        """), language="bash")
        st_space("v", 2)

        # --- 3. Build-arg FOLDER ---
        st_write(bs.sub, "Targeting a specific project", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use --build-arg FOLDER to deploy a specific project.
            The default target is documentation/manuals/sx_manual_intro.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Deploy a specific project
            docker build \\
                --build-arg FOLDER=projects/my_project \\
                -t my-project-app .

            docker run -p 8501:8501 my-project-app
        """), language="bash")
        st_space("v", 2)

        # --- 4. Environment variables ---
        st_write(bs.sub, "Environment variables", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The Dockerfile sets several ENV variables
            for headless operation and performance.
        """))
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
                         "STREAMLIT_SERVER_HEADLESS")
            with g.cell():
                st_write(s.large, "Run without opening a browser")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "PYTHONDONTWRITEBYTECODE")
            with g.cell():
                st_write(s.large, "Skip .pyc file creation")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "UV_LINK_MODE=copy")
            with g.cell():
                st_write(s.large, "Copy files instead of hardlinks (Docker compat)")
        st_space("v", 2)

        # --- 5. Details ---
        show_details(textwrap.dedent("""\
            The container exposes port 8501 with a health check.
            uv is installed from the official Docker image (ghcr.io/astral-sh/uv).
            Dependencies are installed in a cached layer for fast rebuilds.
        """))
