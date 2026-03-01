import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Hugging Face Spaces deployment demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Deploy on Hugging Face Spaces",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # --- 1. What is HF Spaces ---
        st_write(bs.sub, "What is Hugging Face Spaces?", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Hugging Face Spaces is a free hosting platform.
            It supports Docker-based apps out of the box.
            Your StreamTeX project runs as a Docker container.
        """))
        st_space("v", 2)

        # --- 2. Create a Space ---
        st_write(bs.sub, "Create a Space", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Go to huggingface.co/new-space and create a new Space.
            Choose "Docker" as the SDK.
            The Space will build your Dockerfile automatically.
        """))
        st_space("v", 1)

        show_code(file="examples/deploy/hf_create_space.txt", language="text")
        st_space("v", 2)

        # --- 3. Push the project ---
        st_write(bs.sub, "Push your project", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Add the Hugging Face Space as a git remote
            and push your code. The Space builds on push.
        """))
        st_space("v", 1)

        show_code(file="examples/deploy/hf_push.sh", language="bash")
        st_space("v", 2)

        # --- 4. Expected structure ---
        st_write(bs.sub, "Expected repository structure", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The Dockerfile must be at the repository root.
            Hugging Face detects it and builds automatically.
        """))
        st_space("v", 1)

        show_code(file="examples/deploy/hf_repo_structure.txt", language="text")
        st_space("v", 2)

        # --- 5. README configuration ---
        st_write(bs.sub, "README.md metadata", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Add YAML front matter to your README.md
            so Hugging Face knows how to configure the Space.
        """))
        st_space("v", 1)

        show_code(file="examples/deploy/hf_readme_metadata.yml", language="yaml")
        st_space("v", 2)

        # --- 6. Details ---
        show_details(textwrap.dedent("""\
            Free tier has limited CPU and RAM (2 vCPU, 16 GB RAM).
            Spaces go to sleep after ~15 min of inactivity (free tier).
            Upgrade to a paid plan for persistent uptime.
        """))
