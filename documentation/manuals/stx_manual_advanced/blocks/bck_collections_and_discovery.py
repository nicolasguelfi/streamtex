"""Collections System: Multi-project management and discovery (Phase 2).

This block explains the collections system for organizing multiple projects.
Collections enable project discovery, navigation, and organization.
"""

from custom.styles import Styles as s

from blocks.helpers import show_code, show_details, show_explanation
from streamtex import Style, st_block, st_space, st_write
from streamtex.enums import Tags as t


class BlockStyles:
    """Styles for this block."""
    feature_box = Style(
        "background:rgba(100,150,200,0.1);padding:16px;border-radius:8px;border-left:4px solid rgba(100,150,200,0.5);",
        "feature_box"
    )


bs = BlockStyles


def build():
    """Build the collections system documentation block."""

    st_write(s.project.titles.page_title, "Collections: Multi-Project Management", tag=t.h1, toc_lvl="1")
    st_space("v", 1)

    show_explanation("""
The Collections System (Phase 2) enables organizing multiple projects.

Create a hub where users discover, navigate, and access different projects.

Think: Coursera with multiple courses, or a documentation portal with multiple docs.
    """)

    # ========================================================================
    # WHAT ARE COLLECTIONS?
    # ========================================================================
    st_write(s.project.titles.section_title, "What Are Collections?", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.feature_box):
        st_write(s.large, """
A **Collection** is a hub for organizing and launching multiple StreamTeX projects.
It provides a centralized entry point where users can discover and access
different courses, tutorials, or applications.

Each project is a complete, self-contained application (book, course, documentation)
running on its own port.

Examples:
- Training platform with multiple courses
- Documentation portal with different docs
- Learning path with multiple modules
    """)

    st_space("v", 2)

    # ========================================================================
    # COMPONENTS
    # ========================================================================
    st_write(s.project.titles.section_title, "Collections Components", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.project.titles.feature_title, "1. CollectionConfig - Configuration Class")
    show_code("""
from streamtex.collection import CollectionConfig, ProjectMeta

config = CollectionConfig(
    title="My Learning Hub",
    description="Curated courses for learning StreamTeX",
    cards_per_row=3,  # Number of cards per row in the grid
)

# Add projects to the collection
config.projects["intro-course"] = ProjectMeta(
    title="Introduction to StreamTeX",
    description="Learn the basics",
    cover="static/images/covers/intro.png",
    project_url="http://localhost:8502",
    order=1,
)
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "2. ProjectMeta - Project Metadata")
    show_code("""
from streamtex.collection import ProjectMeta

project = ProjectMeta(
    title="Advanced Python",          # Project name (displayed on card)
    description="Deep dive into Python",  # Brief overview
    cover="static/images/cover.png",  # Path to thumbnail image
    project_url="http://localhost:8503",  # URL where project runs
    order=1,                          # Sort order in the collection
)
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "3. st_collection() - Automatic UI")
    show_code("""
from streamtex import st_collection, CollectionConfig

config = CollectionConfig.from_toml("collection.toml")

# Automatic UI: renders title, description, and project cards grid
st_collection(config=config, home_styles=Styles)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # CONFIGURATION METHODS
    # ========================================================================
    st_write(s.project.titles.section_title, "Configuration Methods", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Method 1: TOML Configuration File (Recommended)")
    st_space("v", 0.5)
    st_write(s.medium, "Define your collection declaratively in a TOML file:")
    st_space("v", 1)

    show_code("""
# collection.toml
[collection]
title = "StreamTeX Training Collection"
description = "Introduction, Advanced, and Deployment courses"
cards_per_row = 3

[projects.intro]
title = "Introduction to StreamTeX"
description = "Learn basics: text styling, containers, grids, layouts"
project_url = "http://localhost:8502"
order = 1

[projects.advanced]
title = "Advanced Features"
description = "Master advanced: shared blocks, multi-source, deployment"
project_url = "http://localhost:8503"
order = 2

[projects.deploy]
title = "Deployment Guide"
description = "Deploy: Docker, Streamlit Cloud, Render.com, GCP, CI/CD"
project_url = "http://localhost:8504"
order = 3
    """, language="toml")

    st_space("v", 1)

    show_code("""
# book.py — load from TOML
from pathlib import Path
from streamtex.collection import CollectionConfig

config_path = Path(__file__).parent / "collection.toml"
config = CollectionConfig.from_toml(str(config_path))
    """, language="python")

    st_space("v", 2)

    st_write(s.project.titles.feature_title, "Method 2: Programmatic (Python)")
    show_code("""
from streamtex.collection import CollectionConfig, ProjectMeta

config = CollectionConfig(
    title="StreamTeX Learn",
    description="Complete learning path",
    cards_per_row=2,
)

config.projects["intro"] = ProjectMeta(
    title="Introduction",
    description="Get started with basics",
    project_url="http://localhost:8502",
    order=1,
)
config.projects["advanced"] = ProjectMeta(
    title="Advanced",
    description="Deep dive into concepts",
    project_url="http://localhost:8503",
    order=2,
)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # DISPLAY OPTIONS
    # ========================================================================
    st_write(s.project.titles.section_title, "Displaying Collections", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Option 1: st_collection() — Automatic UI")
    st_space("v", 0.5)
    st_write(s.medium, "Renders title, description, and a grid of project cards automatically:")
    st_space("v", 1)

    show_code("""
from streamtex import st_collection
from custom.styles import Styles as s

st_collection(config=config, home_styles=s)
    """, language="python")

    st_space("v", 2)

    st_write(s.project.titles.feature_title, "Option 2: st_book() — Custom Collection UI")
    st_space("v", 0.5)
    st_write(s.medium,
             "For full control over layout and design, build your own collection "
             "blocks and wire them into st_book():")
    st_space("v", 1)

    show_code("""
# book.py — custom collection UI
from streamtex import st_book
import blocks

st_book([
    blocks.bck_home,  # Your custom block with cards + styling
], paginate=False)


# blocks/bck_home.py — custom card layout
import streamlit as st
from streamtex import st_grid, st_block, st_write, Style
from streamtex.collection import CollectionConfig

config = CollectionConfig.from_toml("collection.toml")

def build():
    with st_grid(cols=config.cards_per_row, grid_style=Style("gap:24px;", "gap")):
        for key, project in config.projects.items():
            with st_block(card_style):
                st_write(s.Large, project.title)
                st_write(s.medium, project.description)
                st.link_button("Open", project.project_url)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # URL OVERRIDES
    # ========================================================================
    st_write(s.project.titles.section_title, "Environment Variable URL Overrides", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.medium,
             "Project URLs from TOML can be overridden by environment variables. "
             "This is useful for deployment where URLs differ from localhost:")
    st_space("v", 1)

    show_code("""
# Pattern: STX_URL_<PROJECT_KEY_UPPER>
# For [projects.test-intro], the env var is STX_URL_TEST_INTRO

# Example: set in Render.com, Docker, or .env
STX_URL_TEST_INTRO=https://intro.onrender.com
STX_URL_TEST_ADVANCED=https://advanced.onrender.com
    """, language="bash")

    st_space("v", 2)

    # ========================================================================
    # PROJECT VS COLLECTION
    # ========================================================================
    st_write(s.project.titles.section_title, "Project vs Collection", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, """
**Single Project** (st_book):
- One application/course/documentation
- Self-contained on one port
- Example: "Python Training Course"

**Collection** (st_collection or custom st_book):
- Multiple projects in one hub
- Project discovery and navigation
- Each project runs on its own port
- Example: "Training Platform" with Intro, Advanced, Deploy courses

**When to use Collections:**
- Multiple independent projects to manage
- Need centralized project hub
- Building platform (multi-course, multi-doc)
    """)

    st_space("v", 2)

    # ========================================================================
    # BEST PRACTICES
    # ========================================================================
    st_write(s.project.titles.section_title, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, """
**Configuration:**
- Use TOML for static collections (easier to maintain)
- Use programmatic CollectionConfig for dynamic collections (loaded from database, API, etc.)
- Always specify project_url correctly (must match running port)

**Content:**
- Use meaningful project titles and descriptive descriptions
- Use cover images for visual appeal (recommended size: 300x200px)
- Set correct order (1, 2, 3...) to control project sequence

**Deployment:**
- Test all project URLs before deploying collection
- Use STX_URL_* environment variables for production URLs
- Each project must be running on its configured port
    """)

    st_space("v", 2)

    show_details("""
Organizing large platforms:

- Break into logical sub-projects
- Each gets its own entry in collection
- Users navigate to relevant content easily
- Easier to maintain and update individually
    """)
