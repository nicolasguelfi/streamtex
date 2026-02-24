"""Block — Deploy on Hugging Face Spaces."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """HuggingFace block styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "HuggingFace Spaces", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(
            "Free Docker-based hosting on Hugging Face. "
            "2 vCPU, 16 GB RAM on the free tier. "
            "The native Streamlit SDK is deprecated; Docker is now required."
        )
        st_space("v", 2)

        # --- Prerequisites ---
        st_write(bs.sub, "Prerequisites", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Install git-lfs (macOS)
            brew install git git-lfs

            # Install git-lfs (Linux)
            sudo apt install git git-lfs

            # Authenticate with HuggingFace
            pip install huggingface-hub
            huggingface-cli login
            # Create a token with Write scope at:
            # Settings → Access Tokens → New token
        """), language="bash")
        st_space("v", 2)

        # --- Automated deployment ---
        st_write(bs.sub, "Automated deployment", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Use the deployment script. It checks prerequisites, "
            "runs preflight validation, configures the git remote, "
            "sets up LFS, and offers to push."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Deploy the default project
            ./deploy/huggingface.sh \\
                https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE

            # Deploy a specific project
            ./deploy/huggingface.sh \\
                https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE \\
                projects/project_aiai18h
        """), language="bash")
        st_space("v", 2)

        # --- Manual steps ---
        st_write(bs.sub, "Manual deployment", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # 1. Create a Docker Space on huggingface.co/new-space

            # 2. Add the HF remote
            git remote add hf \\
                https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE

            # 3. Set up Git LFS
            git lfs install
            git lfs track "*.png" "*.jpg" "*.webp" "*.mp4" "*.gif"

            # 4. Push to HuggingFace
            git push hf main
        """), language="bash")
        st_space("v", 2)

        # --- README metadata ---
        st_write(bs.sub, "README.md metadata", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "HuggingFace reads YAML front-matter from README.md to configure the Space. "
            "A template is available at deploy/templates/hf-readme.yml."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            ---
            title: My StreamTeX App
            emoji: 🚀
            colorFrom: red
            colorTo: red
            sdk: docker
            app_port: 8501
            tags:
            - streamlit
            pinned: false
            short_description: My StreamTeX project
            ---
        """), language="yaml")
        st_space("v", 2)

        show_details(
            "Free tier: apps may sleep after inactivity. "
            "To deploy a different project, change the ARG FOLDER default in the Dockerfile "
            "or configure build args in the Space settings. "
            "If push is rejected, try: git pull hf main --allow-unrelated-histories"
        )
