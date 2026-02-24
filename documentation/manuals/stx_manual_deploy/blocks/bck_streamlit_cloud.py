"""Block — Deploy on Streamlit Community Cloud."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Streamlit Cloud block styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Streamlit Community Cloud", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(
            "The simplest deployment option. Completely free, no Docker required. "
            "Connect your GitHub repo and Streamlit Cloud deploys automatically. "
            "Best for quick demos and prototyping."
        )
        st_space("v", 2)

        # --- Limitations ---
        st_write(bs.sub, "Limitations", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=2, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Aspect")
            with g.cell(): st_write(s.bold + s.large, "Limitation")

            with g.cell(): st_write(s.large, "Docker")
            with g.cell(): st_write(s.project.colors.warning_red + s.large,
                                    "Not supported")
            with g.cell(): st_write(s.large, "Custom domain")
            with g.cell(): st_write(s.project.colors.warning_red + s.large,
                                    "Not available (*.streamlit.app only)")
            with g.cell(): st_write(s.large, "Memory")
            with g.cell(): st_write(s.large, "~1 GB RAM per app")
            with g.cell(): st_write(s.large, "Sleep")
            with g.cell(): st_write(s.large, "After ~12h without traffic")
            with g.cell(): st_write(s.large, "Repository")
            with g.cell(): st_write(s.large, "Must be on GitHub (public or private with admin)")
            with g.cell(): st_write(s.large, "Hosting")
            with g.cell(): st_write(s.large, "US only")

        st_space("v", 2)

        # --- Step 1: Generate requirements.txt ---
        st_write(bs.sub, "Step 1: Generate requirements.txt", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Streamlit Cloud does not support uv or pyproject.toml. "
            "Use the provided script to generate a classic requirements.txt."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Generate requirements.txt from pyproject.toml
            ./deploy/gen-requirements.sh > requirements.txt

            # Commit to the repository
            git add requirements.txt
            git commit -m "Add requirements.txt for Streamlit Cloud"
            git push
        """), language="bash")
        st_space("v", 2)

        # --- Step 2: Create the app ---
        st_write(bs.sub, "Step 2: Create the app", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Steps on share.streamlit.io:
            # 1. Click "New app"
            # 2. Select your GitHub repo
            # 3. Set Main file path:
            #    documentation/manuals/stx_manual_intro/book.py
            #    OR: projects/your_project/book.py
            # 4. Set Python version to 3.13 (optional)
            # 5. Click "Deploy"
        """), language="text")
        st_space("v", 2)

        # --- Step 3: Verify ---
        st_write(bs.sub, "Step 3: Verify and update", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Your app is available at https://your-app-name.streamlit.app. "
            "Streamlit Cloud auto-deploys on every push to the configured branch."
        )
        st_space("v", 2)

        show_details(
            "Streamlit Cloud reads .streamlit/config.toml from the project folder automatically. "
            "Some values are overridden: server.headless is forced to true, "
            "server.port is managed by the platform. "
            "Regenerate requirements.txt if you add new dependencies."
        )
