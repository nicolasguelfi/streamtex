"""Collection home — gradient header + level badge + project cards."""

import os

import streamlit as st
from custom.styles import Styles as s

import streamtex as stx
from streamtex import *
from streamtex.enums import Tags as t
from streamtex.styles import Style

# URLs: environment variables override localhost defaults (set by Render envVars)
_URL_INTRO = os.environ.get("STX_URL_TEST_INTRO", "http://localhost:8502")
_URL_ADVANCED = os.environ.get("STX_URL_TEST_ADVANCED", "http://localhost:8503")
_URL_DEPLOY = os.environ.get("STX_URL_TEST_DEPLOY", "http://localhost:8504")


class BlockStyles:
    """Styles for the collection home page."""

    # --- Header ---
    header = Style(
        "background: linear-gradient(135deg, #f46b45 0%, #eea849 100%); "
        "padding: 40px 20px; border-radius: 8px;",
        "collection_header",
    )
    level_box = Style(
        "background: rgba(46, 196, 182, 0.08); "
        "border-left: 4px solid #2EC4B6; "
        "padding: 20px 24px; border-radius: 0 8px 8px 0;",
        "collection_level_box",
    )
    level_label = Style(
        "color: #2EC4B6; font-weight: bold; font-size: 14pt; "
        "text-transform: uppercase; letter-spacing: 2px;",
        "collection_level_label",
    )
    description = s.large + s.project.colors.neutral_gray

    # --- Cards ---
    card_container = Style.create(
        s.container.bg_colors.dark_bg_secondary
        + "border-radius:12px;padding:24px;transition:all 0.3s ease;"
        + "box-shadow:0 4px 16px rgba(0,0,0,0.3);",
        "card_container",
    )
    card_description = Style.create(
        s.medium + s.text.colors.white + "opacity:0.85;",
        "card_description",
    )
    project_title = Style.create(
        s.large + s.text.weights.bold_weight + s.text.colors.white,
        "project_title",
    )
    grid_with_gap = stx.StxStyles.container.grid.gap_24

    # --- Footer ---
    footer = Style.create(
        s.medium + s.text.colors.white + "opacity:0.6;text-align:center;",
        "collection_footer",
    )


bs = BlockStyles


def build():
    """Render the collection home: header, level badge, project cards."""

    # === Gradient header ===
    st_space("v", 1)
    with st_block(bs.header):
        st_write(
            stx.StxStyles.huge + stx.StxStyles.text.colors.white,
            "StreamTeX Training Course",
            tag=t.div,
        )
        st_write(
            stx.StxStyles.large + stx.StxStyles.text.colors.white,
            "A Streamlit-based content rendering framework",
            tag=t.div,
        )
    st_space("v", 1)

    # === Level badge ===
    with st_block(bs.level_box):
        st_write(bs.level_label, "Collection Hub")
        st_space("v", 0.5)
        st_write(
            s.Large + s.text.weights.bold_weight,
            "Discover and Explore Our Learning Paths",
        )
        st_space("v", 1)
        st_write(
            bs.description,
            "Browse the curated StreamTeX training courses. "
            "Each course is self-contained and can be launched independently.",
        )
        st_space("v", 1)
        with st_list(list_type="ul"):
            st_write(s.medium, "Introduction: text, styles, grids, lists, images, code, export")
            st_write(s.medium, "Advanced: shared blocks, collections, deployment, data visualization")
            st_write(s.medium, "Shared blocks: reusable components across all courses")

    # === Project cards ===
    st_space("v", 2)

    with st_grid(cols=3, responsive=True, grid_style=bs.grid_with_gap):

        # Card 1: Introduction
        with st_block(bs.card_container):
            st_space("v", 1)
            st_write(s.huge + "text-align:center;", "📚")
            st_space("v", 1)
            st_write(bs.project_title + "text-align:center;", "Introduction to StreamTeX")
            st_space("v", 1)
            st_write(
                bs.card_description + "text-align:center;",
                "Learn the basics: text styling, containers, grids, layouts, and more",
            )
            st_space("v", 2)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button("🚀 Open Course", _URL_INTRO, use_container_width=True)
            st_space("v", 1)

        # Card 2: Advanced
        with st_block(bs.card_container):
            st_space("v", 1)
            st_write(s.huge + "text-align:center;", "⚡")
            st_space("v", 1)
            st_write(bs.project_title + "text-align:center;", "Advanced Features & Architecture")
            st_space("v", 1)
            st_write(
                bs.card_description + "text-align:center;",
                "Master advanced concepts: shared blocks, multi-source resolution, and deployment",
            )
            st_space("v", 2)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button("🚀 Open Course", _URL_ADVANCED, use_container_width=True)
            st_space("v", 1)

        # Card 3: Deployment Guide
        with st_block(bs.card_container):
            st_space("v", 1)
            st_write(s.huge + "text-align:center;", "🚀")
            st_space("v", 1)
            st_write(bs.project_title + "text-align:center;", "Deployment Guide")
            st_space("v", 1)
            st_write(
                bs.card_description + "text-align:center;",
                "Deploy StreamTeX projects: Docker, Streamlit Cloud, Render.com, GCP, CI/CD",
            )
            st_space("v", 2)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button("🚀 Open Course", _URL_DEPLOY, use_container_width=True)
            st_space("v", 1)

    # === Footer ===
    st_space("v", 3)
    st.divider()
    st_space("v", 2)
    st_write(
        bs.footer,
        "StreamTeX Training Collection © 2026 | "
        "Interactive documentation for modern web education",
    )
    st_space("v", 2)
