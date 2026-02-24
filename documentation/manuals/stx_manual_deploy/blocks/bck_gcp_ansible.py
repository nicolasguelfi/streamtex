"""Block — Deploy on GCP Compute Engine with Ansible."""

import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os

# Resolve paths to ansible files
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(_project_root)))
_deploy_yml_path = os.path.join(_repo_root, "deploy", "ansible", "deploy.yml")
_inventory_path = os.path.join(_repo_root, "deploy", "ansible", "inventory.ini.example")


class BlockStyles:
    """GCP Ansible block styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "GCP VM + Ansible", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(
            "Full control deployment on a Google Cloud Compute Engine VM. "
            "Ansible automates everything: git clone, venv setup, systemd service. "
            "Best for always-on apps where you want total control."
        )
        st_space("v", 2)

        # --- Prerequisites ---
        st_write(bs.sub, "Prerequisites", toc_lvl="+1")
        st_space("v", 1)

        with st_grid(cols=2, cell_styles=(
            s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout
        )) as g:
            with g.cell(): st_write(s.bold + s.large, "Requirement")
            with g.cell(): st_write(s.bold + s.large, "Details")

            with g.cell(): st_write(s.large, "GCP Account")
            with g.cell(): st_write(s.large, "Billing enabled, Compute Engine API active")

            with g.cell(): st_write(s.large, "VM Instance")
            with g.cell(): st_write(s.large,
                                    "e2-micro or larger, Ubuntu 22.04, HTTP/HTTPS allowed")

            with g.cell(): st_write(s.large, "SSH Key")
            with g.cell(): st_write(s.large,
                                    "ed25519 key added to GCP Metadata > SSH Keys")

            with g.cell(): st_write(s.large, "Ansible")
            with g.cell(): st_write(s.large,
                                    "Installed locally (sudo apt install ansible)")

            with g.cell(): st_write(s.large, "GitHub Repo")
            with g.cell(): st_write(s.large,
                                    "Your StreamTeX project pushed to GitHub")

        st_space("v", 2)

        # --- Step 1: Create VM ---
        st_write(bs.sub, "Step 1: Create the VM", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # In GCP Console:
            # 1. Compute Engine → VM instances → Create Instance
            # 2. Name: streamtex-vm
            # 3. Region/Zone: your choice
            # 4. Machine type: e2-micro (sufficient for most projects)
            # 5. Boot disk: Ubuntu 22.04
            # 6. Firewall: Allow HTTP + HTTPS traffic
            # 7. Note the External IP (e.g. 12.34.56.78)
        """), language="text")
        st_space("v", 2)

        # --- Step 2: SSH ---
        st_write(bs.sub, "Step 2: Configure SSH", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Generate SSH key (if not already done)
            ssh-keygen -t ed25519 -C "your-email@example.com"

            # Copy the public key
            cat ~/.ssh/id_ed25519.pub
            # → Paste in GCP > Compute Engine > Metadata > SSH Keys

            # Test SSH access
            ssh -i ~/.ssh/id_ed25519 your-user@12.34.56.78
        """), language="bash")
        st_space("v", 2)

        # --- Step 3: Configure Ansible ---
        st_write(bs.sub, "Step 3: Configure Ansible", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "Copy the inventory template and fill in your values. "
            "Then edit deploy.yml with your project details."
        )
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Copy the inventory template
            cp deploy/ansible/inventory.ini.example deploy/ansible/inventory.ini

            # Edit with your VM IP and username
            # Then edit deploy/ansible/deploy.yml with your repo URL and project folder
        """), language="bash")
        st_space("v", 1)

        # Show inventory template
        try:
            with open(_inventory_path) as f:
                inventory_content = f.read()
        except FileNotFoundError:
            inventory_content = "# inventory.ini.example not found"

        show_code(inventory_content, language="ini")
        st_space("v", 2)

        # --- Step 4: The playbook ---
        st_write(bs.sub, "Step 4: The Ansible playbook", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(
            "The playbook installs system packages, clones your repo, "
            "creates a Python venv, installs dependencies, "
            "and configures a systemd service for automatic restarts."
        )
        st_space("v", 1)

        try:
            with open(_deploy_yml_path) as f:
                playbook_content = f.read()
        except FileNotFoundError:
            playbook_content = "# deploy.yml not found"

        show_code(playbook_content, language="yaml")
        st_space("v", 2)

        # --- Step 5: Deploy ---
        st_write(bs.sub, "Step 5: Deploy and verify", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Run the playbook
            ansible-playbook -i deploy/ansible/inventory.ini deploy/ansible/deploy.yml

            # SSH into the VM and check the service
            ssh your-user@12.34.56.78
            sudo systemctl status streamtex

            # Open in browser
            # http://12.34.56.78:8501
        """), language="bash")
        st_space("v", 2)

        # --- Maintenance ---
        st_write(bs.sub, "Updating the deployment", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Push changes to GitHub, then re-run the playbook:
            ansible-playbook -i deploy/ansible/inventory.ini deploy/ansible/deploy.yml
            # The playbook does git pull + restarts the service
        """), language="bash")
        st_space("v", 2)

        show_details(
            "Open port 8501 in GCP firewall rules (VPC Network > Firewall). "
            "For HTTPS, set up a reverse proxy (nginx/caddy) with Let's Encrypt. "
            "Cost: e2-micro is ~$5/month. Larger instances for heavier projects. "
            "For multiple projects, run each on a different port and use nginx to route."
        )
