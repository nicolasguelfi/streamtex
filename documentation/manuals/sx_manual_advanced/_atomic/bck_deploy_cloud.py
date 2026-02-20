import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Cloud deployment demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Deploy on Cloud (GCP / AWS)",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # --- 1. General approach ---
        st_write(bs.sub, "General approach", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The workflow is the same on any cloud provider:
            build the Docker image, push it to a registry,
            then pull and run it on a virtual machine.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # General workflow
            # 1. Build the Docker image locally
            # 2. Tag it for your registry
            # 3. Push to the registry
            # 4. SSH into your VM
            # 5. Pull and run the image
        """), language="text")
        st_space("v", 2)

        # --- 2. GCP (Compute Engine) ---
        st_write(bs.sub, "GCP: Google Compute Engine", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Push your image to Google Artifact Registry,
            then pull it on a Compute Engine VM.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Build and tag for GCP Artifact Registry
            docker build -t streamtex-app .
            docker tag streamtex-app \\
                REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest

            # Push to Artifact Registry
            docker push \\
                REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest

            # On the GCP VM (after SSH):
            docker pull \\
                REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest
            docker run -d -p 8501:8501 \\
                REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest
        """), language="bash")
        st_space("v", 2)

        # --- 3. AWS (EC2) ---
        st_write(bs.sub, "AWS: EC2 with ECR", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Push your image to Amazon ECR (Elastic Container Registry),
            then pull it on an EC2 instance.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Authenticate with ECR
            aws ecr get-login-password --region REGION | \\
                docker login --username AWS --password-stdin \\
                ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com

            # Build, tag and push
            docker build -t streamtex-app .
            docker tag streamtex-app \\
                ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest
            docker push \\
                ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest

            # On the EC2 instance (after SSH):
            docker pull \\
                ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest
            docker run -d -p 8501:8501 \\
                ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest
        """), language="bash")
        st_space("v", 2)

        # --- 4. Essential commands summary ---
        st_write(bs.sub, "Essential Docker commands", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=2, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Command")
            with g.cell(): st_write(s.bold + s.large, "Purpose")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "docker build -t name .")
            with g.cell():
                st_write(s.large, "Build image from Dockerfile")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "docker tag src dst")
            with g.cell():
                st_write(s.large, "Tag image for a registry")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "docker push image")
            with g.cell():
                st_write(s.large, "Upload image to registry")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "docker pull image")
            with g.cell():
                st_write(s.large, "Download image from registry")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "docker run -d -p 8501:8501")
            with g.cell():
                st_write(s.large, "Run container in background")
        st_space("v", 2)

        # --- 5. Details ---
        show_details(textwrap.dedent("""\
            Open port 8501 in your cloud firewall rules.
            For HTTPS, set up a reverse proxy (nginx) with a TLS certificate.
            Cloud costs depend on VM size; a small instance is sufficient for StreamTeX.
        """))
