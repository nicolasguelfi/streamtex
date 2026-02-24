"""Collection management and programmatic configuration."""

from custom.styles import Styles as s

from streamtex import *
from streamtex.enums import Tags as t
from streamtex.styles import Style


class BlockStyles:
    """Styles for collection management demo."""

    heading = s.project.titles.main_title + s.center_txt
    section = s.project.titles.section_title
    code_box = Style(
        "background:rgba(40,40,40,0.8);padding:16px;border-radius:8px;overflow:auto;",
        "code_box",
    )
    info_box = Style(
        "background:rgba(100,150,200,0.1);padding:16px;border-radius:8px;",
        "info_box",
    )


bs = BlockStyles


def build():
    """Demonstrate collection configuration and management."""

    st_write(
        bs.heading,
        "Phase 2: Collection Management",
        tag=t.h1,
        toc_lvl="1",
    )
    st_space("v", 2)

    st_write(
        s.large + s.text.colors.reset + "opacity:0.8;",
        "Learn how to create and manage multi-project collections programmatically",
    )
    st_space("v", 3)

    # Section 1: Collection Basics
    st_write(bs.section, "What is a Collection?", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            "A collection is a hub for organizing and launching multiple StreamTeX projects. "
            "It provides a centralized entry point where users can discover and access "
            "different courses, tutorials, or applications.",
        )

    st_space("v", 2)

    # Section 2: CollectionConfig
    st_write(bs.section, "CollectionConfig Class", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Create collections programmatically using CollectionConfig:",
    )
    st_space("v", 1)

    with st_block(bs.code_box):
        st_code("python", """\
from streamtex.collection import CollectionConfig, ProjectMeta

# Create a collection configuration
config = CollectionConfig(
    title="My Learning Hub",
    description="Curated courses for learning StreamTeX",
    cards_per_row=2,
)

# Add projects programmatically
config.projects["intro-course"] = ProjectMeta(
    title="Introduction to StreamTeX",
    description="Learn the basics",
    cover="static/images/covers/intro.png",
    project_url="http://localhost:8502",
    order=1,
)
""")

    st_space("v", 2)

    # Section 3: ProjectMeta
    st_write(bs.section, "ProjectMeta: Project Information", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Each project in a collection has metadata:",
    )
    st_space("v", 1)

    with st_list(list_type="ul"):
        st_write(s.medium, "title — Project name (displayed on card)")
        st_write(s.medium, "description — Brief overview")
        st_write(s.medium, "cover — Path to thumbnail image")
        st_write(s.medium, "project_url — URL where project runs (e.g., http://localhost:8502)")
        st_write(s.medium, "order — Sort order in the collection (1, 2, 3...)")

    st_space("v", 2)

    # Section 4: TOML Configuration
    st_write(bs.section, "TOML Configuration (Declarative)", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Most common: Define your collection in a TOML file:",
    )
    st_space("v", 1)

    with st_block(bs.code_box):
        st_code("toml", """\
[collection]
title = "StreamTeX Training Collection"
description = "Introduction and Advanced courses"
cards_per_row = 2

[projects.intro]
title = "Introduction to StreamTeX"
description = "Learn the basics"
cover = "static/images/covers/intro.png"
project_url = "http://localhost:8502"
order = 1

[projects.advanced]
title = "Advanced Features"
description = "Master advanced concepts"
cover = "static/images/covers/advanced.png"
project_url = "http://localhost:8503"
order = 2
""")

    st_space("v", 2)

    # Section 5: Load from TOML
    st_write(bs.section, "Load Collection from TOML", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Use CollectionConfig.from_toml() to load from file:",
    )
    st_space("v", 1)

    with st_block(bs.code_box):
        st_code("python", """\
from streamtex.collection import CollectionConfig

# Load from TOML file
config_path = Path(__file__).parent / "collection.toml"
config = CollectionConfig.from_toml(str(config_path))

# Use in st_book() or st_collection()
from streamtex import st_collection
st_collection(config=config, home_styles=Styles)
""")

    st_space("v", 2)

    # Section 6: Display Collections
    st_write(bs.section, "Displaying Collections", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Two ways to display a collection:",
    )
    st_space("v", 1)

    with st_list(list_type="ol"):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "st_collection()"),
            " — Automatic collection UI (with query params for project selection)",
        )
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "st_book()"),
            " — Custom collection UI (build your own with blocks and st_link_button)",
        )

    st_space("v", 2)

    # Section 7: Practical Example
    st_write(bs.section, "Practical Example: st_collection()", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.code_box):
        st_code("python", """\
# book.py
import streamlit as st
from streamtex import st_collection, CollectionConfig
from custom.styles import Styles as s
from pathlib import Path

st.set_page_config(
    page_title="Learning Hub",
    layout="wide",
)

# Load configuration
config_path = Path(__file__).parent / "collection.toml"
config = CollectionConfig.from_toml(str(config_path))

# Display collection with home_styles
st_collection(config=config, home_styles=s)
""")

    st_space("v", 2)

    # Section 8: Custom Collection UI
    st_write(bs.section, "Custom Collection UI with st_book()", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "For advanced layouts, create custom collection blocks:",
    )
    st_space("v", 1)

    with st_block(bs.code_box):
        st_code("python", """\
# Custom collection block
import streamlit as st
from streamtex import st_grid, st_block, st_write, st_book

config = CollectionConfig.from_toml("collection.toml")

# book.py uses st_book with custom blocks
st_book([
    blocks.bck_collection_home,  # Your custom block
], paginate=False)

# bck_collection_home.py
def build():
    with st_grid(cols=2, grid_style=Style("gap:24px;", "gap")):
        for project_key, project in config.projects.items():
            with st_block(card_style):
                st_write(s.huge, "📚")  # Custom emoji
                st_write(s.Large, project.title)
                st_write(s.medium, project.description)
                st.link_button("Open", project.project_url)
""")

    st_space("v", 2)

    # Section 9: Best Practices
    st_write(bs.section, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    with st_list(list_type="ol"):
        st_write(
            s.medium,
            "Use TOML for static collections (easier to maintain)",
        )
        st_write(
            s.medium,
            "Use programmatic CollectionConfig for dynamic collections (loaded from database, API, etc.)",
        )
        st_write(
            s.medium,
            "Always specify project_url correctly (must match running port)",
        )
        st_write(
            s.medium,
            "Use cover images for visual appeal (recommended size: 300x200px)",
        )
        st_write(
            s.medium,
            "Set correct order (1, 2, 3...) to control project sequence",
        )
        st_write(
            s.medium,
            "Test all project URLs before deploying collection",
        )

    st_space("v", 3)
