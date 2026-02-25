"""Project cards for the collection home page."""

import os

import streamlit as st
from streamtex import *
from streamtex.styles import Style
from custom.styles import Styles as s

# URLs: environment variables override localhost defaults (set by Render envVars)
_URL_INTRO = os.environ.get("STX_URL_TEST_INTRO", "http://localhost:8502")
_URL_ADVANCED = os.environ.get("STX_URL_TEST_ADVANCED", "http://localhost:8503")
_URL_DEPLOY = os.environ.get("STX_URL_TEST_DEPLOY", "http://localhost:8504")


class BlockStyles:
    """Styles for the project cards."""

    # Card container with modern dark mode styling
    card_container = Style.create(
        s.container.bg_colors.dark_bg_secondary
        + "border-radius:12px;padding:24px;transition:all 0.3s ease;"
        + "box-shadow:0 4px 16px rgba(0,0,0,0.3);",
        "card_container"
    )

    # Card header with icon space
    card_header = Style.create(
        s.large + s.text.weights.bold_weight + s.text.colors.white,
        "card_header"
    )

    # Card description text
    card_description = Style.create(
        s.medium + s.text.colors.white + "opacity:0.85;",
        "card_description"
    )

    # Project title in card
    project_title = Style.create(
        s.large + s.text.weights.bold_weight + s.text.colors.white,
        "project_title"
    )

    # Grid gap style
    grid_with_gap = Style(
        "gap:24px;",
        "grid_with_gap"
    )


bs = BlockStyles


def build():
    """Render the project cards section."""

    # ========================================================================
    # PROJECTS: 2-column grid with modern cards
    # ========================================================================
    st_space("v", 2)

    with st_grid(cols=3, grid_style=bs.grid_with_gap):

        # ====================================================================
        # PROJECT 1: Introduction
        # ====================================================================
        with st_block(bs.card_container):
            st_space("v", 1)

            # Icon + title area
            st_write(
                s.huge + "text-align:center;",
                "📚"
            )
            st_space("v", 1)

            # Project title
            st_write(
                bs.project_title + "text-align:center;",
                "Introduction to StreamTeX"
            )
            st_space("v", 1)

            # Description
            st_write(
                bs.card_description + "text-align:center;",
                "Learn the basics: text styling, containers, grids, layouts, and more"
            )
            st_space("v", 2)

            # Button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button(
                    "🚀 Open Course",
                    _URL_INTRO,
                    use_container_width=True
                )

            st_space("v", 1)

        # ====================================================================
        # PROJECT 2: Advanced
        # ====================================================================
        with st_block(bs.card_container):
            st_space("v", 1)

            # Icon + title area
            st_write(
                s.huge + "text-align:center;",
                "⚡"
            )
            st_space("v", 1)

            # Project title
            st_write(
                bs.project_title + "text-align:center;",
                "Advanced Features & Architecture"
            )
            st_space("v", 1)

            # Description
            st_write(
                bs.card_description + "text-align:center;",
                "Master advanced concepts: shared blocks, multi-source resolution, and deployment"
            )
            st_space("v", 2)

            # Button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button(
                    "🚀 Open Course",
                    _URL_ADVANCED,
                    use_container_width=True
                )

            st_space("v", 1)

        # ====================================================================
        # PROJECT 3: Deployment Guide
        # ====================================================================
        with st_block(bs.card_container):
            st_space("v", 1)

            # Icon + title area
            st_write(
                s.huge + "text-align:center;",
                "🚀"
            )
            st_space("v", 1)

            # Project title
            st_write(
                bs.project_title + "text-align:center;",
                "Deployment Guide"
            )
            st_space("v", 1)

            # Description
            st_write(
                bs.card_description + "text-align:center;",
                "Deploy StreamTeX projects: Docker, Streamlit Cloud, Render.com, GCP, CI/CD"
            )
            st_space("v", 2)

            # Button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button(
                    "🚀 Open Course",
                    _URL_DEPLOY,
                    use_container_width=True
                )

            st_space("v", 1)

    st_space("v", 3)

    # ========================================================================
    # FOOTER: About / Info
    # ========================================================================
    st.divider()
    st_space("v", 2)

    st_write(
        s.medium + s.text.colors.white + "opacity:0.6;text-align:center;",
        "StreamTeX Training Collection © 2026 | "
        "Interactive documentation for modern web education"
    )

    st_space("v", 2)
